# bot.py
import os
import asyncio

async def main():
    bot_token = os.getenv("BOT_TOKEN")
    print("========== TEST ENV ==========")
    print(f"BOT_TOKEN from env: {repr(bot_token)}")
    print("==============================")

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set!")
    else:
        # Просто бесконечный цикл, чтобы контейнер не падал
        while True:
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())