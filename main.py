from pathlib import Path

from pyrogram import Client

from config_data.config import Config, load_config

# from keyboards import create_main_menu

config: Config = load_config()
users_settings_path: Path = Path.cwd() / "users" / "users_settings.json"

userbot = Client(
    "my_userbot", config.tg_userbot.api_id, config.tg_userbot.api_hash, no_updates=True
)

bot = Client(
    "my_bot",
    config.tg_bot.api_id,
    config.tg_bot.api_hash,
    config.tg_bot.bot_token,
    plugins=dict(root="plugins"),
)


if __name__ == "__main__":
    bot.run()
    # create_main_menu()
