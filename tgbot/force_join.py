from pyrogram import Client
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChannelPrivate, PeerIdInvalid

# Chats to force-join (username without @)
FORCE_JOIN_CHATS = [
    ("devilbots971",    "📢 Support Channel", "https://t.me/devilbots971"),
    ("devilbotsupport", "💬 Support Group",   "https://t.me/devilbotsupport"),
]


async def check_membership(client: Client, user_id: int) -> list[tuple[str, str, str]]:
    """
    Returns a list of (username, label, link) for chats the user has NOT joined yet.
    Empty list means the user is in all required chats.
    """
    not_joined = []
    for username, label, link in FORCE_JOIN_CHATS:
        try:
            member = await client.get_chat_member(username, user_id)
            # Banned or kicked counts as not joined
            if member.status.value in ("banned", "kicked", "left"):
                not_joined.append((username, label, link))
        except UserNotParticipant:
            not_joined.append((username, label, link))
        except (ChatAdminRequired, ChannelPrivate, PeerIdInvalid, Exception):
            # If we can't check (e.g. private chat bot isn't in), skip — don't block the user
            pass
    return not_joined
