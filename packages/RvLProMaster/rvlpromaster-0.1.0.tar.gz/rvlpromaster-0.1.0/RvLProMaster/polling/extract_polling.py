from .long_poling import LongPolling
from ..bot import Message, ChatJoinRequest, CallbackQuery, NewChatParticipant, LeftChatParticipant
from ..utils import CreateLog
from .save_polling import SavePolling
from ..bot import pick_command, event_pick, pick_callback_button
import asyncio
import json

class Telegram:
  def __init__(self):
    self.current_event = ''
    self.message = Message
    self.chat_join_request = ChatJoinRequest
    self.callback_query = CallbackQuery
    self.new_chat_participant = NewChatParticipant
    self.left_chat_participant = LeftChatParticipant
  async def ExtractPolling(self, save_polling: bool = False):
    while True:
      try:
        self.out_updates = await LongPolling()
        self.current_event = ''
        # Message
        if "message" in self.out_updates:
          msg_key = self.out_updates["message"]
          
          # message
          self.message.text = msg_key.get("text", "")
          self.message.message_id = msg_key.get("message_id", "")
          self.message.date = msg_key.get("date", "")
          
          # message.chat
          self.message.chat.id = msg_key["chat"].get("id", "")
          self.message.chat.title = msg_key["chat"].get("title", "")
          self.message.chat.username = f"@{msg_key["chat"].get("username", "")}"
          
          # mmessage.chat.from
          self.message.From.id = msg_key["from"].get("id", "")
          self.message.From.first_name = msg_key["from"].get("first_name", "")
          self.message.From.last_name = msg_key["from"].get("last_name", "")
          self.message.From.username = f"@{msg_key["from"].get("username", "")}"          
          
          if "reply_to_message" in msg_key:
            reply_key = msg_key["reply_to_message"]
            # message.reply_to_message
            self.message.reply_to_message.message_id = reply_key.get("message_id", "")
            self.message.reply_to_message.text = reply_key.get("text", "")
            
            # message.reply_to_message.From
            self.message.reply_to_message.From.id = reply_key["from"].get("id", "")
            self.message.reply_to_message.From.first_name = reply_key["from"].get("first_name", "")
            self.message.reply_to_message.From.last_name = reply_key["from"].get("last_name", "")
            self.message.reply_to_message.From.username = f"@{reply_key["from"].get("username", "")}"
            
            # message.reply_to_message.chat
            self.message.reply_to_message.chat.id = reply_key["chat"].get("id", "")
            self.message.reply_to_message.chat.title = reply_key["chat"].get("title", "")
            self.message.reply_to_message.chat.username = f"@{reply_key["chat"].get("username", "")}"
            self.message.reply_to_message.chat.type = reply_key["chat"].get("type", "")
            self.message.reply_to_message.chat.type = reply_key["chat"].get("type", "")
            
            # message.reply_to_message.photo
            if 'photo' in reply_key and len(reply_key['photo']) > 0:
                if reply_key['photo'][0]:
                    self.message.reply_to_message.photo.file_id = reply_key['photo'][0].get("file_id", "")
                if len(reply_key['photo']) > 1 and reply_key['photo'][1]:
                    self.message.reply_to_message.photo.file_id = reply_key['photo'][1].get("file_id", "")
          await self.DispatchCommand()

          # New Chat Participant
          if "new_chat_participant" in self.out_updates["message"]:
            self.current_event = "new_chat_participant"
            
            # new_chat_participant
            self.new_chat_participant.id = self.out_updates["message"]["new_chat_participant"].get("id", "")
            self.new_chat_participant.is_bot = self.out_updates["message"]["new_chat_participant"].get("is_bot", "")  
            self.new_chat_participant.first_name = self.out_updates["message"]["new_chat_participant"].get("first_name", "")
            self.new_chat_participant.last_name = self.out_updates["message"]["new_chat_participant"].get("last_name", "")
            self.new_chat_participant.username = f"@{self.out_updates["message"]["new_chat_participant"].get("username", "")}"
            self.new_chat_participant.language_code = self.out_updates["message"]["new_chat_participant"].get("language_code", "")
            # new_chat_participant.message
            self.new_chat_participant.message.message_id = self.out_updates["message"].get("message_id", "")            
            # new_chat_participant.message.chat
            self.new_chat_participant.message.chat.id = self.out_updates["message"]["chat"].get("id", "")
            self.new_chat_participant.message.chat.title = self.out_updates["message"]["chat"].get("title", "")
            self.new_chat_participant.message.chat.username = f"@{self.out_updates["message"]["chat"].get("username", "")}"
            self.new_chat_participant.message.chat.type = self.out_updates["message"]["chat"].get("type", "")
            await DispatchUser().UserJoined(self.current_event)
          # Left Chat Participant
          elif "left_chat_participant" in self.out_updates["message"]:
            self.current_event = "left_chat_participant"
            
            # left_chat_participant
            self.left_chat_participant.id = self.out_updates["message"]["left_chat_participant"].get("id", "")
            self.left_chat_participant.is_bot = self.out_updates["message"]["left_chat_participant"].get("is_bot", "")  
            self.left_chat_participant.first_name = self.out_updates["message"]["left_chat_participant"].get("first_name", "")
            self.left_chat_participant.last_name = self.out_updates["message"]["left_chat_participant"].get("last_name", "")
            self.left_chat_participant.username = f"@{self.out_updates["message"]["left_chat_participant"].get("username", "")}"
            self.left_chat_participant.language_code = self.out_updates["message"]["left_chat_participant"].get("language_code", "")
            # left_chat_participant.message
            self.left_chat_participant.message.message_id = self.out_updates["message"].get("message_id", "")            
            # left_chat_participant.message.chat
            self.left_chat_participant.message.chat.id = self.out_updates["message"]["chat"].get("id", "")
            self.left_chat_participant.message.chat.title = self.out_updates["message"]["chat"].get("title", "")
            self.left_chat_participant.message.chat.username = f"@{self.out_updates["message"]["chat"].get("username", "")}"
            self.left_chat_participant.message.chat.type = self.out_updates["message"]["chat"].get("type", "")
            await DispatchUser().UserLeft(self.current_event)
        # Callback Query
        elif "callback_query" in self.out_updates:
          self.callback_query.message.message_id = self.out_updates["callback_query"]["message"].get("message_id", "")
          self.callback_query.data = self.out_updates["callback_query"].get("data", "")
          self.callback_query.id = self.out_updates["callback_query"].get("id", "")
          await self.DispatchCallbackQuery()
        
        # Request join
        elif "chat_join_request" in self.out_updates:
          self.current_event = "chat_join_request"
          req_key = self.out_updates["chat_join_request"]
          
          # chat_join_request
          self.chat_join_request.update_id =  req_key.get("update_id", "")
          self.chat_join_request.date = req_key.get("date", "")
          self.chat_join_request.user_chat_id = req_key.get("user_chat_id", "")
          
          # chat_join_request.chat
          self.chat_join_request.chat.id = req_key["chat"].get("id", "")
          self.chat_join_request.chat.title = req_key["chat"].get("title", "")
          self.chat_join_request.chat.username = f"@{req_key["chat"].get("username", "")}"
          self.chat_join_request.chat.type = req_key["chat"].get("type", "")
          
          # chat_join_request.from
          self.chat_join_request.From.id = req_key["from"].get("id", "")
          self.chat_join_request.From.is_bot = req_key["from"].get("is_bot", "")
          self.chat_join_request.From.first_name = req_key["from"].get("first_name", "")
          self.chat_join_request.From.last_name = req_key["from"].get("last_name", "")
          self.chat_join_request.From.username = f"@{req_key["from"].get("username", "")}"
          self.chat_join_request.From.language_code = req_key["from"].get("language_code", "")
          await asyncio.sleep(2)
          await DispatchUser().RequestJoin(self.current_event)
          
        if save_polling == True:
          SavePolling(self.out_updates)
        elif save_polling == False:
          pass
        return self
      except KeyError as poll_key_error:
        CreateLog("ERROR", f"Polling Error: {poll_key_error}")
        
  async def DispatchCommand(self):
    message = self.message
    if message.text:
      command = message.text.split()[0]
      if command in pick_command:
        await pick_command[command]()
  async def DispatchCallbackQuery(self):
    callback_keys = self.callback_query
    if callback_keys.data:
      callback = callback_keys.data
      if callback in pick_callback_button:
        await pick_callback_button[callback]()
        
        
# dispatch event
class DispatchUser:
  def __init__(self) -> None:
    tg = Telegram()
    self.chat_join_request = tg.chat_join_request
    self.new_chat_participant = tg.new_chat_participant
  # User Request
  async def RequestJoin(self, current_event: str):
    if current_event == "chat_join_request":
      current_event = ""
      if "UserRequest" in event_pick:
        await event_pick["UserRequest"]()
        
        # Reset All Value User Request 
        self.chat_join_request.update_id = "" 
        self.chat_join_request.date = "" 
        self.chat_join_request.user_chat_id = "" 
        
        # chat_join_request.chat
        self.chat_join_request.chat.title = "" 
        self.chat_join_request.chat.username = "" 
        self.chat_join_request.chat.type = "" 
        
        # chat_join_request.from
        self.chat_join_request.From.is_bot = ""
        self.chat_join_request.From.first_name = ""
        self.chat_join_request.From.last_name = ""
        self.chat_join_request.From.username = ""
        self.chat_join_request.From.language_code = ""
        
  # User Joined
  async def UserJoined(self, current_event: str):
    if current_event == "new_chat_participant":
      current_event = ""
      if "UserJoined" in event_pick:
        await event_pick["UserJoined"]()
        
        # Reset All Value User Joined
        self.new_chat_participant.id = ""
        self.new_chat_participant.is_bot = ""
        self.new_chat_participant.first_name = ""
        self.new_chat_participant.last_name = ""
        self.new_chat_participant.username = ""
        self.new_chat_participant.language_code = ""
        
        # new_chat_participant.message
        self.new_chat_participant.message.message_id = "" 
        # new_chat_participant.message.chat
        self.new_chat_participant.message.chat.title = "" 
        self.new_chat_participant.message.chat.username = "" 
        self.new_chat_participant.message.chat.type = ""
        
  # User Left
  async def UserLeft(self, current_event: str):
    if current_event == "left_chat_participant":
      current_event = ""
      if "UserLeft" in event_pick:
        await event_pick["UserLeft"]()
        
        # Reset All Value User Left
        self.new_chat_participant.id = ""
        self.new_chat_participant.is_bot = ""
        self.new_chat_participant.first_name = ""
        self.new_chat_participant.last_name = ""
        self.new_chat_participant.username = ""
        self.new_chat_participant.language_code = ""
        
        # new_chat_participant.message
        self.new_chat_participant.message.message_id = "" 
        # new_chat_participant.message.chat
        self.new_chat_participant.message.chat.title = "" 
        self.new_chat_participant.message.chat.username = "" 
        self.new_chat_participant.message.chat.type = ""  