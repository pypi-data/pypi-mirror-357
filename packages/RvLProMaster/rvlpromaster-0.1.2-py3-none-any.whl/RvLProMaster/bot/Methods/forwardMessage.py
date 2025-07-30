from ...config import endpoint
from ...utils import CreateLog
from json import dumps
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError


class forwardMessage:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
  async def Initialize(self,
    chat_id: str | int,
    from_chat_id: str | int,
    message_id: str | int,
    protect_content: bool = False,
    disable_notification: bool = False
  ):
    try:
      async with ClientSession() as session:
        payload = {
          "chat_id": chat_id,
          "from_chat_id": from_chat_id,
          "message_id": message_id,
          "protect_content": protect_content,
          "disable_notification": disable_notification
        }
        async with session.post(f"{endpoint}/forwardMessage", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
      
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self