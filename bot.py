import os

print("==== DEBUG VARIABLES ====")
for k, v in os.environ.items():
    if "TOKEN" in k or "CHAT" in k or "LOGO" in k:
        print(f"{k} = {v!r}")
print("==== END DEBUG ====")
# bot.py
import os
import asyncio

async def main():
    bot_token = os.getenv("BOT_TOKEN")
    print("========== TEST ENV ==========")
    print(f"BOT_TOKEN from env: {repr(BOT_TOKEN)}")
    print("==============================")

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set!")
    else:
        # Просто бесконечный цикл, чтобы контейнер не падал
        while True:
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())