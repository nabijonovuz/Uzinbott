import asyncio
import html
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# ===== SOZLAMALAR =====
# Token va ID Railway "Variables" bo'limidan o'qiladi
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

JOBS_CHANNEL_URL = "https://t.me/KANAL_USERNAME"
MARKET_CHANNEL_URL = "https://t.me/KANAL_USERNAME"

CARD_NUMBER = "XXXX XXXX XXXX XXXX"
CARD_OWNER = "XXXXX XXXXX"
# ======================

WELCOME_TEXT = (
    "👋 Assalomu alaykum!\n\n"
    "Marketplace & Ads | UAE botiga xush kelibsiz.\n"
    "Quyidagilardan birini tanlang:"
)

CV_CHECK_TEXT = "📩 CV’ingizni rasm 📸 yoki PDF 📄 formatida yuboring."

CV_RECEIVED_TEXT = (
    "📩 CV qabul qilindi! ✅\n\n"
    "⏳ CV’ingiz 12 soat ichida UAE tajribasiga ega professional "
    "mutaxassis tomonidan ko‘rib chiqiladi.\n\n"
    "💬 Natija va tavsiyalar sizga yuboriladi. 🤝📄"
)

CV_PAYMENT_TEXT = (
    "💳 To‘lov: 40 AED / 120 000 so‘m\n"
    f"🏦 Karta: {CARD_NUMBER}\n"
    f"👤 Ism-familiya: {CARD_OWNER}\n\n"
    "📸 To‘lov chekini yuboring."
)

CV_CHECK_ACCEPTED_TEXT = (
    "✅ Chek qabul qilindi va sizga 12 soat ichida CV tayyorlab jo‘natamiz.\n\n"
    "Sizga oson bog‘lanish uchun username’ingizni qoldirishni unutmang."
)

ACADEMY_TEXT = (
    "🎓 JOB ACADEMY — ISHGA KIRISHGACHA FULL SUPPORT 🚀\n\n"
    "Anchadan beri ish qidiryapsiz, lekin offer ololmayapsizmi? "
    "Unda Job Academy siz uchun! 💼🔥\n\n"
    "👥 Faqat 10 kishi uchun yopiq guruh\n"
    "📄 Professional CV tayyorlash\n"
    "🎯 Ishga to‘g‘ri topshirish strategiyasi\n"
    "🎤 Interviewga tayyorgarlik\n"
    "💬 Offer olguningizcha doimiy support\n"
    "🚗 Car lift topishda yordam\n"
    "✈️ Change visa uchun arzon chipta topishda yordam\n\n"
    "🎁 FULL SUPPORT — OFFER olguningizcha!\n\n"
    "💰 Narxi: 700 AED\n"
    "▫️ 350 AED — boshlanishida\n"
    "▫️ 350 AED — offer olgandan keyin\n\n"
    "🎁 Bonus: Siz orqali boshqa jobseeker to‘lov qilsa — 200 AED bonus! 💵\n\n"
    "🔥 Joylar: faqat 10 ta\n\n"
    "👉 Qo‘shilish uchun to‘lov qiling va chekni yuboring.\n\n"
    f"💳 Karta: {CARD_NUMBER}\n"
    f"👤 Ism-familiya: {CARD_OWNER}"
)

ACADEMY_ACCEPTED_TEXT = (
    "✅ Chek qabul qilindi va 12 soat ichida sizga javob beramiz.\n\n"
    "Sizga oson bog‘lanishimiz uchun username’ingizni qoldirishni unutmang."
)

SELL_PAYMENT_TEXT = (
    "💳 Kanalga joylash uchun to‘lov:\n\n"
    "💰 100 AED gacha → 10 AED\n"
    "💰 500 AED gacha → 50 AED\n"
    "💰 1,000 AED gacha → 80 AED\n"
    "💰 5,000 AED gacha → 150 AED\n"
    "💰 10,000 AED gacha → 200 AED\n"
    "💰 50,000 AED gacha → 350 AED\n"
    "💰 100,000 AED gacha → 500 AED\n\n"
    f"💳 Karta: {CARD_NUMBER}\n"
    f"👤 Ism-familiya: {CARD_OWNER}\n\n"
    "📸 To‘lovni amalga oshirib, chekni yuboring."
)

SELL_ACCEPTED_TEXT = (
    "✅ So‘rovingiz qabul qilindi va sizga tekshirib 12 soat ichida javob beramiz."
)


class CVCheck(StatesGroup):
    waiting_file = State()


class CVService(StatesGroup):
    name = State()
    phone = State()
    education = State()
    experience = State()
    skills = State()
    languages = State()
    photo = State()
    payment = State()


class Academy(StatesGroup):
    payment = State()


class Sell(StatesGroup):
    name = State()
    photo = State()
    price = State()
    location = State()
    about = State()
    contact = State()
    payment = State()


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💼 Ish vakansiyalari", url=JOBS_CHANNEL_URL)],
            [InlineKeyboardButton(text="📄 CV Checking", callback_data="cv")],
            [InlineKeyboardButton(text="🎓 JOB ACADEMY", callback_data="academy")],
            [InlineKeyboardButton(text="🛒 Marketplace", callback_data="market")],
        ]
    )


def cv_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 CV Checking", callback_data="cv_check")],
            [InlineKeyboardButton(text="✍️ CV Xizmati", callback_data="cv_service")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu")],
        ]
    )


def market_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Marketplace", url=MARKET_CHANNEL_URL)],
            [InlineKeyboardButton(text="📦 Sotish", callback_data="sell")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu")],
        ]
    )


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu")]]
    )


def user_info(message: Message) -> str:
    u = message.from_user
    username = f"@{u.username}" if u.username else "username yo‘q"
    return f"👤 {html.escape(u.full_name)} | {username} | ID: <code>{u.id}</code>"


def esc(value) -> str:
    return html.escape(str(value)) if value else "-"


async def send_to_admin(bot: Bot, text: str, photo_id: str | None = None) -> None:
    try:
        if photo_id:
            await bot.send_photo(ADMIN_ID, photo_id, caption=text[:1024])
        else:
            await bot.send_message(ADMIN_ID, text)
    except Exception as e:
        logging.error("Adminga yuborib bo'lmadi: %s", e)


async def forward_to_admin(bot: Bot, message: Message) -> None:
    try:
        await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    except Exception as e:
        logging.error("Adminga forward qilib bo'lmadi: %s", e)


dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())


@dp.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=main_menu())


@dp.callback_query(F.data == "menu")
async def cb_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(WELCOME_TEXT, reply_markup=main_menu())
    await call.answer()


# ---------- CV ----------
@dp.callback_query(F.data == "cv")
async def cb_cv(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("📄 Kerakli xizmatni tanlang:", reply_markup=cv_menu())
    await call.answer()


@dp.callback_query(F.data == "cv_check")
async def cb_cv_check(call: CallbackQuery, state: FSMContext):
    await state.set_state(CVCheck.waiting_file)
    await call.message.answer(CV_CHECK_TEXT, reply_markup=back_menu())
    await call.answer()


@dp.message(CVCheck.waiting_file, F.photo | F.document)
async def cv_check_file(message: Message, state: FSMContext, bot: Bot):
    await send_to_admin(bot, f"🔍 <b>Yangi CV Checking</b>\n{user_info(message)}")
    await forward_to_admin(bot, message)
    await message.answer(CV_RECEIVED_TEXT, reply_markup=back_menu())
    await state.clear()


@dp.message(CVCheck.waiting_file)
async def cv_check_wrong(message: Message):
    await message.answer(CV_CHECK_TEXT)


@dp.callback_query(F.data == "cv_service")
async def cb_cv_service(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CVService.name)
    await call.message.answer("📄 CV tayyorlash\n\n👤 Ismingizni yozing:")
    await call.answer()


@dp.message(CVService.name, F.text)
async def cv_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CVService.phone)
    await message.answer("📞 Telefon raqamingizni yozing:")


@dp.message(CVService.phone, F.text)
async def cv_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(CVService.education)
    await message.answer("🎓 Education (ta’lim) haqida yozing:")


@dp.message(CVService.education, F.text)
async def cv_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(CVService.experience)
    await message.answer("💼 Experience (ish tajribangiz) haqida yozing:")


@dp.message(CVService.experience, F.text)
async def cv_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(CVService.skills)
    await message.answer("🛠 Skills (ko‘nikmalaringiz) ni yozing:")


@dp.message(CVService.skills, F.text)
async def cv_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(CVService.languages)
    await message.answer("🌐 Languages (biladigan tillaringiz) ni yozing:")


@dp.message(CVService.languages, F.text)
async def cv_languages(message: Message, state: FSMContext):
    await state.update_data(languages=message.text)
    await state.set_state(CVService.photo)
    await message.answer("📸 Rasmingizni yuboring:")


@dp.message(CVService.photo, F.photo)
async def cv_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(CVService.payment)
    await message.answer(CV_PAYMENT_TEXT)


@dp.message(CVService.payment, F.photo | F.document)
async def cv_payment(message: Message, state: FSMContext, bot: Bot):
    d = await state.get_data()
    text = (
        "✍️ <b>Yangi CV Xizmati buyurtmasi</b>\n"
        f"{user_info(message)}\n\n"
        f"👤 Ism: {esc(d.get('name'))}\n"
        f"📞 Telefon: {esc(d.get('phone'))}\n"
        f"🎓 Education: {esc(d.get('education'))}\n"
        f"💼 Experience: {esc(d.get('experience'))}\n"
        f"🛠 Skills: {esc(d.get('skills'))}\n"
        f"🌐 Languages: {esc(d.get('languages'))}"
    )
    await send_to_admin(bot, text, photo_id=d.get("photo"))
    await forward_to_admin(bot, message)
    await message.answer(CV_CHECK_ACCEPTED_TEXT, reply_markup=back_menu())
    await state.clear()


# ---------- JOB ACADEMY ----------
@dp.callback_query(F.data == "academy")
async def cb_academy(call: CallbackQuery, state: FSMContext):
    await state.set_state(Academy.payment)
    await call.message.answer(ACADEMY_TEXT, reply_markup=back_menu())
    await call.answer()


@dp.message(Academy.payment, F.photo | F.document)
async def academy_payment(message: Message, state: FSMContext, bot: Bot):
    await send_to_admin(bot, f"🎓 <b>Job Academy — yangi to‘lov</b>\n{user_info(message)}")
    await forward_to_admin(bot, message)
    await message.answer(ACADEMY_ACCEPTED_TEXT, reply_markup=back_menu())
    await state.clear()


# ---------- MARKETPLACE ----------
@dp.callback_query(F.data == "market")
async def cb_market(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("🛒 Marketplace:", reply_markup=market_menu())
    await call.answer()


@dp.callback_query(F.data == "sell")
async def cb_sell(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Sell.name)
    await call.message.answer("📦 Mahsulot nomini yozing:")
    await call.answer()


@dp.message(Sell.name, F.text)
async def sell_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Sell.photo)
    await message.answer("📸 Mahsulot rasmini yuboring:")


@dp.message(Sell.photo, F.photo)
async def sell_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(Sell.price)
    await message.answer("💰 Narxini yozing (AED):")


@dp.message(Sell.price, F.text)
async def sell_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(Sell.location)
    await message.answer("📍 Joylashuvingizni yozing (shahar/hudud):")


@dp.message(Sell.location, F.text)
async def sell_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(Sell.about)
    await message.answer("📝 Mahsulot haqida yozing:")


@dp.message(Sell.about, F.text)
async def sell_about(message: Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(Sell.contact)
    await message.answer("📞 Aloqa uchun telefon yoki username yozing:")


@dp.message(Sell.contact, F.text)
async def sell_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(Sell.payment)
    await message.answer(SELL_PAYMENT_TEXT)


@dp.message(Sell.payment, F.photo | F.document)
async def sell_payment(message: Message, state: FSMContext, bot: Bot):
    d = await state.get_data()
    text = (
        "📦 <b>Yangi e’lon (Sotish)</b>\n"
        f"{user_info(message)}\n\n"
        f"📦 Mahsulot: {esc(d.get('name'))}\n"
        f"💰 Narxi: {esc(d.get('price'))}\n"
        f"📍 Joylashuv: {esc(d.get('location'))}\n"
        f"📝 Haqida: {esc(d.get('about'))}\n"
        f"📞 Aloqa: {esc(d.get('contact'))}"
    )
    await send_to_admin(bot, text, photo_id=d.get("photo"))
    await forward_to_admin(bot, message)
    await message.answer(SELL_ACCEPTED_TEXT, reply_markup=back_menu())
    await state.clear()


# ---------- Boshqa xabarlar ----------
@dp.message()
async def fallback(message: Message, state: FSMContext):
    if await state.get_state() is None:
        await message.answer("Quyidagilardan birini tanlang:", reply_markup=main_menu())
    else:
        await message.answer(
            "Iltimos, so‘ralgan ma’lumotni to‘g‘ri formatda yuboring. "
            "Bekor qilish uchun /cancel bosing."
        )


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
