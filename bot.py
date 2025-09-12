import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT = os.getenv("ADMIN_CHAT")  # ID админ-чата
LOGO_PATH = os.getenv("LOGO_PATH", "logo.jpg")  # путь к логотипу

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    text = (
        "👋 Добро пожаловать в студию детейлинга *CLUSTER*!\n\n"
        "🚗 Мы предлагаем:\n"
        "— Полировку\n"
        "— Жидкую керамику\n"
        "— Химчистку салона\n\n"
        "Напишите нам, чтобы записаться или задать вопрос."
    )
    if os.path.exists(LOGO_PATH):
        await message.answer_photo(photo=open(LOGO_PATH, "rb"), caption=text, parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

# Все входящие сообщения → в админ-чат
@dp.message()
async def forward_to_admin(message: types.Message):
    if ADMIN_CHAT:
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT,
                text=f"📩 Сообщение от @{message.from_user.username or message.from_user.id}:\n{message.text}"
            )
        except Exception as e:
            print(f"Ошибка пересылки в админ-чат: {e}")

    await message.answer("✅ Спасибо за сообщение! Мы скоро свяжемся с вами.")

async def main():
    print("✅ Bot started successfully")
    await dp.start_polling(bot)

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"⚠️ Ошибка: {e}. Перезапуск через 5 секунд...")
            asyncio.run(asyncio.sleep(5))