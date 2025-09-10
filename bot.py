# bot.py
import asyncio
import os
import re
import datetime
import urllib.parse
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove, FSInputFile, LinkPreviewOptions
)


# ============== ENV ==============
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOGO_PATH = os.getenv("LOGO_PATH", "logo.jpg")

# несколько админов через запятую
raw_admin_ids = os.getenv("ADMIN_CHAT_ID", "0")
ADMIN_CHAT_IDS = [
    int(x) for x in raw_admin_ids.split(",")
    if x.strip() and x.strip().lstrip("-").isdigit()
]

# ============== AIOGRAM ==============
bot = Bot(BOT_TOKEN)   # aiogram 3.x
dp = Dispatcher()

# ============== Названия и Цены ==============
PRETTY = {
    # типы кузова
    "sedan": "Легковой", "cuv": "Кроссовер", "suv": "Внедорожник", "minivan": "Минивэн",
    # разделы
    "wash": "Мойка", "dry": "Уборка/химчистка салона", "polish": "Полировка",
    "wax": "Покрытие воском", "nano": "Нанокерамика", "extras": "Доп. услуги",
    # мойка
    "standard": "Мойка STANDARD", "extra": "Мойка EXTRA", "element": "Мойка ELEMENT",
    "bitumen_remove": "Удаление битумных пятен",
    "disc_decontam": "Очистка дисков (деконтам.)",
    "oxides_remove": "Удаление оксидов/жёлтых пятен",
    "engine_wash": "Мойка двигателя*",
    # салон
    "interior_clean": "Уборка салона",
    "full_chem": "Химчистка салона (полная)",
    "seat_chem": "Химчистка сидений",
    "leather_care": "Обработка кожи салона",
    "ozone": "Озонирование салона",
    # полировка
    "protect": "Защитная полировка",
    "restore": "Восстановительная полировка",
    "headlights": "Полировка фар",
    # воск / допы
    "hard": "Покрытие твёрдым воском",
    "anti_rain": "Антидождь (лобовое)",
    # nano
    "body_coating": "Нанокерамика кузова (индивидуально)",
    "interior_coating": "Нанокерамика интерьера (индивидуально)",
}

PRICES = {
    "wash": {
        "standard": {"sedan": 2500, "cuv": 2700, "suv": 2700, "minivan": 2700},
        "extra":    {"sedan": 4000, "cuv": 4500, "suv": 4500, "minivan": 4500},
        "element":  {"sedan": 6000, "cuv": 7000, "suv": 7000, "minivan": 7000},
        # допы
        "bitumen_remove":  {"sedan": 800,  "cuv": 1000, "suv": 1000, "minivan": 1000},
        "disc_decontam":   {"sedan": 800,  "cuv": 1000, "suv": 1000, "minivan": 1000},
        "oxides_remove":   {"sedan": 800,  "cuv": 1000, "suv": 1000, "minivan": 1000},
        "engine_wash":     {"sedan": 3500, "cuv": 4000, "suv": 4000, "minivan": 4000},
    },
    "dry": {
        "interior_clean":  {"sedan": 1200,  "cuv": 1400, "suv": 1400, "minivan": 1400},
        "full_chem":       {"sedan": 12000, "cuv": 12000,"suv": 12000,"minivan": 12000},
        "seat_chem":       {"sedan": 6000,  "cuv": 6000, "suv": 6000, "minivan": 6000},
        "leather_care":    {"sedan": 2500,  "cuv": 2500, "suv": 2500, "minivan": 2500},
        "ozone":           {"sedan": 2000,  "cuv": 2000, "suv": 2000, "minivan": 2000},
    },
    "polish": {
        "protect":     {"sedan": 12000, "cuv": 15000, "suv": 15000, "minivan": 15000},
        "restore":     {"sedan": 16000, "cuv": 18000, "suv": 18000, "minivan": 18000},
        "headlights":  {"sedan": 2500,  "cuv": 2500,  "suv": 2500,  "minivan": 2500},
    },
    "wax": {"hard": {"sedan": 6000, "cuv": 7000, "suv": 7000, "minivan": 7000}},
    "nano": { "body_coating": None, "interior_coating": None },
    "extras": {"anti_rain": {"sedan": 3000, "cuv": 3500, "suv": 3500, "minivan": 3500}},
}

# ============== Главное меню ==============
def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗓 Онлайн-бронирование")],
            [KeyboardButton(text="💰 Рассчитать стоимость")],
            [KeyboardButton(text="📸 Наши работы"), KeyboardButton(text="⭐ Отзывы")],
            [KeyboardButton(text="🎁 Акции"), KeyboardButton(text="📍 Контакты / Маршрут")],
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start_cmd(m: Message):
    caption = "СТУДИЯ ДЕТЕЙЛИНГА CLUSTER\n\nВыберите действие в меню ниже."
    if os.path.exists(LOGO_PATH):
        await m.answer_photo(FSInputFile(LOGO_PATH), caption=caption, reply_markup=main_menu())
    else:
        await m.answer("🚗 CLUSTER — студия детейлинга\n\nВыберите действие в меню ниже.", reply_markup=main_menu())

@dp.message(Command("help"))
async def help_cmd(m: Message):
    await m.answer("Доступно: онлайн-бронирование, калькулятор, работы, отзывы, акции, контакты.", reply_markup=main_menu())

@dp.message(Command("whereami"))
async def whereami(m: Message):
    await m.answer(f"chat_id: {m.chat.id}")

@dp.message(Command("myid"))
async def myid(m: Message):
    await m.answer(f"Ваш Telegram ID: {m.from_user.id}")

# универсальная «Домой»
HOME_BTN = [InlineKeyboardButton(text="🏠 Главное меню", callback_data="nav:main")]

@dp.callback_query(F.data == "nav:main")
async def back_to_main(c: CallbackQuery):
    await c.message.answer("Вы вернулись в главное меню:", reply_markup=main_menu())
    await c.answer()

# ============== Бронирование ==============
def booking_root_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=PRETTY["wash"],   callback_data="svc:wash")],
        [InlineKeyboardButton(text=PRETTY["dry"],    callback_data="svc:dry")],
        [InlineKeyboardButton(text=PRETTY["polish"], callback_data="svc:polish")],
        [InlineKeyboardButton(text=PRETTY["wax"],    callback_data="svc:wax")],
        [InlineKeyboardButton(text="Лёгкая керамика / кварц", callback_data="svc:lightcoat")],
        [InlineKeyboardButton(text=PRETTY["nano"],   callback_data="svc:nano")],
        [InlineKeyboardButton(text="Исправление вмятин (PDR)", callback_data="svc:pdr")],
        [InlineKeyboardButton(text="Стёкла (ремонт/замена)",   callback_data="svc:glass")],
        [InlineKeyboardButton(text="Тонировка",                callback_data="svc:tint")],
        HOME_BTN
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def share_phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Поделиться номером", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )

@dp.message(F.text == "🗓 Онлайн-бронирование")
async def booking_entry(m: Message):
    await m.answer("Выберите услугу:", reply_markup=ReplyKeyboardRemove())
    await m.answer("Категории услуг:", reply_markup=booking_root_kb())

@dp.callback_query(F.data == "nav:booking_root")
async def back_to_booking_root(c: CallbackQuery):
    await c.message.edit_text("Категории услуг:", reply_markup=booking_root_kb())
    await c.answer()

def with_home(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[*rows,
                         [InlineKeyboardButton(text="⬅️ Назад к разделам", callback_data="nav:booking_root")],
                         HOME_BTN]
    )

def back_home_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к разделам", callback_data="nav:booking_root")],
        HOME_BTN
    ])

def wash_kb() -> InlineKeyboardMarkup:
    return with_home(
        [InlineKeyboardButton(text=PRETTY["standard"], callback_data="wash:standard")],
        [InlineKeyboardButton(text=PRETTY["extra"],    callback_data="wash:extra")],
        [InlineKeyboardButton(text=PRETTY["element"],  callback_data="wash:element")],
        [InlineKeyboardButton(text="Доп. опции мойки", callback_data="wash:extras")],
    )

def wash_extras_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=PRETTY["bitumen_remove"], callback_data="wash:bitumen_remove")],
        [InlineKeyboardButton(text=PRETTY["disc_decontam"],  callback_data="wash:disc_decontam")],
        [InlineKeyboardButton(text=PRETTY["oxides_remove"],  callback_data="wash:oxides_remove")],
        [InlineKeyboardButton(text=PRETTY["engine_wash"],    callback_data="wash:engine_wash")],
        [InlineKeyboardButton(text="⬅️ К мойке", callback_data="svc:wash")],
        HOME_BTN
    ])

def dry_kb() -> InlineKeyboardMarkup:
    return with_home(
        [InlineKeyboardButton(text=PRETTY["interior_clean"], callback_data="dry:interior_clean")],
        [InlineKeyboardButton(text=PRETTY["full_chem"],      callback_data="dry:full_chem")],
        [InlineKeyboardButton(text=PRETTY["seat_chem"],      callback_data="dry:seat_chem")],
        [InlineKeyboardButton(text=PRETTY["leather_care"],   callback_data="dry:leather_care")],
        [InlineKeyboardButton(text=PRETTY["ozone"],          callback_data="dry:ozone")],
    )

def polish_kb() -> InlineKeyboardMarkup:
    return with_home(
        [InlineKeyboardButton(text=PRETTY["protect"],    callback_data="polish:protect")],
        [InlineKeyboardButton(text=PRETTY["restore"],    callback_data="polish:restore")],
        [InlineKeyboardButton(text=PRETTY["headlights"], callback_data="polish:headlights")],
    )

def nano_kb() -> InlineKeyboardMarkup:
    return with_home(
        [InlineKeyboardButton(text=PRETTY["body_coating"],     callback_data="nano:body_coating")],
        [InlineKeyboardButton(text=PRETTY["interior_coating"], callback_data="nano:interior_coating")],
    )

def tint_kb() -> InlineKeyboardMarkup:
    return with_home(
        [InlineKeyboardButton(text="Задняя полусфера",               callback_data="tint:rear")],
        [InlineKeyboardButton(text="Задняя + передние боковые",      callback_data="tint:rear_front")],
        [InlineKeyboardButton(text="Передняя полусфера",             callback_data="tint:front")],
        [InlineKeyboardButton(text="Передняя + задняя полусферы",    callback_data="tint:both")],
    )

booking_state: dict[int, dict] = {}  # {user_id: {"category": "...", "option": "..."}}

@dp.callback_query(F.data.startswith("svc:"))
async def booking_tree(c: CallbackQuery):
    svc = c.data.split(":")[1]
    if svc == "wash":
        await c.message.edit_text(f"{PRETTY['wash']} — выберите опцию:", reply_markup=wash_kb())
    elif svc == "dry":
        await c.message.edit_text(f"{PRETTY['dry']} — выберите опцию:", reply_markup=dry_kb())
    elif svc == "polish":
        await c.message.edit_text(f"{PRETTY['polish']} — выберите тип:", reply_markup=polish_kb())
    elif svc == "wax":
        booking_state[c.from_user.id] = {"category": PRETTY["wax"], "option": PRETTY["hard"]}
        await c.message.edit_text(f"{PRETTY['wax']}. Оставьте телефон для записи.", reply_markup=back_home_kb())
        await c.message.answer("Нажмите кнопку, чтобы поделиться номером:", reply_markup=share_phone_kb())
    elif svc == "lightcoat":
        booking_state[c.from_user.id] = {"category": "Лёгкая керамика/кварц", "option": "—"}
        await c.message.edit_text("Лёгкая керамика/кварц — рассчитайте в калькуляторе или оставьте телефон.", reply_markup=back_home_kb())
        await c.message.answer("Нажмите кнопку, чтобы поделиться номером:", reply_markup=share_phone_kb())
    elif svc == "nano":
        await c.message.edit_text(f"{PRETTY['nano']} — выберите:", reply_markup=nano_kb())
    elif svc == "pdr":
        booking_state[c.from_user.id] = {"category": "Исправление вмятин (PDR)", "option": "по фото"}
        await c.message.edit_text("PDR — пришлите фото вмятины, затем оставьте телефон.", reply_markup=back_home_kb())
        await c.message.answer("Нажмите кнопку, чтобы поделиться номером:", reply_markup=share_phone_kb())
    elif svc == "glass":
        booking_state[c.from_user.id] = {"category": "Стёкла (ремонт/замена)", "option": "уточнить марку/год"}
        await c.message.edit_text("Стёкла — ремонт скола / замена (укажите марку/модель/год).", reply_markup=back_home_kb())
        await c.message.answer("Нажмите кнопку, чтобы поделиться номером:", reply_markup=share_phone_kb())
    elif svc == "tint":
        await c.message.edit_text("Тонировка — выберите вариант:", reply_markup=tint_kb())
    await c.answer()

@dp.callback_query(F.data == "wash:extras")
async def wash_extras(c: CallbackQuery):
    await c.message.edit_text("Доп. опции мойки:", reply_markup=wash_extras_kb())
    await c.answer()

@dp.callback_query(F.data.startswith(("wash:", "dry:", "polish:", "nano:", "tint:")))
async def booking_leaf(c: CallbackQuery):
    cat, opt = c.data.split(":")[0], c.data.split(":")[1]
    cat_name = PRETTY.get(cat, cat)
    opt_name = PRETTY.get(opt, opt)
    booking_state[c.from_user.id] = {"category": cat_name, "option": opt_name}
    await c.message.edit_text(
        f"Вы выбрали: {cat_name} → {opt_name}\n\nОставьте номер телефона для подтверждения записи.",
        reply_markup=back_home_kb()
    )
    await c.message.answer("Нажмите кнопку ниже или напишите номер текстом:", reply_markup=share_phone_kb())
    await c.answer()

@dp.message(F.photo)
async def photo_intake(m: Message):
    await m.answer("Фото получено ✅ Напишите, пожалуйста, номер телефона для связи.", reply_markup=share_phone_kb())

# ============== Калькулятор ==============
@dataclass
class Calc:
    car_type: str | None = None
    category: str | None = None
    option: str | None = None

calc_state: dict[int, Calc] = {}

def calc_types_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=PRETTY["sedan"],   callback_data="calc:type:sedan")],
        [InlineKeyboardButton(text=PRETTY["cuv"],     callback_data="calc:type:cuv")],
        [InlineKeyboardButton(text=PRETTY["suv"],     callback_data="calc:type:suv")],
        [InlineKeyboardButton(text=PRETTY["minivan"], callback_data="calc:type:minivan")],
        HOME_BTN
    ])

def calc_categories_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=PRETTY["wash"],   callback_data="calc:cat:wash")],
        [InlineKeyboardButton(text=PRETTY["dry"],    callback_data="calc:cat:dry")],
        [InlineKeyboardButton(text=PRETTY["polish"], callback_data="calc:cat:polish")],
        [InlineKeyboardButton(text=PRETTY["wax"],    callback_data="calc:cat:wax")],
        [InlineKeyboardButton(text=PRETTY["nano"],   callback_data="calc:cat:nano")],
        [InlineKeyboardButton(text=PRETTY["extras"], callback_data="calc:cat:extras")],
        [InlineKeyboardButton(text="⬅️ Назад к типу авто", callback_data="calc:back_type")],
        HOME_BTN
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def calc_options_kb(category: str) -> InlineKeyboardMarkup:
    opts = list(PRICES[category].keys())
    rows = [[InlineKeyboardButton(text=PRETTY.get(o, o), callback_data=f"calc:opt:{o}")] for o in opts]
    rows.append([InlineKeyboardButton(text="⬅️ Назад к категориям", callback_data="calc:back_cat")])
    rows.append(HOME_BTN)
    return InlineKeyboardMarkup(inline_keyboard=rows)

@dp.message(F.text == "💰 Рассчитать стоимость")
async def calc_start(m: Message):
    calc_state[m.from_user.id] = Calc()
    await m.answer("Выберите тип авто:", reply_markup=ReplyKeyboardRemove())
    await m.answer("Тип кузова:", reply_markup=calc_types_kb())

@dp.callback_query(F.data == "calc:back_type")
async def back_type(c: CallbackQuery):
    await c.message.edit_text("Тип кузова:", reply_markup=calc_types_kb())
    await c.answer()

@dp.callback_query(F.data.startswith("calc:type:"))
async def choose_type(c: CallbackQuery):
    t = c.data.split(":")[2]
    s = calc_state.get(c.from_user.id) or Calc()
    s.car_type = t
    s.category = None
    s.option = None
    calc_state[c.from_user.id] = s
    await c.message.edit_text(f"Тип авто: {PRETTY[t]}\nТеперь выберите категорию:", reply_markup=calc_categories_kb())
    await c.answer()

@dp.callback_query(F.data == "calc:back_cat")
async def back_cat(c: CallbackQuery):
    await c.message.edit_text("Выберите категорию:", reply_markup=calc_categories_kb())
    await c.answer()

@dp.callback_query(F.data.startswith("calc:cat:"))
async def choose_category(c: CallbackQuery):
    cat = c.data.split(":")[2]
    s = calc_state.get(c.from_user.id)
    if not s or not s.car_type:
        await c.message.edit_text("Сначала выберите тип авто:", reply_markup=calc_types_kb())
        await c.answer(); return
    s.category = cat
    s.option = None
    calc_state[c.from_user.id] = s
    await c.message.edit_text(f"{PRETTY[cat]} — выберите опцию:", reply_markup=calc_options_kb(cat))
    await c.answer()

@dp.callback_query(F.data.startswith("calc:opt:"))
async def choose_option(c: CallbackQuery):
    opt = c.data.split(":")[2]
    s = calc_state.get(c.from_user.id)
    if not s or not s.car_type or not s.category:
        await c.message.edit_text("Сначала выберите тип авто:", reply_markup=calc_types_kb())
        await c.answer(); return

    price_map = PRICES[s.category][opt]
    if price_map is None:
        price_text = "индивидуально (уточним по фото/осмотру)"
    else:
        price_text = f"{price_map[s.car_type]} ₽"

    await c.message.edit_text(
        f"🧮 {PRETTY[s.category]} → {PRETTY.get(opt, opt)}\n"
        f"🚗 Тип авто: {PRETTY[s.car_type]}\n"
        f"💰 Стоимость: {price_text}\n\n"
        f"Хотите записаться? Отправьте номер телефона.",
        reply_markup=back_home_kb()
    )
    await c.message.answer("Нажмите кнопку, чтобы поделиться номером:", reply_markup=share_phone_kb())
    s.option = opt
    calc_state[c.from_user.id] = s
    await c.answer()

# ============== Уведомления админам ==============
async def notify_admin(user, phone: str):
    if not ADMIN_CHAT_IDS:
        return
    b = booking_state.get(user.id)
    s = calc_state.get(user.id)

    lines = [
        "🆕 <b>Новая заявка из бота</b>",
        f"👤 @{user.username or 'без_username'} (id {user.id})",
        f"📞 {phone}",
    ]
    if b:
        lines.append(f"🧩 Бронирование: {b.get('category','-')} → {b.get('option','-')}")
    if s and (s.category or s.option or s.car_type):
        cat = PRETTY.get(s.category, s.category) if s.category else "-"
        opt = PRETTY.get(s.option, s.option) if s.option else "-"
        ctype = PRETTY.get(s.car_type, s.car_type) if s.car_type else "-"
        lines.append(f"🧮 Калькулятор: {cat} → {opt} | 🚗 {ctype}")
    lines.append(f"⏱ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    text = "\n".join(lines)

    for chat_id in ADMIN_CHAT_IDS:
        try:
            await bot.send_message(chat_id, text, parse_mode="HTML")
        except Exception as e:
            print(f"[notify_admin -> {chat_id}] {e}")

# ============== Приём телефона ==============
PHONE_RE = re.compile(r"\+?\d[\d\-\s\(\)]{7,}")

async def _store_and_notify(m: Message, phone: str):
    try:
        await notify_admin(m.from_user, phone)
    except Exception as e:
        print(f"[notify_admin error] {e}")
    await m.answer(
        f"Спасибо! Записали номер: {phone}\nМы свяжемся с вами в ближайшее время.",
        reply_markup=main_menu()
    )

@dp.message(F.contact)
async def got_contact(m: Message):
    await _store_and_notify(m, m.contact.phone_number)

@dp.message(F.text.regexp(PHONE_RE.pattern))
async def got_phone_text(m: Message):
    await _store_and_notify(m, m.text.strip())

# ============== Прочее ==============
@dp.message(F.text == "📸 Наши работы")
async def works(m: Message):
    await m.answer("📸 Здесь будут фото/видео «до и после».", reply_markup=main_menu())

@dp.message(F.text == "⭐ Отзывы")
async def reviews(m: Message):
    await m.answer("⭐ Лучшие отзывы + ссылка на Яндекс/2ГИС для нового отзыва.", reply_markup=main_menu())

@dp.message(F.text == "🎁 Акции")
async def promo(m: Message):
    await m.answer("🔥 Акция недели: -20% на полировку до конца месяца.", reply_markup=main_menu())

# Контакты с кнопками-ссылками (deeplink Навигатора)
@dp.message(F.text == "📍 Контакты / Маршрут")
async def contacts(m: Message):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions

    address = "Москва, 1-я улица Измайловского Зверинца, д. 8"
    phone_display = "+7 (926) 190-20-10"
    phone_plain = "+7 (926) 190-20-10"

    LAT = 55.775267
    LON = 37.745690

    # Только Яндекс Карты
    maps_link = f"https://yandex.ru/maps/?pt={LON},{LAT}&z=17&l=map"

    text = (
        f"📍 <b>{address}</b>\n"
        f"📞 <a href='tel:+{phone_plain}'>{phone_display}</a>\n"
        f"💬 WhatsApp: <a href='https://wa.me/{phone_plain}'>wa.me/{phone_plain}</a>\n\n"
        f"🗺 <b>Открыть в Яндекс Картах:</b>"
    )

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Яндекс Карты", url=maps_link)],
    ])

    await m.answer(
        text,
        parse_mode="HTML",
        reply_markup=ikb,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    await m.answer("Готово. Выберите действие:", reply_markup=main_menu())
# ============== Запуск ==============
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())