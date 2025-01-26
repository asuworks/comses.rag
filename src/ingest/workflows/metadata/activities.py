from temporalio import activity

from shared.models.base import IngestModelInput
from shared.models.model_metadata import ModelMetadata


@activity.defn
def generate_model_metadata_from_json(input: IngestModelInput) -> ModelMetadata:
	activity.logger.info(f"Activity generate_model_metadata_from_json {input.metadata_json_path} completed")
	model_metadata = ModelMetadata(id=input.model_id, name=input.model_slug)
	return model_metadata