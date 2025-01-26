import asyncio

from temporalio import workflow

from ingest.workflows.backup.BackupModelFilesWorkflow import \
    BackupModelFilesWorkflow
from ingest.workflows.code.IngestModelCodeWorkflow import \
    IngestModelCodeWorkflow
from ingest.workflows.docs.IngestModelDocsWorkflow import \
    IngestModelDocsWorkflow
from ingest.workflows.metadata.IngestModelMetadataWorkflow import \
    IngestModelMetadataWorkflow
from shared.models.base import IngestModelInput


@workflow.defn
class IngestModelWorkflow:
    @workflow.run
    async def run(self, input: IngestModelInput):
        workflow.logger.info("Starting IngestModelWorkflow")

        # Backup model files
        await workflow.execute_child_workflow(
            BackupModelFilesWorkflow.run,
            id=f"backup-to-minio-{input.model_slug}",
            args=[input]
        )

        # Create asyncio tasks for parallel execution of the remaining workflows
        tasks = [
            asyncio.create_task(self.ingest_metadata(input)),
            asyncio.create_task(self.ingest_docs(input)),
            asyncio.create_task(self.ingest_code(input))
        ]

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

        workflow.logger.info("IngestModelWorkflow completed.")

    @staticmethod
    async def ingest_metadata(input: IngestModelInput):
        await workflow.execute_child_workflow(
            IngestModelMetadataWorkflow.run,
            id=f"ingest-metadata-{input.model_slug}",
            args=[input]
        )

    @staticmethod
    async def ingest_docs(input: IngestModelInput):
        await workflow.execute_child_workflow(
            IngestModelDocsWorkflow.run,
            id=f"ingest-docs-{input.model_slug}",
            args=[input]
        )

    @staticmethod
    async def ingest_code(input: IngestModelInput):
        await workflow.execute_child_workflow(
            IngestModelCodeWorkflow.run,
            id=f"ingest-code-{input.model_slug}",
            args=[input]
        )
