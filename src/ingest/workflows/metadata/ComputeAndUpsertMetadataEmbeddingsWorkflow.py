import asyncio
from datetime import timedelta
from typing import List

from temporalio import workflow

from shared.const import OLLAMA_EMBEDDING_TASK_QUEUE, VECTOR_STORE_TASK_QUEUE
from shared.models.model_metadata import Category, ModelMetadata, Person, \
	ProgrammingLanguage, Tag
from shared.models.vector import VectorPoint

with workflow.unsafe.imports_passed_through():
	from shared.activities.llm_activities import LLMActivities
	from shared.activities.vector_store_activities import VectorStoreActivities



@workflow.defn
class ComputeAndUpsertMetadataEmbeddingsWorkflow:
	def _handle_programming_languages(self,
	                                  languages: List[ProgrammingLanguage],
	                                  desc: str) -> str:
		lang_names = [lang.name for lang in languages] if languages else []
		return f"{desc}: {', '.join(lang_names)}"

	def _handle_authors(self, authors: List[Person], desc: str) -> str:
		author_texts = []
		for author in authors:
			author_text = f"{author.givenName} {author.familyName} ({author.affiliation.name})"
			author_texts.append(author_text)
		return f"{desc}: {'; '.join(author_texts)}"

	def _handle_categories(self, categories: List[Category], desc: str) -> str:
		category_names = [cat.name for cat in categories] if categories else []
		return f"{desc}: {', '.join(category_names)}"

	def _handle_tags(self, tags: List[Tag], desc: str) -> str:
		tag_names = [tag.name for tag in tags] if tags else []
		return f"{desc}: {', '.join(tag_names)}"

	async def _compute_embedding(self, text: str):
		return await workflow.execute_activity_method(
			LLMActivities.compute_embedding,
			task_queue=OLLAMA_EMBEDDING_TASK_QUEUE,
			args=[text],
			heartbeat_timeout=timedelta(seconds=2),
            schedule_to_close_timeout=timedelta(seconds=10)
		)

	async def _upsert_vector_points(self, collection_name: str, points: list):

		await workflow.execute_activity_method(
			VectorStoreActivities.upsert_metadata_vector_points,
			args=[collection_name, points],
			task_queue=VECTOR_STORE_TASK_QUEUE,
			heartbeat_timeout=timedelta(seconds=2),
            schedule_to_close_timeout=timedelta(seconds=10)
		)

	@workflow.run
	async def run(self, model_id: str, model_metadata: ModelMetadata):
		embedding_tasks = []
		field_names = []

		special_handlers = {
			'programming_languages': self._handle_programming_languages,
			'authors': self._handle_authors,
			'categories': self._handle_categories,
			'tags': self._handle_tags
		}

		# Generate embedding tasks for each field
		for field_name, field_value in model_metadata.__dict__.items():
			if field_value is not None:
				field_desc = model_metadata.__class__.__dataclass_fields__[
					field_name].metadata["desc"]

				if field_name in special_handlers:
					embedding_text = special_handlers[field_name](field_value,
					                                              field_desc)
				else:
					embedding_text = f"{field_desc}: {str(field_value)}"

				# Create coroutine instead of task
				embedding_tasks.append(self._compute_embedding(embedding_text))
				field_names.append(field_name)

		# Await all embedding computations in parallel
		vectors = await asyncio.gather(*embedding_tasks)

		# Create vector points from results
		points = [
			VectorPoint(
				id=f"{model_id}_{field_name}",
				vector=vector,
				payload={
					"model_id": model_id,
					"field_name": field_name
				}
			)
			for field_name, vector in zip(field_names, vectors)
		]

		# Upsert all vector points
		await self._upsert_vector_points("model_metadata_embeddings", points)

		workflow.logger.info(
			"ComputeAndUpsertMetadataEmbeddingsWorkflow completed.")