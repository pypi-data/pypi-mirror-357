from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class getFile:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    self.file_path = None
    
  async def Initialize(self, file_id: str):
    try:
      async with ClientSession() as session:
        payload = {'file_id': file_id}
        async with session.post(f"{endpoint}/getFile", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          self.file_path = self.raw_data.get("result", {}).get("file_path")
        return self
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", str(e))
      return self