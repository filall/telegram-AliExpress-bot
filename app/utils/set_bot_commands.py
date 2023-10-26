from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand

from app.config_data.config import get_commands
from app.logger import base_logger as logger


async def set_bot_commands(bot: AsyncTeleBot) -> None:
    logger.debug("Passing commands to bot")
    await bot.set_my_commands([BotCommand(*i) for i in get_commands()])
