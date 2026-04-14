import os
import asyncio
import yt_dlp
from time import time
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import requests
from AsbhaiMusic import app

# Define a dictionary to track the last message timestamp for each user
user_last_message_time = {}
user_command_count = {}

# Define the threshold for command spamming (e.g., 2 commands within 5 seconds)
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

# Path to the cookies file (make sure you have the cookies.txt file in the same directory or provide the full path)
COOKIES_FILE = 'AsbhaiMusic/asbhaibsr/cookies.txt'

# Command to search and download song
@app.on_message(filters.command("song"))
async def download_song(_, message: Message):
    user_id = message.from_user.id
    current_time = time()
    
    # Spam protection: Prevent multiple commands within a short time
    last_message_time = user_last_message_time.get(user_id, 0)
    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(f"{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ")
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time
    
    # Extract query from the message
    query = " ".join(message.command[1:])
    if not query:
        await message.reply("🔗 ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ꜱᴏɴɢ ɴᴀᴍᴇ ᴏʀ ᴜʀʟ ᴛᴏ ꜱᴇᴀʀᴄʜ ꜰᴏʀ 🖇")
        return

    # Searching for the song using YouTubeSearch
    m = await message.reply("🔍ꜱᴇᴀʀᴄʜɪɴɢ...🔎")
    ydl_opts = {
        "format": "bestaudio[ext=m4a]",  # Options to download audio in m4a format
        "noplaylist": True,  # Don't download playlists
        "quiet": True,
        "logtostderr": False,
        "cookiefile": COOKIES_FILE,  # Path to your cookies.txt file
    }

    try:
        # Search for the song
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("😮‍💨 ɴᴏ ʀᴇꜱᴜʟᴛꜱ ꜰᴏᴜɴᴅ. ᴘʟᴇᴀꜱᴇ ᴍᴀᴋᴇ ꜱᴜʀᴇ ʏᴏᴜ ᴛʏᴘᴇᴅ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ꜱᴏɴɢ ɴᴀᴍᴇ ⚠️")
            return

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        
        # Download thumbnail
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        views = results[0]["views"]
        channel_name = results[0]["channel"]

        # Now, download the audio using yt_dlp
        await m.edit("💫 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...💫")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.download([link])

        # Parsing duration (in seconds)
        dur = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(":"))))
        
        # Sending the audio to the user
        await m.edit("😍 ᴜᴘʟᴏᴀᴅɪɴɢ...🎉")
        await message.reply_audio(
            audio_file,
            thumb=thumb_name,
            title=title,
            caption=f"{title}\nʀᴇQᴜᴇꜱᴛᴇᴅ ʙʏ ➪ {message.from_user.mention}\nᴠɪᴇᴡꜱ ➪ {views}\nᴄʜᴀɴɴᴇʟ ➪ {channel_name}",
            duration=dur
        )

        # Cleanup downloaded files
        os.remove(audio_file)
        os.remove(thumb_name)
        await m.delete()

    except Exception as e:
        await m.edit("🙂 ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ! @asbhaibsr ᴘᴍ ")
        print(f"Error: {str(e)}")
