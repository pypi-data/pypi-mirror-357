from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession, FormData
from aiohttp.client_exceptions import ClientConnectorError, ClientError
from json import dumps
from PIL import Image

class sendSticker:
  def __init__(self) -> None:
    self.pretty_print = None
  
  async def Initialize(self,
    chat_id: int | str,
    sticker: str,
    emoji: str,
    protect_content: bool,
    disable_notification: bool,
    reply_message: str | None = None,
    reply_markup: str | None = None
  ):
    try:
      form_data = FormData()
      imgs = Image.open(sticker)
      width, height = imgs.size
      if width > 512 and height > 512:        
        with open(sticker, 'rb') as read_sticker:
          form_data.add_field("sticker", read_sticker, filename=sticker)
          form_data.add_field("chat_id", str(chat_id))
          form_data.add_field("emoji", emoji)
          form_data.add_field("protect_content", str(protect_content).lower())
          form_data.add_field("disable_notification", str(disable_notification).lower())
      else:
        with Image.open(sticker) as resize_images:
          img = resize_images.convert("RGBA")
          mx_size = (512, 512)
          img.thumbnail(mx_size, Image.Resampling.LANCZOS)
          img.save("resized_images.png", format="PNG", optimize=True)
        if reply_message is not None:
          form_data.add_field("reply_to_message_id", reply_message)
        if reply_markup is not None:
          form_data.add_field("reply_markup", reply_markup)
        async with ClientSession() as session:
          async with session.post(f"{endpoint}/sendSticker", data=form_data ) as client:
            self.raw_data = await client.json()
            self.pretty_print = dumps(self.raw_data, indent=2)
          return self
    except (ClientConnectorError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self