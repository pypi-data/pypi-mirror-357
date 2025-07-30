from ...utils import CreateLog
from ...config import endpoint
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientError
from json import dumps


class sendVenue:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None

  async def Initialize(self,
      chat_id: int | str,
      latitude: float,
      longitude: float,
      disable_notification: bool = False,
      protect_content: bool = False,
      title: str | None = None,
      address: str | None = None,
      reply_message: int | str | None = None,
  ):
    try:
      payload = {
          "chat_id": chat_id,
          "latitude": latitude,
          "longitude": longitude,
          "disable_notification": disable_notification,
          "protect_content": protect_content,
          "title": title,
          "address": address,
      }
      if reply_message is not None:
        payload["reply_to_message_id"] = reply_message
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/sendVenue", data=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientConnectorError, ClientError) as e:
      CreateLog.Log(f"sendLocation: {e}", "ERROR")
      return self