from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientError
from json import dumps

class editMessageCaption:
  def __init__(self):
    self.raw_data = None
    self.pretty_print = None
  
  async def Initialize(self,
    chat_id: int | str,
    message_id: int | str,
    caption: str,
    parse_mode: str | None = None
  ):
    try:
      payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption
      }
      if parse_mode is not None:
        payload["parse_mode"] = parse_mode
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/editMessageCaption", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientConnectorError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self