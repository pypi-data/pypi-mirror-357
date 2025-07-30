from typing import Any

class BaseException(Exception):
  pass

class exceptions:
  class TEXT_ESCAPED(BaseException):
    def __init__(self, message: Any, status_code: int):
      self.message = message
      self.status_code = status_code
      super().__init__(message)
    
    def __str__(self) -> str:
      return f"{self.status_code}: {self.message}"