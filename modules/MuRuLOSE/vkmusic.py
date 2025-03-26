from typing import Union, Dict
import aiohttp
from aiohttp.client_exceptions import ServerTimeoutError
import logging
import difflib
import re

from telethon.tl.types import Message
from telethon import types
from .. import loader, utils


"""
    ███    ███ ██    ██ ██████  ██    ██ ██       ██████  ███████ ███████
    ████  ████ ██    ██ ██   ██ ██    ██ ██      ██    ██ ██      ██  
    ██ ████ ██ ██    ██ ██████  ██    ██ ██      ██    ██ ███████ █████
    ██  ██  ██ ██    ██ ██   ██ ██    ██ ██      ██    ██      ██ ██  
    ██      ██  ██████  ██   ██  ██████  ███████  ██████  ███████ ███████ 

                                   
    VKMusic
    📜 Licensed under the GNU AGPLv3	
"""

# meta banner: https://0x0.st/HYVT.jpg
# meta desc: desc
# meta developer: @BruhHikkaModules
# requires: aiohttp difflib

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

@loader.tds
class VKMusic(loader.Module):
    strings = {
        "name": "VKMusic",
        "no_music": "Music is not playing (not all music is displayed in the status).",
        "server_error": "Server of VK does not answering",
        "music_form": (
            "<emoji document_id=5222175680652917218>🎵</emoji> <b>Listening now:</b> <code>{title}</code>"
            "\n<emoji document_id=5269537556336222550>🐱</emoji> <b>Artist:</b> <code>{artist}</code>"
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
                lambda: "Telegram bot username for music search (e.g., @vkmusic_bot)",
                validator=loader.validators.String(),
            ),
        )
        self._vkmusic = VKMusicAPI(self.config["user_id"], self.config["token"])

    def _clean_string(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'\(official video\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(lyrics\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(audio\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(live\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(remix\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(feat\..*?\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(russian ver\.?\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(english ver\.?\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(ver\.?\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(version\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(edit\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'russian version', '', text, flags=re.IGNORECASE)
        text = re.sub(r'english version', '', text, flags=re.IGNORECASE)
        text = re.sub(r'—', '-', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _simplify_query(self, query: str) -> str:
        simplified = query
        parts = simplified.split(' x ')
        if len(parts) > 1:
            simplified = ' x '.join(parts[1:])
        return simplified

async def _get_music_from_bot(self, query: str):
    bot_username = self.config["telegram_bot"]
    messages_to_delete = []
    
    try:
        async with self.client.conversation(bot_username, timeout=20) as conv:
            try:
                request = await conv.send_message(query)
                messages_to_delete.append(request)

                try:
                    response = await conv.get_response(timeout=15)
                    messages_to_delete.append(response)
                except (TimeoutError, asyncio.TimeoutError):
                    await conv.send_message("/start")
                    start_response = await conv.get_response(timeout=10)
                    messages_to_delete.append(start_response)
                    
                    request = await conv.send_message(query)
                    messages_to_delete.append(request)
                    response = await conv.get_response(timeout=15)
                    messages_to_delete.append(response)

                selected_document = None
                selected_title = None
                selected_artist = None

                if hasattr(response, 'reply_markup') and response.reply_markup:
                    for row in response.reply_markup.rows:
                        for button in row.buttons:
                            await response.click(button)
                            file_response = await conv.get_response(timeout=15)
                            
                            if file_response.media and isinstance(file_response.media, types.MessageMediaDocument):
                                document = file_response.media.document
                                for attr in document.attributes:
                                    if isinstance(attr, types.DocumentAttributeAudio):
                                        selected_title = attr.title or "Unknown Title"
                                        selected_artist = attr.performer or "Unknown Artist"
                                        selected_document = document
                                        break
                                
                                if selected_document:
                                    break

                if not selected_document and response.media and isinstance(response.media, types.MessageMediaDocument):
                    document = response.media.document
                    for attr in document.attributes:
                        if isinstance(attr, types.DocumentAttributeAudio):
                            selected_title = attr.title or "Unknown Title"
                            selected_artist = attr.performer or "Unknown Artist"
                            selected_document = document

                await self.client.delete_messages(bot_username, messages_to_delete)
                
                return selected_title, selected_artist, selected_document

            except Exception as e:
                logger.error(f"Ошибка при работе с ботом: {e}")
                await self.client.delete_messages(bot_username, messages_to_delete)
                return None, None, None

    except Exception as e:
        logger.error(f"Критическая ошибка соединения с ботом: {e}")
        return None, None, None

    @loader.command(ru_doc=" - Текущая песня")
    async def vkn(self, message: Message):
        """ - Current song"""
        self._vkmusic = VKMusicAPI(str(self.config["user_id"]), str(self.config["token"]))

        music = await self._vkmusic.get_music()

        if music[0] == 50 or music[0] == 40 or music[0] == 30:
            await utils.answer(message, self.strings["bot_searching"])
            query = f"{music[1]['audio']['artist']} - {music[1]['audio']['title']}" if music[0] == 50 else music[1] if music[0] == 40 else "current song"
            query = self._clean_string(query)
            title, artist, document = await self._get_music_from_bot(query)

            if document:
                file_name = f"{artist or 'Unknown'} - {title or 'Unknown'}.mp3".replace("/", "_").replace("\\", "_").replace(":", "_").strip()
                await utils.answer_file(
                    message,
                    file=document,
                    file_name=file_name,
                    caption=self.strings["music_form"].format(
                        title=title or "Unknown",
                        artist=artist or "Unknown"
                    )
                )
            else:
                await utils.answer(message, self.strings["bot_not_found"])
        elif music == 20:
            await utils.answer(message, self.strings["no_music"])
        elif music == 30:
            await utils.answer(message, self.strings["server_error"])

    @loader.command(ru_doc=" - Инструкции для токена и пользовательского идентификатора")
    async def vkt(self, message: Message):
        """- Instructions for token and user ID"""
        await utils.answer(message, self.strings["instructions"])
