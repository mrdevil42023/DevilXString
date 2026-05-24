import asyncio
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, FloodWait, InviteHashExpired, UsernameNotOccupied
from config import API_ID, API_HASH, AUTO_JOIN_CHATS


async def auto_join_pyrogram(session_string: str):
    """Join all AUTO_JOIN_CHATS using a Pyrogram session string."""
    joined = []
    failed = []
    try:
        async with Client(
            name="auto_joiner_pyro",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            in_memory=True,
        ) as user_client:
            for chat in AUTO_JOIN_CHATS:
                try:
                    await user_client.join_chat(chat)
                    joined.append(chat)
                    print(f"[AutoJoin] Pyrogram: joined {chat}")
                except UserAlreadyParticipant:
                    joined.append(chat)
                    print(f"[AutoJoin] Pyrogram: already in {chat}")
                except FloodWait as e:
                    print(f"[AutoJoin] FloodWait {e.value}s for {chat}, waiting...")
                    await asyncio.sleep(e.value)
                    try:
                        await user_client.join_chat(chat)
                        joined.append(chat)
                    except Exception as ex:
                        print(f"[AutoJoin] Pyrogram: retry failed for {chat}: {ex}")
                        failed.append(chat)
                except Exception as e:
                    print(f"[AutoJoin] Pyrogram: failed to join {chat}: {e}")
                    failed.append(chat)
                await asyncio.sleep(2)
    except Exception as e:
        print(f"[AutoJoin] Pyrogram client error: {e}")

    return joined, failed


async def auto_join_telethon(session_string: str):
    """Join all AUTO_JOIN_CHATS using a Telethon session string."""
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import JoinChannelRequest
    from telethon.errors import UserAlreadyParticipantError, FloodWaitError, UsernameNotOccupiedError

    joined = []
    failed = []
    try:
        async with TelegramClient(StringSession(session_string), API_ID, API_HASH) as user_client:
            for chat in AUTO_JOIN_CHATS:
                try:
                    entity = await user_client.get_entity(chat)
                    await user_client(JoinChannelRequest(entity))
                    joined.append(chat)
                    print(f"[AutoJoin] Telethon: joined {chat}")
                except UserAlreadyParticipantError:
                    joined.append(chat)
                    print(f"[AutoJoin] Telethon: already in {chat}")
                except FloodWaitError as e:
                    print(f"[AutoJoin] FloodWait {e.seconds}s for {chat}, waiting...")
                    await asyncio.sleep(e.seconds)
                    try:
                        entity = await user_client.get_entity(chat)
                        await user_client(JoinChannelRequest(entity))
                        joined.append(chat)
                    except Exception as ex:
                        print(f"[AutoJoin] Telethon: retry failed for {chat}: {ex}")
                        failed.append(chat)
                except Exception as e:
                    print(f"[AutoJoin] Telethon: failed to join {chat}: {e}")
                    failed.append(chat)
                await asyncio.sleep(2)
    except Exception as e:
        print(f"[AutoJoin] Telethon client error: {e}")

    return joined, failed


async def auto_join_chats(session_string: str, session_type: str = "pyrogram"):
    """Dispatch auto-join based on session type."""
    if session_type == "pyrogram":
        return await auto_join_pyrogram(session_string)
    elif session_type == "telethon":
        return await auto_join_telethon(session_string)
    return [], []
