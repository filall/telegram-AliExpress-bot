from telebot.types import Message

from app.loader import bot
from app.logger import bot_logger as logger


@bot.message_handler(state="*")
async def non_command(message: Message) -> None:
    if message.text.lower().startswith("привет"):
        logger.info(
            "Responding to user {user_id}: '{message}'".format(
                user_id=message.from_user.id, message=message.text
            )
        )
        await bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
    else:
        logger.info(
            "Responding to incorrect message from user {user_id}: '{message}'".format(
                user_id=message.from_user.id, message=message.text
            )
        )
        await bot.reply_to(
            message,
            "Извините, я вас не понимаю.\n"
            "Введите /help для получения списка доступных команд",
        )
