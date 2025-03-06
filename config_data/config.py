from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    yatoken: str
    admin_ids: str
    support_id: int


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               yatoken=env('TOKEN'),
                               admin_ids=env('ADMIN_IDS'),
                               support_id=env('SUPPORT_ID')))
