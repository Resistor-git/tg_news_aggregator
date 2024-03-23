from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton

button_all_news = KeyboardButton("Все новости за 12 часов")
button_digest = KeyboardButton("Дайджест за 12 часов")
keyboard_main = ReplyKeyboardMarkup(
    [[button_all_news, button_digest]],
    resize_keyboard=True,
)
