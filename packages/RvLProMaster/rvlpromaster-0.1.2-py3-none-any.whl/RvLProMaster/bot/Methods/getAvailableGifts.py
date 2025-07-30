from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientError
from json import dumps

class getAvailableGifts:
  def __init__(self) -> None:
    self.pretty_print = None
  
  async def Initialize(self):
    try:
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/getAvailableGifts") as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientConnectorError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self