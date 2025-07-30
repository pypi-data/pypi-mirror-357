from .extract_polling import Telegram
from ..utils import GetDate
import asyncio

async def RunBOT(always_run: bool = True, save_polling: bool = False):
  if always_run == True and save_polling == True:
      print(f"⚙️  Bot Running...\nAlways Run: {always_run}\nSave Polling: {save_polling}\nRunning At: {GetDate()}")
      while True:
          await Telegram().ExtractPolling(save_polling=True)
          await asyncio.sleep(1)
  elif always_run == True and save_polling == False:
      print(f"⚙️  Bot Running...\nAlways Run: {always_run}\nSave Polling: {save_polling}\nRunning At: {GetDate()}")
      while True:
          await Telegram().ExtractPolling()
          await asyncio.sleep(1)
  elif always_run == False and save_polling == True:
      print(f"⚙️  Bot Running...\nAlways Run: {always_run}\nSave Polling: {save_polling}\nRunning At: {GetDate()}")
      while True:
          await Telegram().ExtractPolling(save_polling=True)
          await asyncio.sleep(1)
  elif always_run == False and save_polling == False:
      print(f"⚙️  Bot Running...\nAlways Run: {always_run}\nSave Polling: {save_polling}\nRunning At: {GetDate()}")
      await Telegram().ExtractPolling()
      await asyncio.sleep(1)
  else:
      print(f"Please Spesify always_run parameter\nIf Set To True BOT Will Receive The Latest Polls Continuously (Real Time) And Send Any Response Method Only Once\nIf Set To False BOT Will Receive Latest Poll Once And Send Any Response Method Only Once Then Bot Will Stop")