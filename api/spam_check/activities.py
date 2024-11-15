from typing import List, Dict
from temporalio import activity
from temporalio.exceptions import ApplicationError
import json

from spam_check.dto import SpamReport
from shared.clients import ComsesClient


class ComsesSpamCheckActivities:
    def __init__(self, comses_client: ComsesClient):
        self.comses_client = comses_client

    @activity.defn
    async def get_latest_batch_from_comses(self) -> List[Dict]:
        try:
            latest_batch = self.comses_client.get_latest_batch()
            return latest_batch
        except Exception as e:
            raise ApplicationError(f"Failed to get latest batch from CoMSES: {str(e)}")

    @activity.defn
    async def send_spam_report_to_comses(self, spam_report: SpamReport) -> bool:
        try:
            success = self.comses_client.send_spam_report(spam_report)
            return success
        except Exception as e:
            raise ApplicationError(f"Failed to send spam report to CoMSES: {str(e)}")
