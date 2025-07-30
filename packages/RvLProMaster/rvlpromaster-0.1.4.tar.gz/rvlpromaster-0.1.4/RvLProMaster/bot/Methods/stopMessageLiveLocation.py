from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError, ClientResponseError
from ...config import endpoint
from json import dumps
from ...utils import CreateLog

class stopMessageLiveLocation:
  def __init__(self) -> None:
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    message_id: int | str,
    reply_markup: str | None = None,
  ):
    try:
      payload ={
        "chat_id": chat_id,
        "message_id": message_id
      }
      if reply_markup is not None:
        payload["reply_markup"] = reply_markup
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/stopMessageLiveLocation", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = str(dumps(self.raw_data, indent=2))
        return self
      
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", str(e))
      return self