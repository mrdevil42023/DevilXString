import asyncio
from pyrogram import Client
from pyrogram.errors import (
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    FloodWait,
)
from config import API_ID, API_HASH


async def generate_pyrogram_session(phone: str, otp: str, password: str = None) -> str:
    """Generate a Pyrogram string session."""
    client = Client(
        name="session_gen",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
    )
    await client.connect()

    try:
        sent_code = await client.send_code(phone)
        otp_clean = otp.replace(" ", "")

        try:
            await client.sign_in(phone, sent_code.phone_code_hash, otp_clean)
        except SessionPasswordNeeded:
            if not password:
                raise Exception("2FA_REQUIRED")
            await client.check_password(password)

        session_string = await client.export_session_string()
        return session_string

    except PhoneNumberInvalid:
        raise Exception("Invalid phone number. Please try again with the correct format.")
    except PhoneCodeInvalid:
        raise Exception("Invalid OTP. Please try again.")
    except PhoneCodeExpired:
        raise Exception("OTP has expired. Please start over.")
    except PasswordHashInvalid:
        raise Exception("Wrong 2FA password. Please try again.")
    except FloodWait as e:
        raise Exception(f"Too many attempts. Please wait {e.value} seconds and try again.")
    finally:
        await client.disconnect()


async def send_otp_pyrogram(phone: str):
    """Send OTP for Pyrogram session generation. Returns (client, phone_code_hash)."""
    client = Client(
        name="otp_sender",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
    )
    await client.connect()
    try:
        sent_code = await client.send_code(phone)
        return client, sent_code.phone_code_hash
    except PhoneNumberInvalid:
        await client.disconnect()
        raise Exception("Invalid phone number. Please check the format (e.g. +919876543210).")
    except FloodWait as e:
        await client.disconnect()
        raise Exception(f"Too many attempts. Wait {e.value} seconds.")
