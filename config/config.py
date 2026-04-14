import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()


# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID", 29970536))
API_HASH = getenv("API_HASH", "f4bfdcdd4a5c1b7328a7e4f25f024a09")

## Get it from @Botfather in Telegram.
BOT_TOKEN = getenv("BOT_TOKEN")

# Get Your bot username
BOT_USERNAME = getenv("BOT_USERNAME", "AsbhaiMusicBot")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", None)

CLEANMODE_DELETE_MINS = int(
    getenv("CLEANMODE_MINS", 5)
)  # Remember to give value in Seconds

# Custom max audio(music) duration for voice chat. set DURATION_LIMIT in variables with your own time(mins), Default to 60 mins.
DURATION_LIMIT_MIN = int(
    getenv("DURATION_LIMIT", 300)
)  # Remember to give value in Minutes


EXTRA_PLUGINS = getenv("EXTRA_PLUGINS", "False")

# Fill True if you want to load extra plugins
# Fill here the external plugins repo where plugins that you want to load
EXTRA_PLUGINS_REPO = getenv(
    "EXTRA_PLUGINS_REPO",
    "https://github.com/asbhaibsr/Extra-Plugin",
)

# Your folder name in your extra plugins repo where all plugins stored
EXTRA_PLUGINS_FOLDER = getenv("EXTRA_PLUGINS_FOLDER", "plugins")

LOGGERS = "\x54\x68\x65\x54\x65\x6C\x65\x67\x72\x61\x6D\x52\x6F\x62\x6F\x74"  # connect errors api key "Dont change it"
# Duration Limit for downloading Songs in MP3 or MP4 format from bot
SONG_DOWNLOAD_DURATION = int(
    getenv("SONG_DOWNLOAD_DURATION_LIMIT", 1000)
)  # Remember to give value in Minutes

# You'll need a Private Group ID for this.
LOGGER_ID = int(getenv("LOGGER_ID", None))

# Your User ID.
OWNER_ID = list(
    map(int, getenv("OWNER_ID", "7315805581").split())
)  # Input type must be interger

## Fill these variables if you're deploying on heroku.
# Your heroku app name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/asbhaibsr/AsbhaiMusic",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # Fill this variable if your upstream repository is private

# Only  Links formats are  accepted for this Var value.
SUPPORT_CHANNEL = getenv(
    "SUPPORT_CHANNEL", "https://t.me/asbhai_bsr"
)  # Example:- https://t.me/asbhai_bsr
SUPPORT_GROUP = getenv(
    "SUPPORT_GROUP", "https://t.me/aschat_group"
)  # Example:- https://t.me/aschat_group
# Set it in True if you want to leave your assistant after a certain amount of time. [Set time via AUTO_LEAVE_ASSISTANT_TIME]
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "True")

# Time after which you're assistant account will leave chats automatically.
AUTO_LEAVE_ASSISTANT_TIME = int(
    getenv("ASSISTANT_LEAVE_TIME", 1800)
)  # Remember to give value in Seconds

# Set it true if you want your bot to be private only [You'll need to allow CHAT_ID via /authorize command then only your bot will play music in that chat.]
PRIVATE_BOT_MODE = getenv("PRIVATE_BOT_MODE", "False")


# Time sleep duration For Youtube Downloader
YOUTUBE_DOWNLOAD_EDIT_SLEEP = int(getenv("YOUTUBE_EDIT_SLEEP", 3))

# Time sleep duration For Telegram Downloader
TELEGRAM_DOWNLOAD_EDIT_SLEEP = int(getenv("TELEGRAM_EDIT_SLEEP", 5))


# Your Github Repo.. Will be shown on /start Command
GITHUB_REPO = getenv("GITHUB_REPO", "https://github.com/asbhaibsr/AsbhaiMusic")


# Spotify Client.. Get it from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "a29b0b331adf4c428ce3a73a9b20a306")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "e463dede19b04610ad27dc43eb19b56e")

# ========== AI API KEYS ==========
# Groq (Free & Fast) — console.groq.com
GROQ_API_KEY = getenv("GROQ_API_KEY", None)
# Google Gemini (Free) — aistudio.google.com
GEMINI_API_KEY = getenv("GEMINI_API_KEY", None)
# OpenRouter (Free models) — openrouter.ai
OPENROUTER_API_KEY = getenv("OPENROUTER_API_KEY", None)


# Maximum number of video calls allowed on bot. You can later set it via /set_video_limit on telegram
VIDEO_STREAM_LIMIT = int(getenv("VIDEO_STREAM_LIMIT", 999))


# Maximum Limit Allowed for users to save playlists on bot's server
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", 500))

# MaximuM limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 500))


# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))  # Remember to give value in bytes
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 2145386496)) # Remember to give value in bytes

# Chceckout https://www.gbmb.org/mb-to-bytes  for converting mb to bytes


# If you want your bot to setup the commands automatically in the bot's menu set it to true.
SET_CMDS = getenv("SET_CMDS", "False")


# You'll need a Pyrogram String Session for these vars. Generate String from @StringFatherBot or similar
STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)



#   ░█████╗░░██████╗██████╗░██╗  ██╗░░░██╗██████╗░░██████╗██████╗░
#   ██╔══██╗██╔════╝██╔══██╗██║  ██║░░░██║██╔══██╗██╔════╝██╔══██╗
#   ███████║╚█████╗░██████╦╝██║  ██║░░░██║██████╦╝╚█████╗░██████╔╝
#   ██╔══██║░╚═══██╗██╔══██╗██║  ██║░░░██║██╔══██╗░╚═══██╗██╔══██╗
#   ██║░░██║██████╔╝██████╦╝███████╗╚██████╔╝██████╦╝██████╔╝██║░░██║
#   ╚═╝░░╚═╝╚═════╝╚═════╝╚══════╝░╚═════╝╚═════╝╚═════╝╚═╝░░╚═╝
#
#   Owner: @asbhaibsr | Channel: @asbhai_bsr



### DONT TOUCH or EDIT codes after this line
BANNED_USERS = filters.user()
YTDOWNLOADER = 1
LOG = 2
LOG_FILE_NAME = "musiclogs.txt"
TEMP_DB_FOLDER = "tempdb"
adminlist = {}
lyrical = {}
chatstats = {}
votemode = {}
confirmer = {}
userstats = {}
clean = {}

autoclean = []


# Images

START_IMG_URL = getenv(
    "START_IMG_URL",
    "https://telegra.ph/file/d3e855bc548a1ce9649e7.jpg",
)

PING_IMG_URL = getenv(
    "PING_IMG_URL",
    "https://telegra.ph/file/33591be403ae3eaae7217.jpg",
)

PLAYLIST_IMG_URL = getenv(
    "PLAYLIST_IMG_URL",
    "https://telegra.ph/file/b860df3e144c2208a7e5a.jpg",
)

GLOBAL_IMG_URL = getenv(
    "GLOBAL_IMG_URL",
    "https://telegra.ph/file/a9d91437d795b0ae55af8.jpg",
)

STATS_IMG_URL = getenv(
    "STATS_IMG_URL",
    "https://telegra.ph/file/a9d91437d795b0ae55af8.jpg",
)

TELEGRAM_AUDIO_URL = getenv(
    "TELEGRAM_AUDIO_URL",
    "https://telegra.ph/file/84492c50c7a8a8d2603dc.jpg",
)

TELEGRAM_VIDEO_URL = getenv(
    "TELEGRAM_VIDEO_URL",
    "https://telegra.ph/file/84492c50c7a8a8d2603dc.jpg",
)

STREAM_IMG_URL = getenv(
    "STREAM_IMG_URL",
    "https://telegra.ph/file/62f26ca46103beee9a0d5.jpg",
)

SOUNCLOUD_IMG_URL = getenv(
    "SOUNCLOUD_IMG_URL",
    "https://telegra.ph/file/9fbc748ad0d552e403ba6.jpg",
)

YOUTUBE_IMG_URL = getenv(
    "YOUTUBE_IMG_URL",
    "https://telegra.ph/file/2433c1b98d2621623ead3.jpg",
)

SPOTIFY_ARTIST_IMG_URL = getenv(
    "SPOTIFY_ARTIST_IMG_URL",
    "https://telegra.ph/file/38ae0f7b919a8995c7f29.jpg",
)

SPOTIFY_ALBUM_IMG_URL = getenv(
    "SPOTIFY_ALBUM_IMG_URL",
    "https://telegra.ph/file/e17740f22da1fe4162e43.jpg",
)

SPOTIFY_PLAYLIST_IMG_URL = getenv(
    "SPOTIFY_PLAYLIST_IMG_URL",
    "https://telegra.ph/file/010c936d41e9da782780f.jpg",
)


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
SONG_DOWNLOAD_DURATION_LIMIT = int(time_to_seconds(f"{SONG_DOWNLOAD_DURATION}:00"))

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        print(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )


if SUPPORT_GROUP:
    if not re.match("(?:http|https)://", SUPPORT_GROUP):
        print(
            "[ERROR] - Your SUPPORT_GROUP url is wrong. Please ensure that it starts with https://"
        )


if UPSTREAM_REPO:
    if not re.match("(?:http|https)://", UPSTREAM_REPO):
        print(
            "[ERROR] - Your UPSTREAM_REPO url is wrong. Please ensure that it starts with https://"
        )


if GITHUB_REPO:
    if not re.match("(?:http|https)://", GITHUB_REPO):
        print(
            "[ERROR] - Your GITHUB_REPO url is wrong. Please ensure that it starts with https://"
        )
