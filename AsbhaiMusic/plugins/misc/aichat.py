import asyncio
import random
import re
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ChatMemberStatus

from AsbhaiMusic import app
from AsbhaiMusic.utils.database import is_aichat_on, set_aichat, save_ai_memory, get_ai_memory
from AsbhaiMusic.misc import SUDOERS

# ============ GALI FILTER ============
GALI_WORDS = [
    "chutiya", "madarchod", "behenchod", "gandu", "randi", "harami",
    "bhosdike", "saala", "kamina", "kutte", "mc", "bc", "bkl", "bsdk",
    "lawde", "lund", "chut", "gaand", "bhosdi", "maa ki", "behen ki"
]

def contains_gali(text: str) -> bool:
    text_lower = text.lower()
    return any(g in text_lower for g in GALI_WORDS)

def get_roast_reply(text: str) -> str:
    roasts = [
        "aye aye aye 😂 itna kuch mat bol apne aap ke baare mein",
        "bhai tune jo kaha wo tere hi baare mein sach hai lol 💀",
        "acha? interesting self-description hai teri 😏",
        "haha tu khud hi janta hai kya hai tu 😂",
        "chill kar bhai, itna gussa 😂 ghar pe sab theek hai na?",
        "oof shant ho ja pehle, chai pi 😂",
        "itni energy hai toh padhai mein laga na 💀",
        "tera dil dukha hai kya? bata kya hua 😂",
    ]
    return random.choice(roasts)

# ============ AI TOGGLE ============

@app.on_message(filters.command(["chataigirl"]) & filters.group)
async def toggle_aichat(_, message: Message):
    if message.from_user.id not in SUDOERS:
        try:
            member = await app.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply_text("❌ Sirf admins use kar sakte hain!")
        except Exception:
            return

    args = message.command
    if len(args) < 2:
        status = await is_aichat_on(message.chat.id)
        state = "🟢 ON" if status else "🔴 OFF"
        return await message.reply_text(
            f"**🤖 AI Chat Girl Status:** {state}\n\n"
            f"Use: `/chataigirl on` ya `/chataigirl off`"
        )

    action = args[1].lower()
    if action == "on":
        await set_aichat(message.chat.id, True)
        await message.reply_text(
            "**🤖 AI Chat Girl ON!** 🎉\n\n"
            "Ab main seedhe messages ka jawab dungi~\n"
            "Typing dikhaungi bhi, ghabra mat! 😊"
        )
    elif action == "off":
        await set_aichat(message.chat.id, False)
        await message.reply_text("**🤖 AI Chat Girl OFF ho gayi!** 😴")
    else:
        await message.reply_text("❌ `/chataigirl on` ya `/chataigirl off` use karo!")


# ============ AI RESPONSE FUNCTION ============

async def get_ai_response(user_text: str) -> str:
    try:
        import g4f
        providers_to_try = [
            g4f.Provider.Blackbox,
            g4f.Provider.DeepInfra,
            g4f.Provider.Gemini,
        ]
        for provider in providers_to_try:
            try:
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda p=provider: g4f.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            provider=p,
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Tu ek Indian girl hai — naam mat batana. "
                                        "Bilkul dost ki tarah hinglish mein baat kar. "
                                        "Kabhi funny, kabhi thoda roast, kabhi chill. "
                                        "Sirf 1-2 lines mein jawab de. "
                                        "Emoji kabhi kabhi use kar. "
                                        "Seedha jawab de, koi intro mat de. "
                                        "You.com ya koi website ka link mat de kabhi bhi. "
                                        "Agar kuch na pata ho to funny tarike se bata."
                                    )
                                },
                                {"role": "user", "content": user_text}
                            ],
                            stream=False,
                        )
                    ),
                    timeout=12
                )
                if isinstance(response, str) and len(response.strip()) > 2:
                    # you.com ya koi link filter karo
                    if "you.com" in response or "http" in response:
                        continue
                    return response.strip()
            except Exception:
                continue
    except Exception:
        pass
    return None


FALLBACK_REPLIES = [
    "haan bhai sun rahi hun 👀",
    "kya hua? 😂",
    "bol kya chahiye tujhe 😏",
    "hmm... soch rahi hun 🤔",
    "yaar seedha bol na 😅",
    "acha? fir kya? 👀",
    "haan haan, interesting 😂",
    "teri baat samajh aayi, bas answer soch rahi hun lol",
]


# ============ PLAIN MESSAGE CHECK ============

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


# ============ GROUP AI HANDLER ============

@app.on_message(filters.group & filters.text & ~filters.bot, group=15)
async def ai_chat_group(_, message: Message):
    try:
        if not await is_aichat_on(message.chat.id):
            return
        if not is_plain_message(message):
            return
        if not message.text or len(message.text.strip()) < 2:
            return

        user_text = message.text.strip()
        user_id = message.from_user.id if message.from_user else 0

        # Gali check
        if contains_gali(user_text):
            await app.send_chat_action(message.chat.id, ChatAction.TYPING)
            await asyncio.sleep(1.5)
            return await message.reply_text(get_roast_reply(user_text))

        # Typing dikhai
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Memory check
        memory_reply = await get_ai_memory(message.chat.id, user_text)
        if memory_reply:
            await asyncio.sleep(1)
            return await message.reply_text(memory_reply)

        # AI response
        reply = await get_ai_response(user_text)
        if not reply:
            reply = random.choice(FALLBACK_REPLIES)

        await save_ai_memory(message.chat.id, user_id, user_text, reply)
        await asyncio.sleep(1)
        await message.reply_text(reply)

    except Exception:
        pass


# ============ PM AI HANDLER ============

@app.on_message(filters.private & filters.text & ~filters.bot, group=15)
async def ai_chat_pm(_, message: Message):
    try:
        if not message.text or message.text.startswith("/"):
            return
        if message.from_user.id in SUDOERS:
            return  # Owner ko PM mein AI nahi chahiye

        user_text = message.text.strip()
        user_id = message.from_user.id

        if contains_gali(user_text):
            await app.send_chat_action(message.chat.id, ChatAction.TYPING)
            await asyncio.sleep(1)
            return await message.reply_text(get_roast_reply(user_text))

        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        memory_reply = await get_ai_memory(user_id, user_text)
        if memory_reply:
            await asyncio.sleep(1)
            return await message.reply_text(memory_reply)

        reply = await get_ai_response(user_text)
        if not reply:
            reply = random.choice(FALLBACK_REPLIES)

        await save_ai_memory(user_id, user_id, user_text, reply)
        await asyncio.sleep(1)
        await message.reply_text(reply)

    except Exception:
        pass


# ============ OWNER WELCOME ============

@app.on_message(filters.group & filters.new_chat_members, group=14)
async def owner_welcome(_, message: Message):
    try:
        from config import OWNER_ID
        for member in message.new_chat_members:
            if member.id in OWNER_ID:
                welcomes = [
                    f"🔥 **OMG OMG OMG!!** Hamare malik aa gaye!! 👑\n\n"
                    f"Jai ho [{member.first_name}](tg://user?id={member.id}) bhaiya ki! 🙏\n"
                    f"Ab toh party hogi! 🎉🎊",

                    f"🚨 **ALERT ALERT!!** Owner aa gaya group mein!!\n\n"
                    f"Sab log savdhan ho jao 😂\n"
                    f"Welcome [{member.first_name}](tg://user?id={member.id}) bhai! 👑🔥",

                    f"👑 **Maalik ka aagman hua hai!!** 🎊\n\n"
                    f"[{member.first_name}](tg://user?id={member.id}) bhai aa gaye!\n"
                    f"Ab toh sab theek ho jayega 😌🔥",
                ]
                await message.reply_text(
                    random.choice(welcomes),
                    disable_web_page_preview=True
                )
                break
    except Exception:
        pass
