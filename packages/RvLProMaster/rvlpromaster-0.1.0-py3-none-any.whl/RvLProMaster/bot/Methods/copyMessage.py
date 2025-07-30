from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps


class copyMessage:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    from_chat_id: int | str,
    message_id: int | str,
    caption: str | None = None,
    parse_mode: str | None = None,
  ):
    try:
      async with ClientSession() as session:
        payload = {
          'chat_id': chat_id,
          'from_chat_id': from_chat_id,
          'message_id': message_id,
          'parse_mode': parse_mode
        }
        if caption is not None:
          payload['caption'] = caption
        if parse_mode is not None:
          payload['parse_mode'] = parse_mode
        async with session.post(f"{endpoint}/copyMessage", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          return self
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", f"{e}")
      return self