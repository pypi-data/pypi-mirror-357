# message.new_chat_participant
class _NewChatParticipant:
  def __init__(self) -> None:
    self.message = self._message()
    self.id = ''
    self.is_bot = ''
    self.first_name = ''
    self.last_name = ''
    self.username = ''
    self.language_code = ''
  
  class _message:
    def __init__(self) -> None:
      self.chat = self._chat()
      self.message_id = ''
    
    # message.new_chat_participant.chat
    class _chat:
      def __init__(self) -> None:
        self.id = ''
        self.title = ''
        self.username = ''
        self.type = ''
NewChatParticipant = _NewChatParticipant()