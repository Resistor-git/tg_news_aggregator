# todo
# асинхронность 
# логи
# список каналов
# отправление сообщения в телегу


from datetime import datetime, timedelta
from typing import AsyncGenerator

from pyrogram import Client

from config_data.config import Config, load_config

config: Config = load_config()


app = Client(
    'my_bot',
    config.tg_bot.api_id,
    config.tg_bot.api_hash
)


def get_channel_messages(channel_name: str) -> None:
    """
    Gets messages from channels for the period of time.
    """
    _time_of_oldest_message: datetime = datetime.now() - timedelta(minutes=config.time_period)
    messages: AsyncGenerator = app.get_chat_history(channel_name, limit=100)

    for message in messages:
        if message.caption and message.date > _time_of_oldest_message:
            print(message.caption.split('\n')[0])
            print(message.link, '\n')


with app:
    for channel in config.channels:
        print(f'Новости канала {channel}:\n')
        get_channel_messages(channel)
