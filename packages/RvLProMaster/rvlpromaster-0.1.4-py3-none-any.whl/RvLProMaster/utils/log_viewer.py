import glob
import os
from .create_log import CreateLog

def LogViewer():
  for log_posisition in glob.iglob(f"./**/bot.log", recursive=True):
    filepath_log = os.path.abspath(log_posisition)
    with open(filepath_log, "r") as stream:
      return stream.read()
  CreateLog("ERROR", "File Log Not Found")
  return None