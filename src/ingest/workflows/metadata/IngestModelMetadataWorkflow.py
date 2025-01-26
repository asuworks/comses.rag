from datetime import timedelta

from temporalio import workflow
from temporalio.workflow import ChildWorkflowCancellationType, ParentClosePolicy

from ingest.workflows.metadata.ComputeAndUpsertMetadataEmbeddingsWorkflow import \
    ComputeAndUpsertMetadataEmbeddingsWorkflow
from ingest.workflows.metadata.activities import \
    generate_model_metadata_from_json
from shared.activities.postgres_activities import PostgresActivities
from shared.const import POSTGRES_TASK_QUEUE
from shared.models.base import IngestModelInput
from shared.models.model_metadata import ModelMetadata


# Import activities, passing them through the sandbox without reloading the module
# with workflow.unsafe.imports_passed_through():
#     from spam_check.activities import ComsesSpamCheckActivities


# async def execute_child_workflow(obj: SpamCheckModel):
#     workflow_id = f"{GENERATE_AND_SUBMIT_SPAM_REPORT_WORKFLOW_ID_PREFIX}{obj.id}"
#
#     result = await workflow.execute_child_workflow(
#         GenerateAndSubmitLLMReportWorkflow,
#         args=[obj],
#         id=workflow_id,
#         task_queue="spam_check_queue",
#         retry_policy=RetryPolicy(
#             initial_interval=timedelta(seconds=7),
#             maximum_interval=timedelta(seconds=30),
#             maximum_attempts=5,
#         ),
#         parent_close_policy=ParentClosePolicy.REQUEST_CANCEL,
#         cancellation_type=ChildWorkflowCancellationType.WAIT_CANCELLATION_COMPLETED,
#     )
#
#     return result
#
#
# async def execute_parallel_child_workflows(objects: List[SpamCheckModel]):
#     tasks = []
#     for obj in objects:
#         task = execute_child_workflow(obj)
#         tasks.append(task)
#     return await asyncio.gather(*tasks)



@workflow.defn
class IngestModelMetadataWorkflow:

    @workflow.run
    async def run(self, input: IngestModelInput) -> None:
        workflow.logger.info("Starting IngestModelMetadataWorkflow")

        model_metadata: ModelMetadata = await workflow.execute_activity(
            generate_model_metadata_from_json,
            args=[input],
            schedule_to_close_timeout=timedelta(seconds=10)
        )

        await workflow.execute_activity_method(
            PostgresActivities.create_model_from_metadata,
            task_queue=POSTGRES_TASK_QUEUE,
            args=[model_metadata],
            schedule_to_close_timeout=timedelta(seconds=10),
        )

        await workflow.execute_child_workflow(
            ComputeAndUpsertMetadataEmbeddingsWorkflow.run,
            args=[input.model_id, model_metadata],
            id=f"metadata-embeddings-{input.model_slug}",
            # retry_policy=RetryPolicy(
            #     initial_interval=timedelta(seconds=7),
            #     maximum_interval=timedelta(seconds=30),
            #     maximum_attempts=5,
            # ),
            parent_close_policy=ParentClosePolicy.REQUEST_CANCEL,
            cancellation_type=ChildWorkflowCancellationType.WAIT_CANCELLATION_COMPLETED,
        )

        workflow.logger.info(
            f"IngestModelMetadataWorkflow completed."
        )