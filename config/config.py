from dataclasses import dataclass
from dotenv import dotenv_values
import logging

DEFAULT_SHOP_PHOTO_ID='AgACAgUAAxkBAAICG2Xl2wecngswRxnUAe8lN1bRkGQdAAL0ujEbWDApV7UkLxai6G3RAQADAgADcwADNAQ'
ALLOWED_SYMBOLS = 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя '

logger = logging.getLogger(__name__)

@dataclass
class TgBot:
    token: str

@dataclass
class Config:
    TgBot: TgBot

def load_env_values(path: str | None = None):
    env_values = dotenv_values(path)
    return Config(TgBot=TgBot(token=env_values['TOKEN']))