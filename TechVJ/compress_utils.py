import time
import math
import subprocess
import os
from datetime import datetime as dt
from html_telegraph_poster import TelegraphPoster

# --- Global State for Compressor ---
WORKING = []
QUEUE = {}
OK = {}
uptime = dt.now()

# Download default thumb on startup
from config import THUMB
os.system(f"wget {THUMB} -O thumb.jpg")

def stdr(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)
    if len(str(hours)) == 1:
        hours = "0" + str(hours)
    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)
    dur = (
        ((str(hours) + ":") if hours else "00:")
        + ((str(minutes) + ":") if minutes else "00:")
        + ((str(seconds)) if seconds else "")
    )
    return dur

def ts(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
        + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2]

def hbs(size):
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "B", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"

async def progress(current, total, message, start, type_of_ps, file_name=None):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        progress_str = "{0}{1}** {2}%**\n\n".format(
            "".join(["●" for i in range(math.floor(percentage / 10))]),
            "".join(["○" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )
        tmp = (
            progress_str
            + "** Progress:** {0} \n\n** Total Size:** {1}\n\n** Speed:** {2}/s\n\n** Time Left:** {3}\n".format(
                hbs(current),
                hbs(total),
                hbs(speed),
                ts(time_to_completion),
            )
        )
        try:
            if file_name:
                await message.edit_text(f"{type_of_ps}\n\nFile Name: {file_name}\n\n{tmp}")
            else:
                await message.edit_text(f"{type_of_ps}\n\n{tmp}")
        except:
            pass # Ignore floodwaits/message not modified errors during edits

async def info(file, message):
    process = subprocess.Popen(
        ["mediainfo", file, "--Output=HTML"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, stderr = process.communicate()
    out = stdout.decode()
    client = TelegraphPoster(use_api=True)
    client.create_api_token("TGVid-Comp-Mediainfo")
    me = await message._client.get_me()
    page = client.post(
        title="TGVid-Comp-Mediainfo",
        author=me.first_name,
        author_url=f"https://t.me/{me.username}",
        text=out,
    )
    return page["url"]

def code(data):
    OK.update({len(OK): data})
    return str(len(OK) - 1)

def decode(key):
    if OK.get(int(key)):
        return OK[int(key)]
    return None
