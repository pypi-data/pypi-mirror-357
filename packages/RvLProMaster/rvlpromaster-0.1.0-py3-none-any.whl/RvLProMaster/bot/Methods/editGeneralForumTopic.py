from ...utils import CreateLog
from ...config import endpoint
from json import dumps
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError

class editGeneralForumTopic:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self, chat_id: int | str, name: str):
    try:
      payload = {
        "chat_id": chat_id,
        "name": name
      }
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/editGeneralForumTopic", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", str(e))
      return self