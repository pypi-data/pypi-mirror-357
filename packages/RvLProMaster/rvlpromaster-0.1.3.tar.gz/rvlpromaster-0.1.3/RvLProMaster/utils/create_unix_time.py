from typing import Literal, Optional
from .create_log import CreateLog
from datetime import datetime, timedelta, timezone
import time


class UnixTime:
  @classmethod
  def TimeToUnix(cls, input_seconds: int):
    current_time = datetime.now(timezone.utc)
    gather_time = current_time + timedelta(seconds=input_seconds)
    return int(gather_time.timestamp())

  @classmethod
  def convertFromTimestamp(cls,
    preset: Literal['1 Minutes', '1 Hours', '30 Days', '366 Days']
  ):
    # 1 Minutes Unix Time
    if preset == "1 Hours":
      return cls.TimeToUnix(int('3600'))
    # 1 Hours Unix Time
    elif preset == "1 Minutes":
      return cls.TimeToUnix(int('60'))
    # 30 Days Unix Time
    elif preset == "30 Days":
      return cls.TimeToUnix(int('2592000'))
    # 365 Days Unix Time
    elif preset == "366 Days":
      return cls.TimeToUnix(int('31622400'))
    else:
      CreateLog("ERROR", "Please select a valid preset")