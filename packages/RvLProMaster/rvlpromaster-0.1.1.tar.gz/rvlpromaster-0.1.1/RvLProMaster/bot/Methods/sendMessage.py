from ...config import endpoint
from ...utils import CreateLog
from typing import Optional, Union
from ..Types import Message
from ...bot_exceptions import exceptions
import json
import aiohttp

class sendMessage:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    text: int | str,
    parse_mode: str,
    disable_notification: bool | None = None,
    protect_content: bool | None = None,
    reply_markup: str | None = None,
    reply_message: Union[str, int, bool] = True,
  ):
    try:
      async with aiohttp.ClientSession() as session:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification,
            'protect_content': protect_content,
        }
        if reply_markup is not None:
          payload['reply_markup'] = reply_markup
        if reply_message is not None:
          payload['reply_to_message_id'] = reply_message
        if reply_message is True:
          payload['reply_to_message_id'] = Message.message_id
        async with session.post(f"{endpoint}/sendMessage", data=payload) as client:
            self.raw_data = await client.json()
            self.pretty_print = json.dumps(self.raw_data, indent=2)
            
            if not self.raw_data.get('ok', 'true'):
              if "is reserved and must be escaped with the preceding" in self.raw_data['description']:
                raise exceptions.TEXT_ESCAPED('TEXT NEED ESCAPED!', 1000)
            self.message_id = self.raw_data['result'].get('message_id', '')              
            return self
    except KeyError as e:
      CreateLog("ERROR", f"{e}")
      return self