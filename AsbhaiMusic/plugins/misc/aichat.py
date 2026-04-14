import asyncio
import random
from pyrogram import filters
from pyrogram.types import Message

from AsbhaiMusic import app
from AsbhaiMusic.utils.database import is_aichat_on, set_aichat, save_ai_memory, get_ai_memory
from AsbhaiMusic.misc import SUDOERS

# ============ AI CHAT TOGGLE ============

@app.on_message(filters.command(["chataigirl"]) & filters.group)
async def toggle_aichat(_, message: Message):
    if message.from_user.id not in SUDOERS:
        if not message.chat.permissions or not message.from_user:
            return
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
        from pyrogram.enums import ChatMemberStatus
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ Sirf admins use kar sakte hain!")

    args = message.command
    if len(args) < 2:
        status = await is_aichat_on(message.chat.id)
        state = "🟢 ON" if status else "🔴 OFF"
        return await message.reply_text(
            f"**🤖 AI Chat Girl Status:** {state}\n\n"
            f"**Use:** `/chataigirl on` ya `/chataigirl off`"
        )

    action = args[1].lower()
    if action == "on":
        await set_aichat(message.chat.id, True)
        await message.reply_text(
            "**🤖 AI Chat Girl ON ho gayi!** 🎉\n\n"
            "Ab main group mein seedhe messages ka jawab dungi~\n"
            "Reply/tag wale messages pe nahi bolungi! 😊"
        )
    elif action == "off":
        await set_aichat(message.chat.id, False)
        await message.reply_text("**🤖 AI Chat Girl OFF ho gayi!** 😴")
    else:
        await message.reply_text("❌ `/chataigirl on` ya `/chataigirl off` use karo!")


# ============ AI RESPONSE ============

def is_plain_message(message: Message) -> bool:
    if message.reply_to_message:
        return False
    if message.entities:
        from pyrogram.enums import MessageEntityType
        for e in message.entities:
            if e.type in [MessageEntityType.MENTION, MessageEntityType.TEXT_MENTION]:
                return False
    if message.text and message.text.startswith("/"):
        return False
    return True


async def get_ai_response(user_text: str, chat_id: int) -> str:
    try:
        import g4f
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: g4f.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Tu ek Indian girl hai — naam nahi batana. "
                                "Bilkul dost ki tarah baat kar — hinglish mein (Hindi + English mix). "
                                "Funny, chill, thoda roast bhi kar kabhi kabhi. "
                                "Chota jawab de — 1-2 lines. Emoji kabhi kabhi use kar. "
                                "Hello/hi ka jawab seedha de, formal mat ho. "
                                "Koi intro mat de — seedha baat kar jaise yaar karta hai."
                            )
                        },
                        {"role": "user", "content": user_text}
                    ],
                    stream=False,
                )
            ),
            timeout=15
        )
        if isinstance(response, str):
            return response.strip()
        return None
    except Exception:
        return None


FALLBACK_REPLIES = [
    "haan bhai sun rahi hun 👀",
    "kya hua? 😂",
    "bol kya chahiye tujhe 😏",
    "hmm... interesting 🤔",
    "yaar seedha bol na 😅",
    "acha? fir? 👀",
    "haan haan sun rahi hun lol",
]


@app.on_message(filters.group & filters.text & ~filters.bot, group=15)
async def ai_chat_handler(_, message: Message):
    try:
        if not await is_aichat_on(message.chat.id):
            return
        if not is_plain_message(message):
            return
        if not message.text or len(message.text.strip()) < 2:
            return

        user_text = message.text.strip()
        user_id = message.from_user.id if message.from_user else 0

        # Pehle memory mein dekho
        memory_reply = await get_ai_memory(message.chat.id, user_text)
        if memory_reply:
            await message.reply_text(memory_reply)
            return

        # AI se lo
        reply = await get_ai_response(user_text, message.chat.id)

        if not reply:
            reply = random.choice(FALLBACK_REPLIES)

        # Memory mein save karo
        await save_ai_memory(message.chat.id, user_id, user_text, reply)
        await message.reply_text(reply)

    except Exception:
        pass
