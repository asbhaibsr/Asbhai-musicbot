import asyncio
import glob
import os
import random
import logging
import json
import time
from typing import Union
from config import OWNER_ID
from pyrogram import filters
from yt_dlp import YoutubeDL

from AsbhaiMusic import app
from AsbhaiMusic.misc import SUDOERS, SPECIAL_ID

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COOKIES_FILE = "cookies/cookies.txt"
_cookie_warning_sent = False  # Sirf ek baar warning bhejo


def init_youtube_token():
    pass  # OAuth removed - cookies use ho rahi hain


def get_random_cookie():
    folder_path = os.path.join(os.getcwd(), "cookies")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return None
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if not txt_files:
        return None
    return random.choice(txt_files)


async def check_cookies(video_url):
    cookie_file = get_random_cookie()
    if not cookie_file:
        return False
    try:
        loop = asyncio.get_running_loop()
        def _check():
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_file,
                "simulate": True,
                "skip_download": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(video_url, download=False)
            return True
        result = await asyncio.wait_for(
            loop.run_in_executor(None, _check),
            timeout=20
        )
        return result
    except Exception as e:
        logger.error(f"Cookie check failed: {e}")
        return False


# Cookie status check - sirf ek baar owner ko bhejo
@app.on_message(filters.command(["cookiestatus", "cookies", "cookiescheck"]) & filters.user(list(OWNER_ID)))
async def cookie_status_cmd(_, message):
    m = await message.reply_text("🔄 Cookies check kar rahi hun...")
    ok = await check_cookies("https://www.youtube.com/watch?v=LLF3GMfNEYU")
    if ok:
        await m.edit("✅ **Cookies Valid hain!** YouTube songs chalenge.")
    else:
        await m.edit(
            "❌ **Cookies expire ho gayi hain!**\n\n"
            "Firefox se nayi cookies export karo aur\n"
            "`cookies/cookies.txt` ko GitHub pe replace karo.\n\n"
            "Phir Koyeb pe redeploy karo."
        )


# Auto cookie check - bot start hone pe - SIRF ONCE
_startup_check_done = False

async def startup_cookie_check():
    global _startup_check_done, _cookie_warning_sent
    if _startup_check_done:
        return
    _startup_check_done = True
    await asyncio.sleep(30)  # Bot start hone do pehle
    ok = await check_cookies("https://www.youtube.com/watch?v=LLF3GMfNEYU")
    if not ok and not _cookie_warning_sent:
        _cookie_warning_sent = True
        try:
            for owner_id in OWNER_ID:
                await app.send_message(
                    owner_id,
                    "⚠️ **YouTube Cookies expire ho gayi hain!**\n\n"
                    "Songs play nahi honge jab tak nayi cookies nahi daloge.\n\n"
                    "**Kya karna hai:**\n"
                    "1. Firefox se youtube.com cookies export karo\n"
                    "2. `cookies/cookies.txt` GitHub pe replace karo\n"
                    "3. Koyeb pe redeploy karo\n\n"
                    "Ya `/cookiestatus` command se check karo."
                )
                break  # Sirf pehle owner ko bhejo
        except Exception:
            pass
