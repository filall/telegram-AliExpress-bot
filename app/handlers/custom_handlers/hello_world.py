from telebot.types import Message

from app.config_data.config import add_command
from app.loader import bot
from app.logger import base_logger, bot_logger

command = ("helloworld", "Поприветствовать мир")
base_logger.debug(f"Adding command {command} to the list")
add_command(command)


@bot.message_handler(commands=["hello-world", "helloworld"])
async def hello_world(message: Message) -> None:
    bot_logger.info(
        "HELLOWORLD command by user {user_id}. Replying.".format(
            user_id=message.from_user.id
        )
    )
    await bot.reply_to(message, f"Привет, Мир!\nПривет, {message.from_user.full_name}!")
