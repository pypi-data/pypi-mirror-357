from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class sendChatAction:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    action: str
  ):
    try:
      async with ClientSession() as session:
        payload = {
          'chat_id': chat_id,
          'action': action
        }
        async with session.post(f"{endpoint}/sendChatAction", data=payload) as response:
          self.raw_data = await response.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", f"sendChatAction: {e}")
      return self