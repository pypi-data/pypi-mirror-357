from ...config import endpoint
from ...utils import CreateLog
import json
import aiohttp

class logOut:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self):
    try:
      async with aiohttp.ClientSession() as session:
        async with session.post(f"{endpoint}/logOut") as client:
          self.raw_data = await client.json()
          self.pretty_print = json.dumps(self.raw_data, indent=2)
          return self
    except (aiohttp.ClientError, aiohttp.ClientResponseError, KeyError) as e:
      CreateLog("ERROR", f"{e}")
      return self