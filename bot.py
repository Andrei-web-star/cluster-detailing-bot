import os

print("=== DEBUG VARIABLES ===")
for k, v in os.environ.items():
    if "BOT" in k or "TOKEN" in k or "CHAT" in k:
        print(f"{k} = {v}")
print("=== END DEBUG ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set!")

print("BOT_TOKEN is OK ✅")