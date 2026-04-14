import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageDeleteForbidden

from AsbhaiMusic import app
from AsbhaiMusic.utils.database import get_removefile, set_removefile, disable_removefile
from AsbhaiMusic.misc import SUDOERS


# ============ REMOVEFILE TOGGLE ============

@app.on_message(filters.command(["removefile"]) & filters.group)
async def removefile_cmd(_, message: Message):
    if message.from_user.id not in SUDOERS:
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ Sirf admins use kar sakte hain!")

    args = message.command
    if len(args) < 2:
        hours = await get_removefile(message.chat.id)
        if hours:
            return await message.reply_text(
                f"**🗑 Auto File Delete:** 🟢 ON\n"
                f"**Time:** {hours} hour(s) baad delete hogi\n\n"
                f"**Off karne ke liye:** `/removefile off`"
            )
        else:
            return await message.reply_text(
                "**🗑 Auto File Delete:** 🔴 OFF\n\n"
                "**On karne ke liye:**\n"
                "`/removefile on 1` — 1 ghante baad\n"
                "`/removefile on 5` — 5 ghante baad"
            )

    action = args[1].lower()

    if action == "off":
        await disable_removefile(message.chat.id)
        return await message.reply_text("**🗑 Auto File Delete OFF ho gayi!** ✅")

    if action == "on":
        try:
            hours = float(args[2]) if len(args) > 2 else 1.0
            if hours <= 0 or hours > 48:
                return await message.reply_text("❌ Time 1 se 48 hours ke beech hona chahiye!")
        except (ValueError, IndexError):
            return await message.reply_text("❌ Use: `/removefile on 1` ya `/removefile on 5`")

        await set_removefile(message.chat.id, hours)
        await message.reply_text(
            f"**🗑 Auto File Delete ON!** ✅\n\n"
            f"Ab is group mein aane wali **videos aur documents** ko\n"
            f"**{hours} hour(s)** baad automatically delete kar dungi! 🗑"
        )
    else:
        await message.reply_text("❌ Use: `/removefile on 1` ya `/removefile off`")


# ============ FILE WATCHER - AUTO DELETE ============

@app.on_message(
    filters.group & (filters.video | filters.document),
    group=16
)
async def auto_delete_file(_, message: Message):
    try:
        hours = await get_removefile(message.chat.id)
        if not hours:
            return

        delay_seconds = int(hours * 3600)

        async def delete_later():
            await asyncio.sleep(delay_seconds)
            try:
                await message.delete()
            except MessageDeleteForbidden:
                pass
            except Exception:
                pass

        asyncio.create_task(delete_later())

    except Exception:
        pass
