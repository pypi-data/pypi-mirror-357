from ...utils import CreateLog
from ...config import endpoint
from ..Types import Message
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientError
from json import dumps
from typing import Union


class sendLocation:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None

  async def Initialize(self,
      chat_id: int | str,
      latitude: float,
      longitude: float,
      disable_notification: bool = False,
      protect_content: bool = False,
      live_period: int | None = None,
      reply_message: Union[int, str, bool] = True,
  ):
    try:
      payload = {
          "chat_id": chat_id,
          "latitude": latitude,
          "longitude": longitude,
          "disable_notification": disable_notification,
          "protect_content": protect_content
      }
      if reply_message is not None:
        if Message.message_id:
          payload["reply_to_message_id"] = Message.message_id
        elif Message.reply_to_message.message_id:
          payload["reply_to_message_id"] = Message.reply_to_message.message_id
      if live_period is not None:
        payload["live_period"] = live_period
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/sendLocation", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
          self.messsage_id = self.raw_data['result'].get('message_id', '')
        return self
    except (ClientConnectorError, ClientError) as e:
      CreateLog.Log(f"sendLocation: {e}", "ERROR")
      return self