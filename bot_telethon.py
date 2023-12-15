from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel
import datetime

api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone_number = 'YOUR_PHONE_NUMBER'  # можно заменить на bot_token?

client = TelegramClient(phone_number, api_id, api_hash)
client.start()

channel_username = 'YOUR_CHANNEL_USERNAME'
channel_entity = client.get_input_entity(channel_username)

# Определите даты начала и конца (в данном случае, за один день)
start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)


def main():
    messages = client(GetHistoryRequest(
        peer=channel_entity,
        limit=100,  # Количество сообщений для получения
        offset_date=end_date,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))

    for message in messages.messages:
        print(message)

    client.disconnect()


# В этом примере мы используем метод `GetHistoryRequest` для получения сообщений из указанного канала. `limit` определяет сколько сообщений вы хотите получить (в данном случае 100). `offset_date` и `end_date` определяют временной промежуток, за который вы хотите получить сообщения.
# Не забудьте заменить `'YOUR_API_ID'`, `'YOUR_API_HASH'`, `'YOUR_PHONE_NUMBER'` и `'YOUR_CHANNEL_USERNAME'` соответствующими значениями для вашего аккаунта и канала. Будьте уверены, что у вас есть доступ к этому каналу.
# Надеюсь, это поможет вам получить сообщения из нужного канала за день! Если у вас возникнут еще вопросы, я с удовольствием вам помогу. 😊


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('ошибка')  # logger.exception('Uncaught exception')