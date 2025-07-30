from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class editMessageReplyMarkup:
  def __init__(self) -> None:
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    message_id: int | str,
    reply_markup: str
  ):
    try:
      payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": reply_markup
      }
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/editMessageReplyMarkup", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self