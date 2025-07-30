from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class getUserProfilePhotos:
    def __init__(self):
        self.raw_data = None
        self.pretty_print = None
        self.biggest_picture = None

    async def Initialize(self, user_id: int | str, limit: int):
        try:
            async with ClientSession() as session:
                payload = {
                    "user_id": user_id,
                    "limit": limit
                }
                async with session.post(f"{endpoint}/getUserProfilePhotos", json=payload) as response:
                    self.raw_data = await response.json()
                    self.pretty_print = dumps(self.raw_data, indent=2)

                    if self.raw_data.get("ok") and self.raw_data["result"]["total_count"] > 0:
                        photo_group = self.raw_data["result"]["photos"][0]
                        self.biggest_picture = photo_group[-1]['file_id']
            return self

        except (ClientResponseError, ClientError) as e:
            CreateLog("ERROR", str(e))
            return self
