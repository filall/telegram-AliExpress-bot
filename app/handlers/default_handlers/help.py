from telebot.types import Message

from app.config_data.config import get_commands
from app.loader import bot
from app.logger import bot_logger as logger


@bot.message_handler(commands=["help"])
async def bot_help(message: Message) -> None:
    logger.info("Giving help to user {user_id}".format(user_id=message.from_user.id))
    text = [f"/{command} - {description}" for command, description in get_commands()]
    await bot.reply_to(message, "\n".join(text))
