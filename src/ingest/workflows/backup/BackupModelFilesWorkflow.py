import asyncio
import re
from datetime import timedelta

from temporalio import workflow

from shared.activities.minio_activities import MinioActivities
from shared.const import MINIO_TASK_QUEUE
from shared.models.base import IngestModelInput


def get_filename(filepath):
    """
    Extracts the filename from a full file path using regex.

    Args:
        filepath (str): The full file path.

    Returns:
        str: The filename with extension.
    """
    match = re.search(r'[^\\/]+$', filepath)
    return match.group(0) if match else None



async def backup_code_folder(input: IngestModelInput):
    await workflow.execute_activity(
        MinioActivities.upload_folder,
        args=[input.code_folder_path, f"{input.model_slug}/code"],
        task_queue=MINIO_TASK_QUEUE,
        schedule_to_close_timeout=timedelta(seconds=10)
    )


async def backup_original_file(input: IngestModelInput):
    await workflow.execute_activity(
        MinioActivities.upload_file,
        args=[input.original_file_path, f"{input.model_slug}/docs/original/{get_filename(input.original_file_path)}"],
        task_queue=MINIO_TASK_QUEUE,
        schedule_to_close_timeout=timedelta(seconds=10)
    )

async def backup_metadata(input: IngestModelInput):
    await workflow.execute_activity(
        MinioActivities.upload_file,
        args=[input.metadata_json_path, f"{input.model_slug}/metadata.json"],
        task_queue=MINIO_TASK_QUEUE,
        schedule_to_close_timeout=timedelta(seconds=10)
    )


@workflow.defn
class BackupModelFilesWorkflow:
    def __init__(self) -> None:
        pass

    @workflow.run
    async def run(self, input: IngestModelInput):
        workflow.logger.info("Starting BackupModelFilesWorkflow")

        # Create asyncio tasks for parallel execution
        tasks = [
            asyncio.create_task(backup_metadata(input)),
            asyncio.create_task(backup_original_file(input)),
            asyncio.create_task(backup_code_folder(input))
        ]

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

        workflow.logger.info("BackupModelFilesWorkflow completed.")