from typing import List

from temporalio import activity


class TextActivities:
    def __init__(self):
        pass

    @activity.defn
    async def chunk_text(self, text:str, max_chunk_size: int = 250, overlap:int = 50) -> List[str]:
        activity.logger.info("Activity chunk_text completed.")
        return []