from temporalio import workflow
from temporalio.workflow import ChildWorkflowCancellationType, ParentClosePolicy
from temporalio.common import RetryPolicy
from datetime import timedelta

from spam_check.workflows.GenerateAndSubmitLLMReportWorkflow import (
    GenerateAndSubmitLLMReportWorkflow,
)
from spam_check.dto import SpamReport

# Import activities, passing them through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from spam_check.activities import ComsesSpamCheckActivities


@workflow.defn
class CheckSpamWorkflow:

    @workflow.run
    async def run(self) -> list[SpamReport]:
        workflow.logger.info("Starting CheckSpamWorkflow")

        latest_batch = await workflow.execute_activity(
            ComsesSpamCheckActivities.get_latest_batch_from_comses,
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3,
            ),
            start_to_close_timeout=timedelta(minutes=5),
        )

        child_workflows = []
        for obj in latest_batch:
            child_workflow = workflow.start_child_workflow(
                GenerateAndSubmitLLMReportWorkflow,
                args=[obj],
                id=f"spam_check_{obj['id']}",
                task_queue="spam_check_queue",
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                ),
                parent_close_policy=ParentClosePolicy.PARENT_CLOSE_POLICY_TERMINATE,
                cancellation_type=ChildWorkflowCancellationType.WAIT_CANCELLATION_COMPLETED,
            )
            child_workflows.append(child_workflow)

        spam_reports = await workflow.wait_all(child_workflows)

        workflow.logger.info(
            f"CheckSpamWorkflow completed. Processed {len(spam_reports)} objects."
        )
        return spam_reports
