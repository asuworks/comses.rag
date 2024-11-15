from dataclasses import dataclass, field
from temporalio import workflow
from temporalio.workflow import ChildWorkflowCancellationType, ParentClosePolicy
from temporalio.exceptions import ApplicationError
from temporalio.common import RetryPolicy
from datetime import timedelta
import json
from typing import Dict, Optional, List

from shared.const import TASK_QUEUE_COMSES_SPAM_CHECK, TASK_QUEUE_OLLAMA
from spam_check.dto import LLMSpamReport, SpamReport, SpamCheckModel

# Import activities, passing them through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from spam_check.activities import ComsesSpamCheckActivities
    from shared.activities.llm_activities import LLMActivities


@workflow.defn
class GenerateAndSubmitLLMReportWorkflow:
    @workflow.run
    async def run(self, input: SpamCheckModel) -> SpamReport:
        workflow.logger.info(
            f"Starting GenerateAndSubmitLLMReportWorkflow for {input.contentType} with id={input.id}"
        )

        llm_spam_report: LLMSpamReport = await workflow.execute_activity(
            LLMActivities.generate_llm_spam_report,
            args=[input],
            task_queue=TASK_QUEUE_OLLAMA,
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=3),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5,
            ),
            start_to_close_timeout=timedelta(minutes=5),
        )

        spam_report = SpamReport(
            object_id=input.id,
            is_spam=llm_spam_report.is_spam,
            confidence=llm_spam_report.confidence,
            reasoning=llm_spam_report.reasoning,
            spam_indicators=llm_spam_report.spam_indicators,
        )

        ok = await workflow.execute_activity(
            ComsesSpamCheckActivities.send_spam_report_to_comses,
            args=[spam_report],
            task_queue=TASK_QUEUE_COMSES_SPAM_CHECK,
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=3),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5,
            ),
            start_to_close_timeout=timedelta(minutes=1),
        )

        if ok:
            return spam_report
        else:
            raise ApplicationError(f"Failed to send report to comses for {input}")
