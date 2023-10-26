from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage

from app.config_data import config

storage = StateMemoryStorage()
bot = AsyncTeleBot(token=config.BOT_TOKEN, state_storage=storage)
