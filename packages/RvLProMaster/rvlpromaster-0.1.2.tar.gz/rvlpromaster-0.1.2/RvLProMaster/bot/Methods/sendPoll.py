from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class sendPoll:
  def __init__(self):
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    question: str,
    options: list[str],
    is_anonymous: bool = True,
    type: str | None = None,
  ):
    try:
      async with ClientSession() as session:
        payload = {
          "chat_id": chat_id,
          "question": question,
          "options": dumps(options),
          "is_anonymous": is_anonymous,
        }
        if type is not None:
          payload["type"] = type
        async with session.post(f"{endpoint}/sendPoll", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          self.message_id = self.raw_data['result'].get('message_id', '')
        return self
    except (ClientError, ClientResponseError) as e:
      CreateLog("ERROR", str(e))
      return self