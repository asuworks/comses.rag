import asyncio
from typing import List

from temporalio import workflow

from ingest.workflows.docs.GenerateSyntheticDataForDocSectionWorkflow import \
	GenerateSyntheticDataForDocSectionWorkflow
from shared.models.base import DocSection, ModelDoc


@workflow.defn
class GenerateSyntheticDataForModelDocWorkflow:
	@workflow.run
	async def run(self, model_doc: ModelDoc) -> ModelDoc:
		workflow.logger.info(
			"Starting GenerateSyntheticDataForModelDocWorkflow")

		# process all doc sections
		doc_sections_map = self.create_doc_sections_map(model_doc.doc_sections)
		doc_section_tasks = [self.process_doc_section(section, doc_sections_map)
		                     for section in model_doc.doc_sections]
		updated_doc_sections = await asyncio.gather(*doc_section_tasks)

		model_doc.doc_sections = updated_doc_sections

		workflow.logger.info(
			"GenerateSyntheticDataForModelDocWorkflow completed.")
		return model_doc

	@staticmethod
	def create_doc_sections_map(doc_sections: List[DocSection]) -> dict:
		return {section.id: section for section in doc_sections}

	@staticmethod
	def get_title_breadcrumbs(doc_section: DocSection,
	                          doc_sections_map: dict) -> List[str]:
		breadcrumbs = [doc_section.title]
		current_section = doc_section
		while current_section.parent:
			parent_section = doc_sections_map[current_section.parent.id]
			breadcrumbs.insert(0, parent_section.title)
			current_section = parent_section
		return breadcrumbs

	@staticmethod
	async def process_doc_section(doc_section: DocSection,
	                              doc_sections_map: dict) -> DocSection:
		title_breadcrumbs = GenerateSyntheticDataForModelDocWorkflow.get_title_breadcrumbs(
			doc_section, doc_sections_map)

		updated_doc_section = await workflow.execute_child_workflow(
			GenerateSyntheticDataForDocSectionWorkflow.run,
			args=[doc_section, title_breadcrumbs]
		)

		return updated_doc_section