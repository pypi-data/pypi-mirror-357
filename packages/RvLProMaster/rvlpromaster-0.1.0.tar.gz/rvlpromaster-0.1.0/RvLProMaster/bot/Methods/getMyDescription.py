from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class getMyDescription:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    self.description_bot = None
    
  async def Initialize(self):
    try:
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/getMyDescription") as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          if self.raw_data.get("ok") is True:
            self.description_bot = self.raw_data['result'].get("description")
        return self
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", str(e))
      return self
          