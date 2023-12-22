# todo
# асинхронность 
# логи
# список каналов
# отправление сообщения в телегу

import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator

from pyrogram import Client
from pyrogram.types import Message

from config_data.config import Config, load_config

config: Config = load_config()


# с помощью compose() запустить несколько ботов
userbot = Client(
    'my_userbot',
    config.tg_userbot.api_id,
    config.tg_userbot.api_hash
)

bot = Client(
    'my_bot',
    config.tg_bot.api_id,
    config.tg_bot.api_hash,
    config.tg_bot.bot_token
)


async def get_channel_messages(channel_name: str) -> list[Message]:
    """
    Gets messages from channels for the period of time.
    """
    _time_of_oldest_message: datetime = datetime.now() - timedelta(minutes=config.time_period)
    messages: AsyncGenerator = userbot.get_chat_history(channel_name, limit=100)
    filtered_messages = []

    async for message in messages:
        if message.caption and message.date > _time_of_oldest_message:
            filtered_messages.append(message)

    return filtered_messages


def get_data_from_messages(messages):
    for message in messages:
        print(message.caption.split('\n')[0])
        print(message.link, '\n')


async def main():
    async with userbot:
        for channel in config.channels:
            print(f'Новости канала {channel}:\n')
            get_data_from_messages(await get_channel_messages(channel))

    async with bot:
        await bot.send_message(chat_id=5897335213, text='foo111')


userbot.run(main())
bot.run(main())
