import asyncio
import glob
import os
import random
import logging
from config import OWNER_ID
from pyrogram import filters
from yt_dlp import YoutubeDL

from AsbhaiMusic import app
from AsbhaiMusic.misc import SUDOERS

logger = logging.getLogger(__name__)


def get_random_cookie():
    try:
        folder_path = os.path.join(os.getcwd(), "cookies")
        if not os.path.isdir(folder_path):
            return None
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        return random.choice(txt_files) if txt_files else None
    except Exception:
        return None


async def check_cookies_valid() -> bool:
    cookie_file = get_random_cookie()
    if not cookie_file:
        return False
    try:
        loop = asyncio.get_running_loop()

        def _check():
            opts = {
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_file,
                "simulate": True,
                "skip_download": True,
                "socket_timeout": 10,
            }
            with YoutubeDL(opts) as ydl:
                ydl.extract_info(
                    "https://www.youtube.com/watch?v=LLF3GMfNEYU",
                    download=False
                )
            return True

        result = await asyncio.wait_for(
            loop.run_in_executor(None, _check),
            timeout=20
        )
        return result
    except Exception:
        return False


@app.on_message(
    filters.command(["cookiestatus", "cookies", "cookiescheck"])
    & filters.user(list(OWNER_ID))
)
async def cookie_status_cmd(_, message):
    m = await message.reply_text("🔄 Cookies check kar rahi hun...")
    cookie_file = get_random_cookie()
    if not cookie_file:
        return await m.edit(
            "📂 **Cookies folder empty hai!**\n\n"
            "Bot bina cookies ke bhi kaam karta hai.\n"
            "Nayi cookies daalni ho toh:\n"
            "1. Firefox se YouTube cookies export karo\n"
            "2. `cookies/` folder mein daalo\n"
            "3. Redeploy karo"
        )
    ok = await check_cookies_valid()
    if ok:
        await m.edit(f"✅ **Cookies Valid hain!**\nFile: `{os.path.basename(cookie_file)}`")
    else:
        await m.edit(
            "❌ **Cookies expire ho gayi hain!**\n\n"
            "Bot bina cookies ke bhi try karta hai.\n\n"
            "Nayi cookies daalni hain toh:\n"
            "1. Firefox > youtube.com login karo\n"
            "2. Cookie export karo (Netscape format)\n"
            "3. `cookies/cookies.txt` replace karo\n"
            "4. Redeploy karo"
        )


_startup_done = False

async def startup_cookie_check():
    global _startup_done
    if _startup_done:
        return
    _startup_done = True
    await asyncio.sleep(35)
    # Silently check — koi ERROR log nahi
    cookie_file = get_random_cookie()
    if not cookie_file:
        return
    ok = await check_cookies_valid()
    if ok:
        try:
            for owner_id in OWNER_ID:
                await app.send_message(owner_id, "✅ **YouTube Cookies Valid hain!** Bot ready hai 🎵")
                break
        except Exception:
            pass
