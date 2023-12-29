# todo
# асинхронность 
# логи
# список каналов
# отправление сообщения в телегу
# BUG: разрывается ссылка при делении сообщений

import asyncio
import textwrap
import time
from datetime import datetime, timedelta
from typing import AsyncGenerator

from pyrogram import Client, errors
from pyrogram.types import Message

from config_data.config import Config, load_config

config: Config = load_config()

# с помощью compose() запустить несколько ботов
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


####################
# async def get_channel_messages(channel_name: str) -> list[Message]:
#     """
#     Gets messages from channels for the period of time.
#     """
#     _time_of_oldest_message: datetime = datetime.now() - timedelta(minutes=config.time_period)
#     messages: AsyncGenerator = userbot.get_chat_history(channel_name, limit=100)
#     filtered_messages = []

#     async for message in messages:
#         if message.caption and message.date > _time_of_oldest_message:
#             filtered_messages.append(message)

#     return filtered_messages


# def get_data_from_messages(messages):
#     for message in messages:
#         print(message.caption.split('\n')[0])
#         print(message.link, '\n')


# async def main():
#     async with userbot:
#         for channel in config.channels:
#             print(f'Новости канала {channel}:\n')
#             get_data_from_messages(await get_channel_messages(channel))

#     async with bot:
#         await bot.send_message(chat_id=5897335213, text='foo111')


# # userbot.run(main())
# bot.run(main())
##############

def get_channel_messages(channel_name: str) -> list[Message]:
    """
    Gets messages from channels for the period of time.
    """
    _time_of_oldest_message: datetime = datetime.now() - timedelta(minutes=config.time_period)
    messages: AsyncGenerator = userbot.get_chat_history(channel_name, limit=100)
    filtered_messages = []

    for message in messages:
        if message.date > _time_of_oldest_message:
            if message.sender_chat.username == 'echoonline_news' and message.text:
                filtered_messages.append(message)
            elif (message.sender_chat.username in ('svtvnews', 'news_sirena', 'fontankaspb') and
                  message.caption):
                filtered_messages.append(message)
    return list(reversed(filtered_messages))


def get_data_from_messages(messages):
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


def split_long_string(text, length=4096) -> list[str]:
    """
    Splits long message into smaller.
    Does not preserve newline characters!!!
    NOT USED IN THE CURRENT VERSION OF CODE
    """
    return textwrap.wrap(text=text, width=length)


@bot.on_message()
def aggregate_news(client, message):
    news = ''
    with userbot:
        for channel in config.channels:
            news += f'{message_for_user(get_data_from_messages(get_channel_messages(channel)))}\n'
    try:
        bot.send_message(
            chat_id=message.chat.id,
            text=news
        )
    except errors.MessageTooLong:
        print('long message')
        number_of_messages = (len(news) // 4096) + 1
        start = 0
        end = 4096
        for _ in range(number_of_messages):
            bot.send_message(
                chat_id=message.chat.id,
                text=news[start:end]
            )
            start += 4096
            end += 4096
            time.sleep(1)


bot.run()
