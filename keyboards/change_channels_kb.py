import json
import logging.handlers

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from main import config, users_settings_path
from lexicon import CHANNELS_HUMAN_READABLE

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

button_inline_add_channels = InlineKeyboardButton(
    "Добавить каналы", callback_data="add_channels"
)
button_inline_remove_channels = InlineKeyboardButton(
    "Удалить каналы", callback_data="remove_channels"
)
button_inline_go_to_settings = InlineKeyboardButton(
    "Вернуться назад", callback_data="settings"
)
keyboard_inline_add_remove_channels = InlineKeyboardMarkup(
    [[button_inline_add_channels], [button_inline_remove_channels]]
)


def keyboard_inline_change_channels(
    user_id: int, action: str
) -> InlineKeyboardMarkup | None:
    """
    Creates inline keyboard with buttons for adding and removing channels.
    If user wants to add channels, returns keyboard with missing channels.
    If user wants to remove channels, returns keyboard with already added channels.
    """
    with open(users_settings_path, "r") as f:
        buttons: list[InlineKeyboardButton] = []
        users_settings = json.load(f)
        try:
            for user in users_settings:
                if user["id"] == user_id:
                    user_channels = user["channels"]
                    if "remove" in action:
                        for channel in user_channels:
                            buttons.append(
                                InlineKeyboardButton(
                                    text=CHANNELS_HUMAN_READABLE[channel],
                                    callback_data=f"remove_{channel}",
                                )
                            )
                    elif "add" in action:
                        for channel in config.channels:
                            if channel not in user_channels:
                                buttons.append(
                                    InlineKeyboardButton(
                                        text=CHANNELS_HUMAN_READABLE[channel],
                                        callback_data=f"add_{channel}",
                                    )
                                )
                    break
        except KeyError:
            logger.exception(f"Human readable name for channel {channel} not found")
        if buttons:
            buttons.append(button_inline_go_to_settings)
            return InlineKeyboardMarkup([[button] for button in buttons])
        return None
