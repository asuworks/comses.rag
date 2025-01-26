import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker

from ingest.workflows.IngestModelWorkflow import IngestModelWorkflow
from ingest.workflows.backup.BackupModelFilesWorkflow import \
    BackupModelFilesWorkflow
from ingest.workflows.code.IngestModelCodeWorkflow import \
    IngestModelCodeWorkflow
from ingest.workflows.docs.ComputeAndUpsertModelDocEmbeddingsWorkflow import \
    ComputeAndUpsertModelDocEmbeddingsWorkflow, ComputeEmbeddingsWorkflow, \
    PopulateChunkAnswersCollectionWorkflow, PopulateChunkQuestionsCollectionWorkflow, \
    PopulateChunksCollectionWorkflow, \
    PopulateDocSectionAnswersCollectionWorkflow, PopulateDocSectionQuestionsCollectionWorkflow, \
    PopulateDocSectionSummaryChunksCollectionWorkflow, \
    PopulateModelDocSummaryChunksCollectionWorkflow
from ingest.workflows.docs.GenerateSyntheticDataForChunksWorkflow import \
    GenerateSyntheticDataForChunksWorkflow
from ingest.workflows.docs.GenerateSyntheticDataForDocSectionWorkflow import \
    GenerateSyntheticDataForDocSectionWorkflow
from ingest.workflows.docs.GenerateSyntheticDataForModelDocWorkflow import \
    GenerateSyntheticDataForModelDocWorkflow
from ingest.workflows.docs.IngestModelDocsWorkflow import \
    IngestModelDocsWorkflow
from ingest.workflows.docs.activities import ModelDocsActivities
from ingest.workflows.metadata.ComputeAndUpsertMetadataEmbeddingsWorkflow import \
    ComputeAndUpsertMetadataEmbeddingsWorkflow
from ingest.workflows.metadata.IngestModelMetadataWorkflow import \
    IngestModelMetadataWorkflow
from ingest.workflows.metadata.activities import \
    generate_model_metadata_from_json
from shared.activities.text_activities import TextActivities
from shared.const import INGEST_MODEL_TASK_QUEUE
from shared.utils.logging_config import logger


async def main():
    load_dotenv()

    TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")

    INGEST_WORKER_MAX_ACTIVITIES_PER_SECOND = float(
        os.getenv("INGEST_WORKER_MAX_ACTIVITIES_PER_SECOND", "1")
    )
    INGEST_WORKER_MAX_CONCURRENT_ACTIVITIES = int(
        os.getenv("INGEST_WORKER_MAX_CONCURRENT_ACTIVITIES", "1")
    )

    logger.info(
        f"INGEST_WORKER_MAX_ACTIVITIES_PER_SECOND = {INGEST_WORKER_MAX_ACTIVITIES_PER_SECOND} from .env loaded."
    )
    logger.info(
        f"INGEST_WORKER_MAX_CONCURRENT_ACTIVITIES = {INGEST_WORKER_MAX_CONCURRENT_ACTIVITIES} from .env loaded."
    )

    client = None
    tp = None
    worker = None

    try:
        client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
        tp = ThreadPoolExecutor()

        docs_activities = ModelDocsActivities()
        text_activities = TextActivities()
        logger.info("Worker running...")

        worker = Worker(
            client,
            task_queue=INGEST_MODEL_TASK_QUEUE,
            workflows=[
                IngestModelWorkflow,
                IngestModelMetadataWorkflow,
                IngestModelDocsWorkflow,
                IngestModelCodeWorkflow,
                BackupModelFilesWorkflow,
                GenerateSyntheticDataForModelDocWorkflow,
                GenerateSyntheticDataForDocSectionWorkflow,
                GenerateSyntheticDataForChunksWorkflow,
                ComputeAndUpsertModelDocEmbeddingsWorkflow,
                PopulateChunksCollectionWorkflow,
                PopulateModelDocSummaryChunksCollectionWorkflow,
                PopulateDocSectionSummaryChunksCollectionWorkflow,
                PopulateChunkQuestionsCollectionWorkflow,
                PopulateChunkAnswersCollectionWorkflow,
                PopulateDocSectionQuestionsCollectionWorkflow,
                PopulateDocSectionAnswersCollectionWorkflow,
                ComputeAndUpsertMetadataEmbeddingsWorkflow,
                ComputeEmbeddingsWorkflow,
            ],
            activities=[
                generate_model_metadata_from_json,
                docs_activities.split_markdown,
                docs_activities.convert_pdf_to_markdown,
                text_activities.chunk_text
            ],
            max_activities_per_second=INGEST_WORKER_MAX_ACTIVITIES_PER_SECOND,
            max_concurrent_activities=INGEST_WORKER_MAX_CONCURRENT_ACTIVITIES,
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
