from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError, ClientResponseError
from json import dumps


class sendDice:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
  
  async def Initialize(self,
    chat_id: int | str,
    emoji: str | None = None,
    disable_notification: bool = False,
    protect_content: bool = False,
  ):
    try:
      payload = {
        "chat_id": chat_id,
        "disable_notification": disable_notification,
        "protect_content": protect_content,
      }
      if emoji is None:
        payload['emoji'] = emoji
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/sendDice", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          return self
    except (ClientError, ClientResponseError, KeyError) as e:
      CreateLog("ERROR", f"{e}")
      return self