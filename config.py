import os

# --- Core Telegram Configs ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "16732227"))
API_HASH = os.environ.get("API_HASH", "8b5594ad7ad37f3a0a7ddbfb3963bb51")

# --- Restricted Bot Configs ---
ADMINS = int(os.environ.get("ADMINS", "5868426717"))
DB_URI = os.environ.get("DB_URI", "") 
DB_NAME = os.environ.get("DB_NAME", "vjsavecontentbot")
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))

# --- Compressor Bot Configs ---
OWNER = os.environ.get("OWNER", "5868426717")
DEV = int(os.environ.get("DEV", "5868426717"))
THUMB = os.environ.get("THUMBNAIL", "https://graph.org/file/1cc8d7082dc910c0ccee8.jpg")

# Directory paths for processing
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads")
ENCODE_DIR = os.environ.get("ENCODE_DIR", "encode")

# Auto-create processing directories if they don't exist
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
if not os.path.exists(ENCODE_DIR):
    os.makedirs(ENCODE_DIR)

# Global FFMPEG code list (Mutable so /setcode can update it)
ffmpegcode = ["-preset veryfast -c:v libx264 -b:a 64k -crf 38 -map 0 -c:s copy"]
