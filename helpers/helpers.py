import logging.handlers
import re
from datetime import datetime, timedelta
from typing import AsyncGenerator

from pyrogram.types import Message

from main import config, userbot

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")

file_handler = logging.handlers.RotatingFileHandler(
    "logs/bot.log", encoding="utf-8", maxBytes=1 * 1024 * 1024, backupCount=2
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


CHANNELS_WITH_TEXT = ("agentstvonews", "novaya_europe", "bbcrussian")
CHANNELS_WITH_CAPTIONS = ("news_sirena", "fontankaspb")


def get_channel_messages(channel_name: str) -> list[Message]:
    """
    Gets messages from channels for the period of time.
    Some messages contain useful info in message.text, others in message.caption
    """
    time_of_oldest_message: datetime = datetime.now() - timedelta(
        minutes=config.time_period
    )
    messages: AsyncGenerator = userbot.get_chat_history(
        channel_name, limit=config.messages_per_channel_limit
    )
    filtered_messages = []
    for message in messages:
        if message.date > time_of_oldest_message:
            if config.debug:
                with open("debug.txt", "a", encoding="utf-8") as file:
                    file.write(f"{message},\n")
            if message.sender_chat.username in CHANNELS_WITH_TEXT and message.text:
                filtered_messages.append(message)
            elif message.sender_chat.username in CHANNELS_WITH_CAPTIONS:
                filtered_messages.append(message)
    return list(reversed(filtered_messages))


def get_headers_from_messages(messages: list[Message]) -> list[tuple[str, str]]:
    """
    Returns first paragraphs of messages and links to them.
    Different channels may have different message structure.
    """
    headers: list[tuple[str, str]] = []
    for message in messages:
        if message.sender_chat.username in CHANNELS_WITH_TEXT and message.text:
            news_message = message.text.split("\n")[0]
            news_link = message.link
            headers.append((news_message, news_link))
        elif message.sender_chat.username in CHANNELS_WITH_CAPTIONS and message.caption:
            news_message = message.caption.split("\n")[0]
            news_link = message.link
            headers.append((news_message, news_link))
    return headers


def message_for_user(data: list[tuple[str, str]]) -> str:
    """
    Creates a final message for user.
    Combines all headers and links to messages into one string.
    Divides message if it is too long.
    Returns a list of strings.
    """
    result = ""
    for tup in data:
        result += f"{tup[0]}\n{tup[1]}\n"
    return result


def digest_filter(messages: list[Message]) -> list[Message]:
    """
    Filters provided messages by the keywords.
    """
    digests: list[Message] = []
    _keywords: re.Pattern = re.compile(
        r"(.*Утро.*Главное.*)"
        r"|#водномпосте"
        r"|Что произошло к утру"
        r"|Что произошло за ночь"
        r"|#Что_происходит"
        r"|Главное за день"
        r"|Главные события дня",
        flags=re.IGNORECASE,
    )
    _digest_channels_with_text: tuple[str, ...] = ("novaya_europe", "fontankaspb")
    _digest_channels_with_captions: tuple[str, ...] = ("news_sirena",)
    for message in messages:
        if message.sender_chat.username in _digest_channels_with_text and message.text:
            if _keywords.search(message.text):
                digests.append(message)
        elif (
            message.sender_chat.username in _digest_channels_with_captions
            and message.caption
        ):
            if _keywords.search(message.caption):
                digests.append(message)
    return digests
