import os

print("=== ENV DEBUG START ===")
print("BOT_TOKEN =", repr(os.getenv("BOT_TOKEN")))
print("ADMIN_CHAT_ID =", repr(os.getenv("ADMIN_CHAT_ID")))
print("LOGO_PATH =", repr(os.getenv("LOGO_PATH")))
print("=== ENV DEBUG END ===")

import time
time.sleep(300)  # держим контейнер живым 5 минут
