from ...config import endpoint
from ...utils import CreateLog
from typing import Literal
import json
import aiohttp

class deleteMessage:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    message_id: int | str,
  ):
    try:
      async with aiohttp.ClientSession() as session:
        payload = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        async with session.post(f"{endpoint}/deleteMessage", data=payload) as client:
            self.raw_data = await client.json()
            self.pretty_print = json.dumps(self.raw_data, indent=2)
            return self
    except (aiohttp.ClientError, aiohttp.ClientResponseError, KeyError) as e:
      CreateLog("ERROR", f"{e}")