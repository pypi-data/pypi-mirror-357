from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientError
from json import dumps

class stopPoll:
  def __init__(self) -> None:
    self.pretty_print = None
  
  async def Initialize(self,
    chat_id: int | str,
    message_id: int | str
  ):
    try:
      payload = {
        "chat_id": chat_id,
        "message_id": message_id,
      }
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/stopPoll", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientConnectorError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self