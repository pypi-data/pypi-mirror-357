from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class editChatInviteLink:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    invite_link: str,
    name: str | None = None,
    expire_date: int | str | None = None,
    member_limit: int | str | None = None,
    creates_join_request: bool = False,
  ):
    try:
      async with ClientSession() as session:
        payload = {
          "chat_id": chat_id,
          "invite_link": invite_link,
          "creates_join_request": creates_join_request
        }
        if name is not None:
          payload["name"] = name
        if expire_date is not None:
          payload["expire_date"] = expire_date
        if member_limit is not None:
          payload["member_limit"] = member_limit
        async with session.post(f"{endpoint}/editChatInviteLink", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self