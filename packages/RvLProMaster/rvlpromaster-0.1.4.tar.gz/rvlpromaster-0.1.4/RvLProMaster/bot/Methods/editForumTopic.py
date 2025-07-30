from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class editForumTopic:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    message_thread_id: int | str,
    name: str | None = None,
    icon_custom_emoji_id: str | None = None,
  ):
    try:
      payload = {
        "chat_id": chat_id,
        "message_thread_id": message_thread_id
      }
      if name is not None:
        payload["name"] = name
      if icon_custom_emoji_id is not None:
        payload["icon_custom_emoji_id"] = icon_custom_emoji_id
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/editForumTopic", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self