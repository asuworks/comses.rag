from datetime import timedelta
from typing import List

from temporalio import workflow
from temporalio.workflow import ChildWorkflowCancellationType, ParentClosePolicy

from ingest.workflows.docs.ComputeAndUpsertModelDocEmbeddingsWorkflow import \
	ComputeAndUpsertModelDocEmbeddingsWorkflow
from ingest.workflows.docs.GenerateSyntheticDataForModelDocWorkflow import \
	GenerateSyntheticDataForModelDocWorkflow
from ingest.workflows.docs.activities import ModelDocsActivities
from shared.activities.minio_activities import MinioActivities
from shared.activities.postgres_activities import PostgresActivities
from shared.const import MINIO_TASK_QUEUE, POSTGRES_TASK_QUEUE
from shared.models.base import DocSection, IngestModelInput, ModelDoc


@workflow.defn
class IngestModelDocsWorkflow:
	def __init__(self) -> None:
		# define workflow state here
		# self.params = None
		pass

	@workflow.run
	async def run(self, input: IngestModelInput) -> None:
		workflow.logger.info("Starting IngestModelDocsWorkflow")

		markdown_local_path, image_folder_local_path = await workflow.execute_activity(
			ModelDocsActivities.convert_pdf_to_markdown,
			args=[input.original_file_path],
            schedule_to_close_timeout=timedelta(seconds=10)
		)

		# backup markdown file
		await workflow.execute_activity(
			MinioActivities.upload_file,
			args=[markdown_local_path, f"{input.model_slug}/docs/model_docs.md"],
			task_queue=MINIO_TASK_QUEUE,
			schedule_to_close_timeout=timedelta(seconds=10)
		)
		# backup images
		await workflow.execute_activity(
			MinioActivities.upload_folder,
			args=[image_folder_local_path, f"{input.model_slug}/docs/images"],
			task_queue=MINIO_TASK_QUEUE,
			schedule_to_close_timeout=timedelta(seconds=10)
		)

		# split local markdown file into DocSections
		doc_sections: List[DocSection] = await workflow.execute_activity(
			ModelDocsActivities.split_markdown,
			args=[markdown_local_path],
            schedule_to_close_timeout=timedelta(seconds=10)
		)

		model_doc = ModelDoc(
			id=f"{input.model_id}_model_doc",
			model_id=input.model_id,
			doc_sections = doc_sections
		)

		# Generate synthetic data with LLM for ModelDoc
		model_doc_with_synthetic_data: ModelDoc = await workflow.execute_child_workflow(
			GenerateSyntheticDataForModelDocWorkflow.run,
			args=[model_doc],
			id=f"doc-add-synth-data-{input.model_slug}",
			# retry_policy=RetryPolicy(
			#     initial_interval=timedelta(seconds=7),
			#     maximum_interval=timedelta(seconds=30),
			#     maximum_attempts=5,
			# ),
			parent_close_policy=ParentClosePolicy.REQUEST_CANCEL,
			cancellation_type=ChildWorkflowCancellationType.WAIT_CANCELLATION_COMPLETED,
		)

		# save ModelDoc to models_db
		await workflow.execute_activity(
			PostgresActivities.save_model_doc,
			task_queue=POSTGRES_TASK_QUEUE,
			args=[model_doc_with_synthetic_data],
            schedule_to_close_timeout=timedelta(seconds=10)
		)

		# compute and store all ModelDoc embeddings
		await workflow.execute_child_workflow(
			ComputeAndUpsertModelDocEmbeddingsWorkflow.run,
			args=[model_doc_with_synthetic_data],
			id=f"doc-embeddings-{input.model_slug}",
			# retry_policy=RetryPolicy(
			#     initial_interval=timedelta(seconds=7),
			#     maximum_interval=timedelta(seconds=30),
			#     maximum_attempts=5,
			# ),
			parent_close_policy=ParentClosePolicy.REQUEST_CANCEL,
			cancellation_type=ChildWorkflowCancellationType.WAIT_CANCELLATION_COMPLETED,
		)

		workflow.logger.info(
			f"IngestModelDocsWorkflow completed."
		)