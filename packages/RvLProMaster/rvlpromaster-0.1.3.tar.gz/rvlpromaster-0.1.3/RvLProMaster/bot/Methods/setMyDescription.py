from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class setMyDescription:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
  
  async def Initialize(self, description: str):
    try:
      payload = {'description': description}
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/setMyDescription", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", str(e))
      return self