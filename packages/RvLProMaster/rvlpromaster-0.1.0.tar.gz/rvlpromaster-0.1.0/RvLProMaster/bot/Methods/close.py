from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class close:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self):
    try:
      async with ClientSession() as session:
        async with session.get(f"{endpoint}/close") as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          return self
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", f"{e}")
      return self