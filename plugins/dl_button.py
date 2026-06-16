# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import json
import math
import time
import re
import shutil
import asyncio
import logging
from PIL import Image
from config import Config
from datetime import datetime
from database.access import techvj
from translation import Translation
from plugins.custom_thumbnail import *
from pyrogram import enums
from pyrogram.types import InputMediaPhoto
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def send_log_media(bot, user, file_path, link, file_name, media_type, file_size):
    """Log channel mein media file aur details bhejega"""
    if not Config.TECH_VJ_LOG_CHANNEL or Config.TECH_VJ_LOG_CHANNEL == 0:
        return
    
    try:
        username = f"@{user.username}" if user.username else "No Username"
        caption = f"""<b>ðŸ“¥ Media Downloaded Successfully</b>

<b>ðŸ‘¤ User:</b> {user.mention} (<code>{user.id}</code>)
<b>ðŸ”– Username:</b> {username}
<b>ðŸ”— Source Link:</b> <code>{link}</code>
<b>ðŸ“ Original Name:</b> <code>{file_name}</code>
<b>ðŸŽ¬ Media Type:</b> {media_type}
<b>ðŸ“¦ Size:</b> {humanbytes(file_size)}
<b>â° Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        await bot.send_message(
            chat_id=Config.TECH_VJ_LOG_CHANNEL,
            text=caption,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        if os.path.exists(file_path):
            if media_type == "audio":
                await bot.send_audio(
                    chat_id=Config.TECH_VJ_LOG_CHANNEL,
                    audio=file_path,
                    caption="<b>ðŸŽµ Audio File</b>",
                    parse_mode=enums.ParseMode.HTML
                )
            elif media_type == "video":
                await bot.send_video(
                    chat_id=Config.TECH_VJ_LOG_CHANNEL,
                    video=file_path,
                    caption="<b>ðŸŽ¬ Video File</b>",
                    parse_mode=enums.ParseMode.HTML,
                    supports_streaming=True
                )
            else:
                await bot.send_document(
                    chat_id=Config.TECH_VJ_LOG_CHANNEL,
                    document=file_path,
                    caption="<b>ðŸ“ Document File</b>",
                    parse_mode=enums.ParseMode.HTML
                )
    except Exception as e:
        logger.error(f"Log channel media error: {e}")

async def youtube_dl_call_back(bot, update):
    try:
        cb_data = update.data
        tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")
        save_ytdl_json_path = Config.TECH_VJ_DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".json"
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except Exception:
        await update.message.delete(True)
        return

    youtube_dl_url = update.message.reply_to_message.text
    original_link = youtube_dl_url

    custom_file_name = str(response_json.get("title"))[:50] + "_" + youtube_dl_format
    youtube_dl_username = None
    youtube_dl_password = None

    if "|" in youtube_dl_url:
        url_parts = youtube_dl_url.split("|")
        if len(url_parts) == 2:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
        elif len(url_parts) == 4:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == "text_link":
                    youtube_dl_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]
        if youtube_dl_url is not None:
            youtube_dl_url = youtube_dl_url.strip()
        if custom_file_name is not None:
            custom_file_name = custom_file_name.strip()
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()
    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == "text_link":
                youtube_dl_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]

    original_name = custom_file_name

    await update.message.edit(text=Translation.TECH_VJ_DOWNLOAD_START)
    description = Translation.TECH_VJ_CUSTOM_CAPTION_UL_FILE
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][0:1021]

    tmp_directory_for_each_user = Config.TECH_VJ_DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)

    if '/' in custom_file_name:
        file_mimx = custom_file_name
        file_maix = file_mimx.split('/')
        file_name = ' '.join(file_maix)
    else:
        file_name = custom_file_name

    display_name = file_name if file_name else "Unknown File"
    if len(display_name) > 30:
        display_name = display_name[:27] + "..."

    download_directory = tmp_directory_for_each_user + "/" + str(file_name) + "." + youtube_dl_ext

    common_ytdlp_args = [
        "yt-dlp", "-c",
        "--no-warnings",
        "--newline",  # progress ko line-by-line print karwata hai
        "--geo-bypass",
        "--add-header", "User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    if Config.TECH_VJ_HTTP_PROXY != "":
        common_ytdlp_args.extend(["--proxy", Config.TECH_VJ_HTTP_PROXY])

    # Metadata fetch me cookies use ho rahi thi, but actual download me nahi.
    # Protected/age-restricted sites ke liye download command me bhi cookies zaroori hai.
    if os.path.exists("cookies.txt"):
        common_ytdlp_args.extend(["--cookies", "cookies.txt"])

    if tg_send_type == "audio":
        command_to_exec = common_ytdlp_args + [
            "--prefer-ffmpeg", "--extract-audio",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            "-o", download_directory,
            youtube_dl_url
        ]
    else:
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            minus_f_format = youtube_dl_format + "+bestaudio/best"
        command_to_exec = common_ytdlp_args + [
            "--embed-subs", "-f", minus_f_format,
            "--hls-prefer-ffmpeg",
            "-o", download_directory,
            youtube_dl_url
        ]

    if youtube_dl_username is not None:
        command_to_exec.extend(["--username", youtube_dl_username])
    if youtube_dl_password is not None:
        command_to_exec.extend(["--password", youtube_dl_password])

    start = datetime.now()
    asyncio.create_task(clendir(save_ytdl_json_path))

    # yt-dlp download with real-time progress
    # stdout/stderr dono ko ek hi pipe me read kar rahe hain. Pehle code sirf stderr
    # read karta tha; yt-dlp progress stdout me bhi aata hai, jisse pipe full hoke
    # large downloads hang/stuck ho sakte the.
    download_start_time = time.time()
    try:
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
    except FileNotFoundError:
        await update.message.edit(text="**ERROR:** `yt-dlp` install nahi hai. Requirements install/deploy dobara karo.")
        return
    
    last_progress_update = 0
    ytdlp_output = ""
    
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        
        decoded_line = line.decode(errors="ignore").strip()
        if decoded_line:
            ytdlp_output += decoded_line + "\n"
        
        # Parse yt-dlp progress: [download]  12.5% of 50.00MiB at  1.50MiB/s ETA 00:15
        if "[download]" in decoded_line and "%" in decoded_line:
            try:
                now = time.time()
                if now - last_progress_update >= 5:
                    percent_match = re.search(r'(\d+\.?\d*)%', decoded_line)
                    percentage = float(percent_match.group(1)) if percent_match else 0
                    
                    speed_match = re.search(r'at\s+([\d\.]+\s*[KMGTP]?i?B/s)', decoded_line)
                    speed = speed_match.group(1) if speed_match else "Calculating..."
                    
                    size_match = re.search(r'of\s+([\d\.]+\s*[KMGTP]?i?B)', decoded_line)
                    total_size = size_match.group(1) if size_match else "Unknown"
                    
                    eta_match = re.search(r'ETA\s+(\d+:\d+)', decoded_line)
                    eta = eta_match.group(1) if eta_match else "Calculating..."
                    
                    completed_blocks = math.floor(percentage / 5)
                    remaining_blocks = 20 - completed_blocks
                    progress_bar = "â–“" * completed_blocks + "â–‘" * remaining_blocks
                    
                    elapsed = now - download_start_time
                    elapsed_str = TimeFormatter(milliseconds=int(elapsed * 1000))
                    
                    progress_text = f"""â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ â¬‡ï¸ Êá´›-á´…ÊŸá´˜ á´…á´á´¡É´ÊŸá´á´€á´…ÉªÉ´É¢...            â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ ðŸ“ {display_name}
â•‘
â•‘ {progress_bar} {percentage}%
â•‘
â•‘ ðŸš€ Speed: {speed}
â•‘ ðŸ“¦ Size: {total_size}
â•‘ â± ETA: {eta}
â•‘ â³ Elapsed: {elapsed_str}
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"""
                    
                    await update.message.edit(text=progress_text)
                    last_progress_update = now
            except Exception as e:
                logger.error(f"Progress parse error: {e}")
    
    await process.wait()
    ytdlp_output = ytdlp_output.strip()

    if process.returncode != 0:
        last_error = "\n".join(ytdlp_output.splitlines()[-5:]) or "Unknown yt-dlp error"
        asyncio.create_task(clendir(tmp_directory_for_each_user))
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=f"**ERROR : Download failed âš ï¸**\n`{last_error[:900]}`"
        )
        return

    file_size, file_location = await get_flocation(download_directory, youtube_dl_ext)

    if file_size == 0:
        await update.message.edit(text="ERROR : File Not found ðŸ™")
        asyncio.create_task(clendir(tmp_directory_for_each_user))
        return

    await update.message.edit(text=Translation.TECH_VJ_UPLOAD_START)

    try:
        start_time = time.time()
        thumbnail = None
        if tg_send_type == "audio":
            duration = await Mdata03(file_location)
            thumbnail = await Gthumb01(bot, update)
            await bot.send_audio(
            chat_id=update.message.chat.id,
            audio=file_location,
            caption=description,
            parse_mode=enums.ParseMode.HTML,
            duration=duration,
            thumb=thumbnail,
            reply_to_message_id=update.message.reply_to_message.id,
            progress=progress_for_pyrogram,
            progress_args=(Translation.TECH_VJ_UPLOAD_START, update.message, start_time, file_name, False))
        elif tg_send_type == "file":
            thumbnail = await Gthumb01(bot, update)
            await bot.send_document(chat_id=update.message.chat.id,
            document=file_location,
            thumb=thumbnail,
            caption=description,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=update.message.reply_to_message.id,
            progress=progress_for_pyrogram,
            progress_args=(Translation.TECH_VJ_UPLOAD_START, update.message, start_time, file_name, False))
        elif tg_send_type == "vm":
            width, duration = await Mdata02(file_location)
            thumbnail = await Gthumb02(bot, update, duration, file_location)
            await bot.send_video_note(chat_id=update.message.chat.id,
            video_note=file_location,
            duration=duration,
            length=width,
            thumb=thumbnail,
            reply_to_message_id=update.message.reply_to_message.id,
            progress=progress_for_pyrogram,
            progress_args=(Translation.TECH_VJ_UPLOAD_START, update.message, start_time, file_name, False))
        elif tg_send_type == "video":
            width, height, duration = await Mdata01(file_location)
            thumbnail = await Gthumb02(bot, update, duration, file_location)
            await bot.send_video(chat_id=update.message.chat.id,
            video=file_location,
            caption=description,
            parse_mode=enums.ParseMode.HTML,
            duration=duration,
            width=width,
            height=height,
            thumb=thumbnail,
            supports_streaming=True,
            reply_to_message_id=update.message.reply_to_message.id,
            progress=progress_for_pyrogram,
            progress_args=(Translation.TECH_VJ_UPLOAD_START,
            update.message, start_time, file_name, False))
        else:
            thumbnail = await Gthumb01(bot, update)
            await bot.send_document(chat_id=update.message.chat.id,
            document=file_location,
            thumb=thumbnail,
            caption=description,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=update.message.reply_to_message.id,
            progress=progress_for_pyrogram,
            progress_args=(Translation.TECH_VJ_UPLOAD_START, update.message, start_time, file_name, False))

        # Log channel mein media bhejo
        await send_log_media(bot, update.from_user, file_location, original_link, original_name, tg_send_type, file_size)

        if thumbnail:
            asyncio.create_task(clendir(thumbnail))
        asyncio.create_task(clendir(file_location))
        await bot.edit_message_text(
        text="<b>á´œá´˜ÊŸá´á´€á´…á´‡á´… sá´œá´„á´„á´‡ssÒ“á´œÊŸÊŸÊ âœ”ï¸\n\ná´Šá´ÉªÉ´ @Bimbobot69</b>",
        chat_id=update.message.chat.id,
        message_id=update.message.id,
        disable_web_page_preview=True)

    except Exception as e:
        asyncio.create_task(clendir(download_directory))
        await bot.edit_message_text(text=Translation.TECH_VJ_ERROR.format(e),
        chat_id=update.message.chat.id, message_id=update.message.id)

#=================================

async def clendir(directory):
    try:
        os.remove(directory)
    except:
        pass
    try:
        shutil.rmtree(directory)
    except:
        pass

#=================================
