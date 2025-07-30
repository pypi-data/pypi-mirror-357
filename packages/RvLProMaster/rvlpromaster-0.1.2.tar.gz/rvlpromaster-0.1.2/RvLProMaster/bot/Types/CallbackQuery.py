class _CallbackQuery:
    def __init__(self) -> None:
      self.message = self._Message()
      self.data = ''
      self.id = ''
      
    class _Message:
      def __init__(self) -> None:
        self.message_id = ''
      
CallbackQuery  = _CallbackQuery()