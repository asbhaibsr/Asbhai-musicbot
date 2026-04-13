import asyncio

from AsbhaiMusic.core.bot import ChampuBot
from AsbhaiMusic.core.dir import dirr
from AsbhaiMusic.core.git import git
from AsbhaiMusic.core.userbot import Userbot
from AsbhaiMusic.misc import dbb, heroku, sudo

from .logging import LOGGER

EMOJIS = ["PPLAY_1", "PPLAY_2", "PPLAY_3", "PPLAY_4", "PPLAY_5",
          "PPLAY_6", "PPLAY_7", "PPLAY_8", "PPLAY_9", "PPLAY_10",
          "PPLAY_11", "PPLAY_12", "PPLAY_13", "PPLAY_14", "PPLAY_15",
          "PPLAY_16", "PPLAY_17"]

dirr()
git()
dbb()
heroku()
sudo()

app = ChampuBot()
userbot = Userbot()

from .platforms import *

YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()
HELPABLE = {}
