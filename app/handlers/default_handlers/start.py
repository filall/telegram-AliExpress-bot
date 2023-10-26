from telebot.types import Message

from app.database.models import create_user
from app.loader import bot
from app.logger import bot_logger as logger


@bot.message_handler(commands=["start"])
async def bot_start(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    if await create_user(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
    ):
        logger.info("Greeting user {user_id}".format(user_id=message.from_user.id))
        await bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
    else:
        logger.info(
            "Welcoming back user {user_id}".format(user_id=message.from_user.id)
        )
        await bot.reply_to(
            message, f"Рад вас снова видеть, {message.from_user.full_name}!"
        )
