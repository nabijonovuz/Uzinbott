import asyncio
import html
import logging
import os

import stats
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
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

JOBS_CHANNEL_URL = "https://t.me/uzinuae"
MARKET_CHANNEL_URL = "https://t.me/uzinuae"

CARD_NUMBER = "XXXX XXXX XXXX XXXX"
CARD_OWNER = "XXXXX XXXXX"
# ======================

LANGS = ("uz", "ru", "en")
PICK_LANG_TEXT = "🌐 Tilni tanlang / Выберите язык / Choose your language"

TEXTS = {
    "uz": {
        "welcome": "👋 Assalomu alaykum!\n\nMarketplace & Ads | UAE botiga xush kelibsiz.\nQuyidagilardan birini tanlang:",
        "btn_jobs": "💼 Ish vakansiyalari",
        "btn_cv": "📄 CV Checking",
        "btn_academy": "🎓 JOB ACADEMY",
        "btn_market": "🛒 Marketplace",
        "btn_lang": "🌐 Til / Язык / Language",
        "btn_back": "⬅️ Orqaga",
        "btn_menu": "⬅️ Bosh menyu",
        "btn_cv_check": "🔍 CV Checking",
        "btn_cv_service": "✍️ CV Xizmati",
        "btn_market_view": "🛍️ Marketplace",
        "btn_sell": "📦 Sotish",
        "cv_menu_title": "📄 Kerakli xizmatni tanlang:",
        "market_title": "🛒 Marketplace:",
        "cv_check_prompt": "📩 CV’ingizni rasm 📸 yoki PDF 📄 formatida yuboring.",
        "cv_received": "📩 CV qabul qilindi! ✅\n\n⏳ CV’ingiz 12 soat ichida UAE tajribasiga ega professional mutaxassis tomonidan ko‘rib chiqiladi.\n\n💬 Natija va tavsiyalar sizga yuboriladi. 🤝📄",
        "cv_q_name": "📄 CV tayyorlash\n\n👤 Ismingizni yozing:",
        "cv_q_phone": "📞 Telefon raqamingizni yozing:",
        "cv_q_edu": "🎓 Education (ta’lim) haqida yozing:",
        "cv_q_exp": "💼 Experience (ish tajribangiz) haqida yozing:",
        "cv_q_skills": "🛠 Skills (ko‘nikmalaringiz) ni yozing:",
        "cv_q_langs": "🌐 Languages (biladigan tillaringiz) ni yozing:",
        "cv_q_photo": "📸 Rasmingizni yuboring:",
        "cv_pay": "💳 To‘lov: 40 AED / 120 000 so‘m\n🏦 Karta: {card}\n👤 Ism-familiya: {owner}\n\n📸 To‘lov chekini yuboring.",
        "cv_accepted": "✅ Chek qabul qilindi va sizga 12 soat ichida CV tayyorlab jo‘natamiz.\n\nSizga oson bog‘lanish uchun username’ingizni qoldirishni unutmang.",
        "academy": "🎓 JOB ACADEMY — ISHGA KIRISHGACHA FULL SUPPORT 🚀\n\nAnchadan beri ish qidiryapsiz, lekin offer ololmayapsizmi? Unda Job Academy siz uchun! 💼🔥\n\n👥 Faqat 10 kishi uchun yopiq guruh\n📄 Professional CV tayyorlash\n🎯 Ishga to‘g‘ri topshirish strategiyasi\n🎤 Interviewga tayyorgarlik\n💬 Offer olguningizcha doimiy support\n🚗 Car lift topishda yordam\n✈️ Change visa uchun arzon chipta topishda yordam\n\n🎁 FULL SUPPORT — OFFER olguningizcha!\n\n💰 Narxi: 700 AED\n▫️ 350 AED — boshlanishida\n▫️ 350 AED — offer olgandan keyin\n\n🎁 Bonus: Siz orqali boshqa jobseeker to‘lov qilsa — 200 AED bonus! 💵\n\n🔥 Joylar: faqat 10 ta\n\n👉 Qo‘shilish uchun to‘lov qiling va chekni yuboring.\n\n💳 Karta: {card}\n👤 Ism-familiya: {owner}",
        "academy_accepted": "✅ Chek qabul qilindi va 12 soat ichida sizga javob beramiz.\n\nSizga oson bog‘lanishimiz uchun username’ingizni qoldirishni unutmang.",
        "sell_q_name": "📦 Mahsulot nomini yozing:",
        "sell_q_photo": "📸 Mahsulot rasmini yuboring:",
        "sell_q_price": "💰 Narxini yozing (AED):",
        "sell_q_loc": "📍 Joylashuvingizni yozing (shahar/hudud):",
        "sell_q_about": "📝 Mahsulot haqida yozing:",
        "sell_q_contact": "📞 Aloqa uchun telefon yoki username yozing:",
        "sell_pay": "💳 Kanalga joylash uchun to‘lov:\n\n💰 100 AED gacha → 10 AED\n💰 500 AED gacha → 50 AED\n💰 1,000 AED gacha → 80 AED\n💰 5,000 AED gacha → 150 AED\n💰 10,000 AED gacha → 200 AED\n💰 50,000 AED gacha → 350 AED\n💰 100,000 AED gacha → 500 AED\n\n💳 Karta: {card}\n👤 Ism-familiya: {owner}\n\n📸 To‘lovni amalga oshirib, chekni yuboring.",
        "sell_accepted": "✅ So‘rovingiz qabul qilindi va sizga tekshirib 12 soat ichida javob beramiz.",
        "cancelled": "Bekor qilindi.",
        "pick_option": "Quyidagilardan birini tanlang:",
        "wrong_format": "Iltimos, so‘ralgan ma’lumotni to‘g‘ri formatda yuboring. Bekor qilish uchun /cancel bosing.",
    },
    "ru": {
        "welcome": "👋 Здравствуйте!\n\nДобро пожаловать в бот Marketplace & Ads | UAE.\nВыберите один из вариантов:",
        "btn_jobs": "💼 Вакансии",
        "btn_cv": "📄 Проверка CV",
        "btn_academy": "🎓 JOB ACADEMY",
        "btn_market": "🛒 Marketplace",
        "btn_lang": "🌐 Til / Язык / Language",
        "btn_back": "⬅️ Назад",
        "btn_menu": "⬅️ Главное меню",
        "btn_cv_check": "🔍 Проверка CV",
        "btn_cv_service": "✍️ Составление CV",
        "btn_market_view": "🛍️ Marketplace",
        "btn_sell": "📦 Продать",
        "cv_menu_title": "📄 Выберите нужную услугу:",
        "market_title": "🛒 Marketplace:",
        "cv_check_prompt": "📩 Отправьте своё резюме (CV) в виде фото 📸 или PDF 📄.",
        "cv_received": "📩 Резюме получено! ✅\n\n⏳ Ваше резюме будет проверено в течение 12 часов профессиональным специалистом с опытом работы в ОАЭ.\n\n💬 Результат и рекомендации будут отправлены вам. 🤝📄",
        "cv_q_name": "📄 Составление резюме\n\n👤 Напишите ваше имя:",
        "cv_q_phone": "📞 Напишите ваш номер телефона:",
        "cv_q_edu": "🎓 Напишите об образовании (Education):",
        "cv_q_exp": "💼 Напишите об опыте работы (Experience):",
        "cv_q_skills": "🛠 Напишите ваши навыки (Skills):",
        "cv_q_langs": "🌐 Напишите, какими языками вы владеете (Languages):",
        "cv_q_photo": "📸 Отправьте своё фото:",
        "cv_pay": "💳 Оплата: 40 AED / 120 000 сум\n🏦 Карта: {card}\n👤 Имя и фамилия: {owner}\n\n📸 Отправьте чек об оплате.",
        "cv_accepted": "✅ Чек получен, мы подготовим и отправим вам резюме в течение 12 часов.\n\nНе забудьте оставить ваш username, чтобы нам было удобно с вами связаться.",
        "academy": "🎓 JOB ACADEMY — ПОЛНАЯ ПОДДЕРЖКА ДО ТРУДОУСТРОЙСТВА 🚀\n\nУже давно ищете работу, но не получается получить оффер? Тогда Job Academy для вас! 💼🔥\n\n👥 Закрытая группа всего на 10 человек\n📄 Подготовка профессионального резюме\n🎯 Правильная стратегия подачи заявок\n🎤 Подготовка к собеседованию\n💬 Постоянная поддержка до получения оффера\n🚗 Помощь в поиске попутки (car lift)\n✈️ Помощь в поиске дешёвых билетов для смены визы (change visa)\n\n🎁 FULL SUPPORT — ДО ПОЛУЧЕНИЯ ОФФЕРА!\n\n💰 Стоимость: 700 AED\n▫️ 350 AED — в начале\n▫️ 350 AED — после получения оффера\n\n🎁 Бонус: если через вас оплатит другой соискатель — бонус 200 AED! 💵\n\n🔥 Мест: всего 10\n\n👉 Чтобы присоединиться, оплатите и отправьте чек.\n\n💳 Карта: {card}\n👤 Имя и фамилия: {owner}",
        "academy_accepted": "✅ Чек получен, мы ответим вам в течение 12 часов.\n\nНе забудьте оставить ваш username, чтобы нам было удобно с вами связаться.",
        "sell_q_name": "📦 Напишите название товара:",
        "sell_q_photo": "📸 Отправьте фото товара:",
        "sell_q_price": "💰 Напишите цену (AED):",
        "sell_q_loc": "📍 Напишите ваше местоположение (город/район):",
        "sell_q_about": "📝 Напишите о товаре:",
        "sell_q_contact": "📞 Напишите телефон или username для связи:",
        "sell_pay": "💳 Оплата за размещение в канале:\n\n💰 до 100 AED → 10 AED\n💰 до 500 AED → 50 AED\n💰 до 1,000 AED → 80 AED\n💰 до 5,000 AED → 150 AED\n💰 до 10,000 AED → 200 AED\n💰 до 50,000 AED → 350 AED\n💰 до 100,000 AED → 500 AED\n\n💳 Карта: {card}\n👤 Имя и фамилия: {owner}\n\n📸 Совершите оплату и отправьте чек.",
        "sell_accepted": "✅ Ваш запрос принят, мы проверим его и ответим вам в течение 12 часов.",
        "cancelled": "Отменено.",
        "pick_option": "Выберите один из вариантов:",
        "wrong_format": "Пожалуйста, отправьте запрошенные данные в правильном формате. Для отмены нажмите /cancel.",
    },
    "en": {
        "welcome": "👋 Hello!\n\nWelcome to the Marketplace & Ads | UAE bot.\nPlease choose one of the options below:",
        "btn_jobs": "💼 Job vacancies",
        "btn_cv": "📄 CV Checking",
        "btn_academy": "🎓 JOB ACADEMY",
        "btn_market": "🛒 Marketplace",
        "btn_lang": "🌐 Til / Язык / Language",
        "btn_back": "⬅️ Back",
        "btn_menu": "⬅️ Main menu",
        "btn_cv_check": "🔍 CV Checking",
        "btn_cv_service": "✍️ CV Writing Service",
        "btn_market_view": "🛍️ Marketplace",
        "btn_sell": "📦 Sell",
        "cv_menu_title": "📄 Choose the service you need:",
        "market_title": "🛒 Marketplace:",
        "cv_check_prompt": "📩 Send your CV as a photo 📸 or a PDF 📄.",
        "cv_received": "📩 CV received! ✅\n\n⏳ Your CV will be reviewed within 12 hours by a professional with UAE experience.\n\n💬 The result and recommendations will be sent to you. 🤝📄",
        "cv_q_name": "📄 CV preparation\n\n👤 Please write your name:",
        "cv_q_phone": "📞 Please write your phone number:",
        "cv_q_edu": "🎓 Tell us about your education:",
        "cv_q_exp": "💼 Tell us about your work experience:",
        "cv_q_skills": "🛠 List your skills:",
        "cv_q_langs": "🌐 List the languages you speak:",
        "cv_q_photo": "📸 Send your photo:",
        "cv_pay": "💳 Payment: 40 AED / 120 000 UZS\n🏦 Card: {card}\n👤 Full name: {owner}\n\n📸 Please send the payment receipt.",
        "cv_accepted": "✅ Receipt received. We will prepare your CV and send it within 12 hours.\n\nPlease don’t forget to leave your username so we can reach you easily.",
        "academy": "🎓 JOB ACADEMY — FULL SUPPORT UNTIL YOU GET HIRED 🚀\n\nHave you been job hunting for a long time but can’t land an offer? Then Job Academy is for you! 💼🔥\n\n👥 Private group for only 10 people\n📄 Professional CV preparation\n🎯 The right job application strategy\n🎤 Interview preparation\n💬 Ongoing support until you get an offer\n🚗 Help finding a car lift\n✈️ Help finding cheap tickets for a visa change\n\n🎁 FULL SUPPORT — UNTIL YOU GET AN OFFER!\n\n💰 Price: 700 AED\n▫️ 350 AED — at the start\n▫️ 350 AED — after you get an offer\n\n🎁 Bonus: if another job seeker pays through you — 200 AED bonus! 💵\n\n🔥 Spots: only 10\n\n👉 To join, make the payment and send the receipt.\n\n💳 Card: {card}\n👤 Full name: {owner}",
        "academy_accepted": "✅ Receipt received. We will get back to you within 12 hours.\n\nPlease don’t forget to leave your username so we can reach you easily.",
        "sell_q_name": "📦 Write the product name:",
        "sell_q_photo": "📸 Send a photo of the product:",
        "sell_q_price": "💰 Write the price (AED):",
        "sell_q_loc": "📍 Write your location (city/area):",
        "sell_q_about": "📝 Describe the product:",
        "sell_q_contact": "📞 Write a phone number or username for contact:",
        "sell_pay": "💳 Fee for posting in the channel:\n\n💰 up to 100 AED → 10 AED\n💰 up to 500 AED → 50 AED\n💰 up to 1,000 AED → 80 AED\n💰 up to 5,000 AED → 150 AED\n💰 up to 10,000 AED → 200 AED\n💰 up to 50,000 AED → 350 AED\n💰 up to 100,000 AED → 500 AED\n\n💳 Card: {card}\n👤 Full name: {owner}\n\n📸 Please make the payment and send the receipt.",
        "sell_accepted": "✅ Your request has been received. We will review it and get back to you within 12 hours.",
        "cancelled": "Cancelled.",
        "pick_option": "Please choose one of the options below:",
        "wrong_format": "Please send the requested information in the correct format. Press /cancel to cancel.",
    },
}


def t(lang: str, key: str) -> str:
    text = TEXTS.get(lang, TEXTS["uz"])[key]
    return text.format(card=CARD_NUMBER, owner=CARD_OWNER)


def lang_of(user) -> str:
    return stats.get_lang(user.id) or "uz"


# ---------- Holatlar ----------
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


# ---------- Tugmalar ----------
def lang_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        ]
    )


def main_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_jobs"), url=JOBS_CHANNEL_URL)],
            [InlineKeyboardButton(text=t(lang, "btn_cv"), callback_data="cv")],
            [InlineKeyboardButton(text=t(lang, "btn_academy"), callback_data="academy")],
            [InlineKeyboardButton(text=t(lang, "btn_market"), callback_data="market")],
            [InlineKeyboardButton(text=t(lang, "btn_lang"), callback_data="choose_lang")],
        ]
    )


def cv_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_cv_check"), callback_data="cv_check")],
            [InlineKeyboardButton(text=t(lang, "btn_cv_service"), callback_data="cv_service")],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu")],
        ]
    )


def market_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_market_view"), url=MARKET_CHANNEL_URL)],
            [InlineKeyboardButton(text=t(lang, "btn_sell"), callback_data="sell")],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu")],
        ]
    )


def back_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_menu"), callback_data="menu")]]
    )


# ---------- Yordamchi funksiyalar (admin xabarlari o'zbekcha) ----------
def user_info(message: Message) -> str:
    u = message.from_user
    username = f"@{u.username}" if u.username else "username yo‘q"
    return (
        f"👤 {html.escape(u.full_name)} | {username} | ID: <code>{u.id}</code>"
        f" | 🌐 {lang_of(u)}"
    )


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
stats.setup(dp, ADMIN_ID)


# ---------- Start, til, bosh menyu ----------
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    lang = stats.get_lang(message.from_user.id)
    if lang is None:
        await message.answer(PICK_LANG_TEXT, reply_markup=lang_menu())
    else:
        await message.answer(t(lang, "welcome"), reply_markup=main_menu(lang))


@dp.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    lang = lang_of(message.from_user)
    await message.answer(t(lang, "cancelled"), reply_markup=main_menu(lang))


@dp.callback_query(F.data == "choose_lang")
async def cb_choose_lang(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(PICK_LANG_TEXT, reply_markup=lang_menu())
    await call.answer()


@dp.callback_query(F.data.startswith("lang_"))
async def cb_lang(call: CallbackQuery, state: FSMContext):
    code = call.data.split("_", 1)[1]
    if code not in LANGS:
        await call.answer()
        return
    stats.set_lang(call.from_user.id, code)
    await state.clear()
    await call.message.answer(t(code, "welcome"), reply_markup=main_menu(code))
    await call.answer()


@dp.callback_query(F.data == "menu")
async def cb_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = lang_of(call.from_user)
    await call.message.answer(t(lang, "welcome"), reply_markup=main_menu(lang))
    await call.answer()


# ---------- CV ----------
@dp.callback_query(F.data == "cv")
async def cb_cv(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = lang_of(call.from_user)
    await call.message.answer(t(lang, "cv_menu_title"), reply_markup=cv_menu(lang))
    await call.answer()


@dp.callback_query(F.data == "cv_check")
async def cb_cv_check(call: CallbackQuery, state: FSMContext):
    await state.set_state(CVCheck.waiting_file)
    lang = lang_of(call.from_user)
    await call.message.answer(t(lang, "cv_check_prompt"), reply_markup=back_menu(lang))
    await call.answer()


@dp.message(CVCheck.waiting_file, F.photo | F.document)
async def cv_check_file(message: Message, state: FSMContext, bot: Bot):
    lang = lang_of(message.from_user)
    await send_to_admin(bot, f"🔍 <b>Yangi CV Checking</b>\n{user_info(message)}")
    await forward_to_admin(bot, message)
    await message.answer(t(lang, "cv_received"), reply_markup=back_menu(lang))
    await state.clear()


@dp.message(CVCheck.waiting_file)
async def cv_check_wrong(message: Message):
    await message.answer(t(lang_of(message.from_user), "cv_check_prompt"))


@dp.callback_query(F.data == "cv_service")
async def cb_cv_service(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CVService.name)
    await call.message.answer(t(lang_of(call.from_user), "cv_q_name"))
    await call.answer()


@dp.message(CVService.name, F.text)
async def cv_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CVService.phone)
    await message.answer(t(lang_of(message.from_user), "cv_q_phone"))


@dp.message(CVService.phone, F.text)
async def cv_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(CVService.education)
    await message.answer(t(lang_of(message.from_user), "cv_q_edu"))


@dp.message(CVService.education, F.text)
async def cv_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(CVService.experience)
    await message.answer(t(lang_of(message.from_user), "cv_q_exp"))


@dp.message(CVService.experience, F.text)
async def cv_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(CVService.skills)
    await message.answer(t(lang_of(message.from_user), "cv_q_skills"))


@dp.message(CVService.skills, F.text)
async def cv_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(CVService.languages)
    await message.answer(t(lang_of(message.from_user), "cv_q_langs"))


@dp.message(CVService.languages, F.text)
async def cv_languages(message: Message, state: FSMContext):
    await state.update_data(languages=message.text)
    await state.set_state(CVService.photo)
    await message.answer(t(lang_of(message.from_user), "cv_q_photo"))


@dp.message(CVService.photo, F.photo)
async def cv_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(CVService.payment)
    await message.answer(t(lang_of(message.from_user), "cv_pay"))


@dp.message(CVService.payment, F.photo | F.document)
async def cv_payment(message: Message, state: FSMContext, bot: Bot):
    lang = lang_of(message.from_user)
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
    await message.answer(t(lang, "cv_accepted"), reply_markup=back_menu(lang))
    await state.clear()


# ---------- JOB ACADEMY ----------
@dp.callback_query(F.data == "academy")
async def cb_academy(call: CallbackQuery, state: FSMContext):
    await state.set_state(Academy.payment)
    lang = lang_of(call.from_user)
    await call.message.answer(t(lang, "academy"), reply_markup=back_menu(lang))
    await call.answer()


@dp.message(Academy.payment, F.photo | F.document)
async def academy_payment(message: Message, state: FSMContext, bot: Bot):
    lang = lang_of(message.from_user)
    await send_to_admin(bot, f"🎓 <b>Job Academy — yangi to‘lov</b>\n{user_info(message)}")
    await forward_to_admin(bot, message)
    await message.answer(t(lang, "academy_accepted"), reply_markup=back_menu(lang))
    await state.clear()


# ---------- MARKETPLACE ----------
@dp.callback_query(F.data == "market")
async def cb_market(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = lang_of(call.from_user)
    await call.message.answer(t(lang, "market_title"), reply_markup=market_menu(lang))
    await call.answer()


@dp.callback_query(F.data == "sell")
async def cb_sell(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Sell.name)
    await call.message.answer(t(lang_of(call.from_user), "sell_q_name"))
    await call.answer()


@dp.message(Sell.name, F.text)
async def sell_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Sell.photo)
    await message.answer(t(lang_of(message.from_user), "sell_q_photo"))


@dp.message(Sell.photo, F.photo)
async def sell_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(Sell.price)
    await message.answer(t(lang_of(message.from_user), "sell_q_price"))


@dp.message(Sell.price, F.text)
async def sell_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(Sell.location)
    await message.answer(t(lang_of(message.from_user), "sell_q_loc"))


@dp.message(Sell.location, F.text)
async def sell_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(Sell.about)
    await message.answer(t(lang_of(message.from_user), "sell_q_about"))


@dp.message(Sell.about, F.text)
async def sell_about(message: Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(Sell.contact)
    await message.answer(t(lang_of(message.from_user), "sell_q_contact"))


@dp.message(Sell.contact, F.text)
async def sell_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(Sell.payment)
    await message.answer(t(lang_of(message.from_user), "sell_pay"))


@dp.message(Sell.payment, F.photo | F.document)
async def sell_payment(message: Message, state: FSMContext, bot: Bot):
    lang = lang_of(message.from_user)
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
    await message.answer(t(lang, "sell_accepted"), reply_markup=back_menu(lang))
    await state.clear()


# ---------- Boshqa xabarlar ----------
@dp.message()
async def fallback(message: Message, state: FSMContext):
    lang = stats.get_lang(message.from_user.id)
    if lang is None:
        await message.answer(PICK_LANG_TEXT, reply_markup=lang_menu())
    elif await state.get_state() is None:
        await message.answer(t(lang, "pick_option"), reply_markup=main_menu(lang))
    else:
        await message.answer(t(lang, "wrong_format"))


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
