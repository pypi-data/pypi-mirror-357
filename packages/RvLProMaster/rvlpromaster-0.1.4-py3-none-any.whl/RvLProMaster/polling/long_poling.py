from ..bot import bot
from .clear_polling import ClearPolling
import asyncio
import aiohttp

async def LongPolling():
  await ClearPolling()
  offset = None
  while True:
    from_updates = await bot.Updates.getUpdates(offset)
    inbound_updates = from_updates.raw_data
    if inbound_updates and "result" in inbound_updates:
      for outbound_updates in inbound_updates['result']:
        offset = outbound_updates["update_id"] + 1
        return outbound_updates
      await asyncio.sleep(1)