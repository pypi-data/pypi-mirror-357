from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError, ClientResponseError
from ...config import endpoint
from json import dumps
from ...utils import CreateLog

class approveChatJoinRequest:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self, chat_id: int | str, user_id: int | str):
    try:
      payload = {
        "chat_id": chat_id,
        "user_id": user_id
      }
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/approveChatJoinRequest", data=payload) as response:
          self.raw_data = await response.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          return self
    except (ClientError, ClientResponseError, KeyError) as e:
      CreateLog("ERROR", f"{e}")
      return self