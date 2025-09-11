import os
from aiogram import Bot, Dispatcher
import asyncio

# Проверяем переменные окружения
print("==== DEBUG VARIABLES ====")
for k, v in os.environ.items():
    if "BOT" in k or "CHAT" in k or "LOGO" in k:
        print(f"{k} = {v}")
print("==== END DEBUG ====")

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