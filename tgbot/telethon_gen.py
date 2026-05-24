from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError,
    FloodWaitError,
)
from config import API_ID, API_HASH


async def send_otp_telethon(phone: str):
    """Send OTP for Telethon session. Returns (client, phone_code_hash)."""
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    try:
        result = await client.send_code_request(phone)
        return client, result.phone_code_hash
    except PhoneNumberInvalidError:
        await client.disconnect()
        raise Exception("Invalid phone number. Please check the format (e.g. +919876543210).")
    except FloodWaitError as e:
        await client.disconnect()
        raise Exception(f"Too many attempts. Wait {e.seconds} seconds.")


async def sign_in_telethon(client: TelegramClient, phone: str, phone_code_hash: str, otp: str, password: str = None) -> str:
    """Sign in and return the session string."""
    from telethon.errors import SessionPasswordNeededError
    otp_clean = otp.replace(" ", "")
    try:
        await client.sign_in(phone, otp_clean, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        if not password:
            raise Exception("2FA_REQUIRED")
        await client.sign_in(password=password)
    except PhoneCodeInvalidError:
        raise Exception("Invalid OTP. Please try again.")
    except PhoneCodeExpiredError:
        raise Exception("OTP has expired. Please start over.")
    except PasswordHashInvalidError:
        raise Exception("Wrong 2FA password. Please try again.")
    except FloodWaitError as e:
        raise Exception(f"Too many attempts. Wait {e.seconds} seconds.")

    session_string = client.session.save()
    await client.disconnect()
    return session_string
