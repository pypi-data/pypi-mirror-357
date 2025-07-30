class MESSAGE:
    def __init__(self) -> None:
        self.From = self._from()
        self.chat = self.Chat()
        self.reply_to_message = self.ReplyToMessage()
        self.text = '' # message.text
        self.date = '' # message.date
        self.message_id = '' # message.message_id
    
    # message.reply_to_message    
    class ReplyToMessage:
        def __init__(self) -> None:
            self.message_id = '' # message.reply_to_message.message_id
            self.text = '' # message.reply_to_message.text
            self.From = self._from() # message.reply_to_message.From
            self.chat = self.Chat() # message.reply_to_message.chat
            self.photo = self._photo()
            
        class _photo:
            def __init__(self) -> None:
                self.file_id = '' # message.reply_to_message.photo.file_id
        # message.reply_to_message.From
        class _from:
            def __init__(self) -> None:
                self.id = '' # message.reply_to_message.From.id
                self.is_bot = '' # message.reply_to_message.From.is_bot
                self.first_name = '' # message.reply_to_message.From.first_name
                self.last_name = '' # message.reply_to_message.From.last_name
                self.username = '' # message.reply_to_message.From.username
                
        # message.reply_to_message.chat
        class Chat:
            def __init__(self) -> None:
                self.id = '' # message.reply_to_message.chat.id
                self.title = '' # message.reply_to_message.chat.title
                self.username = '' # message.reply_to_message.chat.username
                self.type = '' # message.reply_to_message.chat.type
    
    # message.From
    class _from:
        def __init__(self) -> None:
            self.id = '' # message.From.id
            self.first_name = '' # message.From.first_name
            self.last_name = '' # message.From.last_name
            self.username = '' # message.From.username

    # message.chat
    class Chat:
        def __init__(self) -> None:
            self.id = '' # message.chat.id
            self.title = '' # message.chat.title
            self.username = '' # message.chat.username
# create istance
Message = MESSAGE()