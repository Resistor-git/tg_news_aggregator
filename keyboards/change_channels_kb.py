import json

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from main import config

# from users import users_settings


button_inline_add_channels = InlineKeyboardButton(
    "Добавить каналы", callback_data="add_channels"
)
button_inline_remove_channels = InlineKeyboardButton(
    "Удалить каналы", callback_data="remove_channels"
)
button_inline_novaya_europe = InlineKeyboardButton(
    "Новая", callback_data="add_novaya_europe"
)
button_inline_add_bbcrussian = InlineKeyboardButton(
    "BBC Russian", callback_data="add_bbcrussian"
)
button_inline_add_fontanka = InlineKeyboardButton(
    "Фонтанка", callback_data="add_fontanka"
)
button_inline_add_news_sirena = InlineKeyboardButton(
    "Сирена", callback_data="add_news_sirena"
)
button_inline_add_agentstvonews = InlineKeyboardButton(
    "Агентство", callback_data="add_agentstvonews"
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
    with open("users/users_settings.json", "r") as f:
        buttons: list[InlineKeyboardButton] = []
        users_settings = json.load(f)
        for user in users_settings:
            if user["id"] == user_id:
                user_channels = user["channels"]
                if "remove" in action:
                    for channel in user_channels:
                        buttons.append(
                            InlineKeyboardButton(
                                text=channel, callback_data=f"remove_{channel}"
                            )
                        )
                elif "add" in action:
                    for channel in config.channels:
                        if channel not in user_channels:
                            buttons.append(
                                InlineKeyboardButton(
                                    text=channel, callback_data=f"add_{channel}"
                                )
                            )
                break
        if buttons:
            return InlineKeyboardMarkup([[button] for button in buttons])
        return None
        # return InlineKeyboardMarkup([[button] for button in buttons])
