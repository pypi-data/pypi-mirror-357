from datetime import datetime

def GetDate():
    return datetime.now().strftime("%A, %d %B %Y %I.%M %p")