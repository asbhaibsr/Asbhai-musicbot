import asyncio
import random
import os
import aiohttp
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ChatMemberStatus

from AsbhaiMusic import app
from AsbhaiMusic.utils.database import is_aichat_on, set_aichat, save_ai_memory, get_ai_memory
from AsbhaiMusic.misc import SUDOERS

# ============ GALI FILTER ============
GALI_WORDS = [
    "chutiya", "madarchod", "behenchod", "gandu", "randi", "harami",
    "bhosdike", "kamina", "kutte", "mc", "bc", "bkl", "bsdk",
    "lawde", "lund", "chut", "gaand", "bhosdi", "maa ki", "behen ki"
]

ROAST_REPLIES = [
    "aye aye 😂 itna kuch mat bol apne baare mein",
    "bhai ye toh teri hi description hai lol 💀",
    "acha? interesting self-roast hai tera 😏",
    "haha tu khud hi janta hai kya hai tu 😂",
    "chill kar yaar, chai pi pehle ☕😂",
    "itni energy hai toh padhai mein laga na 💀",
    "oof shant! ghar pe sab theek hai na? 😂",
    "tera dil dukha hai kya bhai? 😂 bata kya hua",
]

FALLBACK_REPLIES = [
    "haan bhai sun rahi hun 👀",
    "kya hua? 😂",
    "bol kya chahiye tujhe 😏",
    "hmm soch rahi hun 🤔",
    "yaar seedha bol na 😅",
    "acha? fir kya? 👀",
    "haan haan interesting 😂",
    "samajh gayi bas 😌",
    "kya scene hai bhai 😂",
    "teri baat sun li 👂",
]

SYSTEM_PROMPT = (
    "Tu ek Indian girl hai. Apna naam mat batana. "
    "Hinglish mein baat kar — Hindi aur English mix. "
    "Bilkul close friend ki tarah — chill, funny, kabhi kabhi thoda roast. "
    "Sirf 1-2 choti lines mein jawab de. "
    "Kabhi kabhi emoji use kar. "
    "Koi website link mat de. Koi intro mat de jaise 'main hu' wala. "
    "Seedha jawab de jaise yaar karta hai. "
    "Agar kuch na pata ho to funny tarike se bata."
)

def contains_gali(text: str) -> bool:
    t = text.lower()
    return any(g in t for g in GALI_WORDS)

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

def is_bad_response(text: str) -> bool:
    bad = ["you.com", "pricing", "please log", "sign in", "login to", "http://", "https://", "subscribe"]
    return any(b in text.lower() for b in bad)


# ============ AI RESPONSE - GROQ PRIMARY ============

async def get_groq_response(user_text: str) -> str:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "max_tokens": 150,
                "temperature": 0.9,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"].strip()
                    if not is_bad_response(reply):
                        return reply[:300]
    except Exception:
        pass
    return None


# ============ AI RESPONSE - G4F FALLBACK ============

async def get_g4f_response(user_text: str) -> str:
    try:
        import g4f
        from g4f.Provider import (
            AItianhu, AiChatting, AiService, Aibn, Ails,
            Aivvm, Berlin, ChatAiGpt, ChatForAi, Cromicle,
            EasyChat, FreeChatgpt, GPTalk, GeekGpt, Gpt6,
            GptChatly, GptTalkRu, OnlineGpt, Opchatgpts,
            TalkAi, Theb, V50, Vitalentum, Wewordle, Wuguokai
        )

        providers = [
            AItianhu, AiChatting, Aibn, Ails, Aivvm,
            Berlin, ChatAiGpt, ChatForAi, Cromicle,
            EasyChat, FreeChatgpt, GPTalk, GeekGpt, Gpt6,
            GptChatly, GptTalkRu, OnlineGpt, Opchatgpts,
            TalkAi, Theb, V50, Vitalentum, Wewordle, Wuguokai
        ]
        random.shuffle(providers)

        for provider in providers[:6]:  # 6 try karo
            try:
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda p=provider: g4f.ChatCompletion.create(
                            model=g4f.models.gpt_35_turbo,
                            provider=p,
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": user_text}
                            ],
                            stream=False,
                        )
                    ),
                    timeout=10
                )
                if isinstance(response, str) and len(response.strip()) > 2:
                    if not is_bad_response(response):
                        return response.strip()[:300]
            except Exception:
                continue
    except Exception:
        pass
    return None


async def get_ai_response(user_text: str) -> str:
    # Pehle Groq try karo (agar API key ho)
    reply = await get_groq_response(user_text)
    if reply:
        return reply
    # Phir g4f try karo
    reply = await get_g4f_response(user_text)
    if reply:
        return reply
    return None


# ============ AI TOGGLE COMMAND ============

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
        groq_status = "✅ Set hai" if os.getenv("GROQ_API_KEY") else "❌ Set nahi (g4f use hogi)"
        return await message.reply_text(
            f"**🤖 AI Chat Girl:** {'🟢 ON' if status else '🔴 OFF'}\n"
            f"**Groq API:** {groq_status}\n\n"
            f"`/chataigirl on` ya `/chataigirl off`"
        )

    action = args[1].lower()
    if action == "on":
        await set_aichat(message.chat.id, True)
        await message.reply_text(
            "**🤖 AI Chat Girl ON!** 🎉\n"
            "Seedhe messages ka jawab dungi, typing bhi dikhaungi~ 😊"
        )
    elif action == "off":
        await set_aichat(message.chat.id, False)
        await message.reply_text("**🤖 AI Chat Girl OFF!** 😴")
    else:
        await message.reply_text("❌ `/chataigirl on` ya `/chataigirl off`")


# ============ GROUP HANDLER ============

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

        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        if contains_gali(user_text):
            await asyncio.sleep(1)
            return await message.reply_text(random.choice(ROAST_REPLIES))

        # Memory check
        memory_reply = await get_ai_memory(message.chat.id, user_text)
        if memory_reply:
            await asyncio.sleep(1.5)
            return await message.reply_text(memory_reply)

        reply = await get_ai_response(user_text)
        if not reply:
            reply = random.choice(FALLBACK_REPLIES)

        await save_ai_memory(message.chat.id, user_id, user_text, reply)
        await asyncio.sleep(1)
        await message.reply_text(reply)

    except Exception:
        pass


# ============ PM HANDLER ============

@app.on_message(filters.private & filters.text & ~filters.bot, group=15)
async def ai_chat_pm(_, message: Message):
    try:
        if not message.text or message.text.startswith("/"):
            return
        if message.from_user.id in SUDOERS:
            return

        user_text = message.text.strip()
        user_id = message.from_user.id

        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        if contains_gali(user_text):
            await asyncio.sleep(1)
            return await message.reply_text(random.choice(ROAST_REPLIES))

        memory_reply = await get_ai_memory(user_id, user_text)
        if memory_reply:
            await asyncio.sleep(1.5)
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
                    f"🔥 **OMG OMG!!** Hamare malik aa gaye!! 👑\n\nJai ho [{member.first_name}](tg://user?id={member.id}) bhaiya ki! 🙏\nAb toh party hogi! 🎉",
                    f"🚨 **ALERT!!** Owner aa gaya group mein!!\nSab savdhan ho jao 😂\nWelcome [{member.first_name}](tg://user?id={member.id}) bhai! 👑🔥",
                    f"👑 **Maalik ka aagman hua hai!!** 🎊\n[{member.first_name}](tg://user?id={member.id}) bhai aa gaye!\nAb sab theek ho jayega 😌🔥",
                    f"🎺 Dhol bajao!! [{member.first_name}](tg://user?id={member.id}) bhai aa gaye!! 🥳\nGroup mein raunak aa gayi! 🔥",
                ]
                await message.reply_text(
                    random.choice(welcomes),
                    disable_web_page_preview=True
                )
                break
    except Exception:
        pass
