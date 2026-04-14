import asyncio
import importlib
from aiohttp import web
from pyrogram import idle

import config
from config import BANNED_USERS
from AsbhaiMusic import HELPABLE, LOGGER, app, userbot
from AsbhaiMusic.core.call import Champu
from AsbhaiMusic.plugins import ALL_MODULES
from AsbhaiMusic.utils.database import get_banned_users, get_gbanned



async def health_check(request):
    return web.Response(text="OK", status=200)

async def start_health_server():
    app_web = web.Application()
    app_web.router.add_get("/", health_check)
    app_web.router.add_get("/health", health_check)
    runner = web.AppRunner(app_web)
    await runner.setup()
    port = int(__import__("os").getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def init():
    await start_health_server()
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER("AsbhaiMusic").error(
            "ᴀssɪsᴛᴀɴᴛ ᴄʟɪᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs ɴᴏᴛ ᴅᴇғɪɴᴇᴅ, ᴇxɪᴛɪɴɢ..."
        )
        return
    if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
        LOGGER("AsbhaiMusic").warning(
            "ɴᴏ sᴘᴏᴛɪғʏ ᴠᴀʀs ᴅᴇғɪɴᴇᴅ. ʏᴏᴜʀ ʙᴏᴛ ᴡᴏɴ'ᴛ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴘʟᴀʏ sᴘᴏᴛɪғʏ ǫᴜᴇʀɪᴇs..."
        )

    await app.start()
    await userbot.start()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    for all_module in ALL_MODULES:
        imported_module = importlib.import_module(all_module)

        if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
            if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                HELPABLE[imported_module.__MODULE__.lower()] = imported_module
    LOGGER("AsbhaiMusic.plugins").info("sᴜᴄᴄᴇssғᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇs...")

    await Champu.start()
    await Champu.decorators()
    LOGGER("AsbhaiMusic").info("AsbhaiMusic Bot has been successfully started.\n\n@asbhaibsr")
    await idle()


if __name__ == "__main__":
    asyncio.get_event_loop_policy().get_event_loop().run_until_complete(init())
    LOGGER("AsbhaiMusic").info("sᴛᴏᴘᴘɪɴɢ ᴄʜᴀᴍᴘᴜᴍᴜsɪᴄ! ɢᴏᴏᴅʙʏᴇ")
