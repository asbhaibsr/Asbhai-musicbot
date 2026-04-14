import asyncio
import glob
import os
import random
import re
from typing import Union

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from yt_dlp import YoutubeDL

import config
from AsbhaiMusic.utils.database import is_on_off
from AsbhaiMusic.utils.formatters import time_to_seconds


# ============================================================
#   COOKIES — Optional, bina cookies ke bhi kaam karta hai
#   Agar cookies/folder mein koi .txt file nahi — None return
#   Agar cookie invalid/expired hai — yt-dlp skip kar deta hai
# ============================================================

def cookies():
    """
    cookies/ folder se random .txt file return karo.
    Nahi mili ya folder nahi — None return karo (crash nahi).
    """
    try:
        folder_path = os.path.join(os.getcwd(), "cookies")
        if not os.path.isdir(folder_path):
            return None
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        if not txt_files:
            return None
        return random.choice(txt_files)
    except Exception:
        return None


def get_ytdl_options(ytdl_opts, commandline=True):
    """
    yt-dlp options mein cookies add karo (agar available ho).
    Cookies nahi hain — original options waise hi return karo.
    """
    cookie_file = cookies()
    if not cookie_file:
        return ytdl_opts

    if commandline:
        if isinstance(ytdl_opts, list):
            return ytdl_opts + ["--cookies", cookie_file]
        elif isinstance(ytdl_opts, str):
            return ytdl_opts + f" --cookies {cookie_file}"
        elif isinstance(ytdl_opts, dict):
            ytdl_opts["cookiefile"] = cookie_file
    else:
        if isinstance(ytdl_opts, dict):
            ytdl_opts["cookiefile"] = cookie_file
    return ytdl_opts


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset: offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        cmd = ["yt-dlp", "-g", "-f", "best[height<=?720][width<=?1280]", link]
        cmd = get_ytdl_options(cmd, commandline=True)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        base_cmd = f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download"
        cookie = cookies()
        if cookie:
            base_cmd += f" --cookies {cookie}"
        base_cmd += f" {link}"
        playlist = await shell_cmd(base_cmd)
        try:
            result = playlist.split("\n")
            result = [k for k in result if k != ""]
        except Exception:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ytdl_opts = get_ytdl_options(ytdl_opts, commandline=False)
        ydl = YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except Exception:
                    continue
                if "dash" not in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except KeyError:
                        continue
                    formats_available.append({
                        "format": format["format"],
                        "filesize": format["filesize"],
                        "format_id": format["format_id"],
                        "ext": format["ext"],
                        "format_note": format["format_note"],
                        "yturl": link,
                    })
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            vidid = link
            link = self.base + link
        else:
            pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=|embed\/|v\/|live_stream\?stream_id=|(?:\/|\?|&)v=)?([^&\n]+)"
            match = re.search(pattern, link)
            vidid = match.group(1) if match else link
        loop = asyncio.get_running_loop()

        def _base_opts():
            opts = {
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            return get_ytdl_options(opts, commandline=False)

        def audio_dl():
            opts = _base_opts()
            opts["format"] = "bestaudio/best"
            opts["outtmpl"] = "downloads/%(id)s.%(ext)s"
            try:
                x = YoutubeDL(opts)
                info = x.extract_info(link, False)
                xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if os.path.exists(xyz):
                    return xyz
                x.download([link])
                return xyz
            except Exception:
                # Cookies se fail — bina cookies ke try karo
                try:
                    opts_no_cookie = {
                        "format": "bestaudio/best",
                        "outtmpl": "downloads/%(id)s.%(ext)s",
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                        "quiet": True,
                        "no_warnings": True,
                    }
                    x = YoutubeDL(opts_no_cookie)
                    info = x.extract_info(link, False)
                    xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                    if os.path.exists(xyz):
                        return xyz
                    x.download([link])
                    return xyz
                except Exception:
                    raise

        def video_dl():
            opts = _base_opts()
            opts["format"] = "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])"
            opts["outtmpl"] = "downloads/%(id)s.%(ext)s"
            try:
                x = YoutubeDL(opts)
                info = x.extract_info(link, False)
                xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if os.path.exists(xyz):
                    return xyz
                x.download([link])
                return xyz
            except Exception:
                # Bina cookies ke try
                opts_no_cookie = {
                    "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                }
                x = YoutubeDL(opts_no_cookie)
                info = x.extract_info(link, False)
                xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if os.path.exists(xyz):
                    return xyz
                x.download([link])
                return xyz

        def song_video_dl():
            opts = _base_opts()
            opts["format"] = f"{format_id}+140"
            opts["outtmpl"] = f"downloads/{title}"
            opts["prefer_ffmpeg"] = True
            opts["merge_output_format"] = "mp4"
            x = YoutubeDL(opts)
            x.download([link])

        def song_audio_dl():
            opts = _base_opts()
            opts["format"] = format_id
            opts["outtmpl"] = f"downloads/{title}.%(ext)s"
            opts["prefer_ffmpeg"] = True
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
            x = YoutubeDL(opts)
            x.download([link])

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4"
        elif songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3"
        elif video:
            if await is_on_off(config.YTDOWNLOADER):
                direct = True
                downloaded_file = await loop.run_in_executor(None, video_dl)
            else:
                cmd = ["yt-dlp", "-g", "-f", "best[height<=?720][width<=?1280]"]
                cmd = get_ytdl_options(cmd, commandline=True)
                cmd.append(link)
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    downloaded_file = stdout.decode().split("\n")[0]
                    direct = None
                else:
                    return
        else:
            direct = True
            downloaded_file = await loop.run_in_executor(None, audio_dl)

        return downloaded_file, direct
