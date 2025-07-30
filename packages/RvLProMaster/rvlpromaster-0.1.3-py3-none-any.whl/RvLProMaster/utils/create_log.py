from typing import Literal
from datetime import datetime
import os
import inspect
import glob

def findLog():
    """Find the log file in the current directory and its subdirectories."""
    for log_position in glob.iglob(f"./**/bot.log", recursive=True):
        return os.path.abspath(log_position)
    return None

def CreateLog(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    message: str
):
    """The Utility function for creating logs.

    Args:
        level : Log Level
            - DEBUG: Debugging information
            - INFO: General information
            - WARNING: Warning messages
            - ERROR: Error messages
            - CRITICAL: Critical error messages
        message (str): Your Message Wants to display into log
    """
    now = datetime.now()
    day_name = now.strftime('%A')  # nama hari
    formatted_time = now.strftime('%d-%B-%Y %I:%M:%S %p')
    call_frame = inspect.stack()[1]
    get_running_file = os.path.basename(call_frame.filename).replace('.py', '')
    log_pattern = f"{day_name} {formatted_time} {level} {get_running_file} - {message}"
    print(log_pattern)
    with open(str(findLog()), "a") as f:
        f.write(f"\n{log_pattern}") 
    