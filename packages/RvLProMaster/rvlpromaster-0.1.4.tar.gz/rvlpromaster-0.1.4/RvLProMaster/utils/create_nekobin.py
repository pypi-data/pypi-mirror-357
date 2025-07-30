from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from ..config import nekobin_api
from .create_log import CreateLog

async def CreateNekobin(pasted_text: str):
  """Pasted Text Into Nekobin

  Args:
      pasted_text (str): Your Pasted Text
  """
  payload = {'content': pasted_text}
  async with ClientSession() as session:
    async with session.post(f"{nekobin_api}/api/documents", data=payload) as client:
      raw_data = await client.json()
      if 'result' in raw_data:
        keys = raw_data['result'].get("key")
        return f"{nekobin_api}/{keys}"
      else:
        CreateLog("ERROR", "Not Found Keys")
        
        
    