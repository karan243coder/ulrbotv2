# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging, requests, urllib.parse, os, time, shutil, asyncio, json, math, aiohttp
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

from config import Config
from pyrogram import filters, enums
from database.access import techvj
from translation import Translation
from database.adduser import AddUser
from pyrogram import Client as Tech_VJ
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from helper_funcs.display_progress import humanbytes
from helper_funcs.help_uploadbot import DownLoadFile
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from utils import verify_user, check_token, check_verification, get_token

# Direct file extensions
DIRECT_FILE_EXTENSIONS = [
    '.mp4', '.mkv', '.mov', '.avi', '.webm', '.flv', '.m4v', '.3gp',
    '.mp3', '.m4a', '.wav', '.flac', '.aac', '.ogg', '.wma',
    '.pdf', '.zip', '.rar', '.7z', '.tar', '.gz', '.apk',
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg',
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt',
    '.exe', '.dmg', '.iso', '.torrent'
]

async def send_log(bot, action, user, link, extra=""):
    """Log channel mein activity bhejega"""
    if Config.TECH_VJ_LOG_CHANNEL and Config.TECH_VJ_LOG_CHANNEL != 0:
        try:
            username = f"@{user.username}" if user.username else "No Username"
            text = f"""<b>📊 New Bot Activity</b>

<b>👤 User:</b> {user.mention} (<code>{user.id}</code>)
<b>🔖 Username:</b> {username}
<b>⚡ Action:</b> {action}
<b>🔗 Link:</b> <code>{link}</code>
{extra}"""
            await bot.send_message(
                chat_id=Config.TECH_VJ_LOG_CHANNEL,
                text=text,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Log channel error: {e}")

async def is_direct_download_url(url):
    """Check karega ki URL direct file link hai ya nahi"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True, timeout=10) as response:
                content_type = response.headers.get('Content-Type', '').lower()
                content_length = response.headers.get('Content-Length')
                
                if any(ct in content_type for ct in [
                    'video/', 'audio/', 'application/octet-stream', 
                    'application/zip', 'application/pdf', 'application/x-rar',
                    'image/', 'application/vnd.android.package-archive'
                ]):
                    return True
                
                parsed_url = urlparse(url)
                path = parsed_url.path.lower()
                if any(path.endswith(ext) for ext in DIRECT_FILE_EXTENSIONS):
                    return True
                
                if content_length and int(content_length) > 1024 * 1024:
                    return True
                    
    except Exception as e:
        logger.warning(f"Direct download check failed: {e}")
        
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()
    if any(path.endswith(ext) for ext in DIRECT_FILE_EXTENSIONS):
        return True
        
    return False

@Tech_VJ.on_message(filters.private & ~filters.via_bot & filters.regex(pattern=".*http.*"))
async def echo(bot, update):
    if not await check_verification(bot, update.from_user.id) and Config.TECH_VJ == True:
        btn = [[
            InlineKeyboardButton("👨‍💻 ᴠᴇʀɪғʏ", url=await get_token(bot, update.from_user.id, f"https://telegram.me/{Config.TECH_VJ_BOT_USERNAME}?start="))
        ],[
            InlineKeyboardButton("🔻 ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ ᴀɴᴅ ᴠᴇʀɪғʏ 🔺", url=f"{Config.TECH_VJ_TUTORIAL}")
        ]]
        await update.reply_text(
            text="<b>ᴅᴜᴇ ᴛᴏ ᴏᴠᴇʀʟᴏᴀᴅ ᴏɴ ʙᴏᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴠᴇʀɪғʏ ғɪʀsᴛ\nᴋɪɴᴅʟʏ ᴠᴇʀɪғʏ ғɪʀsᴛ\n\nɪғ ʏᴏᴜ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ᴛʜᴇɴ ᴛᴀᴘ ᴏɴ ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ ʙᴜᴛᴛᴏɴ ᴛʜᴇɴ sᴇᴇ 60 sᴇᴄᴏɴᴅ ᴠɪᴅᴇᴏ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴠᴇʀɪғʏ ʙᴜᴛᴛᴏɴ ᴀɴᴅ ᴠᴇʀɪғʏ</b>",
            protect_content=True,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return

    await AddUser(bot, update)
    imog = await update.reply_text("**ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴅᴇᴀʀ...⚡**", reply_to_message_id=update.id)

    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None
    url = update.text

    if "|" in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0]
            file_name = url_parts[1]
        elif len(url_parts) == 4:
            url = url_parts[0]
            file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
        else:
            for entity in update.entities:
                if entity.type == "text_link":
                    url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    url = url[o:o + l]
        if url is not None:
            url = url.strip()
        if file_name is not None:
            file_name = file_name.strip()
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()
        logger.info(url)
        logger.info(file_name)
    else:
        for entity in update.entities:
            if entity.type == "text_link":
                url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                url = url[o:o + l]

    # Log channel mein link bhejo
    original_name = file_name if file_name else "Not Set"
    await send_log(bot, "Link Received", update.from_user, url, f"<b>📁 Custom Name:</b> {original_name}")

    # Powerful configuration for yt-dlp
    command_to_exec = [
        "yt-dlp",
        "--no-warnings",
        "--youtube-skip-dash-manifest",
        "--geo-bypass",
        "--add-header", "User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-j",
        url
    ]

    if Config.TECH_VJ_HTTP_PROXY != "":
        command_to_exec.extend(["--proxy", Config.TECH_VJ_HTTP_PROXY])

    # Auto-detect cookies file for protected/age-restricted websites
    if os.path.exists("cookies.txt"):
        command_to_exec.extend(["--cookies", "cookies.txt"])

    if youtube_dl_username is not None:
        command_to_exec.extend(["--username", youtube_dl_username])
    if youtube_dl_password is not None:
        command_to_exec.extend(["--password", youtube_dl_password])

    process = await asyncio.create_subprocess_exec(*command_to_exec,
    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()

    if e_response and "nonnumeric port" not in e_response:
        # Yt-dlp fail ho gaya, direct download try karo
        await imog.edit("**ʏᴛ-ᴅʟᴘ ғᴀɪʟᴇᴅ, ᴄʜᴇᴄᴋɪɴɢ ғᴏʀ ᴅɪʀᴇᴄᴛ ᴅᴏᴡɴʟᴏᴀᴅ...**")
        try:
            is_direct = await is_direct_download_url(url)
            if is_direct:
                inline_keyboard = []
                cb_string_file = "{}={}={}".format("file", "DIRECT", "AUTO")
                cb_string_video = "{}={}={}".format("video", "DIRECT", "AUTO")
                inline_keyboard.append([
                    InlineKeyboardButton("📁 Download File", callback_data=(cb_string_file).encode("UTF-8")),
                    InlineKeyboardButton("🎬 Download as Video", callback_data=(cb_string_video).encode("UTF-8"))
                ])
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                await imog.delete(True)
                await bot.send_message(
                    chat_id=update.chat.id,
                    text="**ᴅɪʀᴇᴄᴛ ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ ✅**\n\nᴄʜᴏᴏsᴇ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʏᴘᴇ:",
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML,
                    reply_to_message_id=update.id
                )
                return
        except Exception as e:
            logger.error(f"Direct download check error: {e}")
        
        error_message = e_response.replace(Translation.TECH_VJ_ERROR_YTDLP, "")
        if "This video is only available for registered users." in error_message or "Sign in" in error_message:
            error_message = Translation.TECH_VJ_SET_CUSTOM_USERNAME_PASSWORD
        else:
            # Show the actual error to the user instead of a generic text
            actual_error = error_message.split('\n')[0][:200]
            error_message = f"sᴀɪᴅ ɪɴᴠᴀʟɪᴅ ᴜʀʟ 🚸\n\n**Reason:** `{actual_error}`\n*(If it needs a login, add cookies.txt to your bot files)*"
            
        await bot.send_message(chat_id=update.chat.id,
        text=Translation.TECH_VJ_NO_VOID_FORMAT_FOUND.format(str(error_message)),
        disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML,
        reply_to_message_id=update.id)
        await imog.delete(True)
        return False

    if t_response:
        x_reponse = t_response
        if "\n" in x_reponse:
            x_reponse, _ = x_reponse.split("\n")
        response_json = json.loads(x_reponse)
        save_ytdl_json_path = Config.TECH_VJ_DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)

        inline_keyboard = []
        duration = None
        if "duration" in response_json:
            duration = response_json["duration"]

        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                if format_string is None:
                    format_string = formats.get("format")
                format_ext = formats.get("ext")
                approx_file_size = ""
                if "filesize" in formats:
                    approx_file_size = humanbytes(formats["filesize"])
                cb_string_video = "{}|{}|{}".format(
                    "video", format_id, format_ext)
                cb_string_file = "{}|{}|{}".format(
                    "file", format_id, format_ext)
                if format_string is not None and not "audio only" in format_string:
                    ikeyboard = [
                        InlineKeyboardButton(
                            "S " + format_string + " video " + approx_file_size + " ",
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        InlineKeyboardButton(
                            "D " + format_ext + " " + approx_file_size + " ",
                            callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                else:
                    ikeyboard = [
                        InlineKeyboardButton(
                            "SVideo [" +
                            "] ( " +
                            approx_file_size + " )",
                            callback_data=(cb_string_video).encode("UTF-8")
                        ),
                        InlineKeyboardButton(
                            "DFile [" +
                            "] ( " +
                            approx_file_size + " )",
                            callback_data=(cb_string_file).encode("UTF-8")
                        )
                    ]
                inline_keyboard.append(ikeyboard)

            if duration is not None:
                cb_string_64 = "{}|{}|{}".format("audio", "64k", "mp3")
                cb_string_128 = "{}|{}|{}".format("audio", "128k", "mp3")
                cb_string = "{}|{}|{}".format("audio", "320k", "mp3")
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "MP3 " + "(" + "64 kbps" + ")", callback_data=cb_string_64.encode("UTF-8")),
                    InlineKeyboardButton(
                        "MP3 " + "(" + "128 kbps" + ")", callback_data=cb_string_128.encode("UTF-8"))
                ])
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "MP3 " + "(" + "320 kbps" + ")", callback_data=cb_string.encode("UTF-8"))
                ])

        else:
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_file = "{}|{}|{}".format(
                "file", format_id, format_ext)
            cb_string_video = "{}|{}|{}".format(
                "video", format_id, format_ext)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "SVideo",
                    callback_data=(cb_string_video).encode("UTF-8")
                ),
                InlineKeyboardButton(
                    "DFile",
                    callback_data=(cb_string_file).encode("UTF-8")
                )
            ])

        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await imog.delete(True)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.TECH_VJ_FORMAT_SELECTION + "\n" + Translation.TECH_VJ_SET_CUSTOM_USERNAME_PASSWORD,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=update.id
        )

    else:
        # Yt-dlp response nahi aaya, direct download try karo
        await imog.edit("**ɴᴏ ғᴏʀᴍᴀᴛ ғᴏᴜɴᴅ, ᴄʜᴇᴄᴋɪɴɢ ғᴏʀ ᴅɪʀᴇᴄᴛ ᴅᴏᴡɴʟᴏᴀᴅ...**")
        try:
            is_direct = await is_direct_download_url(url)
            if is_direct:
                inline_keyboard = []
                cb_string_file = "{}={}={}".format("file", "DIRECT", "AUTO")
                cb_string_video = "{}={}={}".format("video", "DIRECT", "AUTO")
                inline_keyboard.append([
                    InlineKeyboardButton("📁 Download File", callback_data=(cb_string_file).encode("UTF-8")),
                    InlineKeyboardButton("🎬 Download as Video", callback_data=(cb_string_video).encode("UTF-8"))
                ])
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                await imog.delete(True)
                await bot.send_message(
                    chat_id=update.chat.id,
                    text="**ᴅɪʀᴇᴄᴛ ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ ✅**\n\nᴄʜᴏᴏsᴇ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʏᴘᴇ:",
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML,
                    reply_to_message_id=update.id
                )
                return
        except Exception as e:
            logger.error(f"Direct download check error: {e}")

        inline_keyboard = []
        cb_string_file = "{}={}={}".format(
            "file", "LFO", "NONE")
        cb_string_video = "{}={}={}".format(
            "video", "OFL", "ENON")
        inline_keyboard.append([
            InlineKeyboardButton(
                "SVideo",
                callback_data=(cb_string_video).encode("UTF-8")
            ),
            InlineKeyboardButton(
                "DFile",
                callback_data=(cb_string_file).encode("UTF-8")
            )
        ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await imog.delete(True)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.TECH_VJ_FORMAT_SELECTION,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=update.id
        )
