import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker

from ingest.workflows.docs.IngestModelDocsWorkflow import \
    IngestModelDocsWorkflow
from ingest.workflows.metadata.IngestModelMetadataWorkflow import \
    IngestModelMetadataWorkflow
from shared.activities.postgres_activities import PostgresActivities
from shared.const import POSTGRES_TASK_QUEUE
from shared.prisma.models_db_prisma_client import \
    Prisma as PrismaClient
from shared.utils.logging_config import logger


async def main():
    load_dotenv()

    TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
    MODELS_DB_URL = os.getenv("MODELS_DB_URL")

    if not MODELS_DB_URL:
        logger.error("MODELS_DB_URL is not set in the environment variables.")
        return


    prisma_client = None
    temporal_client = None
    tp = None
    worker = None

    try:
        prisma_client = PrismaClient(datasource={"url": MODELS_DB_URL})
        await prisma_client.connect()

        temporal_client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
        tp = ThreadPoolExecutor()

        postgres_activities = PostgresActivities(prisma_client)

        worker = Worker(
            temporal_client,
            task_queue=POSTGRES_TASK_QUEUE,
            workflows=[IngestModelMetadataWorkflow, IngestModelDocsWorkflow],
            activities=[
                postgres_activities.save_model_doc,
                postgres_activities.create_model_from_metadata,
            ],
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

        if prisma_client:
            await prisma_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
