# todo
# асинхронность 
# логи
# заменить названия каналов на id
# запилить debug режим
# BUG: разрывается ссылка при делении сообщений

import asyncio
import textwrap
import time
from datetime import datetime, timedelta
from typing import AsyncGenerator

from pyrogram import Client, errors, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config_data.config import Config, load_config

config: Config = load_config()

userbot = Client(
    'my_userbot',
    config.tg_userbot.api_id,
    config.tg_userbot.api_hash,
    no_updates=True
)

bot = Client(
    'my_bot',
    config.tg_bot.api_id,
    config.tg_bot.api_hash,
    config.tg_bot.bot_token
)

button_all_news_24 = KeyboardButton('Все новости за 24 часа')
button_digest_24 = KeyboardButton('Дайджест за 24 часа')
keyboard = ReplyKeyboardMarkup(
            [[button_all_news_24], [button_digest_24]],
            resize_keyboard=True
)


def get_channel_messages(channel_name: str) -> list[Message]:
    """
    Gets messages from channels for the period of time.
    """
    _time_of_oldest_message: datetime = datetime.now() - timedelta(minutes=config.time_period)
    messages: AsyncGenerator = userbot.get_chat_history(channel_name, limit=config.messages_per_channel_limit)
    filtered_messages = []

    # if config.debug:
    #     for message in messages:
    #         print(message)

    for message in messages:
        if message.date > _time_of_oldest_message:
            if message.sender_chat.username in (
                    'agentstvonews',
                    'novaya_europe',
                    'bbcrussian'
            ) and message.text:
                filtered_messages.append(message)
            elif (message.sender_chat.username in (
                    'news_sirena',
                    'fontankaspb') and
                  message.caption):
                filtered_messages.append(message)
    return list(reversed(filtered_messages))


def get_data_from_messages(messages: list) -> list[tuple[str, str]]:
    """
    Returns first paragraphs of messages and links to them.
    Different channels may have different message structure.
    """
    headers: list[tuple[str, str]] = []
    for message in messages:
        if message.sender_chat.username == 'echoonline_news':
            news_message = message.text.split('\n')[0]
            news_link = message.link
            headers.append((news_message, news_link))
        elif message.sender_chat.username in ('svtvnews', 'news_sirena', 'fontankaspb'):
            news_message = message.caption.split('\n')[0]
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
    result = ''
    for tup in data:
        result += f'{tup[0]}\n{tup[1]}\n'
    return result


def split_long_string(text: str, length=config.max_message_length) -> list[str]:
    """
    Splits long message into smaller.
    Does not preserve newline characters!!!
    NOT USED IN THE CURRENT VERSION OF CODE
    """
    return textwrap.wrap(text=text, width=length)


@bot.on_message(filters.command(['start']))
def start_command(client, message):
    bot.send_message(
        chat_id=message.chat.id,
        text='Кнопки ниже позволяют прочитать все новости за 24 ч. или только выжимку из некоторых каналов.',
        reply_markup=keyboard
        )


@bot.on_message(filters.command(['all_news_24']) | filters.regex('Все новости за 24 часа'))
def aggregate_news(client, message):
    news = ''
    with userbot:
        for channel in config.channels:
            news += f'{message_for_user(get_data_from_messages(get_channel_messages(channel)))}\n'
    if config.debug:
        print('DEBUG MODE')
        print(news)
        bot.send_message(
            chat_id=message.chat.id,
            text='Прямо сейчас бот обновляется и поэтому не работает. '
                 'Пожалуйста, подождите. Если бот недоступен уже несколько часов, '
                 'сообщите об этом разработчику.'
        )
        return
    try:
        bot.send_message(
            chat_id=message.chat.id,
            text=news
        )
    except errors.MessageTooLong:
        print('long message')
        number_of_messages = (len(news) // config.max_message_length) + 1
        start = 0
        end = config.max_message_length
        for _ in range(number_of_messages):
            bot.send_message(
                chat_id=message.chat.id,
                text=news[start:end]
            )
            start += config.max_message_length
            end += config.max_message_length
            time.sleep(1)
    except errors.MessageEmpty:
        bot.send_message(
            chat_id=message.chat.id,
            text='Извините, что-то пошло не так.'
        )
        if config.admin_chat_id:
            bot.send_message(
                chat_id=config.admin_chat_id,
                text=f'Возникла ошибка: MessageEmpty'
                     f'Запрос пользователя:'
                     f'{message}'
            )


@bot.on_message(filters.command(['help']))
def help_command(client, message):
    bot.send_message(
        chat_id=message.chat.id,
        text='/start - Начать работу с ботом (обновить кнопки)\n'
             '/all_news_24 - Все новости за 24 часа\n'
             '/digest_24 - Дайджест за 24 часа из избранных источников\n'
             '/help - Справка/помощь'
    )


bot.run()
