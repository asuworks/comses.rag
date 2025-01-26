import asyncio
from typing import List

from temporalio import workflow

from shared.activities.llm_activities import LLMActivities
from shared.models.base import Chunk


@workflow.defn
class GenerateSyntheticDataForChunksWorkflow:
	@workflow.run
	async def run(self, chunks: List[Chunk], title_breadcrumbs: List[str],
	              doc_section_content: str) -> List[Chunk]:
		workflow.logger.info("Starting GenerateSyntheticDataForChunksWorkflow")

		chunk_tasks = [
			self.process_chunk(chunk, title_breadcrumbs, doc_section_content)
			for chunk in chunks]
		updated_chunks = await asyncio.gather(*chunk_tasks)

		workflow.logger.info("Completed GenerateSyntheticDataForChunksWorkflow")
		return updated_chunks

	@staticmethod
	async def process_chunk(chunk: Chunk, title_breadcrumbs: List[str],
	                        doc_section_content: str) -> Chunk:
		context = {
			"doc_section_content": doc_section_content,
			"title_breadcrumbs": title_breadcrumbs
		}

		tasks = [
			workflow.execute_activity(
				LLMActivities.add_context_to_chunk,
				args=[chunk, context],
				task_queue="llm_task_queue"
			),
			workflow.execute_activity(
				LLMActivities.add_chunk_summary,
				args=[chunk],
				task_queue="llm_task_queue"
			),
			workflow.execute_activity(
				LLMActivities.add_chunk_qas,
				args=[chunk],
				task_queue="llm_task_queue"
			)
		]
		results = await asyncio.gather(*tasks)

		# Merge the results back into the chunk
		for result in results:
			chunk = GenerateSyntheticDataForChunksWorkflow.merge_chunk(chunk,
			                                                           result)

		return chunk

	@staticmethod
	def merge_chunk(original: Chunk, updated: Chunk) -> Chunk:
		if hasattr(updated, 'content_with_context'):
			original.content_with_context = updated.content_with_context
		if hasattr(updated, 'summary'):
			original.summary = updated.summary
		if hasattr(updated, 'qas'):
			original.qas = updated.qas
		return original