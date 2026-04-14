from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient

import config

from ..logging import LOGGER

if config.MONGO_DB_URI is None:
    LOGGER(__name__).error(
        "ɴᴏ ᴍᴏɴɢᴏ ᴅʙ ᴜʀʟ ғᴏᴜɴᴅ! ᴘʟᴇᴀsᴇ sᴇᴛ MONGO_DB_URI ɪɴ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs."
    )
    import sys
    sys.exit(1)
else:
    _mongo_async_ = _mongo_client_(config.MONGO_DB_URI)
    _mongo_sync_ = MongoClient(config.MONGO_DB_URI)
    mongodb = _mongo_async_.AsbhaiMusic
    pymongodb = _mongo_sync_.AsbhaiMusic
