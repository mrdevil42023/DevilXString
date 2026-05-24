from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔑 Pyrogram Session", callback_data="gen_pyrogram"),
            InlineKeyboardButton("📡 Telethon Session", callback_data="gen_telethon"),
        ],
        [
            InlineKeyboardButton("📋 My Sessions", callback_data="my_sessions"),
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/mrdevil12"),
        ],
    ])


def cancel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])


def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="start")],
    ])


def session_type_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔑 Pyrogram", callback_data="gen_pyrogram"),
            InlineKeyboardButton("📡 Telethon", callback_data="gen_telethon"),
        ],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="start")],
    ])


def force_join_keyboard(not_joined: list, pending_action: str) -> InlineKeyboardMarkup:
    """
    Shows a join button for each un-joined chat, plus a 'I've Joined' button
    that re-checks and then proceeds to `pending_action`.
    """
    rows = []
    for _username, label, link in not_joined:
        rows.append([InlineKeyboardButton(f"➕ Join {label}", url=link)])
    rows.append([InlineKeyboardButton("✅ I've Joined — Continue", callback_data=f"check_join:{pending_action}")])
    rows.append([InlineKeyboardButton("🏠 Back to Menu", callback_data="start")])
    return InlineKeyboardMarkup(rows)
