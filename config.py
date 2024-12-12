from os import environ
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = environ.get("BOT_TOKEN")
CHAT_ID = int(environ.get("CHAT_ID"))
OWNER_ID = int(environ.get("OWNER_ID"))
EXTRA_IDS = environ.get("EXTRA_IDS")  # Comma separated list of extra user IDs
