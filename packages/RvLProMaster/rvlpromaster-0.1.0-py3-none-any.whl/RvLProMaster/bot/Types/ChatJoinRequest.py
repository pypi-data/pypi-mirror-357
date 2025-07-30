class _ChatJoinRequest:
    """
    This class represents a request to join a chat.
    """
    def __init__(self) -> None:
      self.chat = self._chat()
      self.From = self._from()
      self.update_id = ''
      self.user_chat_id = ''
      self.date = ''
    
    # chat
    class _chat:
      def __init__(self) -> None:
        self.id = ''
        self.title = ''
        self.username = ''
        self.type = ''
    
    # from
    class _from:
      def __init__(self) -> None:
        self.id = ''
        self.is_bot = ''
        self.first_name = ''
        self.last_name = ''
        self.username = ''
        self.language_code = ''
        
ChatJoinRequest = _ChatJoinRequest()