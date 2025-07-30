from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError, ClientResponseError
from ...config import endpoint
from json import dumps
from ...utils import CreateLog

class createChatInviteLink:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    self.invite_link = None
    
  async def Initialize(self,
    chat_id: int | str,
    name: str | int | None = None,
    expire_date: str | int | None = None, 
    member_limit: str | int | None = None,
    creates_join_request: bool | None = None
  ):
    try:
        payload = {'chat_id': chat_id}
        if name is not None:
          payload['name'] = name
        if expire_date is not None:
          payload['expire_date'] = expire_date
        if member_limit is not None:
          payload['member_limit'] = member_limit
        if creates_join_request is not None:
          payload['creates_join_request'] = creates_join_request
        async with ClientSession() as session:
          async with session.post(f"{endpoint}/createChatInviteLink", data=payload) as client:
            self.raw_data = await client.json()
            self.pretty_print = dumps(self.raw_data, indent=2)
            if self.raw_data.get("result") and self.raw_data.get("result"):
              self.invite_link = self.raw_data['result'].get('invite_link')
              self.invite_link_name = self.raw_data['result'].get('name')
            return self
    except (ClientError, ClientResponseError, KeyError) as e:
      CreateLog("ERROR", str(e))
      return self