import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker

from spam_check.activities import ComsesSpamCheckActivities
from shared.clients import ComsesClient
from shared.const import TASK_QUEUE_COMSES_SPAM_CHECK
from spam_check.workflows.CheckSpamWorkflow import CheckSpamWorkflow
from spam_check.workflows.GenerateAndSubmitLLMReportWorkflow import (
    GenerateAndSubmitLLMReportWorkflow,
)

from shared.utils.logging_config import logger


async def main():
    load_dotenv()

    TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
    COMSES_URL = os.getenv("COMSES_URL")
    COMSES_API_KEY = os.getenv("COMSES_API_KEY")

    logger.info(f"COMSES_URL = {COMSES_URL} from .env loaded.")

    client = None
    tp = None
    worker = None

    try:
        client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
        tp = ThreadPoolExecutor()

        comses_client = ComsesClient(COMSES_URL, COMSES_API_KEY)
        comses_spam_check_activities = ComsesSpamCheckActivities(comses_client)

        logger.info("Worker running...")

        worker = Worker(
            client,
            task_queue=TASK_QUEUE_COMSES_SPAM_CHECK,
            workflows=[
                CheckSpamWorkflow,
                GenerateAndSubmitLLMReportWorkflow,
            ],
            activities=[
                comses_spam_check_activities.get_latest_batch_from_comses,
                comses_spam_check_activities.send_spam_report_to_comses,
            ],
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
