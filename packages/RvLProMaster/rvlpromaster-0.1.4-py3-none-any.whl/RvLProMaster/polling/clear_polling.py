from ..config import endpoint
import aiohttp

async def ClearPolling():
  async with aiohttp.ClientSession() as session:
    async with session.get(f"{endpoint}/getUpdates") as client:
      raw_data = await client.json()
      
      if raw_data["result"]:
        search_offset = max(update["update_id"] for update in raw_data["result"]) + 1
        payload = {'offset': search_offset}
        async with session.get(f"{endpoint}/getUpdates", params=payload) as clients:
          await clients.read()
      else:
        pass