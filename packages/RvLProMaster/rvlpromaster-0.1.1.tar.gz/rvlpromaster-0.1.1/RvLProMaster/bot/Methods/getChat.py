from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class getChat:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    #
    self.group_picture = None
    
    
  async def Initialize(self, chat_id: str | int):
    try:
      payload = {'chat_id': chat_id}
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/getChat", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          if self.raw_data.get("ok") is True:
            self.group_picture = self.raw_data["result"]["photo"].get("big_file_id", "")
        return self
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self