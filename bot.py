import os
import logging
from logging.handlers import RotatingFileHandler
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# --- Logging Setup ---
LOG_FILE_NAME = "TG-videoCompress@Log.txt"

if os.path.exists(LOG_FILE_NAME):
    with open(LOG_FILE_NAME, "r+") as f_d:
        f_d.truncate(0)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=2097152000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

# Keep Pyrogram's internal logs from spamming the console
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGS = logging.getLogger(__name__)

# --- Bot Initialization ---
class Bot(Client):
    def __init__(self):
        super().__init__(
            "merged_bot_session",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        await super().start()
        LOGS.info('Bot Started! Merged Restricted Save & Compressor Logic')

    async def stop(self, *args):
        await super().stop()
        LOGS.info('Bot Stopped. Bye!')

if __name__ == "__main__":
    Bot().run()
