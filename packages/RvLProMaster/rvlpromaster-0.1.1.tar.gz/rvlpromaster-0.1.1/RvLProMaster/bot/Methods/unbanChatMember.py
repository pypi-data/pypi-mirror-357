from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps


class unbanChatMember:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    user_id: int | str,
    only_if_banned: bool = False,
  ):
    try:
      async with ClientSession() as session:
        payload = {
          "chat_id": chat_id,
          "user_id": user_id,
          "only_if_banned": only_if_banned
        }
        async with session.post(f"{endpoint}/unbanChatMember", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self