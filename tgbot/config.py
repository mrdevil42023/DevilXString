import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

# Owner ID — only this user can use admin commands
OWNER_ID = 6107980637

# Groups/channels to auto-join after session generation
# Use @username strings — they work reliably for both Pyrogram and Telethon
AUTO_JOIN_CHATS = [
    "devilbots971",       # Support channel: https://t.me/devilbots971
    "devilbotsupport",    # Support group:   https://t.me/devilbotsupport
]

# Bot info
BOT_NAME = "Devil X String"
BOT_USERNAME = "StringGenBot"
SUPPORT_CHAT = "https://t.me/devilbots971"

# Path to start image (relative to tgbot/)
START_IMAGE = os.path.join(os.path.dirname(__file__), "start_image.png")
