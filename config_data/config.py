from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    api_id: str
    api_hash: str


@dataclass
class Config:
    tg_bot: TgBot
    channels: list


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            api_id=env('API_ID'),
            api_hash=env('API_HASH')
        ),
        channels=env.list('CHANNELS')
    )
