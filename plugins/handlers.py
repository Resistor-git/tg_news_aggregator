import time
import logging
import logging.handlers


from pyrogram import Client, errors, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton

from main import config, userbot
from helpers.helpers import (
    get_channel_messages,
    get_headers_from_messages,
    message_for_user,
    digest_filter,
)

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


button_all_news = KeyboardButton("Все новости за 12 часов")
button_digest = KeyboardButton("Дайджест за 12 часов")
keyboard = ReplyKeyboardMarkup(
    [[button_all_news], [button_digest]], resize_keyboard=True
)


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
        logger.debug("DEBUG MODE")
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


@Client.on_message(filters.command(["digest"]) | filters.regex("Дайджест за 12 часов"))
def digest(client, message):
    """
    Sends digest messages to the client. If there are no digests, sends informational message.
    """
    empty_digest = True
    with userbot:
        for channel in config.channels:
            digests = digest_filter(get_channel_messages(channel))
            if len(digests) > 0:
                empty_digest = False
                for digest_message in digests:
                    if digest_message.text:
                        client.send_message(
                            chat_id=message.chat.id,
                            text=f"{digest_message.text}\n"
                            f"Ссылка на оригинал {digest_message.link}",
                        )
                    elif digest_message.caption:
                        client.send_message(
                            chat_id=message.chat.id,
                            text=f"{digest_message.caption}\n"
                            f"Ссылка на оригинал {digest_message.link}",
                        )
    if empty_digest:
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
