import os
import sys
import io
import time
import asyncio
import psutil
import signal
import traceback
from datetime import datetime as dt
from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER, DEV, ffmpegcode
from TechVJ.compress_utils import ts, uptime, WORKING, QUEUE

# Helper auth check
def is_auth(user_id):
    return str(user_id) in OWNER or user_id == DEV

@Client.on_message(filters.command("cmds") & filters.private)
async def cmds_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    await message.reply_text(
        "**Available Commands 😉**\n\n"
        "/start - __Check Bot is Working Or Not__\n"
        "/help - __Get Detailed Help__\n"
        "/setcode - __Set Custom FFMPEG Code__\n"
        "/getcode - __Print Current FFMPEG Code__\n"
        "/logs - __Get Bot Logs__\n"
        "/ping - __Check Ping__\n"
        "/sysinfo - __Get System Info__\n"
        "/renew - __Clear Cached Downloads__\n"
        "/clear - __Clear Queued Files__\n"
        "/showthumb - __Show Current Thumbnail__\n"
        "/cmds - __List Available Commands__"
    )

@Client.on_message(filters.command("ping") & filters.private)
async def ping_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    stt = dt.now()
    ed = dt.now()
    v = ts(int((ed - uptime).seconds) * 1000)
    ms = (ed - stt).microseconds / 1000
    p = f"Ping = {ms}ms"
    await message.reply_text(v + "\n" + p)

@Client.on_message(filters.command("sysinfo") & filters.private)
async def sysinfo_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    try:
        process = await asyncio.create_subprocess_shell(
            "neofetch --stdout", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        result = str(stdout.decode().strip()) + str(stderr.decode().strip())
        await message.reply_text(f"**{result}**")
    except Exception:
        await message.reply_text("**Install neofetch first**")

@Client.on_message(filters.command("setcode") & filters.private)
async def setcode_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    if len(message.command) < 2:
        return await message.reply_text("**Please provide the ffmpeg code after the command.**")
    
    new_code = message.text.split(" ", maxsplit=1)[1]
    ffmpegcode.clear()
    ffmpegcode.insert(0, new_code)
    await message.reply_text(f"**Changed FFMPEG Code to**\n\n`{new_code}`")

@Client.on_message(filters.command("getcode") & filters.private)
async def getcode_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    await message.reply_text(f"**Your Current FFMPEG Code is**\n\n`{ffmpegcode[0]}`")

@Client.on_message(filters.command("logs") & filters.private)
async def logs_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    if os.path.exists("TG-videoCompress@Log.txt"):
        await message.reply_document("TG-videoCompress@Log.txt")
    else:
        await message.reply_text("**No log file found.**")

@Client.on_message(filters.command("showthumb") & filters.private)
async def showthumb_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    if os.path.exists("thumb.jpg"):
        await message.reply_photo(photo="thumb.jpg", caption="**Your Current Thumbnail.**")
    else:
        await message.reply_text("**No thumbnail found.**")

@Client.on_message(filters.command("clear") & filters.private)
async def clear_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    QUEUE.clear()
    await message.reply_text("**Cleared Queued Files!**")

@Client.on_message(filters.command("renew") & filters.private)
async def renew_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    WORKING.clear()
    QUEUE.clear()
    os.system("rm -rf downloads/*")
    os.system("rm -rf encode/*")
    
    # Kill ongoing ffmpeg processes
    for proc in psutil.process_iter():
        try:
            if proc.name() == "ffmpeg":
                os.kill(proc.pid, signal.SIGKILL)
        except:
            pass
            
    await message.reply_text("**Cleared Queued, Working Files, Cached Downloads, and killed active FFMPEG processes!**")

@Client.on_message(filters.command("bash") & filters.private)
async def bash_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")
    
    if len(message.command) < 2:
        return await message.reply_text("**Provide a command.**")
        
    cmd = message.text.split(" ", maxsplit=1)[1]
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    e = stderr.decode()
    if not e: e = "No Error"
    o = stdout.decode()
    if not o: o = "**Tip**: \n`If you want to see the results of your code, I suggest printing them to stdout.`"
    
    OUTPUT = f"**QUERY:**\n__Command:__\n`{cmd}` \n__PID:__\n`{process.pid}`\n\n**stderr:** \n`{e}`\n**Output:**\n{o}"
    
    if len(OUTPUT) > 4095:
        with io.BytesIO(str.encode(OUTPUT)) as out_file:
            out_file.name = "exec.txt"
            await client.send_document(message.chat.id, out_file, caption=cmd)
    else:
        await message.reply_text(OUTPUT)
