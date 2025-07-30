from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError, ClientResponseError
from ...config import endpoint
from json import dumps
from ...utils import CreateLog


class setChatStickerSet:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self, chat_id: int | str, sticker_set_name: str):
    try:
      payload = {
        "chat_id": chat_id,
        "sticker_set_name": sticker_set_name
      }
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/setChatStickerSet", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          return self
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self