from typing import List

from temporalio import activity

from shared.models.vector import VectorPoint


class VectorStoreActivities:
	def __init__(self, vector_store_client):
		self.client = vector_store_client

	@activity.defn
	async def upsert_metadata_vector_points(self, collection_name: str,
	                 points: List[VectorPoint]) -> None:
		"""
		Upserts points into a Qdrant collection.

		Args:
			collection_name: Name of the collection to upsert points into
			points: List of PointStruct objects containing vectors and metadata
		"""
		# self.client.upsert(
		# 	collection_name=collection_name,
		# 	points=[
		# 		PointStruct(
		# 			id=point.id,
		# 			vector=point.vector,
		# 			payload=point.payload
		# 		) for point in points
		# 	]
		# )

		activity.logger.info(f"Activity upsert_metadata_vector_points completed.")