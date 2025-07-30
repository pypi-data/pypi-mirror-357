class ParseMode:
  """A class to handle parse modes for messages.
  - HTML
  - Markdown
  - MarkdownV2
  """
  @classmethod
  def HTML(cls):
    """HTML parse mode"""
    return "HTML"
  @classmethod
  def Markdown(cls):
    """Markdown parse mode"""
    return "Markdown"
  @classmethod
  def MarkdownV2(cls):
    """MarkdownV2 parse mode"""
    return "MarkdownV2"