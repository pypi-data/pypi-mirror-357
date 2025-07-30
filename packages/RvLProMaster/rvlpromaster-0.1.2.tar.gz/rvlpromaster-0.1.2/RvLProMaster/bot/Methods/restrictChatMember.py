from ...config import endpoint
from ...utils import CreateLog
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError, ClientError
from json import dumps

class restrictChatMember:
  def __init__(self) -> None:
    self.raw_data = None
    self.pretty_print = None
    
  async def Initialize(self,
    chat_id: int | str,
    user_id: int | str,
    until_date: int | str | None = None,
    
    # User Permissions
    canSendMessage: bool = False,
    canSendAudio: bool = True,
    canSendDocument: bool = True,
    canSendPhoto: bool = True,
    canSendVideo: bool = True,
    canSendVideoNote: bool = True,
    canSendVoiceNote: bool = True,
    canSendPoll: bool = False,
    canSendOtherMessage: bool = True,
    canAddWebPagePreviews: bool = True,
    canChangeInfo: bool = False,
    canInviteUsers: bool = False,
    canPinMessages: bool = False,
    canManageTopics: bool = False
  ):
    try:
      payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "permissions": {
          "can_send_messages": canSendMessage,
          "can_send_audios": canSendAudio,
          "can_send_documents": canSendDocument,
          "can_send_photos": canSendPhoto,
          "can_send_videos": canSendVideo,
          "can_send_video_notes": canSendVideoNote,
          "can_send_voice_notes": canSendVoiceNote,
          "can_send_polls": canSendPoll,
          "can_send_other_messages": canSendOtherMessage,
          "can_add_web_page_previews": canAddWebPagePreviews,
          "can_change_info": canChangeInfo,
          "can_invite_users": canInviteUsers,
          "can_pin_messages": canPinMessages,
          "can_manage_topics": canManageTopics
        }
      }
      if until_date is not None:
        payload["until_date"] = until_date
      async with ClientSession() as session:
        async with session.post(f"{endpoint}/restrictChatMember", json=payload) as client:
          self.raw_data = await client.json()
          self.pretty_print = dumps(self.raw_data, indent=2)
        return self
    except (ClientResponseError, ClientError) as e:
      CreateLog("ERROR", str(e))
      return self