import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker
from shared.clients import JsonChatOllamaClient, OllamaJSONClient
from shared.activities.llm_activities import LLMActivities

from spam_check.workflows.GenerateAndSubmitLLMReportWorkflow import (
    GenerateAndSubmitLLMReportWorkflow,
)
from shared.const import TASK_QUEUE_OLLAMA
from shared.utils.logging_config import logger


async def main():
    load_dotenv()

    TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
    COMSES_URL = os.getenv("COMSES_URL")
    OLLAMA_URL = os.getenv("OLLAMA_URL")
    OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2")

    logger.info(f"COMSES_URL = {COMSES_URL} from .env loaded.")
    logger.info(f"OLLAMA_URL = {OLLAMA_URL} from .env loaded.")
    logger.info(f"OLLAMA_DEFAULT_MODEL = {OLLAMA_DEFAULT_MODEL} from .env loaded.")

    client = None
    tp = None
    worker = None

    try:
        client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
        tp = ThreadPoolExecutor()

        llm_client = JsonChatOllamaClient(OLLAMA_URL, OLLAMA_DEFAULT_MODEL)
        llm_activities = LLMActivities(llm_client)

        logger.info("Worker running...")

        worker = Worker(
            client,
            task_queue=TASK_QUEUE_OLLAMA,
            workflows=[
                GenerateAndSubmitLLMReportWorkflow,
            ],
            activities=[
                llm_activities.generate_llm_spam_report,
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
