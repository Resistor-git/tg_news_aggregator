import asyncio
import textwrap
import time
import logging
import logging.handlers
from datetime import datetime, timedelta
from typing import AsyncGenerator

from pyrogram import Client, errors, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from bot_pyrogram import config, userbot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")

file_handler = logging.handlers.RotatingFileHandler(
    "logs/bot.log", encoding="utf-8", maxBytes=1 * 1024 * 1024, backupCount=2
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

CHANNELS_WITH_TEXT = ("agentstvonews", "novaya_europe", "bbcrussian")
CHANNELS_WITH_CAPTIONS = ("news_sirena", "fontankaspb")

button_all_news = KeyboardButton("Все новости за 12 часов")
button_digest = KeyboardButton("Дайджест за 12 часов")
keyboard = ReplyKeyboardMarkup(
    [[button_all_news], [button_digest]], resize_keyboard=True
)


def get_channel_messages(channel_name: str) -> list[Message]:
    """
    Gets messages from channels for the period of time.
    Some messages contain useful info in message.text, others in message.caption
    """
    _time_of_oldest_message: datetime = datetime.now() - timedelta(
        minutes=config.time_period
    )
    messages: AsyncGenerator = userbot.get_chat_history(
        channel_name, limit=config.messages_per_channel_limit
    )
    filtered_messages = []

    for message in messages:
        if message.date > _time_of_oldest_message:
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


def split_long_string(text: str, length=config.max_message_length) -> list[str]:
    """
    Splits long message into smaller.
    Does not preserve newline characters!!!
    NOT USED IN THE CURRENT VERSION OF CODE
    """
    return textwrap.wrap(text=text, width=length)


@Client.on_message(filters.command(["start"]))
def start_command(client, message):
    client.send_message(
        chat_id=message.chat.id,
        text="Кнопки ниже позволяют прочитать все новости за 12 ч. или только выжимку из некоторых каналов.",
        reply_markup=keyboard,
    )


@Client.on_message(
    filters.command(["all_news"]) | filters.regex("Все новости за 12 часов")
)
def all_news(client, message):
    news: str = ""
    with userbot:
        for channel in config.channels:
            news += f"{message_for_user(get_headers_from_messages(get_channel_messages(channel)))}\n"
    if config.debug:
        print("DEBUG MODE")
        print(news)
        client.send_message(
            chat_id=message.chat.id,
            text="Прямо сейчас бот обновляется и поэтому не работает. "
            "Пожалуйста, подождите. Если бот недоступен уже несколько часов, "
            "сообщите об этом разработчику.",
        )
        return
    try:
        client.send_message(chat_id=message.chat.id, text=news)
    except errors.MessageTooLong:
        logger.debug("long message")
        number_of_messages = (len(news) // config.max_message_length) + 1
        start = 0
        end = config.max_message_length
        for _ in range(number_of_messages):
            client.send_message(chat_id=message.chat.id, text=news[start:end])
            start += config.max_message_length
            end += config.max_message_length
            time.sleep(1)
    except errors.MessageEmpty:
        client.send_message(
            chat_id=message.chat.id, text="Извините, что-то пошло не так."
        )
        if config.admin_chat_id:
            client.send_message(
                chat_id=config.admin_chat_id,
                text=f"Возникла ошибка: MessageEmpty"
                f"Запрос пользователя:"
                f"{message}",
            )
    logger.info(
        f"Пользователь {message.from_user.username} воспользовался получением заголовков."
    )


def digest_filter(messages: list[Message]) -> list[Message]:
    """
    Filters provided messages by the keywords.
    """
    digests: list[Message] = []
    _keywords = (
        "#водномпосте",
        "Что произошло к утру",
        "Что произошло за ночь",
        "#Что_происходит",
        "Главное за день",
        "Главные события дня",
        "Главное за выходные",
    )
    _digest_channels_with_text = ("novaya_europe", "fontankaspb")
    _digest_channels_with_captions = ("news_sirena",)
    for message in messages:
        if message.sender_chat.username in _digest_channels_with_text and message.text:
            for keyword in _keywords:
                if keyword in message.text:
                    digests.append(message)
        elif (
            message.sender_chat.username in _digest_channels_with_captions
            and message.caption
        ):
            for keyword in _keywords:
                if keyword in message.caption:
                    digests.append(message)
    return digests


@Client.on_message(filters.command(["digest"]) | filters.regex("Дайджест за 12 часов"))
def digest(client, message):
    """
    Sends digest messages to the client. If there are no digests, sends informational message.
    """
    _empty_digest = True
    with userbot:
        for channel in config.channels:
            digests = digest_filter(get_channel_messages(channel))
            if len(digests) > 0:
                _empty_digest = False
                for digest_message in digests:
                    client.send_message(
                        chat_id=message.chat.id,
                        text=f"{digest_message.caption}\n"
                        f"Ссылка на оригинал {digest_message.link}",
                    )
    if _empty_digest:
        client.send_message(
            chat_id=message.chat.id,
            text="К сожалению, дайджесты за последнее время не найдены. Вероятно, их ещё не опубликовали.",
        )
    logger.info(f"Пользователь {message.from_user.username} воспользовался дайджестом.")


@Client.on_message(filters.command(["help"]))
def help_command(client, message):
    client.send_message(
        chat_id=message.chat.id,
        text="/start - Начать работу с ботом (обновить кнопки)\n"
        "/all_news - Все новости за 12 часов\n"
        "/digest - Дайджест за 12 часов из избранных источников\n"
        "/help - Справка/помощь",
    )
