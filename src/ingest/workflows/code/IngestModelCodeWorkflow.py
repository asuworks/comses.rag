

from temporalio import workflow
from shared.models.base import IngestModelInput

@workflow.defn
class IngestModelCodeWorkflow:

    @workflow.run
    async def run(self, input: IngestModelInput) -> None:
        workflow.logger.info("IngestModelCodeWorkflow not implemented!")