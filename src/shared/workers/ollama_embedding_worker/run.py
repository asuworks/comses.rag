import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker

from ingest.workflows.docs.ComputeAndUpsertModelDocEmbeddingsWorkflow import \
    ComputeAndUpsertModelDocEmbeddingsWorkflow, ComputeEmbeddingsWorkflow
from ingest.workflows.metadata.ComputeAndUpsertMetadataEmbeddingsWorkflow import \
    ComputeAndUpsertMetadataEmbeddingsWorkflow
from shared.activities.llm_activities import LLMActivities
from shared.clients import OllamaClient
from shared.const import OLLAMA_EMBEDDING_TASK_QUEUE
from shared.utils.logging_config import logger


async def main():
    load_dotenv()

    TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")

    OLLAMA_URL = os.getenv("OLLAMA_URL")
    OLLAMA_DEFAULT_EMBEDDING_MODEL = os.getenv("OLLAMA_DEFAULT_EMBEDDING_MODEL", "nomic-embed-text")

    OLLAMA_EMBEDDING_WORKER_MAX_CONCURRENT_ACTIVITIES = int(
        os.getenv("OLLAMA_EMBEDDING_WORKER_MAX_CONCURRENT_ACTIVITIES", "1")
    )
    OLLAMA_EMBEDDING_WORKER_MAX_ACTIVITIES_PER_SECOND = float(
        os.getenv("OLLAMA_EMBEDDING_WORKER_MAX_ACTIVITIES_PER_SECOND", "1")
    )

    logger.info(f"OLLAMA_URL = {OLLAMA_URL} from .env loaded.")
    logger.info(f"OLLAMA_DEFAULT_EMBEDDING_MODEL = {OLLAMA_DEFAULT_EMBEDDING_MODEL} from .env loaded.")
    logger.info(
        f"OLLAMA_EMBEDDING_WORKER_MAX_CONCURRENT_ACTIVITIES = {OLLAMA_EMBEDDING_WORKER_MAX_CONCURRENT_ACTIVITIES} from .env loaded."
    )
    logger.info(
        f"OLLAMA_EMBEDDING_WORKER_MAX_ACTIVITIES_PER_SECOND = {OLLAMA_EMBEDDING_WORKER_MAX_ACTIVITIES_PER_SECOND} from .env loaded."
    )

    client = None
    tp = None
    worker = None

    try:
        client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
        tp = ThreadPoolExecutor()

        llm_client = OllamaClient(OLLAMA_URL, OLLAMA_DEFAULT_EMBEDDING_MODEL)
        llm_activities = LLMActivities(llm_client)

        worker = Worker(
            client,
            task_queue=OLLAMA_EMBEDDING_TASK_QUEUE,
            workflows=[
                ComputeAndUpsertMetadataEmbeddingsWorkflow,
                ComputeAndUpsertModelDocEmbeddingsWorkflow,
                ComputeEmbeddingsWorkflow
            ],
            activities=[
                llm_activities.compute_embedding,
            ],
            max_concurrent_activities=OLLAMA_EMBEDDING_WORKER_MAX_CONCURRENT_ACTIVITIES,
            max_activities_per_second=OLLAMA_EMBEDDING_WORKER_MAX_ACTIVITIES_PER_SECOND,
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
