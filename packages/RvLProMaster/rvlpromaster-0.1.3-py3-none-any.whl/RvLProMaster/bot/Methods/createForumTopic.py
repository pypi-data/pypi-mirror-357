from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError, ClientResponseError
from ...config import endpoint
from json import dumps
from ...utils import CreateLog


class createForumTopic:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    name: str,
    icon_color: str | None = None,
    icon_custom_emoji_id: str | None = None,
  ):
    try:
      payload = {
        "chat_id": chat_id,
        "name": name
      }
      if icon_color is not None:
        payload["icon_color"] = icon_color
      if icon_custom_emoji_id is not None:  
        payload["icon_custom_emoji_id"] = icon_custom_emoji_id
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/createForumTopic", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", str(e))
      return self