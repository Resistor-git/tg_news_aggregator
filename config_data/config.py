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


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_userbot=TgUserBot(
            api_id=env('API_ID'),
            api_hash=env('API_HASH')
        ),
        tg_bot=TgBot(
            api_id=env('API_ID'),
            api_hash=env('API_HASH'),
            bot_token=env('BOT_TOKEN')
        ),
        channels=env.list('CHANNELS'),
        time_period=env.int('TIME_PERIOD_MINUTES')
    )
