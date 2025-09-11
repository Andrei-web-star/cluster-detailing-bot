import os

print("=== DEBUG VARIABLES ===")
for key, value in os.environ.items():
    if "BOT" in key or "TOKEN" in key or "CHAT" in key or "LOGO" in key:
        print(f"{key} = {value}")
print("=== END DEBUG ===")

import asyncio
from aiogram import Bot, Dispatcher

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    print("Bot started OK ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())