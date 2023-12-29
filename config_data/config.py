from dataclasses import dataclass
from environs import Env


@dataclass
class TgUserBot:
    api_id: str
    api_hash: str


@dataclass
class TgBot:
    api_id: str
    api_hash: str
    bot_token: str


@dataclass
class Config:
    tg_userbot: TgUserBot
    tg_bot: TgBot
    channels: list
    time_period: int
    max_message_length: int
    debug: bool
    admin_chat_id: int | None = None


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_userbot=TgUserBot(
            api_id=env.int('API_ID'),
            api_hash=env.int('API_HASH')
        ),
        tg_bot=TgBot(
            api_id=env.int('API_ID'),
            api_hash=env.int('API_HASH'),
            bot_token=env.int('BOT_TOKEN')
        ),
        channels=env.list('CHANNELS'),
        time_period=env.int('TIME_PERIOD_MINUTES'),
        max_message_length=env.int('MAX_MESSAGE_LENGTH'),
        admin_chat_id=env('ADMIN_CHAT_ID'),
        debug=env.bool('DEBUG')
    )
