from temporalio import activity

from temporalio import activity

from shared.models.base import ModelDoc
from shared.models.model_metadata import ModelMetadata


class PostgresActivities:
    def __init__(self, postgres_client):
        self.postgres_client = postgres_client

    @activity.defn
    async def save_model_doc(self, model_doc:ModelDoc) -> None:
        activity.logger.info("Activity save_model_doc completed.")

    @activity.defn
    def create_model_from_metadata(self, model_metadata: ModelMetadata) -> None:
        """
		Creates the main Model object from ModelMetadata
		@returns model_id
		"""
        activity.logger.info(
            "Activity create_model_from_metadata completed.")