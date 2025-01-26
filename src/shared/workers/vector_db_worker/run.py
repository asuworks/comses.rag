import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from temporalio.client import Client
from temporalio.worker import Worker

from ingest.workflows.docs.ComputeAndUpsertModelDocEmbeddingsWorkflow import \
    ComputeAndUpsertModelDocEmbeddingsWorkflow
from ingest.workflows.metadata.ComputeAndUpsertMetadataEmbeddingsWorkflow import \
    ComputeAndUpsertMetadataEmbeddingsWorkflow
from shared.activities.vector_store_activities import VectorStoreActivities
from shared.const import VECTOR_STORE_TASK_QUEUE
from shared.utils.logging_config import logger


async def main():
    load_dotenv()

    TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")

    VECTOR_DB_HOST = os.getenv("VECTOR_DB_HOST")
    VECTOR_DB_PORT = os.getenv("VECTOR_DB_PORT")
    VECTOR_STORE_WORKER_MAX_CONCURRENT_ACTIVITIES = int(
        os.getenv("VECTOR_STORE_WORKER_MAX_CONCURRENT_ACTIVITIES", "1")
    )
    VECTOR_STORE_WORKER_MAX_ACTIVITIES_PER_SECOND = float(
        os.getenv("VECTOR_STORE_WORKER_MAX_ACTIVITIES_PER_SECOND", "1")
    )

    logger.info(f"VECTOR_DB_HOST = {VECTOR_DB_HOST} from .env loaded.")
    logger.info(f"VECTOR_DB_PORT = {VECTOR_DB_PORT} from .env loaded.")
    logger.info(
        f"VECTOR_STORE_WORKER_MAX_CONCURRENT_ACTIVITIES = {VECTOR_STORE_WORKER_MAX_CONCURRENT_ACTIVITIES} from .env loaded."
    )
    logger.info(
        f"VECTOR_STORE_WORKER_MAX_ACTIVITIES_PER_SECOND = {VECTOR_STORE_WORKER_MAX_ACTIVITIES_PER_SECOND} from .env loaded."
    )

    client = None
    tp = None
    worker = None

    try:
        client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
        tp = ThreadPoolExecutor()

        vector_store_client = QdrantClient(host=VECTOR_DB_HOST, port=VECTOR_DB_PORT)
        vector_store_activities = VectorStoreActivities(vector_store_client)

        worker = Worker(
            client,
            task_queue=VECTOR_STORE_TASK_QUEUE,
            workflows=[
                ComputeAndUpsertMetadataEmbeddingsWorkflow,
                ComputeAndUpsertModelDocEmbeddingsWorkflow
            ],
            activities=[
                vector_store_activities.upsert_metadata_vector_points,
            ],
            max_concurrent_activities=VECTOR_STORE_WORKER_MAX_CONCURRENT_ACTIVITIES,
            max_activities_per_second=VECTOR_STORE_WORKER_MAX_ACTIVITIES_PER_SECOND,
            activity_executor=tp,
        )

        logger.info("Worker running...")
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
