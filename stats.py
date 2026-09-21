import asyncio
import logging
import os
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.types import Message

DB_PATH = os.environ.get("DB_PATH", "users.db")


def _db() -> sqlite3.Connection:
    folder = os.path.dirname(DB_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, "
        "joined TEXT DEFAULT CURRENT_TIMESTAMP, active INTEGER DEFAULT 1)"
    )
    try:
        con.execute("ALTER TABLE users ADD COLUMN lang TEXT")
    except sqlite3.OperationalError:
        pass
    return con


def get_lang(user_id: int):
    try:
        con = _db()
        row = con.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)).fetchone()
        con.close()
        return row[0] if row and row[0] else None
    except Exception as e:
        logging.error("Tilni o'qib bo'lmadi: %s", e)
        return None


def set_lang(user_id: int, lang: str) -> None:
    try:
        con = _db()
        with con:
            con.execute(
                "INSERT INTO users (user_id, lang) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang",
                (user_id, lang),
            )
        con.close()
    except Exception as e:
        logging.error("Tilni saqlab bo'lmadi: %s", e)


def add_user(user) -> None:
    con = _db()
    with con:
        con.execute(
            "INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET "
            "username=excluded.username, full_name=excluded.full_name, active=1",
            (user.id, user.username, user.full_name),
        )
    con.close()


def mark_inactive(user_id: int) -> None:
    con = _db()
    with con:
        con.execute("UPDATE users SET active=0 WHERE user_id=?", (user_id,))
    con.close()


def all_active_ids() -> list[int]:
    con = _db()
    rows = con.execute("SELECT user_id FROM users WHERE active=1").fetchall()
    con.close()
    return [r[0] for r in rows]


def get_stats() -> dict:
    con = _db()
    q = lambda sql: con.execute(sql).fetchone()[0]
    data = {
        "total": q("SELECT COUNT(*) FROM users"),
        "active": q("SELECT COUNT(*) FROM users WHERE active=1"),
        "today": q("SELECT COUNT(*) FROM users WHERE date(joined)=date('now')"),
        "week": q("SELECT COUNT(*) FROM users WHERE date(joined)>=date('now','-6 days')"),
    }
    con.close()
    return data


def setup(dp: Dispatcher, admin_id: int) -> None:
    async def tracker(handler, event, data):
        user = getattr(event, "from_user", None)
        if user and not user.is_bot:
            try:
                add_user(user)
            except Exception as e:
                logging.error("Foydalanuvchini saqlab bo'lmadi: %s", e)
        return await handler(event, data)

    dp.message.outer_middleware(tracker)
    dp.callback_query.outer_middleware(tracker)

    async def cmd_stats(message: Message):
        if message.from_user.id != admin_id:
            return
        s = get_stats()
        await message.answer(
            "📊 <b>Bot statistikasi</b>\n\n"
            f"👥 Jami foydalanuvchi: <b>{s['total']}</b>\n"
            f"✅ Faol (botni bloklamagan): <b>{s['active']}</b>\n"
            f"🆕 Bugun qo‘shilgan: <b>{s['today']}</b>\n"
            f"📅 Oxirgi 7 kun: <b>{s['week']}</b>"
        )

    async def cmd_broadcast(message: Message, bot: Bot):
        if message.from_user.id != admin_id:
            return

        source = message.reply_to_message
        text = (message.text or "").partition(" ")[2].strip()
        if not source and not text:
            await message.answer(
                "📣 Reklama yuborish:\n\n"
                "1) Reklama xabarini (rasm bilan ham bo‘ladi) shu chatga yozing\n"
                "2) O‘sha xabarga <b>Reply</b> qilib <code>/broadcast</code> yozing\n\n"
                "Yoki oddiy matn: <code>/broadcast Matn</code>"
            )
            return

        ids = all_active_ids()
        await message.answer(f"⏳ {len(ids)} ta foydalanuvchiga yuborilmoqda...")

        async def send(uid: int):
            if source:
                await bot.copy_message(uid, message.chat.id, source.message_id)
            else:
                await bot.send_message(uid, text)

        ok = blocked = failed = 0
        for uid in ids:
            try:
                try:
                    await send(uid)
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                    await send(uid)
                ok += 1
            except TelegramForbiddenError:
                mark_inactive(uid)
                blocked += 1
            except Exception as e:
                logging.error("Broadcast xato (%s): %s", uid, e)
                failed += 1
            await asyncio.sleep(0.05)

        await message.answer(
            "✅ Yuborish tugadi\n\n"
            f"📨 Yetkazildi: {ok}\n"
            f"🚫 Botni bloklaganlar: {blocked}\n"
            f"⚠️ Xato: {failed}"
        )

    dp.message.register(cmd_stats, Command("stats"))
    dp.message.register(cmd_broadcast, Command("broadcast"))
