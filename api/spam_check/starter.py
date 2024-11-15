from fastapi import FastAPI, HTTPException

from uuid import uuid4
from temporalio.client import Client
import uvicorn

from shared.const import TASK_QUEUE_COMSES_SPAM_CHECK
from spam_check.workflows.GenerateAndSubmitLLMReportWorkflow import (
    GenerateAndSubmitLLMReportWorkflow,
    SpamCheckModel,
)


app = FastAPI()


@app.post("/get-spam-report")
async def get_spam_report(request: SpamCheckModel):
    try:
        client = await Client.connect("localhost:7233")
        result = await client.execute_workflow(
            GenerateAndSubmitLLMReportWorkflow.run,
            args=[request],
            id=f"spam-check-{uuid4()}",
            task_queue=TASK_QUEUE_COMSES_SPAM_CHECK,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8003)
