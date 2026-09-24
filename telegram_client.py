from pathlib import Path

from telethon import TelegramClient

from config import API_ID, API_HASH, SESSION_NAME


session_path = Path(SESSION_NAME)

session_path.parent.mkdir(
    parents=True,
    exist_ok=True
)


client = TelegramClient(
    str(session_path),
    API_ID,
    API_HASH
)