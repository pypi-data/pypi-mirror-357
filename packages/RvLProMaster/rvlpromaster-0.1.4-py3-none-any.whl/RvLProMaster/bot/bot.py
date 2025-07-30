from typing import Literal, Union, Optional
from .Updates import getUpdates
from .Methods import (
  getMe,
  sendMessage,
  approveChatJoinRequest,
  declineChatJoinRequest,
  deleteMessage,
  sendPhoto,
  logOut,
  sendVideo,
  close,
  forwardMessage,
  sendDocument,
  copyMessage,
  sendAudio,
  sendVoice,
  sendDice,
  sendAnimation,
  sendVideoNote,
  sendLocation,
  sendVenue,
  sendPoll,
  sendChatAction,
  getUserProfilePhotos,
  getFile,
  banChatMember,
  unbanChatMember,
  restrictChatMember,
  banChatSenderChat,
  unbanChatSenderChat,
  setChatPermissions,
  exportChatInviteLink,
  createChatInviteLink,
  editChatInviteLink,
  pinChatMessage,
  unpinChatMessage,
  unpinAllChatMessages,
  leaveChat,
  getChat,
  getChatAdministrators,
  getChatMemberCount,
  getChatMember,
  setChatStickerSet,
  deleteChatStickerSet,
  getForumTopicIconStickers,
  createForumTopic,
  editForumTopic,
  closeForumTopic,
  reopenForumTopic,
  deleteForumTopic,
  unpinAllForumTopicMessages,
  editGeneralForumTopic,
  closeGeneralForumTopic,
  reopenGeneralForumTopic,
  hideGeneralForumTopic,
  unhideGeneralForumTopic,
  unpinAllGeneralForumTopicMessages,
  answerCallbackQuery,
  getUserChatBoosts,
  setMyName,
  getMyName,
  setMyDescription,
  getMyDescription,
  setMyShortDescription,
  getMyShortDescription,
  editMessageText,
  editMessageCaption,
  editMessageMedia,
  editMessageLiveLocation,
  stopMessageLiveLocation,
  editMessageReplyMarkup,
  stopPoll,
  getAvailableGifts
)
from .bot_command import BotCommands
from .events import EventWatcher


class Bot:
  def __init__(self):
    self.Updates = self._Updates()
    self.Methods = self._Methods()
  
  # Updates
  class _Updates:
    def __init__(self):
      pass
    
    # updates: getUpdates
    async def getUpdates(self, offset: None):
      """Use this method to receive incoming updates using long polling (wiki). Returns an Array of Update objects.
  
      Args:
          offset (int): Identifier of the first update to be returned. Must be greater by one than the highest among the identifiers of previously received updates. By default, updates starting with the earliest unconfirmed update are returned. An update is considered confirmed as soon as getUpdates is called with an offset higher than its update_id. The negative offset can be specified to retrieve updates starting from -offset update from the end of the updates queue. All previous updates will be forgotten.
      """
      return await getUpdates().Initialize(offset)
    
  # Methods
  class _Methods:
    def __init__(self):
      pass
    
    # methods: getMe
    async def getMe(self):
      """Use this method to get information about the bot. Returns a User object on success."""
      return await getMe().Initialize()
    
    # methods: sendMessage
    async def sendMessage(self,
      chat_id: int | str,
      text: int | str,
      parse_mode: str,
      disable_notification: bool | None = None,
      protect_content: bool | None = None,
      reply_markup: str | None = None,
      reply_message: Union[str, int, bool] = True,
    ):
      """Use this method to send text messages. On success, the sent Message is returned.
  
      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          text (str): Text of the message to be sent.
          parse_mode (str): Send MarkdownV2, HTML or Markdown style for parsing entities in the message text.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          reply_markup (str): Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
          reply_message (int,str,bool): If the message is a reply, ID of the original message.
      """
      return await sendMessage().Initialize(
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode,
        disable_notification=disable_notification,
        protect_content=protect_content,
        reply_markup=reply_markup,
        reply_message=reply_message
      )
      
    # methods: approveChatJoinRequest
    async def approveChatJoinRequest(self,
      chat_id: int | str,
      user_id: int | str
    ):
      """Use this method to approve a chat join request. The bot must be an administrator in the chat for this to work and must have the can_invite_users administrator right. Returns True on success.
  
      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          user_id (int): Unique identifier of the target user.
      """
      return await approveChatJoinRequest().Initialize(
        chat_id,
        user_id
      )
    # methods: declineChatJoinRequest
    async def declineChatJoinRequest(self,
      chat_id: int | str,
      user_id: int | str
    ):
      """Use this method to decline a chat join request. The bot must be an administrator in the chat for this to work and must have the can_invite_users administrator right. Returns True on success.
  
      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          user_id (int): Unique identifier of the target user.
      """
      return await declineChatJoinRequest().Initialize(
        chat_id,
        user_id
      )
      
    # methods: deleteMessage
    async def deleteMessage(self,
      chat_id: int | str,
      message_id: int | str
    ):
      """Use this method to delete a message, including service messages, with the following limitations:
          - A message can only be deleted if it was sent less than 48 hours ago.
          - Service messages about a supergroup, channel, or forum topic creation can't be deleted.
          - A dice message in a private chat can only be deleted if it was sent more than 24 hours ago.
          - Bots can delete outgoing messages in private chats, groups, and supergroups.
          - Bots can delete incoming messages in private chats.
          - Bots granted can_post_messages permissions can delete outgoing messages in channels.
          - If the bot is an administrator of a group, it can delete any message there.
          - If the bot has can_delete_messages permission in a supergroup or a channel, it can delete any message there.
          Returns True on success.
      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of the message to delete.
      """
      return await deleteMessage().Initialize(
        chat_id,
        message_id
      )
      
    # methods: sendPhoto
    async def sendPhoto(self,
      chat_id: int | str,
      photo: str,
      caption: str | None = None,
      parse_mode: str | None = None,
      has_spoiler: bool = False,
      disable_notification: bool = False,
      protect_content: bool = False,
      reply_markup: str | None = None,
      reply_message: Union[int, str, bool] = True
    ):
      """Use this method to send photos. On success, the sent Message is returned.
  
      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          photo (str): Photo to send. Pass a file_id as String to send a photo that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a photo from the Internet, or upload a new photo using multipart/form-data.
          caption (str): Photo caption (may also be used when resending photos by file_id), 0-1024 characters after entities parsing.
          parse_mode (str | None): Send MarkdownV2, HTML or Markdown style for parsing entities in the message text.
          has_spoiler (bool): Disables link previews for links in this message.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          reply_markup (str): Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
          reply_message (int | str | None): If the message is a reply, ID of the original message.
      """
      return await sendPhoto().Initialize(
        chat_id,
        photo,
        caption,
        parse_mode,
        has_spoiler,
        disable_notification,
        protect_content,
        reply_markup,
        reply_message
      )
      
    # methods: logOut
    async def logOut(self):
      """Use this method to log out from the cloud Bot API server before launching the bot locally. You must log out the bot before running it in local mode. The method will return True on success.
  
      Note:
          You must log out the bot before running it in local mode.
      """
      return await logOut().Initialize()
    # methods: sendVideo
    async def sendVideo(self,
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
      """Use this method to send video files, Telegram clients support MPEG4 videos (other formats may be sent as Document). On success, the sent Message is returned. Bots can currently send video files of up to 50 MB in size, this limit may be changed in the future.

      Args:
          chat_id (int | str): Unique identifier for the target chat or username of the target channel (in the format @channelusername)
          video (str): Video from url or path/to/video.mp4 to send. Pass a file_id as String to send a video that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a video from the Internet, or upload a new video using multipart/form-data
          caption (str | None, optional): _description_. Video caption (may also be used when resending videos by file_id), 0-1024 characters after entities parsing
          parse_mode (Literal[&quot;MarkdownV2&quot;, &quot;HTML&quot;, &quot;Markdown&quot;], optional): Mode for parsing entities in the video caption. See formatting options for more details. Defaults to "MarkdownV2".
          has_spoiler (bool): Disables link previews for links in this message.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          reply_markup (str): Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
          reply_message (int): If the message is a reply, ID of the original message.

      Returns:
          _type_: _description_
      """
      return await sendVideo().Initialize(
        chat_id,
        video,
        caption,
        parse_mode,
        has_spoiler,
        disable_notification,
        protect_content,
        reply_markup,
        reply_message
      )
    
    # methods: close
    async def close(self):
      """Use this method to close the bot instance before moving it from one local server to another. You need to delete the webhook before calling this method to ensure that the bot isn't launched again after server restart. The method will return error 429 in the first 10 minutes after the bot is launched. Returns True on success. Requires no parameters."""
      return await close().Initialize()
    # methods: forwardMessage
    async def forwardMessage(self,
      chat_id: int | str,
      from_chat_id: int | str,
      message_id: int | str,
      protect_content: bool = False,
      disable_notification: bool = False
    ):
      """Use this method to forward messages of any kind. Service messages and messages with protected content can't be forwarded. On success, the sent Message is returned.
  
      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          from_chat_id (int): Unique identifier for the chat where the original message was sent (or channel username in the format @channelusername).
          message_id (int): Identifier of the original message.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
      """
      return await forwardMessage().Initialize(
        chat_id,
        from_chat_id,
        message_id,
        protect_content,
        disable_notification
      )
    # methods: sendDocument
    async def sendDocument(self,
      chat_id: int | str,
      document: str,
      caption: str | None = None,
      parse_mode: str | None = None,
      disable_notification: bool = False,
      protect_content: bool = False,
      reply_markup: str | None = None,
      reply_message: Union[int, str, bool] = True,
    ):
      """Use this method to send general files. On success, the sent Message is returned. Bots can currently send files of any type of up to 50 MB in size, this limit may be changed in the future.

      Args:
          chat_id (int | str): Unique identifier for the target chat or username of the target channel (in the format @channelusername)
          document (str): document from url or path/to/file to send	File to send. Pass a file_id as String to send a file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a file from the Internet, or upload a new one using multipart/form-data. More information on Sending Files »
          caption (str | None, optional): _description_. Video caption (may also be used when resending videos by file_id), 0-1024 characters after entities parsing
          parse_mode (str | None): Mode for parsing entities in the video caption. See formatting options for more details. Defaults to "MarkdownV2".
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          reply_markup (str): Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
          reply_message (int): If the message is a reply, ID of the original message.
      """
      return await sendDocument().Initialize(
        chat_id,
        document,
        caption,
        parse_mode,
        disable_notification,
        protect_content,
        reply_markup,
        reply_message
      )
    # methods: copyMessage
    async def copyMessage(self,
      chat_id: int | str,
      from_chat_id: int | str,
      message_id: int | str,
      caption: str | None = None,
      parse_mode: str | None = None,
      reply_markup: str | None = None,
      reply_message: int | str | None = None
    ):
      """Use this method to copy messages of any kind. Service messages and messages with protected content can't be copied. The method is analogous to the method forwardMessage, but the copied message doesn't have a link to the original message. Returns the MessageId of the sent message on success.
  
      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          from_chat_id (int): Unique identifier for the chat where the original message was sent (or channel username in the format @channelusername).
          message_id (int): Identifier of the original message.
          caption (str): New caption for media, 0-1024 characters after entities parsing.
          parse_mode (str): Send MarkdownV2, HTML or Markdown style for parsing entities in the message text.
      """
      return await copyMessage().Initialize(
        chat_id,
        from_chat_id,
        message_id,
        caption,
        parse_mode
      )
    # methods: sendAudio
    async def sendAudio(self,
      chat_id: int | str,
      audio: str,
      caption: str | None = None,
      parse_mode: Literal["MarkdownV2", "HTML", "Markdown"] = "MarkdownV2",
      disable_notification: bool = False,
      protect_content: bool = False,
      reply_markup: str | None = None,
      reply_message: Union[int, str, bool] = True
    ):
      """Use this method to send audio files, if you want Telegram clients to display them in the music player. Your audio must be in an audio/mpeg or audio/ogg format. On success, the sent Message is returned. Bots can currently send audio files of up to 50 MB in size, this limit may be changed in the future.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          audio (str): Audio file to send. Pass a file_id as String to send an audio file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get an audio file from the Internet, or upload a new one using multipart/form-data.
          caption (str): Audio caption, 0-1024 characters after entities parsing.
          parse_mode (str): Send MarkdownV2, HTML or Markdown style for parsing entities in the message text.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          reply_markup (str): Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
          reply_message (int): If the message is a reply, ID of the original message.
      """
      return await sendAudio().Initialize(
        chat_id,
        audio,
        caption,
        parse_mode,
        disable_notification,
        protect_content,
        reply_markup,
        reply_message
      )
      
    # methods: sendVoice
    async def sendVoice(self,
      chat_id: int | str,
      voice: str,
      caption: str | None = None,
      parse_mode: Literal["MarkdownV2", "HTML", "Markdown"] = "MarkdownV2",
      disable_notification: bool = False,
      protect_content: bool = False,
      reply_markup: str | None = None,
      reply_message: Union[int, str, bool] = True
    ):
      """Use this method to send audio files, if you want Telegram clients to display them in the music player. Your audio must be in an audio/mpeg or audio/ogg format. On success, the sent Message is returned. Bots can currently send audio files of up to 50 MB in size, this limit may be changed in the future.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          voice (str): Audio file to send. Pass a file_id as String to send an audio file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get an audio file from the Internet, or upload a new one using multipart/form-data.
          caption (str): Audio caption, 0-1024 characters after entities parsing.
          parse_mode (str): Send MarkdownV2, HTML or Markdown style for parsing entities in the message text.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          reply_markup (str): Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
          reply_message (int | str | bool): If the message is a reply, ID of the original message.
      """
      return await sendVoice().Initialize(
        chat_id,
        voice,
        caption,
        parse_mode,
        disable_notification,
        protect_content,
        reply_markup,
        reply_message
      )
    
    # methods: sendDice
    async def sendDice(self,
      chat_id: int | str,
      emoji: str | None = None,
      disable_notification: bool = False,
      protect_content: bool = False,
      reply_markup: str | None = None,
    ):
      """Use this method to send an animated emoji that displays a random value. On success, the sent Message is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          emoji (str): Emoji on which the dice throw animation is based. Currently, must be one of the following: “🎲”, “🎯”, “🏁”, “🎳”, “🎰”. Dice can have values from 1-6.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
      """
      return await sendDice().Initialize(
        chat_id,
        emoji,
        disable_notification,
        protect_content,
      )
    # methods: sendAnimation
    async def sendAnimation(self,
      chat_id: int | str,
      animation: str,
      caption: str | None = None,
      parse_mode: str | None = None,
      has_spoiler: bool = False,
      disable_notification: bool = False,
      protect_content: bool = False,
      reply_markup: str | None = None,
      reply_message: Union[int, str, bool] = True
    ):
      """Use this method to send animation files (GIF or H.264/MPEG-4 AVC video without sound). On success, the sent Message is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          animation (str): Animation file to send. Pass a file_id as String to send an animation that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get an animation from the Internet, or upload a new one using multipart/form-data.
          caption (str): Animation caption (may also be used when resending animation by file_id), 0-1024 characters after entities parsing.
          parse_mode (str | None): Send MarkdownV2, HTML or Markdown style for parsing entities in the message text.
          has_spoiler (bool): Disables link previews for links in this message.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          reply_markup (str): Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
          reply_message (int): If the message is a reply, ID of the original message.
      """
      return await sendAnimation().Initialize(
        chat_id,
        animation,
        caption,
        parse_mode,
        has_spoiler,
        disable_notification,
        protect_content,
        reply_markup,
        reply_message
      )
    
    # methods: sendVideoNote
    async def sendVideoNote(self,
      chat_id: int | str,
      video_note: str,
      caption: str | None = None,
      parse_mode: str | None = None,
      disable_notification: bool = False,
      protect_content: bool = False,
      reply_markup: str | None = None,
      reply_message: Union[int, str, bool] = True
    ):
      """Use this method to send video messages (available in Telegram apps). On success, the sent Message is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          video_note (str): Video note to send. Pass a file_id as String to send a video note that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a video note from the Internet, or upload a new one using multipart/form-data.
          caption (str): Video note caption (may also be used when resending video notes by file_id), 0-1024 characters after entities parsing.
          parse_mode (str): Send MarkdownV2, HTML or Markdown style for parsing entities in the message text.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          reply_markup (str): Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
          reply_message (int | str | bool): If the message is a reply, ID of the original message.
      """
      return await sendVideoNote().Initialize(
        chat_id,
        video_note,
        caption,
        parse_mode,
        disable_notification,
        protect_content,
        reply_markup,
        reply_message
      )
    # methods: sendLocation
    async def sendLocation(self,
      chat_id: int | str,
      latitude: float,
      longitude: float,
      disable_notification: bool = False,
      protect_content: bool = False,
      live_period: int | None = None,
      reply_message: Union[int, str, bool] = True
    ):
      """Use this method to send point on the map. On success, the sent Message is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          latitude (float): Latitude of the location.
          longitude (float): Longitude of the location.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          live_period (int | None): Period in seconds for which the location will be updated (see Live Locations, should be between 60 and 86400.
          reply_message (int | str | bool): If the message is a reply, ID of the original message.
      """
      return await sendLocation().Initialize(
        chat_id,
        latitude,
        longitude,
        disable_notification,
        protect_content,
        live_period,
        reply_message
      )
    # methods: sendVenue
    async def sendVenue(self,
      chat_id: int | str,
      latitude: float,
      longitude: float,
      disable_notification: bool = False,
      protect_content: bool = False,
      title: str | None = None,
      address: str | None = None,
      reply_message: Union[int, str, bool] = True
    ):
      """Use this method to send information about a venue. On success, the sent Message is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          latitude (float): Latitude of the location.
          longitude (float): Longitude of the location.
          disable_notification (bool): Sends the message silently. Users will receive a notification with no sound.
          protect_content (bool): Protects the contents of the sent message from forwarding and saving.
          title (str | None): Name of the venue.
          address (str | None): Address of the venue.
          reply_message (int | str | bool): If the message is a reply, ID of the original message.
      """
      return await sendVenue().Initialize(
        chat_id,
        latitude,
        longitude,
        disable_notification,
        protect_content,
        title,
        address,
        reply_message
      )
    
    # methods: sendPoll
    async def sendPoll(self,
      chat_id: int | str,
      question: str,
      options: list[str],
      is_anonymous: bool = True,
      type: str | None = None
    ):
      """Use this method to send a native poll. On success, the sent Message is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          question (str): Poll question, 1-255 characters.
          options (list[str]): List of answer options, 2-10 strings 1-100 characters each.
          is_anonymous (bool): Pass True if the poll needs to be anonymous, defaults to True. Non-anonymous polls can't be sent to private chats.
          type (str | None): Poll type, “quiz” or “regular”, defaults to “regular”.
      """
      return await sendPoll().Initialize(
        chat_id,
        question,
        options,
        is_anonymous,
        type
      )
      
    # methods: sendChatAction
    async def sendChatAction(self,
      chat_id: int | str,
      action: str
    ):
      """Use this method when you need to tell the user that something is happening on the bot's side. The status is set for 5 seconds or less (when a message arrives from your bot, Telegram clients clear its typing status after 5 seconds). Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          action (str): Type of action to broadcast. Choose one, depending on what the user is about to receive: typing for text messages, upload_photo for photos, record_video or upload_video for videos, record_audio or upload_audio for audio files, upload_document for general files, record_video_note or upload_video_note for video notes.
            - typing: bot will simulate typing
            - upload_photo: bot will simulate upload photos
            - record_video: bot will simulate recording video
            - upload_video: bot will simulate upload video
            - record_audio: bot will simulate recording audio
            - upload_audio: bot will simulate upload audio
            - upload_document: bot will simulate upload document
            - record_video_note: bot will simulate recording video note
            - upload_video_note: bot will simulate upload video note
            - choose_sticker: bot will simulate choosing sticker
      """
      return await sendChatAction().Initialize(
        chat_id,
        action
      )
    
    # methods: getUserProfilePhotos
    async def getUserProfilePhotos(self,
      user_id: int | str,
      limit: int = 100,
    ):
      """Use this method to get a list of profile pictures for a user. Returns a UserProfilePhotos object.

      Args:
          user_id (int): Unique identifier of the target user.
          limit (int): Limits the number of photos to be retrieved. Values between 1-100 are accepted. Defaults to 100.
      """
      return await getUserProfilePhotos().Initialize(
        user_id,
        limit
      )
    # methods: getFile
    async def getFile(self,
      file_id: str
    ):
      """Use this method to get basic info about a file and prepare it for downloading. For the moment, bots can download files of up to 20MB in size. On success, a File object is returned.

      Args:
          file_id (str): File id to be downloaded.
      """
      return await getFile().Initialize(
        file_id
      )
    # methods: banChatMember
    async def banChatMember(self,
      chat_id: int | str,
      user_id: int | str,
      until_date: int | str | None = None,
      revoke_messages: bool = False
    ):
      """Use this method to ban a user in a supergroup or channel. In the current implementation, the user will not be able to send messages to the group or channel. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          user_id (int): Unique identifier of the target user.
          until_date (int | str | None): Date when the user will be unbanned, unix time. If user is banned for more than 366 days or less than 30 seconds from the current time, then they are considered to be banned forever.
          revoke_messages (bool): Pass True if the user's messages should be removed.
      """
      return await banChatMember().Initialize(
        chat_id,
        user_id,
        until_date,
        revoke_messages
      )
    # methods: unbanChatMember
    async def unbanChatMember(self,
      chat_id: int | str,
      user_id: int | str,
      only_if_banned: bool = False
    ):
      """Use this method to unban a previously banned user in a supergroup or channel. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          user_id (int): Unique identifier of the target user.
          only_if_banned (bool): Pass True if the user is banned.
      """
      return await unbanChatMember().Initialize(
        chat_id,
        user_id,
        only_if_banned
      )
    # methods: restrictChatMember
    async def restrictChatMember(self,
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
      """Use this method to restrict a user in a supergroup. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          user_id (int): Unique identifier of the target user.
          until_date (int | str | None): Date when restrictions will be lifted for the user, unix time. If user is restricted for more than 366 days or less than 30 seconds from the current time, then they are considered to be restricted forever.
          
          **User Permissions**
            - canSendMessage (bool): Pass True if the user can send text messages, contacts, locations and venues.
            - canSendAudio (bool): Pass True if the user can send audios, such as voice notes and music files.
            - canSendDocument (bool): Pass True if the user can send documents.
            - canSendPhoto (bool): Pass True if the user can send photos.
            - canSendVideo (bool): Pass True if the user can send videos.
            - canSendVideoNote (bool): Pass True if the user can send video notes.
            - canSendVoiceNote (bool): Pass True if the user can send voice notes.
            - canSendPoll (bool): Pass True if the user can send polls.
            - canSendOtherMessage (bool): Pass True if the user can send other messages, such as stickers, media, location-based games and live locations.
            - canAddWebPagePreviews (bool): Pass True if the user can add web page previews to their messages.
            - canChangeInfo (bool): Pass True if the user is allowed to change the chat title, photo and other settings.
            - canInviteUsers (bool): Pass True if the user is allowed to invite new users to the chat.
            - canPinMessages (bool): Pass True if the user is allowed to pin messages.
            - canManageTopics (bool): Pass True if the user is allowed to create, rename, close and reopen forum topics.
      """
      return await restrictChatMember().Initialize(
        chat_id,
        user_id,
        until_date,
        canSendMessage,
        canSendAudio,
        canSendDocument,
        canSendPhoto,
        canSendVideo,
        canSendVideoNote,
        canSendVoiceNote,
        canSendPoll,
        canSendOtherMessage,
        canAddWebPagePreviews,
        canChangeInfo,
        canInviteUsers,
        canPinMessages,
        canManageTopics
      )
      
    # methods: banChatSenderChat
    async def banChatSenderChat(self,
      chat_id: int | str,
      sender_chat_id: int | str
    ):
      """Use this method to ban a channel chat in a supergroup or channel. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          sender_chat_id (int): Unique identifier of the target sender chat.
      """
      return await banChatSenderChat().Initialize(
        chat_id,
        sender_chat_id
      )
      
    # methods: unbanChatSenderChat
    async def unbanChatSenderChat(self,
      chat_id: int | str,
      sender_chat_id: int | str
    ):
      """Use this method to unban a previously banned channel chat in a supergroup or channel. The bot must be an administrator for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          sender_chat_id (int): Unique identifier of the target sender chat.
      """
      return await unbanChatSenderChat().Initialize(
        chat_id,
        sender_chat_id
      )
      
    # methods: setChatPermissions
    async def setChatPermissions(self,
      chat_id: int | str,
      
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
      """Use this method to set default chat permissions in a supergroup or channel. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          **User Permissions**
            - canSendMessage (bool): Pass True if the user can send text messages, contacts, locations and venues.
            - canSendAudio (bool): Pass True if the user can send audios, such as voice notes and music files.
            - canSendDocument (bool): Pass True if the user can send documents.
            - canSendPhoto (bool): Pass True if the user can send photos.
            - canSendVideo (bool): Pass True if the user can send videos.
            - canSendVideoNote (bool): Pass True if the user can send video notes.
            - canSendVoiceNote (bool): Pass True if the user can send voice notes.
            - canSendPoll (bool): Pass True if the user can send polls.
            - canSendOtherMessage (bool): Pass True if the user can send other messages, such as stickers, media, location-based games and live locations.
            - canAddWebPagePreviews (bool): Pass True if the user can add web page previews to their messages.
            - canChangeInfo (bool): Pass True if the user is allowed to change the chat title, photo and other settings.
            - canInviteUsers (bool): Pass True if the user is allowed to invite new users to the chat.
            - canPinMessages (bool): Pass True if the user is allowed to pin messages.
            - canManageTopics (bool): Pass True if the user is allowed to create, rename, close and reopen forum topics.
          
      """
      return await setChatPermissions().Initialize(
        chat_id,
        canSendMessage,
        canSendAudio,
        canSendDocument,
        canSendPhoto,
        canSendVideo,
        canSendVideoNote,
        canSendVoiceNote,
        canSendPoll,
        canSendOtherMessage,
        canAddWebPagePreviews,
        canChangeInfo,
        canInviteUsers,
        canPinMessages,
        canManageTopics
      )
    
    # methods: exportChatInviteLink
    async def exportChatInviteLink(self,
      chat_id: int | str
    ):
      """Use this method to export a new invite link for a chat. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns the new invite link as String on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
      """
      return await exportChatInviteLink().Initialize(chat_id)
    
    # methods: createChatInviteLink
    async def createChatInviteLink(self,
      chat_id: int | str,
      name: str | None = None,
      expire_date: int | str | None = None,
      member_limit: int | None = None,
      creates_join_request: bool = False
    ):
      """Use this method to create an additional invite link for a chat. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns the new invite link as String on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          name (str | None): Invite link name.
          expire_date (int | str | None): Point in time (Unix timestamp) when the link will expire.
          member_limit (int | None): The maximum number of users that can be members of the chat simultaneously after joining the chat via this invite link; 1-99999.
          creates_join_request (bool): Pass True if a user joined the chat via this invite link, they should be asked to join the chat via a join request.
      """
      return await createChatInviteLink().Initialize(
        chat_id,
        name,
        expire_date,
        member_limit,
        creates_join_request
      )
      
    # methods: editChatInviteLink
    async def editChatInviteLink(self,
      chat_id: int | str,
      invite_link: str,
      name: str | None = None,
      expire_date: int | str | None = None,
      member_limit: int | None = None,
      creates_join_request: bool = False
    ):
      """Use this method to edit a non-primary invite link created by the bot. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns the new invite link as String on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          invite_link (str): Invite link to be edited.
          name (str | None): Invite link name.
          expire_date (int | str | None): Point in time (Unix timestamp) when the link will expire.
          member_limit (int | None): The maximum number of users that can be members of the chat simultaneously after joining the chat via this invite link; 1-99999.
          creates_join_request (bool): Pass True if a user joined the chat via this invite link, they should be asked to join the chat via a join request.
      """
      return await editChatInviteLink().Initialize(
        chat_id,
        invite_link,
        name,
        expire_date,
        member_limit,
        creates_join_request
      )
    
    # methods: pinChatMessage
    async def pinChatMessage(self,
      chat_id: int | str,
      message_id: int | str,
      disable_notification: bool = False
    ):
      """Use this method to add a message to the list of pinned messages in a chat. If the chat is not a private chat, the bot must be an administrator in the chat for this to work and must have the 'can_pin_messages' administrator right in a supergroup or 'can_edit_messages' administrator right in a channel. Returns True on success

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of a message to pin.
          disable_notification (bool): Pass True if it is not necessary to send a notification to all group members about the new pinned message.
      """
      return await pinChatMessage().Initialize(
        chat_id,
        message_id,
        disable_notification
      )
    
    # methods: unpinChatMessage
    async def unpinChatMessage(self,
      chat_id: int | str,
      message_id: int | str
    ):
      """Use this method to remove a message from the list of pinned messages in a chat. If the chat is not a private chat, the bot must be an administrator in the chat for this to work and must have the 'can_pin_messages' administrator right in a supergroup or 'can_edit_messages' administrator right in a channel. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of a message to unpin.
      """
      return await unpinChatMessage().Initialize(
        chat_id,
        message_id
      )
      
    # methods: unpinAllChatMessages
    async def unpinAllChatMessages(self,
      chat_id: int | str
    ):
      """Use this method to clear the list of pinned messages in a chat. If the chat is not a private chat, the bot must be an administrator in the chat for this to work and must have the 'can_pin_messages' administrator right in a supergroup or 'can_edit_messages' administrator right in a channel. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
      """
      return await unpinAllChatMessages().Initialize(chat_id)
    
    # methods: leaveChat
    async def leaveChat(self,
      chat_id: int | str
    ):
      """Use this method for your bot to leave a group, supergroup or channel. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
      """
      return await leaveChat().Initialize(chat_id)
    
    # methods: getChat
    async def getChat(self,
      chat_id: int | str
    ):
      """Use this method to get up to date information about the chat (current name of the user for one-on-one conversations, current username of a user for private chats and supergroups, and current title of a supergroup or channel). Returns a Chat object on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
      """
      return await getChat().Initialize(chat_id)
    
    # methods: getChatAdministrators
    async def getChatAdministrators(self,
      chat_id: int | str
    ):
      """Use this method to get a list of administrators in a chat. On success, returns an Array of ChatMember objects that contains information about all chat administrators except other bots. If the chat is a group or a supergroup and no administrator was appointed, only the creator will be returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
      """
      return await getChatAdministrators().Initialize(chat_id)
    
    # methods: getChatMemberCount
    async def getChatMemberCount(self,
      chat_id: int | str
    ):
      """Use this method to get the number of members in a chat. Returns Int on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
      """
      return await getChatMemberCount().Initialize(chat_id)
    
    # methods: getChatMember
    async def getChatMember(self,
      chat_id: int | str,
      user_id: int | str
    ):
      """Use this method to get information about a member of a chat. The method is only guaranteed to work for other users if the bot is an administrator in the chat. Returns a ChatMember object on success.


      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          user_id (int): Unique identifier of the target user.
      """
      return await getChatMember().Initialize(chat_id, user_id)
    
    # methods: setChatSticker
    async def setChatStickerSet(self,
      chat_id: int | str,
      sticker_set_name: str
    ):
      """Use this method to set a new group sticker set for a supergroup. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Use the field can_set_sticker_set optionally returned in getChat requests to check if the bot can use this method. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          sticker_set_name (str): Name of the sticker set to be set as the group sticker set.
      """
      return await setChatStickerSet().Initialize(chat_id, sticker_set_name)
    # methods: deleteChatStickerSet
    async def deleteChatStickerSet(self,
      chat_id: int | str
    ):
      """Use this method to delete the group sticker set from a supergroup. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Use the field can_set_sticker_set optionally returned in getChat requests to check if the bot can use this method. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
      """
      return await deleteChatStickerSet().Initialize(chat_id)
    
    # methods: getForumTopicIconStickers
    async def getForumTopicIconStickers(self):
      """Use this method to get custom emoji stickers, which can be used as forum topic icons. Returns an Array of Sticker objects."""
      return await getForumTopicIconStickers().Initialize()
    # methods: createForumTopic
    async def createForumTopic(self,
      chat_id: int | str,
      name: str,
      icon_color: str | None = None,
      icon_custom_emoji_id: str | None = None
    ):
      """Use this method to create a topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns information about the created topic as a ForumTopic object.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          name (str): Name of the topic.
          icon_color (str | None): Color of the topic icon in RGB format.
          icon_custom_emoji_id (str | None): Unique identifier of the custom emoji shown as the topic icon.
      """
      return await createForumTopic().Initialize(
        chat_id,
        name,
        icon_color,
        icon_custom_emoji_id
      )
    # methods: editForumTopic
    async def editForumTopic(self,
      chat_id: int | str,
      message_thread_id: int | str,
      name: str | None = None,
      icon_custom_emoji_id: str | None = None
    ):
      """Use this method to edit a topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_thread_id (int): Unique identifier for the target message thread of the forum topic.
          name (str | None): Name of the topic.
          icon_custom_emoji_id (str | None): Unique identifier of the custom emoji shown as the topic icon.
      """
      return await editForumTopic().Initialize(
        chat_id,
        message_thread_id,
        name,
        icon_custom_emoji_id
      )
    # methods: closeForumTopic
    async def closeForumTopic(self,
      chat_id: int | str,
      message_thread_id: int | str
    ):
      """Use this method to close an open topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_thread_id (int): Unique identifier for the target message thread of the forum topic.
      """
      return await closeForumTopic().Initialize(chat_id, message_thread_id)
    
    # methods: reopenForumTopic
    async def reopenForumTopic(self,
      chat_id: int | str,
      message_thread_id: int | str
    ):
      """Use this method to reopen a closed topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_thread_id (int): Unique identifier for the target message thread of the forum topic.
      """
      return await reopenForumTopic().Initialize(chat_id, message_thread_id)
    
    # methods: deleteForumTopic
    async def deleteForumTopic(self,
      chat_id: int | str,
      message_thread_id: int | str
    ):
      """Use this method to delete a forum topic along with all its messages in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_thread_id (int): Unique identifier for the target message thread of the forum topic.
      """
      return await deleteForumTopic().Initialize(chat_id, message_thread_id)
    
    # methods: unpinAllForumTopicMessages
    async def unpinAllForumTopicMessages(self,
      chat_id: int | str,
      message_thread_id: int | str
    ):
      """Use this method to clear the list of pinned messages in a forum topic. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_thread_id (int): Unique identifier for the target message thread of the forum topic.
      """
      return await unpinAllForumTopicMessages().Initialize(chat_id, message_thread_id)
    
    # methods: editGeneralForumTopic
    async def editGeneralForumTopic(self,
      chat_id: int | str,
      name: str
    ):
      """Use this method to edit the name of the 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          name (str): Name of the topic.
      """
      return await editGeneralForumTopic().Initialize(chat_id, name)
    
    # methods: closeGeneralForumTopic
    async def closeGeneralForumTopic(self, chat_id: str | int):
      """Use this method to close an open 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the can_manage_topics administrator rights. Returns True on success.

      Args:
          chat_id (str | int): Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)
      """
      return await closeGeneralForumTopic().Initialize(chat_id)
    
    # methods: reopenGeneralForumTopic
    async def reopenGeneralForumTopic(self, chat_id: str | int):
      """Use this method to reopen a closed 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the can_manage_topics administrator rights. Returns True on success.

      Args:
          chat_id (str | int): Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)
      """
      return await reopenGeneralForumTopic().Initialize(chat_id)
    
    # methods: hideGeneralForumTopic
    async def hideGeneralForumTopic(self, chat_id: str | int):
      """Use this method to hide the 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the can_manage_topics administrator rights. Returns True on success.

      Args:
          chat_id (str | int): Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)
      """
      return await hideGeneralForumTopic().Initialize(chat_id)
    
    # methods: unhideGeneralForumTopic
    async def unhideGeneralForumTopic(self, chat_id: str | int):
      """Use this method to unhide the 'General' topic in a forum supergroup chat. The bot must be an administrator in the chat for this to work and must have the can_manage_topics administrator rights. Returns True on success.

      Args:
          chat_id (str | int): Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)
      """
      return await unhideGeneralForumTopic().Initialize(chat_id)
    
    # methods: unpinAllGeneralForumTopicMessages
    async def unpinAllGeneralForumTopicMessages(self, chat_id: str | int):
      """Use this method to clear the list of pinned messages in a forum topic. The bot must be an administrator in the chat for this to work and must have the appropriate administrator rights. Returns True on success.

      Args:
          chat_id (str | int): Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)
      """
      return await unpinAllGeneralForumTopicMessages().Initialize(chat_id)

    # methods: answerCallbackQuery
    async def answerCallbackQuery(self,
      callback_query_id: int | str,
      text: str,
      show_alert: bool = True,
      url: str | None = None,
      cache_time: int | str | None = None,
    ):
      """Use this method to send answers to callback queries sent from inline keyboards. The answer will be shown to the user as a notification at the top of the chat screen or as an alert. On success, True is returned.

      Args:
          callback_query_id (int | str): Unique identifier for the query to be answered.
          text (str): Text of the notification. If not specified, nothing will be shown to the user, 0-200 characters.
          show_alert (bool): If true, an alert will be shown by the client instead of a simple notification at the top of the chat screen. Defaults to False.
          url (str | None): URL that will be opened by the user's client. If you have created a Game and accepted payments, then you may use this parameter to show a 'Pay' button. Otherwise, you may use links like telegram.me/your_bot?start=XXXX where XXXX will be replaced with the actual query string.
          cache_time (int | str | None): The maximum amount of time in seconds that the result of the callback query may be cached client-side. Defaults to 0.
      """
      return await answerCallbackQuery().Initialize(
        callback_query_id,
        text,
        show_alert,
        url,
        cache_time
      )
      
    # methods: getUserChatBoosts
    async def getUserChatBoosts(self,
      chat_id: int | str,
      user_id: int | str
    ):
      """Use this method to get the number of boosts a user has in a chat. Returns an Array of Boost objects.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          user_id (int): Unique identifier of the target user.
      """
      return await getUserChatBoosts().Initialize(chat_id, user_id) 
    # methods: setMyName
    async def setMyName(self,
      name: str,
      language_code: str | None = None
    ):
      """Use this method to set the bot's name. Returns True on success.

      Args:
          name (str): New bot's name.
          language_code (str | None): A two-letter ISO 639-1 language code or an empty string.
      """
      return await setMyName().Initialize(name, language_code)
    # methods: getMyName
    async def getMyName(self):
      """Use this method to get the bot's name. Returns a BotName object on success.
      """
      return await getMyName().Initialize()
    # methods: setMyDescription
    async def setMyDescription(self,
      description: str
    ):
      """Use this method to set the bot's description. Returns True on success.

      Args:
          description (str): New bot's description.
      """
      return await setMyDescription().Initialize(description)
    # methods: getMyDescription
    async def getMyDescription(self):
      """Use this method to get the bot's description. Returns a BotDescription object on success.
      """
      return await getMyDescription().Initialize()
    
    # methods: setMyShortDescription
    async def setMyShortDescription(self, short_description: str):
      return await setMyShortDescription().Initialize(short_description)
    # methods: getMyShortDescription
    async def getMyShortDescription(self):
      return await getMyShortDescription().Initialize()
    # methods: editMessageText
    async def editMessageText(self,
      chat_id: int | str,
      message_id: int | str,
      text: str,
      parse_mode: str | None = None,
      reply_markup: str | None = None
    ):
      """Use this method to edit text messages sent by the bot or via the bot (for inline bots). On success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of the original message.
          text (str): New text of the message.
          parse_mode (str | None): Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or inline URLs in your bot's message.
          reply_markup (str | None): A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
      """
      return await editMessageText().Initialize(
        chat_id,
        message_id,
        text,
        parse_mode,
        reply_markup
      )
    
    # methods: editMessageCaption
    async def editMessageCaption(self,
      chat_id: int | str,
      message_id: int | str,
      caption: str,
      parse_mode: str | None = None
    ):
      """Use this method to edit captions of messages sent by the bot or via the bot (for inline bots). On success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of the original message.
          caption (str): New caption of the message.
          parse_mode (str | None): Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or inline URLs in your bot's message.
      """
      return await editMessageCaption().Initialize(
        chat_id,
        message_id,
        caption,
        parse_mode
      )
    # methods: editMessageMedia
    async def editMessageMedia(self,
      chat_id: int | str,
      message_id: int | str,
      media: str,
      type_media: str,
      caption: str | None = None,
      parse_mode: str | None = None,
      has_spoiler: bool = False,
      reply_markup: str | None = None
    ):
      """Use this method to edit media messages sent by the bot or via the bot (for inline bots). On success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of the original message.
          media (str): New media content of the message.
          type_media (str): Type of media content.
          caption (str | None): New caption of the message.
          parse_mode (str | None): Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or inline URLs in your bot's message.
          has_spoiler (bool): Pass True if the media content should be marked as spoiler.
          reply_markup (str | None): A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
      """
      return await editMessageMedia().Initialize(
        chat_id,
        message_id,
        media,
        type_media,
        caption,
        parse_mode,
        has_spoiler,
        reply_markup
      )
    
    # methods: editMessageLiveLocation
    async def editMessageLiveLocation(self,
      chat_id: int | str,
      message_id: int | str,
      latitude: str | float,
      longitude: str | float,
      live_period: int | None = None,
      reply_markup: str | None = None
    ):
      """Use this method to edit live location messages sent by the bot or via the bot (for inline bots). On success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of the original message.
          latitude (str | float): Latitude of new location.
          longitude (str | float): Longitude of new location.
          live_period (int | None): Period in seconds for which the location will be updated (see Live Locations).
          reply_markup (str | None): A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
      """
      return await editMessageLiveLocation().Initialize(
        chat_id,
        message_id,
        latitude,
        longitude,
        live_period,
        reply_markup
      )
    # methods: stopMessageLiveLocation
    async def stopMessageLiveLocation(self,
      chat_id: int | str,
      message_id: int | str,
      reply_markup: str | None = None
    ):
      """Use this method to stop updating a live location message sent by the bot or via the bot (for inline bots). On success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of the original message.
          reply_markup (str | None): A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
      """
      return await stopMessageLiveLocation().Initialize(chat_id, message_id, reply_markup)
    # methods: editMessageReplyMarkup
    async def editMessageReplyMarkup(self,
      chat_id: int | str,
      message_id: int | str,
      reply_markup: str
    ):
      """Use this method to edit only the reply markup of messages sent by the bot or via the bot (for inline bots). On success, if edited message is sent by the bot, the edited Message is returned, otherwise True is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of the original message.
          reply_markup (str): A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
      """
      return await editMessageReplyMarkup().Initialize(chat_id, message_id, reply_markup)
    
    # methods: stopPoll
    async def stopPoll(self,
      chat_id: int | str,
      message_id: int | str
    ):
      """Use this method to stop a poll which was sent by the bot. On success, the stopped Poll object is returned.

      Args:
          chat_id (int): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
          message_id (int): Identifier of the original message with the poll.
      """
      return await stopPoll().Initialize(chat_id, message_id)
    # methods: getAvailableGifts
    async def getAvailableGifts(self):
      """Returns the list of gifts that can be sent by the bot to users and channel chats. Requires no parameters. Returns a Gifts object."""
      return await getAvailableGifts().Initialize()
  # Bot Commands
  def command(self, command: str):
    return BotCommands(command)
  
  # Bot  Event
  def EventWatchers(self, event_list: Literal["UserRequest", "UserJoined", "UserLeft"]):
    return EventWatcher(event_list)
bot = Bot()