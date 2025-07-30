## Hi Welcome To RvLProMaster 

##### First You Need Make Virtual Environment
```bash
python3 -m venv .venv
```

##### You Need Activate Virtual Environment
```bash
source .venv/bin/activate
```

##### Install This Project
```bash
pip install RvLProMaster
```

##### Create File Main.py To Use Bots
```python
from RvLProMaster import RunBOT, Message, bot
import asyncio


@bot.command("/start")
async def command_start():
  await bot.Methods.sendMessage(
  Message.chat.id,
  f"*Hi I'm Bots*",
  "MarkdownV2",
  reply_message=True,
)

if __name__ == __main__:
  try:
  asyncio.run(RunBOT(always_run=True, save_polling=True))
  except KeyboardInterrupt:
    print("\nBot Stopped")
```

### Notes:
The first time the bot is run, you will be asked for a `token` and `endpoint`, so fill it in with the `token` and `endpoint` of your choice.


#### Contact Me
<a href="https://t.me/YudhoPatrianto"><img alt="Telegram" src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" /></a>