from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class setMyName:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
  async def Initialize(self, name: str, language_code: str | None = None):
    try:
      payload = {"name": name}
      if language_code is not None:
        payload["language_code"] = language_code
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/setMyName", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", str(e))
      return self
          