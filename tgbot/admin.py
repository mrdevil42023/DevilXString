import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated,
    PeerIdInvalid, UserNotParticipant
)

from config import OWNER_ID
from database import get_all_sessions, get_user_sessions, supabase


# ─── Owner filter ─────────────────────────────────────────────────────────────

def owner_filter(_, __, message) -> bool:
    return getattr(message.from_user, "id", None) == OWNER_ID

owner_only = filters.create(owner_filter)

# Shared broadcast state
broadcast_state: dict = {}   # {OWNER_ID: "waiting"} or absent


def is_broadcast_waiting() -> bool:
    return broadcast_state.get(OWNER_ID) == "waiting"


# ─── Admin panel keyboard ──────────────────────────────────────────────────────

def admin_panel_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 All Users",   callback_data="admin_users"),
            InlineKeyboardButton("📊 Stats",       callback_data="admin_back"),
        ],
        [InlineKeyboardButton("📢 Broadcast",      callback_data="admin_broadcast")],
    ])


def stats_text(all_sessions):
    total = len(all_sessions)
    pyro  = sum(1 for s in all_sessions if s.get("session_type") == "pyrogram")
    tele  = sum(1 for s in all_sessions if s.get("session_type") == "telethon")
    users = len(set(s.get("user_id") for s in all_sessions))
    return (
        "╔══════════════════════════════╗\n"
        "║       📊 **Bot Statistics**      ║\n"
        "╚══════════════════════════════╝\n\n"
        f"👥 **Total Unique Users:** `{users}`\n"
        f"📦 **Total Sessions:**     `{total}`\n\n"
        f"🔑 **Pyrogram Sessions:**  `{pyro}`\n"
        f"📡 **Telethon Sessions:**  `{tele}`\n\n"
        "🤖 **Bot Status:** Online ✅"
    )


# ─── Register all admin handlers ──────────────────────────────────────────────

def register_admin_handlers(app: Client):

    # ── /stats ────────────────────────────────────────────────────────────────

    @app.on_message(filters.command("stats") & filters.private & owner_only)
    async def stats_cmd(client: Client, message: Message):
        try:
            sessions = get_all_sessions()
            await message.reply_text(stats_text(sessions), reply_markup=admin_panel_keyboard())
        except Exception as e:
            await message.reply_text(f"❌ Error: `{e}`")


    # ── /users ────────────────────────────────────────────────────────────────

    @app.on_message(filters.command("users") & filters.private & owner_only)
    async def users_cmd(client: Client, message: Message):
        try:
            all_sessions = get_all_sessions()
            if not all_sessions:
                await message.reply_text("📋 No users have generated sessions yet.")
                return

            seen, unique = set(), []
            for s in all_sessions:
                uid = s.get("user_id")
                if uid not in seen:
                    seen.add(uid)
                    unique.append(s)

            lines = [f"👥 **All Users** ({len(unique)} total)\n"]
            for i, s in enumerate(unique[:20], 1):
                uid   = s.get("user_id", "?")
                uname = s.get("username", "")
                lines.append(f"`{i}.` `{uid}` — {'@' + uname if uname else 'No username'}")
            if len(unique) > 20:
                lines.append(f"\n_...and {len(unique) - 20} more._")

            await message.reply_text(
                "\n".join(lines),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Stats", callback_data="admin_back")]
                ])
            )
        except Exception as e:
            await message.reply_text(f"❌ Error: `{e}`")


    # ── /broadcast ────────────────────────────────────────────────────────────

    @app.on_message(filters.command("broadcast") & filters.private & owner_only)
    async def broadcast_cmd(client: Client, message: Message):
        broadcast_state[OWNER_ID] = "waiting"
        await message.reply_text(
            "📢 **Broadcast**\n\n"
            "Send me the message to broadcast to **all users**.\n\n"
            "✅ Supports: text, photos, videos, stickers, documents, voice\n"
            "❌ To cancel, send /cancel or tap the button below.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel Broadcast", callback_data="admin_cancel_broadcast")]
            ])
        )


    # ── Broadcast message receiver (owner-only, fires only when waiting) ──────

    @app.on_message(filters.private & owner_only, group=1)
    async def broadcast_receive(client: Client, message: Message):
        # Only intercept when waiting for a broadcast message
        if not is_broadcast_waiting():
            return
        # Don't intercept commands (let them pass through normally)
        if message.text and message.text.startswith("/"):
            return

        broadcast_state.pop(OWNER_ID, None)

        all_sessions  = get_all_sessions()
        unique_ids    = list(set(s.get("user_id") for s in all_sessions))
        total         = len(unique_ids)

        if total == 0:
            await message.reply_text("⚠️ No users to broadcast to yet.")
            return

        sent = failed = blocked = deactivated = 0
        status_msg = await message.reply_text(
            f"📤 **Broadcasting...**\n\n"
            f"👥 Total recipients: `{total}`\n"
            f"⏳ Starting..."
        )

        for i, uid in enumerate(unique_ids, 1):
            try:
                await message.copy(uid)
                sent += 1
            except FloodWait as e:
                await asyncio.sleep(e.value + 1)
                try:
                    await message.copy(uid)
                    sent += 1
                except Exception:
                    failed += 1
            except UserIsBlocked:
                blocked += 1
            except InputUserDeactivated:
                deactivated += 1
            except Exception:
                failed += 1

            # Update progress every 10 users or on last user
            if i % 10 == 0 or i == total:
                progress = int((i / total) * 20)
                bar = "█" * progress + "░" * (20 - progress)
                try:
                    await status_msg.edit_text(
                        f"📤 **Broadcasting...**\n\n"
                        f"`[{bar}]` {i}/{total}\n\n"
                        f"✅ Sent:        `{sent}`\n"
                        f"🚫 Blocked:     `{blocked}`\n"
                        f"💤 Deactivated: `{deactivated}`\n"
                        f"❌ Failed:      `{failed}`"
                    )
                except Exception:
                    pass

            await asyncio.sleep(0.05)

        await status_msg.edit_text(
            "✅ **Broadcast Complete!**\n\n"
            f"👥 **Total:**        `{total}`\n"
            f"✅ **Sent:**         `{sent}`\n"
            f"🚫 **Blocked:**      `{blocked}`\n"
            f"💤 **Deactivated:**  `{deactivated}`\n"
            f"❌ **Failed:**       `{failed}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Broadcast Again", callback_data="admin_broadcast")],
                [InlineKeyboardButton("📊 Back to Stats",  callback_data="admin_back")],
            ])
        )


    # ── /ban ──────────────────────────────────────────────────────────────────

    @app.on_message(filters.command("ban") & filters.private & owner_only)
    async def ban_cmd(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("⚠️ Usage: `/ban <user_id>`")
            return
        try:
            target_id = int(args[1])
            supabase.table("sessions").delete().eq("user_id", target_id).execute()
            await message.reply_text(f"✅ Banned `{target_id}` and deleted all their sessions.")
        except Exception as e:
            await message.reply_text(f"❌ Error: `{e}`")


    # ── /unban ────────────────────────────────────────────────────────────────

    @app.on_message(filters.command("unban") & filters.private & owner_only)
    async def unban_cmd(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("⚠️ Usage: `/unban <user_id>`")
            return
        await message.reply_text(f"✅ User `{args[1]}` is now unbanned.")


    # ── /userinfo ─────────────────────────────────────────────────────────────

    @app.on_message(filters.command("userinfo") & filters.private & owner_only)
    async def userinfo_cmd(client: Client, message: Message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("⚠️ Usage: `/userinfo <user_id>`")
            return
        try:
            target_id = int(args[1])
            sessions  = get_user_sessions(target_id)
            if not sessions:
                await message.reply_text(f"ℹ️ User `{target_id}` has no sessions.")
                return

            s    = sessions[0]
            text = (
                f"👤 **User Info**\n\n"
                f"🆔 **User ID:**       `{target_id}`\n"
                f"👤 **Username:**      @{s.get('username', 'N/A')}\n"
                f"📦 **Total Sessions:** `{len(sessions)}`\n\n"
                "**Sessions:**\n"
            )
            for i, sess in enumerate(sessions, 1):
                stype   = sess.get("session_type", "?").upper()
                preview = sess.get("session_string", "")[:30] + "..."
                text   += f"\n`{i}.` {stype} — `{preview}`"

            await message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚫 Ban User", callback_data=f"admin_ban_{target_id}")]
                ])
            )
        except Exception as e:
            await message.reply_text(f"❌ Error: `{e}`")


    # ── Admin callback queries ─────────────────────────────────────────────────

    @app.on_callback_query(
        filters.create(lambda _, __, q: getattr(q.from_user, "id", None) == OWNER_ID
                       and q.data.startswith("admin_"))
    )
    async def admin_callbacks(client: Client, query: CallbackQuery):
        data = query.data

        if data == "admin_users":
            await query.answer()
            all_sessions = get_all_sessions()
            seen, unique = set(), []
            for s in all_sessions:
                uid = s.get("user_id")
                if uid not in seen:
                    seen.add(uid)
                    unique.append(s)
            lines = [f"👥 **All Users** ({len(unique)} total)\n"]
            for i, s in enumerate(unique[:15], 1):
                uid   = s.get("user_id", "?")
                uname = s.get("username", "")
                lines.append(f"`{i}.` `{uid}` — {'@' + uname if uname else 'No username'}")
            if len(unique) > 15:
                lines.append(f"\n_...and {len(unique) - 15} more._")
            await query.message.edit_text(
                "\n".join(lines),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Stats", callback_data="admin_back")]
                ])
            )

        elif data == "admin_broadcast":
            await query.answer()
            broadcast_state[OWNER_ID] = "waiting"
            await query.message.edit_text(
                "📢 **Broadcast**\n\n"
                "Send me the message to broadcast to **all users**.\n\n"
                "✅ Supports: text, photos, videos, stickers, documents, voice\n"
                "❌ Tap Cancel or send /cancel to abort.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancel Broadcast", callback_data="admin_cancel_broadcast")]
                ])
            )

        elif data == "admin_cancel_broadcast":
            broadcast_state.pop(OWNER_ID, None)
            await query.answer("Broadcast cancelled.", show_alert=True)
            sessions = get_all_sessions()
            await query.message.edit_text(stats_text(sessions), reply_markup=admin_panel_keyboard())

        elif data == "admin_back":
            await query.answer()
            sessions = get_all_sessions()
            await query.message.edit_text(stats_text(sessions), reply_markup=admin_panel_keyboard())

        elif data.startswith("admin_ban_"):
            target_id = int(data.replace("admin_ban_", ""))
            supabase.table("sessions").delete().eq("user_id", target_id).execute()
            await query.answer(f"User {target_id} banned!", show_alert=True)
            await query.message.edit_text(f"✅ User `{target_id}` banned and sessions deleted.")
