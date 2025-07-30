from ..utils import CreateLog
import os
import json
import sys


def SavePolling(out_updates: str):
  """save polling data to a file"""
  base_dir = os.getcwd()
  full_path = f"{base_dir}/event.json"
  pretty_print = str(json.dumps(out_updates, indent=2))
  
  if os.path.exists(full_path):
    with open(full_path, "w") as f:
      f.write(pretty_print)
  else:
    CreateLog("ERROR", f"File Not Found")
    with open(full_path, "w") as f:
      f.write(pretty_print)