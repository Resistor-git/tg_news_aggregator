import logging.handlers
import json

from pyrogram import Client, errors, filters
from pyrogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from main import config, userbot
from helpers.helpers import (
    get_channel_messages,
    get_headers_from_messages,
    message_for_user,
    digest_filter,
    add_new_user_if_not_exists,
)

# from users import users_settings
from keyboards import (
    keyboard_inline_change_channels,
    keyboard_inline_add_remove_channels,
)
from lexicon import LEXICON

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
button_add_channel = KeyboardButton("Добавить каналы")
button_remove_channel = KeyboardButton("Удалить каналы")
button_go_to_start = KeyboardButton("Вернуться к новостям")
button_add_novaya = KeyboardButton("Новая")
button_add_bbcrussian = KeyboardButton("BBC")
button_add_fontanka = KeyboardButton("Фонтанка")
button_add_sirena = KeyboardButton("Сирена")
button_add_agentstvo = KeyboardButton("Агентство")
keyboard_main = ReplyKeyboardMarkup(
    [[button_all_news], [button_digest]], resize_keyboard=True
)
keyboard_add_remove_channels = ReplyKeyboardMarkup(
    [[button_add_channel], [button_remove_channel], [button_go_to_start]],
    resize_keyboard=True,
)

# button_inline_add_fontanka = InlineKeyboardButton(
#     "Фонтанка", callback_data="add_fontanka"
# )


@Client.on_message(filters.command(["start"]) | filters.regex("Вернуться к новостям"))
def start_command(client, message: Message):
    client.send_message(
        chat_id=message.chat.id,
        text="Кнопки ниже позволяют прочитать все новости за 12 ч. или только выжимку из некоторых каналов.",
        reply_markup=keyboard_main,
    )
    add_new_user_if_not_exists(message.chat.id)


@Client.on_message(
    filters.command(["all_news"]) | filters.regex("Все новости за 12 часов")
)
def all_news(client, message: Message):
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
def digest(client, message: Message):
    """
    Sends digest messages to the client. If there are no digests, sends informational message.
    """
    empty_digest = True
    if config.debug:
        client.send_message(
            chat_id=message.chat.id,
            text="В данный момент бот обновляется поэтому может выдавать неожиданные результаты или вовсе не отвечать.",
        )
    with userbot:
        for channel in config.channels:
            digests = digest_filter(get_channel_messages(channel))
            if len(digests) > 0:
                empty_digest = False
                for digest_message in digests:
                    client.forward_messages(
                        chat_id=message.chat.id,
                        from_chat_id=digest_message.sender_chat.username,
                        message_ids=digest_message.id,
                    )
    if empty_digest:
        client.send_message(
            chat_id=message.chat.id,
            text="К сожалению, дайджесты за последнее время не найдены. Вероятно, их ещё не опубликовали.",
        )
    logger.info(f"Пользователь {message.from_user.username} воспользовался дайджестом.")


@Client.on_message(filters.command(["settings"]))
def settings(client, message: Message):
    """
    Shows user settings.
    If user is not registered - adds new user.
    """
    add_new_user_if_not_exists(message.chat.id)
    user_channels: list[str] | None = None
    with open("users/users_settings.json", "r") as f:
        users_settings = json.load(f)
        for user in users_settings:
            if user["id"] == message.chat.id:
                user_channels = user["channels"]
                break
    if not user_channels:
        client.send_message(
            chat_id=message.chat.id,
            text=LEXICON["no_subscriptions"],
            reply_markup=keyboard_inline_add_remove_channels,
        )
    else:
        client.send_message(
            chat_id=message.chat.id,
            text=f"Ваши текущие подписки: {user_channels}",
            reply_markup=keyboard_inline_add_remove_channels,
        )


# @Client.on_message(filters.command(["add_channels"]) | filters.regex("Добавить каналы"))
# def add_channels_keyboard(client, message: Message):
#     """
#     Creates keyboard with available channels.
#     Shows only channels that user is not subscribed to.
#     """
#     user_channels: list[str] | None = None
#     keyboard_add_channels: list[list[KeyboardButton]] = [[button_go_to_start]]
#     channel_to_button = {
#         "fontankaspb": button_add_fontanka,
#         "bbcrussian": button_add_bbcrussian,
#         "novaya_europe": button_add_novaya,
#         "news_sirena": button_add_sirena,
#         "agentstvonews": button_add_agentstvo,
#     }
#     with open("users/users_settings.json", "r") as f:
#         for user in users_settings:
#             if user["id"] == message.chat.id:
#                 user_channels = user["channels"]
#                 break
#     if user_channels:
#         for channel in user_channels:
#             keyboard_add_channels.append([channel_to_button[channel]])
#         client.send_message(
#             chat_id=message.chat.id,
#             text="Выберите каналы, которые хотите добавить",
#             reply_markup=ReplyKeyboardMarkup(
#                 keyboard_add_channels, resize_keyboard=True
#             ),
#         )


# @Client.on_message(filters.command(["add_channels"]) | filters.regex("Добавить каналы"))
# def add_keyboard(client, message: Message):
#     all_channels: list[str] = config.channels
#     user_channels: list[str] | None = None
#     with open("users/users_settings.json", "r") as f:
#         for user in users_settings:
#             if user["id"] == message.chat.id:
#                 user_channels = user["channels"]
#                 break
#         if user_channels:
#
#
#     client.send_message(
#         chat_id=message.chat.id,
#         text="Выберите каналы, которые хотите добавить",
#         reply_markup=keyboard_add_remove_channels,
#     )


# @Client.on_callback_query(filters.regex("remove_channels"))
# def remove_channels(client, query: CallbackQuery):
#     logger.debug(query.data)
#     _keyboard: InlineKeyboardMarkup = keyboard_inline_change_channels(
#         query.from_user.id, query.data
#     )
#     if _keyboard:
#         client.send_message(
#             chat_id=query.message.chat.id,
#             text=LEXICON["delete_channels_list"],
#             reply_markup=_keyboard,
#         )
#     else:
#         client.send_message(
#             chat_id=query.message.chat.id,
#             text=LEXICON["no_subscriptions"],
#             reply_markup=keyboard_inline_add_remove_channels,
#         )


@Client.on_callback_query(filters.regex("remove_"))
def remove_channel(client, query: CallbackQuery):
    logger.debug(f"{query.data} for user {query.from_user.id}")
    _keyboard: InlineKeyboardMarkup = keyboard_inline_change_channels(
        query.from_user.id, query.data
    )
    with open("users/users_settings.json", "r") as f:
        users_settings: list[dict] = json.load(f)
        users_settings_changed: bool = False
        for user in users_settings:
            if user["id"] == query.from_user.id:
                user_channels = user["channels"]
                try:
                    user_channels.remove(query.data.replace("remove_", ""))
                    user["channels"] = user_channels
                    users_settings_changed = True
                except ValueError:
                    client.send_message(
                        chat_id=query.message.chat.id,
                        text=f"Вы не подписаны на {query.data.replace('remove_', '')}.\n"
                        f"{LEXICON['delete_channels_list']}",
                        reply_markup=_keyboard,
                    )
                break
    if users_settings_changed:
        with open("users/users_settings.json", "w") as f:
            json.dump(users_settings, f, indent=4)
        _keyboard_channels_to_remove: InlineKeyboardMarkup = (
            keyboard_inline_change_channels(query.from_user.id, query.data)
        )
        if _keyboard_channels_to_remove:
            client.send_message(
                chat_id=query.message.chat.id,
                text=f"Канал {query.data.replace('remove_', '')} удален из вашего списка.\n"
                f"{LEXICON['delete_channels_list']}",
                reply_markup=_keyboard_channels_to_remove,
            )
        else:
            client.send_message(
                chat_id=query.message.chat.id,
                text=LEXICON["no_subscriptions"],
                reply_markup=keyboard_inline_add_remove_channels,
            )


@Client.on_callback_query(filters.regex("add_"))
def add_channel(client, query: CallbackQuery):
    logger.debug(f"{query.data} for user {query.from_user.id}")
    _keyboard_channels_to_add: InlineKeyboardMarkup = keyboard_inline_change_channels(
        query.from_user.id, query.data
    )
    users_settings_changed: bool = False
    if _keyboard_channels_to_add:
        client.send_message(
            chat_id=query.message.chat.id,
            text=LEXICON["add_channels_list"],
            reply_markup=_keyboard_channels_to_add,
        )
    else:
        client.send_message(
            chat_id=query.message.chat.id,
            text=LEXICON["subscribed_to_all_channels"],
            reply_markup=keyboard_inline_add_remove_channels,
        )


@Client.on_message(filters.command(["help"]))
def help_command(client, message: Message):
    client.send_message(
        chat_id=message.chat.id,
        text="/start - Начать работу с ботом (обновить кнопки)\n"
        "/all_news - Все новости за 12 часов\n"
        "/digest - Дайджест за 12 часов из избранных источников\n"
        "/settings - Управление подписками\n"
        "/help - Справка/помощь",
    )
