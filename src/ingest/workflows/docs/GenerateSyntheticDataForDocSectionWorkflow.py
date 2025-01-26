import asyncio
from typing import List

from temporalio import workflow

from ingest.workflows.docs.GenerateSyntheticDataForChunksWorkflow import \
	GenerateSyntheticDataForChunksWorkflow
from shared.activities.llm_activities import LLMActivities
from shared.models.base import DocSection


@workflow.defn
class GenerateSyntheticDataForDocSectionWorkflow:
	@workflow.run
	async def run(self, doc_section: DocSection,
	              title_breadcrumbs: List[str]) -> DocSection:
		workflow.logger.info(
			f"Starting GenerateSyntheticDataForDocSectionWorkflow for {doc_section.title}")

		context = {
			"title_breadcrumbs": title_breadcrumbs,
			"title": doc_section.title
		}

		doc_section_tasks = [
			workflow.execute_activity(
				LLMActivities.add_context_to_doc_section,
				args=[doc_section, context],
				task_queue="llm_task_queue"
			),
			workflow.execute_activity(
				LLMActivities.add_doc_section_summary,
				args=[doc_section],
				task_queue="llm_task_queue"
			),
			workflow.execute_activity(
				LLMActivities.add_doc_section_qas,
				args=[doc_section],
				task_queue="llm_task_queue"
			)
		]

		chunk_task = workflow.execute_child_workflow(
			GenerateSyntheticDataForChunksWorkflow.run,
			args=[doc_section.chunks, title_breadcrumbs, doc_section.content]
		)

		results = await asyncio.gather(*doc_section_tasks, chunk_task)

		# Merge the results back into the doc_section
		for result in results[:-1]:  # Exclude the last result, which is from the chunk workflow
			doc_section = GenerateSyntheticDataForDocSectionWorkflow.merge_doc_section(
				doc_section, result)

		doc_section.chunks = results[-1]  # Update chunks with the result from GenerateSyntheticDataForChunksWorkflow

		workflow.logger.info(
			f"Completed GenerateSyntheticDataForDocSectionWorkflow for {doc_section.title}")
		return doc_section

	@staticmethod
	def merge_doc_section(original: DocSection, updated: DocSection) -> DocSection:
		if hasattr(updated, 'content_with_context'):
			original.content_with_context = updated.content_with_context
		if hasattr(updated, 'summary'):
			original.summary = updated.summary
		if hasattr(updated, 'qas'):
			original.qas = updated.qas
		return original