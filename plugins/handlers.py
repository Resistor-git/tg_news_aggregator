import logging.handlers
import json

from pyrogram import Client, errors, filters
from pyrogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from main import config, userbot, users_settings_path
from helpers.helpers import (
    get_channel_messages,
    get_headers_from_messages,
    message_for_user,
    digest_filter,
    add_new_user_if_not_exists,
    get_user_subscriptions,
)

from keyboards import (
    keyboard_inline_change_channels,
    keyboard_inline_add_remove_channels,
)
from lexicon import LEXICON, CHANNELS_HUMAN_READABLE

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
keyboard_main = ReplyKeyboardMarkup(
    [[button_all_news, button_digest]],
    resize_keyboard=True,
)


@Client.on_message(filters.command(["start"]))
def start_command(client, message: Message):
    """
    Creates new user if user does not exist.
    Creates the keyboard to get news.
    """
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
    """
    Get headers of all news for the specified period (default is 12 hours).
    Only news from subscriptions are included.
    """
    news: str = ""
    user_channels = get_user_subscriptions(message.from_user.id)
    with userbot:
        if not user_channels:
            client.send_message(
                chat_id=message.chat.id, text=LEXICON["no_subscriptions"]
            )
            return
        for channel in user_channels:
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
            chat_id=message.chat.id,
            text="Извините, что-то пошло не так. Создателю бота направлено сообщение с информацией об ошибке.\n"
            "Пожалуйста, сообщите о случившемся разработчику.",
        )
        if config.admin_chat_id:
            client.send_message(
                chat_id=config.admin_chat_id,
                text=f"Возникла ошибка: MessageEmpty\n"
                f"Пользователь: {message.from_user.username}\n"
                f"Запрос пользователя:\n"
                f"{message}",
            )
    logger.info(
        f"Пользователь {message.from_user.username} воспользовался получением заголовков."
    )


@Client.on_message(filters.command(["digest"]) | filters.regex("Дайджест за 12 часов"))
def digest(client, message: Message):
    """
    Sends digest messages to the client. If there are no digests, sends informational message.
    Only news from subscriptions are included.
    """
    empty_digest = True
    user_channels = get_user_subscriptions(message.from_user.id)
    if config.debug:
        client.send_message(
            chat_id=message.chat.id,
            text="В данный момент бот обновляется поэтому может выдавать неожиданные результаты или вовсе не отвечать.",
        )
    with userbot:
        if not user_channels:
            client.send_message(
                chat_id=message.chat.id, text=LEXICON["no_subscriptions"]
            )
            return
        for channel in user_channels:
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
            text=LEXICON["empty_digest"],
        )
    logger.info(f"Пользователь {message.from_user.username} воспользовался дайджестом.")


@Client.on_message(filters.command(["settings"]))
def settings(client, message: Message):
    """
    Shows user settings.
    If user is not registered - adds new user.
    """
    add_new_user_if_not_exists(message.chat.id)
    user_channels: list[str] | None = get_user_subscriptions(message.chat.id)
    if not user_channels:
        client.send_message(
            chat_id=message.chat.id,
            text=LEXICON["no_subscriptions"],
            reply_markup=keyboard_inline_add_remove_channels,
        )
    else:
        client.send_message(
            chat_id=message.chat.id,
            text=f"Ваши текущие подписки: "
            f"{', '.join([CHANNELS_HUMAN_READABLE[channel] for channel in user_channels])}.",
            reply_markup=keyboard_inline_add_remove_channels,
        )


@Client.on_callback_query(filters.regex("settings"))
def call_settings(client, query):
    """
    Calls settings function.
    Used to handle cases when settings are called by inline buttons.
    """
    settings(client, query.message)


@Client.on_callback_query(filters.regex("remove_"))
def remove_channel(client, query: CallbackQuery):
    """
    Remove channel from user settings using inline keyboard.
    """
    logger.debug(f"{query.data} for user {query.from_user.id}")
    _keyboard: InlineKeyboardMarkup = keyboard_inline_change_channels(
        query.from_user.id, query.data
    )
    with open(users_settings_path, "r") as f:
        users_settings: list[dict] = json.load(f)
        users_settings_changed: bool = False
        for user in users_settings:
            if user["id"] == query.from_user.id:
                user_channels = user["channels"]
                if not user_channels:
                    client.send_message(
                        chat_id=query.message.chat.id,
                        text=LEXICON["no_subscriptions"],
                        reply_markup=keyboard_inline_add_remove_channels,
                    )
                    break
                try:
                    user_channels.remove(query.data.replace("remove_", ""))
                    user["channels"] = user_channels
                    users_settings_changed = True
                except ValueError:
                    client.send_message(
                        chat_id=query.message.chat.id,
                        text=f"{LEXICON['delete_channels_list']}",
                        reply_markup=_keyboard,
                    )
                break
    if users_settings_changed:
        with open(users_settings_path, "w") as f:
            json.dump(users_settings, f, indent=4)
        _keyboard_channels_to_remove: InlineKeyboardMarkup = (
            keyboard_inline_change_channels(query.from_user.id, query.data)
        )
        if _keyboard_channels_to_remove:
            client.send_message(
                chat_id=query.message.chat.id,
                text=f"Канал {CHANNELS_HUMAN_READABLE[query.data.replace('remove_', '')]} "
                f"удалён из вашего списка.\n"
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
    """
    Add channel to user settings using inline keyboard.
    """
    logger.debug(f"{query.data} for user {query.from_user.id}")
    _keyboard_channels_to_add: InlineKeyboardMarkup = keyboard_inline_change_channels(
        query.from_user.id, query.data
    )
    users_settings: list[dict] = json.load(open(users_settings_path))
    users_settings_changed: bool = False
    for user in users_settings:
        if user["id"] == query.from_user.id:
            user_channels = user["channels"]
            if query.data == "add_channels":
                if _keyboard_channels_to_add:
                    client.send_message(
                        chat_id=query.message.chat.id,
                        text=f"{LEXICON['add_channels_list']}",
                        reply_markup=_keyboard_channels_to_add,
                    )
                else:
                    client.send_message(
                        chat_id=query.message.chat.id,
                        text=f"{LEXICON['subscribed_to_all_channels']}",
                        reply_markup=keyboard_inline_add_remove_channels,
                    )
            elif query.data.replace("add_", "") not in user_channels:
                user_channels.append(query.data.replace("add_", ""))
                users_settings_changed = True
            else:
                client.send_message(
                    chat_id=query.message.chat.id,
                    text=f"Вы уже подписаны на {CHANNELS_HUMAN_READABLE[query.data.replace('add_', '')]}.\n"
                    f"{LEXICON['add_channels_list']}",
                    reply_markup=_keyboard_channels_to_add,
                )
            break
    if users_settings_changed:
        with open(users_settings_path, "w") as f:
            json.dump(users_settings, f, indent=4)
        _keyboard_channels_to_add = keyboard_inline_change_channels(
            query.from_user.id, query.data
        )
        if _keyboard_channels_to_add:
            client.send_message(
                chat_id=query.message.chat.id,
                text=f"Вы подписались на {CHANNELS_HUMAN_READABLE[query.data.replace('add_', '')]}.\n"
                f"{LEXICON['add_channels_list']}",
                reply_markup=_keyboard_channels_to_add,
            )
        else:
            client.send_message(
                chat_id=query.message.chat.id,
                text=f"Вы подписались на {CHANNELS_HUMAN_READABLE[query.data.replace('add_', '')]}.\n"
                f"{LEXICON['subscribed_to_all_channels']}",
                reply_markup=keyboard_inline_add_remove_channels,
            )


@Client.on_message(filters.command(["help"]))
def help_command(client, message: Message):
    client.send_message(
        chat_id=message.chat.id,
        text="Доступные команды:\n"
        "/start - Начать работу с ботом (обновить кнопки)\n"
        "/all_news - Все новости за 12 часов\n"
        "/digest - Дайджест за 12 часов из избранных источников\n"
        "/settings - Управление подписками\n"
        "/help - Справка/помощь\n"
        "\n"
        "Если у вас пропали кнопки для получения новостей, напечатайте /start или выберите /start в меню ",
    )
