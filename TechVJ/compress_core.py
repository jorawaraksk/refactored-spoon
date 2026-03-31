import os
import time
import asyncio
import signal
import psutil
from pathlib import Path
from datetime import datetime as dt
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER, DEV, ffmpegcode
from TechVJ.compress_utils import progress, ts, hbs, info, code, decode

# Global lock to ensure only one video processes at a time (prevents CPU crashes)
processing_lock = asyncio.Lock()

def is_auth(user_id):
    return str(user_id) in OWNER or user_id == DEV

# --- Callbacks for Stats and Cancel ---

@Client.on_callback_query(filters.regex(r"^stats(.*)"))
async def stats_callback(client: Client, cb: CallbackQuery):
    try:
        wah = cb.matches[0].group(1)
        wh = decode(wah)
        out, dl, id = wh.split(";")
        ot = hbs(int(Path(out).stat().st_size))
        ov = hbs(int(Path(dl).stat().st_size))
        processing_file_name = dl.replace("downloads/", "").replace("_", " ")
        ans = f"Processing Media:\n{processing_file_name}\n\nDownloaded:\n{ov}\n\nCompressed:\n{ot}"
        await cb.answer(ans, show_alert=True)
    except Exception:
        await cb.answer("Something Went Wrong.\nSend Media Again.", show_alert=True)

@Client.on_callback_query(filters.regex(r"^skip(.*)"))
async def skip_callback(client: Client, cb: CallbackQuery):
    try:
        wah = cb.matches[0].group(1)
        wh = decode(wah)
        out, dl, id = wh.split(";")
        
        await cb.message.delete()
        os.system("rm -rf downloads/*")
        os.system("rm -rf encode/*")
        
        # Kill the active FFmpeg process to stop compression immediately
        for proc in psutil.process_iter():
            if proc.name() == "ffmpeg":
                os.kill(proc.pid, signal.SIGKILL)
                
        await cb.answer("Task Cancelled Successfully.", show_alert=True)
    except Exception:
        await cb.answer("Failed to cancel or task already finished.", show_alert=True)

# --- Thumbnail Saver ---

@Client.on_message(filters.photo & filters.private)
async def save_thumb(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return
    await message.download("thumb.jpg")
    await message.reply_text("**Thumbnail Saved Successfully.**")

# --- Core Video Compression Logic ---

@Client.on_message(filters.private & (filters.video | filters.document))
async def encode_handler(client: Client, message: Message):
    if not is_auth(message.from_user.id):
        return await message.reply_text("**Sorry You're not An Authorised User!**")

    # Check if it's actually a video
    if message.document and not message.document.mime_type.startswith(("video", "application/octet-stream")):
        return

    # If another process is running, let the user know they are in the queue
    if processing_lock.locked():
        queue_msg = await message.reply_text("**Another task is processing. Added to Queue...**")

    # Lock ensures 1-by-1 processing to save CPU
    async with processing_lock:
        if 'queue_msg' in locals():
            await queue_msg.delete()
            
        status_msg = await message.reply_text("**📥 Downloading...**")
        start_time = dt.now()
        ttt = time.time()
        
        # Determine filename
        if message.video:
            filename = message.video.file_name or f"video_{dt.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        else:
            filename = message.document.file_name or f"video_{dt.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
        dl_path = os.path.join("downloads", filename)
        
        try:
            # Pyrogram Native Download
            dl = await client.download_media(
                message,
                file_name=dl_path,
                progress=progress,
                progress_args=(status_msg, ttt, f"**📥 Downloading**\n__{filename}__", None)
            )
        except Exception as e:
            return await status_msg.edit_text(f"**Download Error:** `{e}`")

        download_end = dt.now()
        
        # File paths setup
        base_name = os.path.basename(dl)
        ext = base_name.split(".")[-1]
        out_name = base_name.replace(f".{ext}", ".mkv")
        out_path = os.path.join("encode", out_name)
        thumb_path = "thumb.jpg" if os.path.exists("thumb.jpg") else None

        dtime = ts(int((download_end - start_time).seconds) * 1000)
        
        # Setup Callback Data
        hehe = f"{out_path};{dl};0"
        wah = code(hehe)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 STATS", callback_data=f"stats{wah}")],
            [InlineKeyboardButton("❌ CANCEL", callback_data=f"skip{wah}")]
        ])
        
        await status_msg.edit_text("**🗜 Compressing...**", reply_markup=buttons)
        
        # FFmpeg Subprocess
        cmd = f'ffmpeg -i "{dl}" {ffmpegcode[0]} "{out_path}" -y'
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        er = stderr.decode()
        
        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            if os.path.exists(dl): os.remove(dl)
            if os.path.exists(out_path): os.remove(out_path)
            return await status_msg.edit_text(f"**Compression Error:**\n\n`{er}`")

        compress_end = dt.now()
        ttt = time.time()
        
        await status_msg.edit_text("**📤 Uploading...**")
        
        # Size calculations
        org_size = os.path.getsize(dl)
        com_size = os.path.getsize(out_path)
        pe = 100 - ((com_size / org_size) * 100)
        per = f"{pe:.2f}%"
        
        # Fetch Mediainfo
        a1 = await info(dl, status_msg)
        a2 = await info(out_path, status_msg)
        
        x = dtime
        xx = ts(int((compress_end - download_end).seconds) * 1000)
        
        # Pyrogram Native Upload
        try:
            await client.send_document(
                chat_id=message.chat.id,
                document=out_path,
                thumb=thumb_path,
                caption=(
                    f"<b>File Name:</b> {base_name}\n\n"
                    f"<b>Original File Size:</b> {hbs(org_size)}\n"
                    f"<b>Encoded File Size:</b> {hbs(com_size)}\n"
                    f"<b>Encoded Percentage:</b> {per}\n\n"
                    f"<b>Get Mediainfo Here:</b> <a href='{a1}'>Before</a> / <a href='{a2}'>After</a>\n\n"
                    f"<i>Downloaded in {x}\nEncoded in {xx}</i>"
                ),
                progress=progress,
                progress_args=(status_msg, ttt, f"**📤 Uploading**\n__{out_name}__", None)
            )
        except Exception as e:
            await status_msg.edit_text(f"**Upload Error:** `{e}`")
            
        await status_msg.delete()
        
        # Cleanup
        if os.path.exists(dl): os.remove(dl)
        if os.path.exists(out_path): os.remove(out_path)
