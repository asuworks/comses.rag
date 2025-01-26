from typing import List, Tuple

from temporalio import activity

from shared.models.base import DocSection


class ModelDocsActivities:
	@activity.defn
	def convert_pdf_to_markdown(self,
	                          docs_file_path: str) -> Tuple[str, str]:
		activity.logger.warning(f"Starting activity convert_pdf_to_markdown {docs_file_path}")

		return "markdown_local_path", "image_folder_local_path"

	@activity.defn
	def split_markdown(self, markdown_local_path: str) -> List[DocSection]:
		"""
		Creates the main Model object from ModelMetadata
		@returns model_id
		"""
		activity.logger.warning(
			"Starting activity create_model_from_metadata")
		return []