from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError, ClientResponseError
from ...config import endpoint
from json import dumps
from ...utils import CreateLog

class getChatMemberCount:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    self.total_members = None
  async def Initialize(self, chat_id: int | str):
    try:
      payload = {'chat_id': chat_id}
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/getChatMemberCount", data=payload) as response:
          self.raw_data = await response.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          if self.raw_data.get("ok") is True:
            member_total = self.raw_data["result"]
            self.total_members = f"{member_total} Members"
          return self
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", f"{e}")
      return self