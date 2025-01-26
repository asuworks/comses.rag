import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from minio import Minio
from temporalio.client import Client
from temporalio.worker import Worker

from ingest.workflows.backup.BackupModelFilesWorkflow import \
    BackupModelFilesWorkflow
from ingest.workflows.docs.IngestModelDocsWorkflow import \
    IngestModelDocsWorkflow
from shared.activities.minio_activities import MinioActivities
from shared.const import MINIO_TASK_QUEUE
from shared.utils.logging_config import logger


async def main():
    load_dotenv()

    TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")

    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_PORT = os.getenv("MINIO_PORT")
    MINIO_HOST = f"{MINIO_ENDPOINT}:{MINIO_PORT}"
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
    FS_ROOT = os.getenv("FILE_STORAGE_ROOT")

    # Log environment variables
    logger.info(f"TEMPORAL_URL: {TEMPORAL_ADDRESS}")
    logger.info(f"TEMPORAL_NAMESPACE: {TEMPORAL_NAMESPACE}")
    logger.info(f"MINIO_HOST: {MINIO_HOST}")
    logger.info(f"MINIO_BUCKET_NAME: {MINIO_BUCKET_NAME}")
    logger.info(f"FILE_STORAGE_ROOT: {FS_ROOT}")

    MINIO_WORKER_MAX_CONCURRENT_ACTIVITIES = int(
        os.getenv("MINIO_WORKER_MAX_CONCURRENT_ACTIVITIES", "1")
    )
    MINIO_WORKER_MAX_ACTIVITIES_PER_SECOND = float(
        os.getenv("MINIO_WORKER_MAX_ACTIVITIES_PER_SECOND", "1")
    )

    logger.info(
        f"MINIO_WORKER_MAX_CONCURRENT_ACTIVITIES = {MINIO_WORKER_MAX_CONCURRENT_ACTIVITIES} from .env loaded."
    )
    logger.info(
        f"MINIO_WORKER_MAX_ACTIVITIES_PER_SECOND = {MINIO_WORKER_MAX_ACTIVITIES_PER_SECOND} from .env loaded."
    )

    client = None
    tp = None
    worker = None

    try:
        client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
        tp = ThreadPoolExecutor()

        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,  # Set this to True if using HTTPS
        )
        minio_activities = MinioActivities(minio_client, FS_ROOT, MINIO_BUCKET_NAME)
        logger.info("Worker running...")

        worker = Worker(
            client,
            task_queue=MINIO_TASK_QUEUE,
            workflows=[
                BackupModelFilesWorkflow,
                IngestModelDocsWorkflow
            ],
            activities=[
                minio_activities.upload_file,
                minio_activities.upload_folder
            ],
            max_concurrent_activities=MINIO_WORKER_MAX_CONCURRENT_ACTIVITIES,
            max_activities_per_second=MINIO_WORKER_MAX_ACTIVITIES_PER_SECOND,
            activity_executor=tp,
        )
        await worker.run()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise
    finally:
        if worker:
            await worker.shutdown()
        if tp:
            tp.shutdown(wait=True)


if __name__ == "__main__":
    asyncio.run(main())
