# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging
import math
import os
import time
import shutil

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from config import Config
from translation import Translation

async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message,
    start,
    file_name="",
    is_download=False
):
    now = time.time()
    diff = now - start
    
    if round(diff % 10.00) == 0 or current == total or current == 0:
        if total == 0:
            return
        
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        # Progress bar with 20 blocks
        completed_blocks = math.floor(percentage / 5)
        remaining_blocks = 20 - completed_blocks
        progress_bar = "▓" * completed_blocks + "░" * remaining_blocks
        
        # Action emoji
        action_emoji = "⬇️" if is_download else "⬆️"
        action_text = "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ" if is_download else "ᴜᴘʟᴏᴀᴅɪɴɢ"
        
        # Clean filename
        display_name = file_name if file_name else "ᴜɴᴋɴᴏᴡɴ ғɪʟᴇ"
        if len(display_name) > 30:
            display_name = display_name[:27] + "..."

        # Hi-tech progress message
        tmp = f"""╔════════════════════════════════════╗
║ {action_emoji} {action_text}...              ║
╠════════════════════════════════════╣
║ 📁 {display_name}
║
║ {progress_bar} {round(percentage, 2)}%
║
║ 🚀 Speed: {humanbytes(speed)}/s
║ 📦 Size: {humanbytes(current)} / {humanbytes(total)}
║ ⏱ ETA: {estimated_total_time if estimated_total_time else '0 s'}
║ ⏳ Elapsed: {elapsed_time if elapsed_time else '0 s'}
╚════════════════════════════════════╝"""

        try:
            await message.edit(text=tmp)
        except Exception as e:
            logger.error(f"Progress edit error: {e}")
            pass


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]
