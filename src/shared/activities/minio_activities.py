from temporalio import activity


class MinioActivities:
    def __init__(self, minio_client, local_fs_root: str, minio_default_bucket_name: str):
        self.minio_client = minio_client
        self.local_fs_root = local_fs_root
        self.minio_default_bucket_name = minio_default_bucket_name

    @activity.defn
    async def upload_file(self, file_path: str, object_name:str) -> None:
        activity.logger.info("Activity upload_file completed.")

    @activity.defn
    async def upload_folder(self, folder_path: str, object_name:str) -> None:
        activity.logger.info("Activity upload_folder not implemented!")