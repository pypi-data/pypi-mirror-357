from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientError
from json import dumps

class answerCallbackQuery:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    callback_query_id: int | str,
    text: str,
    show_alert: bool = True,
    url: str | None = None,
    cache_time: int | str | None = None,
  ):
    try:
      payload = {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert
      }
      if url is not None:
        payload["url"] = url
      if cache_time is not None:
        payload["cache_time"] = cache_time
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/answerCallbackQuery", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self.raw_data
    
    except (ClientConnectorError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self
      