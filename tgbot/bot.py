import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import FloodWait

from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, BOT_NAME, START_IMAGE
from keyboards import start_keyboard, cancel_keyboard, back_keyboard, session_type_keyboard, force_join_keyboard
from force_join import check_membership
from messages import (
    START_TEXT, HELP_TEXT, PYROGRAM_START, TELETHON_START,
    OTP_TEXT, TWO_FA_TEXT, SUCCESS_PYROGRAM, SUCCESS_TELETHON, NO_SESSIONS
)
from database import save_session, get_user_sessions, init_db
from helpers import auto_join_chats
from admin import register_admin_handlers

app = Client(
    name="string_gen_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
)

# State storage: user_id -> state dict
user_states = {}


def get_state(user_id: int) -> dict:
    return user_states.get(user_id, {})


def set_state(user_id: int, **kwargs):
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id].update(kwargs)


def clear_state(user_id: int):
    user_states.pop(user_id, None)


# ─── helpers ──────────────────────────────────────────────────────────────────

def _force_join_text(not_joined: list) -> str:
    lines = ["⚠️ **Access Restricted!**\n",
             "You must join our official channels before generating a session.\n"]
    for _username, label, link in not_joined:
        lines.append(f"👉 {label}: {link}")
    lines.append("\nClick the buttons below to join, then tap **✅ I've Joined — Continue**.")
    return "\n".join(lines)


def build_start_text(user) -> str:
    first = user.first_name or ""
    last = user.last_name or ""
    user_name = (first + " " + last).strip() or user.username or "User"
    return START_TEXT.format(bot_name=BOT_NAME, user_name=user_name)


async def send_start(message: Message):
    text = build_start_text(message.from_user)
    await message.reply_photo(
        photo=START_IMAGE,
        caption=text,
        reply_markup=start_keyboard(),
    )


# ─── /start command ───────────────────────────────────────────────────────────

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    clear_state(message.from_user.id)
    await send_start(message)


# ─── /help command ────────────────────────────────────────────────────────────

@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
    await message.reply_text(
        HELP_TEXT,
        reply_markup=back_keyboard(),
        disable_web_page_preview=True,
    )


# ─── /generate command ────────────────────────────────────────────────────────

@app.on_message(filters.command("generate") & filters.private)
async def generate_cmd(client: Client, message: Message):
    clear_state(message.from_user.id)
    await message.reply_text(
        "**Choose the session type you want to generate:**",
        reply_markup=session_type_keyboard(),
    )


# ─── /mysessions command ──────────────────────────────────────────────────────

@app.on_message(filters.command("mysessions") & filters.private)
async def mysessions_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    sessions = get_user_sessions(user_id)
    if not sessions:
        await message.reply_text(NO_SESSIONS, reply_markup=session_type_keyboard())
        return

    text = "📋 **Your Saved Sessions:**\n\n"
    for i, s in enumerate(sessions, 1):
        session_str = s.get("session_string", "")
        preview = session_str[:30] + "..." if len(session_str) > 30 else session_str
        text += f"**{i}. {s.get('session_type', 'unknown').upper()} Session**\n"
        text += f"   Preview: `{preview}`\n\n"

    await message.reply_text(text, reply_markup=back_keyboard())


# ─── Callback query handlers ──────────────────────────────────────────────────

@app.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data

    if data == "start":
        clear_state(user_id)
        await query.message.delete()
        text = build_start_text(query.from_user)
        await query.message.reply_photo(
            photo=START_IMAGE,
            caption=text,
            reply_markup=start_keyboard(),
        )

    elif data == "help":
        await query.message.edit_text(
            HELP_TEXT,
            reply_markup=back_keyboard(),
            disable_web_page_preview=True,
        )

    elif data == "my_sessions":
        sessions = get_user_sessions(user_id)
        if not sessions:
            await query.message.edit_text(NO_SESSIONS, reply_markup=session_type_keyboard())
            return
        text = "📋 **Your Saved Sessions:**\n\n"
        for i, s in enumerate(sessions, 1):
            session_str = s.get("session_string", "")
            preview = session_str[:30] + "..." if len(session_str) > 30 else session_str
            text += f"**{i}. {s.get('session_type', 'unknown').upper()} Session**\n"
            text += f"   Preview: `{preview}`\n\n"
        await query.message.edit_text(text, reply_markup=back_keyboard())

    elif data == "gen_pyrogram":
        not_joined = await check_membership(client, user_id)
        if not_joined:
            await query.answer("⚠️ Please join our channels first!", show_alert=True)
            await query.message.edit_text(
                _force_join_text(not_joined),
                reply_markup=force_join_keyboard(not_joined, "gen_pyrogram"),
                disable_web_page_preview=True,
            )
            return
        clear_state(user_id)
        set_state(user_id, step="pyrogram_phone")
        await query.message.edit_text(
            PYROGRAM_START,
            reply_markup=cancel_keyboard(),
        )

    elif data == "gen_telethon":
        not_joined = await check_membership(client, user_id)
        if not_joined:
            await query.answer("⚠️ Please join our channels first!", show_alert=True)
            await query.message.edit_text(
                _force_join_text(not_joined),
                reply_markup=force_join_keyboard(not_joined, "gen_telethon"),
                disable_web_page_preview=True,
            )
            return
        clear_state(user_id)
        set_state(user_id, step="telethon_phone")
        await query.message.edit_text(
            TELETHON_START,
            reply_markup=cancel_keyboard(),
        )

    elif data.startswith("check_join:"):
        pending_action = data.split(":", 1)[1]
        not_joined = await check_membership(client, user_id)
        if not_joined:
            await query.answer("❌ You haven't joined yet! Please join and try again.", show_alert=True)
            await query.message.edit_text(
                _force_join_text(not_joined),
                reply_markup=force_join_keyboard(not_joined, pending_action),
                disable_web_page_preview=True,
            )
            return
        # All joined — proceed to the pending action
        await query.answer("✅ Verified! Let's go.")
        clear_state(user_id)
        if pending_action == "gen_pyrogram":
            set_state(user_id, step="pyrogram_phone")
            await query.message.edit_text(PYROGRAM_START, reply_markup=cancel_keyboard())
        elif pending_action == "gen_telethon":
            set_state(user_id, step="telethon_phone")
            await query.message.edit_text(TELETHON_START, reply_markup=cancel_keyboard())

    elif data == "cancel":
        clear_state(user_id)
        await query.message.edit_text(
            "❌ **Cancelled.**\n\nReturning to main menu.",
            reply_markup=start_keyboard(),
        )

    await query.answer()


# ─── Message handler for session generation flow ──────────────────────────────

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "generate", "mysessions"]))
async def message_handler(client: Client, message: Message):
    from admin import is_broadcast_waiting
    user_id = message.from_user.id

    # Let admin.py's broadcast_receive handle this message
    if user_id == OWNER_ID and is_broadcast_waiting():
        return

    text = message.text.strip()
    state = get_state(user_id)
    step = state.get("step")

    # ── PYROGRAM FLOW ──────────────────────────────────────────────────────────

    if step == "pyrogram_phone":
        phone = text
        if not phone.startswith("+"):
            await message.reply_text(
                "⚠️ Invalid phone format. Please include the country code.\n**Example:** `+919876543210`",
                reply_markup=cancel_keyboard(),
            )
            return

        status_msg = await message.reply_text("⏳ Sending OTP to your Telegram...")
        try:
            from pyrogram_gen import send_otp_pyrogram
            pyro_client, phone_code_hash = await send_otp_pyrogram(phone)
            set_state(user_id, step="pyrogram_otp", phone=phone,
                      phone_code_hash=phone_code_hash, pyro_client=pyro_client)
            await status_msg.edit_text(OTP_TEXT, reply_markup=cancel_keyboard())
        except Exception as e:
            clear_state(user_id)
            await status_msg.edit_text(
                f"❌ **Error:** {e}\n\nTry again with /generate",
                reply_markup=back_keyboard(),
            )

    elif step == "pyrogram_otp":
        otp = text.replace(" ", "")
        pyro_client = state.get("pyro_client")
        phone = state.get("phone")
        phone_code_hash = state.get("phone_code_hash")

        status_msg = await message.reply_text("⏳ Verifying OTP...")
        try:
            from pyrogram.errors import SessionPasswordNeeded
            await pyro_client.sign_in(phone, phone_code_hash, otp)
            session_string = await pyro_client.export_session_string()
            await pyro_client.disconnect()

            await _finish_pyrogram_session(user_id, message, status_msg, session_string)
        except SessionPasswordNeeded:
            set_state(user_id, step="pyrogram_2fa")
            await status_msg.edit_text(TWO_FA_TEXT, reply_markup=cancel_keyboard())
        except Exception as e:
            if pyro_client:
                try:
                    await pyro_client.disconnect()
                except Exception:
                    pass
            clear_state(user_id)
            await status_msg.edit_text(
                f"❌ **Error:** {e}\n\nTry again with /generate",
                reply_markup=back_keyboard(),
            )

    elif step == "pyrogram_2fa":
        password = text
        pyro_client = state.get("pyro_client")
        status_msg = await message.reply_text("⏳ Checking 2FA password...")
        try:
            await pyro_client.check_password(password)
            session_string = await pyro_client.export_session_string()
            await pyro_client.disconnect()

            await _finish_pyrogram_session(user_id, message, status_msg, session_string)
        except Exception as e:
            if pyro_client:
                try:
                    await pyro_client.disconnect()
                except Exception:
                    pass
            clear_state(user_id)
            await status_msg.edit_text(
                f"❌ **Error:** {e}\n\nTry again with /generate",
                reply_markup=back_keyboard(),
            )

    # ── TELETHON FLOW ──────────────────────────────────────────────────────────

    elif step == "telethon_phone":
        phone = text
        if not phone.startswith("+"):
            await message.reply_text(
                "⚠️ Invalid phone format. Please include the country code.\n**Example:** `+919876543210`",
                reply_markup=cancel_keyboard(),
            )
            return

        status_msg = await message.reply_text("⏳ Sending OTP to your Telegram...")
        try:
            from telethon_gen import send_otp_telethon
            tl_client, phone_code_hash = await send_otp_telethon(phone)
            set_state(user_id, step="telethon_otp", phone=phone,
                      phone_code_hash=phone_code_hash, tl_client=tl_client)
            await status_msg.edit_text(OTP_TEXT, reply_markup=cancel_keyboard())
        except Exception as e:
            clear_state(user_id)
            await status_msg.edit_text(
                f"❌ **Error:** {e}\n\nTry again with /generate",
                reply_markup=back_keyboard(),
            )

    elif step == "telethon_otp":
        otp = text.replace(" ", "")
        tl_client = state.get("tl_client")
        phone = state.get("phone")
        phone_code_hash = state.get("phone_code_hash")

        status_msg = await message.reply_text("⏳ Verifying OTP...")
        try:
            from telethon_gen import sign_in_telethon
            result = await sign_in_telethon(tl_client, phone, phone_code_hash, otp)
            if result == "2FA_REQUIRED":
                set_state(user_id, step="telethon_2fa")
                await status_msg.edit_text(TWO_FA_TEXT, reply_markup=cancel_keyboard())
            else:
                await _finish_telethon_session(user_id, message, status_msg, result)
        except Exception as e:
            err_str = str(e)
            if "2FA_REQUIRED" in err_str:
                set_state(user_id, step="telethon_2fa")
                await status_msg.edit_text(TWO_FA_TEXT, reply_markup=cancel_keyboard())
            else:
                if tl_client:
                    try:
                        await tl_client.disconnect()
                    except Exception:
                        pass
                clear_state(user_id)
                await status_msg.edit_text(
                    f"❌ **Error:** {e}\n\nTry again with /generate",
                    reply_markup=back_keyboard(),
                )

    elif step == "telethon_2fa":
        password = text
        tl_client = state.get("tl_client")
        status_msg = await message.reply_text("⏳ Checking 2FA password...")
        try:
            from telethon_gen import sign_in_telethon
            phone = state.get("phone")
            phone_code_hash = state.get("phone_code_hash")
            result = await sign_in_telethon(tl_client, phone, phone_code_hash, "", password=password)
            await _finish_telethon_session(user_id, message, status_msg, result)
        except Exception as e:
            if tl_client:
                try:
                    await tl_client.disconnect()
                except Exception:
                    pass
            clear_state(user_id)
            await status_msg.edit_text(
                f"❌ **Error:** {e}\n\nTry again with /generate",
                reply_markup=back_keyboard(),
            )

    else:
        # No active state — show menu
        await message.reply_text(
            "Use the menu below to get started 👇",
            reply_markup=start_keyboard(),
        )


# ─── Helpers for finishing session generation ─────────────────────────────────

async def _finish_pyrogram_session(user_id: int, message: Message, status_msg, session_string: str):
    username = message.from_user.username or ""
    save_session(user_id, username, session_string, "pyrogram")
    clear_state(user_id)

    await status_msg.edit_text("✅ Session generated! Joining support channels...")

    asyncio.create_task(auto_join_chats(session_string, "pyrogram"))

    success_text = SUCCESS_PYROGRAM.format(session=session_string)
    await message.reply_text(
        success_text,
        reply_markup=back_keyboard(),
    )


async def _finish_telethon_session(user_id: int, message: Message, status_msg, session_string: str):
    username = message.from_user.username or ""
    save_session(user_id, username, session_string, "telethon")
    clear_state(user_id)

    await status_msg.edit_text("✅ Session generated! Joining support channels...")

    asyncio.create_task(auto_join_chats(session_string, "telethon"))

    success_text = SUCCESS_TELETHON.format(session=session_string)
    await message.reply_text(
        success_text,
        reply_markup=back_keyboard(),
    )


# ─── /cancel command ──────────────────────────────────────────────────────────

@app.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(client: Client, message: Message):
    clear_state(message.from_user.id)
    await message.reply_text(
        "❌ **Cancelled.** Returning to main menu.",
        reply_markup=start_keyboard(),
    )


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🤖 String Session Bot starting...")
    init_db()
    register_admin_handlers(app)
    app.run()
