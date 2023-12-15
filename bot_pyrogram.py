# todo
# асинхронность 
# логи
# список каналов
# отправление сообщения в телегу

import logging

from pyrogram import Client
from datetime import datetime, timedelta

from config_data.config import Config, load_config

config: Config = load_config()
# time_period =


# Создание клиента Pyrogram
app = Client(
    'my_bot',
    config.tg_bot.api_id,
    config.tg_bot.api_hash
)


# # Функция для получения сообщений из канала
# def get_channel_messages(channel_username):
#     # Получаем текущую дату и время
#     now = datetime.now()
    
#     # Вычисляем время начала периода - 24 часа назад
#     start_time = now - timedelta(hours=24)
    
#     # Получаем timestamp начала и конца периода
#     from_time = start_time.timestamp()
#     to_time = now.timestamp()
    
#     # Получаем сообщения из канала за указанный период времени
#     messages = app.get_chat_history(channel_username, limit=1)
    
#     # Выводим текст каждого сообщения
#     for message in messages:
#         print(message)
#         print('------')

# Запуск клиента Pyrogram
# with app:
#     get_channel_messages('@echofm_online')


def get_channel_messages(channel_name: str) -> None:
    messages = app.get_chat_history(channel_name, limit=10)

    for message in messages:
        if message.caption:
            print(message.caption.split('\n')[0])
            print(message.link, '\n')


with app:
    for channel in config.channels:
        print(f'Новости канала {channel}:\n')
        get_channel_messages(channel)
