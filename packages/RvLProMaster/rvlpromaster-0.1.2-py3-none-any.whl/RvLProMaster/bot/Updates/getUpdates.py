from ...config import endpoint
from ...utils import CreateLog
import json
import aiohttp

class getUpdates:
  def __init__(self):
    self.raw_data = None
    self.pretty_print = None
  
  async def Initialize(self, offset: None):
    try:
      async with aiohttp.ClientSession() as session:
          payload = {'timeout': 0}
          if offset is not None:
              payload['offset'] = offset
          async with session.get(f"{endpoint}/getUpdates", params=payload) as client:
              self.raw_data = await client.json() # raw data 
              self.pretty_print = json.dumps(self.raw_data, indent=2) # pretty print
              return self
    except (aiohttp.ClientError, aiohttp.ClientResponseError, KeyError) as e:
      CreateLog("ERROR", f"{e}")
      return self