# ---------------------------------------------------------------------------------
#  /\_/\  🌐 This module was loaded through https://t.me/hikkamods_bot
# ( o.o )  🔐 Licensed under the GNU AGPLv3.
#  > ^ <   ⚠️ Owner of heta.hikariatama.ru doesn't take any responsibilities or intellectual property rights regarding this script
# ---------------------------------------------------------------------------------
# Name: VKMusic
# Description: vk music now
# Author: BHikkaModules    
# Commands:
# .vkmpnow | .vkmtoken
# ---------------------------------------------------------------------------------


__version__ = (1, 0, 0)

# module by: @BruhHikkaModules, modification: @kdevwp
#   you can edit this module
#            2022 - 2025
# 🔒 Licensed under the AGPL-3.0
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @BruhHikkaModules, @kdevwp

from typing import Union, Dict
import aiohttp
from aiohttp.client_exceptions import ServerTimeoutError
import logging
from telethon.tl.types import Message
from telethon import types
from .. import loader, utils
from telethon.utils import get_display_name

logger = logging.getLogger(__name__)

class VKMusicAPI:
    def __init__(self, user_id: str, token: str) -> Union[Dict, int]:
        self.token = token
        self.user_id = user_id

    async def get_music(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api.vk.com/method/status.get?user_id={self.user_id}&access_token={self.token}&v=5.199"
                ) as response:
                    data: dict = await response.json()
                    if data['response'].get('audio') is not None:
                        return 50, data['response']
                    else:
                        return 40, data['response']['text']
        except ServerTimeoutError:
            return 30
            
    async def get_current_position(self, owner_id, audio_id):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api.vk.com/method/audio.getById?audios={owner_id}_{audio_id}&access_token={self.token}&v=5.199"
                ) as response:
                    data: dict = await response.json()
                    if 'response' in data and len(data['response']) > 0:
                        return data['response'][0].get('progress', 0)
                    return 0
        except Exception as e:
            logger.error(f"Error getting current position: {e}")
            return 0

@loader.tds
class VKMusic(loader.Module):
    strings = {
        "name": "VKMusic",
        "no_music": "Music is not playing (not all music is displayed in the status).",
        "server_error": "Server of VK does not answering",
        "music_form": (
            "<emoji document_id=5222175680652917218>🎵</emoji> <b>Listening now:</b> <code>{title}</code>"
            "\n<emoji document_id=5269537556336222550>🐱</emoji> <b>Artist:</b> <code>{artist}</code>"
            "\n<emoji document_id=5328274090262275771>🕓</emoji> <b>Duration:</b> <code>{current_time} | {total_time}</code>"
        ),
        "instructions": (
            "<b>Go to <a href='https://vkhost.github.io/'>vkhost</a>, open settings, leave anytime access and status,"
            "and click get, copy the token and id, and then paste it in properly (in config).</b>"
        ),
        "not_russia": (
            "\n<emoji document_id=5303281542422865331>🇷🇺</emoji> VK gave not all information about" 
            "the track because your userbot server is outside the Russian Federation."
        ),
        "bot_searching": "Searching via Telegram bot...",
        "bot_not_found": "Music not found via Telegram bot.",
        "bot_start": "Bot requires /start, initializing..."
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "token",
                "token",
                lambda: "How get token: .vkmtoken",
                validator=loader.validators.Hidden(loader.validators.String()),
            ),
            loader.ConfigValue(
                "user_id",
                "1278631",
                lambda: "Here your userid, (about this in .vkmtoken)",
                validator=loader.validators.Hidden(loader.validators.String()),
            ),
            loader.ConfigValue(
                "telegram_bot",
                "@vkm_bot",
                lambda: "Telegram bot username for music search (e.g., @vkm_bot)",
                validator=loader.validators.String(),
            ),
        )
        self._vkmusic = VKMusicAPI(self.config["user_id"], self.config["token"])

    def format_time(self, seconds):
        """Форматирует время в секундах в формат MM:SS"""
        if not seconds:
            seconds = 0
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}:{remaining_seconds:02d}"

    async def _get_music_from_bot(self, query: str):
        bot_username = self.config["telegram_bot"]
        messages_to_delete = []
        
        async with self.client.conversation(bot_username) as conv:
            request = await conv.send_message(query)
            messages_to_delete.append(request)

            try:
                response = await conv.get_response(timeout=10)
                messages_to_delete.append(response)
            except TimeoutError:
                await conv.send_message("/start")
                messages_to_delete.append(await conv.get_response(timeout=5))
                await conv.send_message(query)
                messages_to_delete.append(await conv.get_response(timeout=10))
                response = messages_to_delete[-1]

            if response.reply_markup and hasattr(response.reply_markup, "rows"):
                music_response = await response.click(0)
                file_response = await conv.get_response(timeout=10)
                messages_to_delete.append(file_response)
            else:
                file_response = response

            if file_response.media and isinstance(file_response.media, types.MessageMediaDocument):
                document = file_response.media.document
                duration = 0
                for attr in document.attributes:
                    if isinstance(attr, types.DocumentAttributeAudio):
                        title = attr.title or "Unknown Title"
                        artist = attr.performer or "Unknown Artist"
                        duration = attr.duration or 0
                        await self.client.delete_messages(bot_username, messages_to_delete)
                        return title, artist, document, duration
                await self.client.delete_messages(bot_username, messages_to_delete)
                return None, None, document, 0
            await self.client.delete_messages(bot_username, messages_to_delete)
            return None, None, None, 0

    @loader.command(ru_doc=" - Текущая песня")
    async def vkmpnow(self, message: Message):
        "– Инструкция по получению токена."
        self._vkmusic = VKMusicAPI(str(self.config["user_id"]), str(self.config["token"]))

        music = await self._vkmusic.get_music()

        if music[0] == 50:
            title = music[1]['audio']["title"]
            artist = music[1]['audio']["artist"]
            url = music[1]['audio']["url"]
            
            duration = music[1]['audio'].get("duration", 0)
            
            owner_id = music[1]['audio'].get("owner_id")
            audio_id = music[1]['audio'].get("id")
            
            if owner_id and audio_id:
                current_position = await self._vkmusic.get_current_position(owner_id, audio_id)
            else:
                current_position = music[1]['audio'].get("progress", 0)
            
            total_time = self.format_time(duration)
            current_time = self.format_time(current_position)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        audio_data = await resp.read()
                        file_name = f"{artist} - {title}.mp3".replace("/", "_").replace("\\", "_")
                        await utils.answer_file(
                            message,
                            file=audio_data,
                            file_name=file_name,
                            caption=self.strings["music_form"].format(
                                title=title, 
                                artist=artist,
                                current_time=current_time,
                                total_time=total_time
                            )
                        )
                    else:
                        await utils.answer(message, self.strings["server_error"])
        elif music[0] == 40 or music[0] == 30:
            await utils.answer(message, self.strings["bot_searching"])
            query = music[1] if music[0] == 40 else "current song"
            title, artist, document, duration = await self._get_music_from_bot(query)

            if document:
                total_time = self.format_time(duration)
                current_time = "0:00"
                
                file_name = f"{artist or 'Unknown'} - {title or 'Unknown'}.mp3".replace("/", "_").replace("\\", "_")
                await utils.answer_file(
                    message,
                    file=document,
                    file_name=file_name,
                    caption=self.strings["music_form"].format(
                        title=title or "Unknown",
                        artist=artist or "Unknown",
                        current_time=current_time,
                        total_time=total_time
                    )
                )
            else:
                await utils.answer(message, self.strings["bot_not_found"])
        elif music == 20:
            await utils.answer(message, self.strings["no_music"])
        elif music == 30:
            await utils.answer(message, self.strings["server_error"])

    @loader.command(ru_doc=" - Инструкции для токена и пользовательского идентификатора")
    async def vkmtoken(self, message: Message):
        "– Инструкция по получению токена."
        await utils.answer(message, self.strings["instructions"])
