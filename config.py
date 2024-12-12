from os import environ
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = environ.get("BOT_TOKEN")
CONDITIONS = environ.get("CONDITIONS")  # Text bases conditions for the contest

try:
    CHAT_ID = int(environ.get("CHAT_ID"))
    OWNER_ID = int(environ.get("OWNER_ID"))
    EXTRA_IDS = environ.get("EXTRA_IDS").split(
        ","
    )  # Comma separated list of extra user IDs
except ValueError:
    raise Exception("CHAT_ID and OWNER_ID must be integers")
