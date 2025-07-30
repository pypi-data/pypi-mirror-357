from ...config import endpoint
from ...utils import CreateLog
from typing import Literal, Union
from ..Types import Message
import json
import aiohttp

class sendVideo:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
  chat_id: int | str,
  video: str,
  caption: str | None = None,
  parse_mode: Literal["MarkdownV2", "HTML", "Markdown"] = "MarkdownV2",
  has_spoiler: bool = False,
  disable_notification: bool = False,
  protect_content: bool = False,
  reply_markup: str | None = None,
  reply_message: Union[str, int, bool] = True
  ):
    try:
        async with aiohttp.ClientSession() as session:
            # Links
            if video.startswith('https://') or video.startswith('http://'):
                payload = {
                    'chat_id': chat_id,
                    'video': video,
                    'caption': caption,
                    'parse_mode': parse_mode,
                    'has_spoiler': has_spoiler,
                    'disable_notification': disable_notification,
                    'protect_content': protect_content,
                    'reply_to_message_id': reply_message
                }
                if reply_markup is not None:
                    payload['reply_markup'] = reply_markup
                if reply_message is True:
                    if Message.message_id:
                        payload['reply_to_message_id'] = Message.message_id
                    elif Message.reply_to_message.message_id:
                        payload['reply_to_message_id'] = Message.reply_to_message.message_id
                async with session.post(f"{endpoint}/sendvideo", data=payload) as client:
                    self.raw_data = await client.json()
                    self.pretty_print = json.dumps(self.raw_data, indent=2)
                    self.message_id = self.raw_data['result'].get('message_id', '')
                    return self
                
            # File
            elif video.endswith('.jpg') or video.endswith('.mp4'):
                form_data = aiohttp.FormData()
                
                if reply_markup is not None:
                    form_data.add_field('reply_markup', reply_markup)
                    
                if reply_message is True:
                    if Message.message_id:
                        form_data.add_field('reply_to_message_id', str(Message.message_id))
                    elif Message.reply_to_message.message_id:
                        form_data.add_field('reply_to_message_id', str(Message.reply_to_message.message_id))
                with open(video, 'rb') as read_video:
                    form_data.add_field('video', read_video, filename=video)
                    form_data.add_field('chat_id', str(chat_id))
                    form_data.add_field('caption', str(caption))
                    form_data.add_field('parse_mode', str(parse_mode))
                    form_data.add_field('has_spoiler', str(has_spoiler).lower())
                    form_data.add_field('disable_notification', str(disable_notification).lower())
                    form_data.add_field('protect_content', str(protect_content).lower())
                    form_data.add_field('reply_to_message_id', str(reply_message))
                    async with session.post(f"{endpoint}/sendvideo", data=form_data) as client:
                        self.raw_data = await client.json()
                        self.pretty_print = json.dumps(self.raw_data, indent=2)
                        self.message_id = self.raw_data['result'].get('message_id', '')
                        return self
            else:
                payload = {
                    'chat_id': chat_id,
                    'video': video,
                    'caption': caption,
                    'parse_mode': parse_mode,
                    'has_spoiler': has_spoiler,
                    'disable_notification': disable_notification,
                    'protect_content': protect_content,
                    'reply_to_message_id': reply_message
                }
                if reply_markup is not None:
                    payload['reply_markup'] = reply_markup
                async with session.post(f"{endpoint}/sendVideo", data=payload) as client:
                    self.raw_data = await client.json()
                    self.pretty_print = json.dumps(self.raw_data, indent=2)
                    self.message_id = self.raw_data['result'].get('message_id', '')
                    return self
                
    except (aiohttp.ClientError, aiohttp.ClientResponseError, KeyError) as e:
        CreateLog("ERROR", f"{e}")
        return self