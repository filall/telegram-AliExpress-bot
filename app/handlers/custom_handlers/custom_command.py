from telebot.types import Message

from app.config_data.config import add_command
from app.loader import bot
from app.logger import base_logger, bot_logger
from app.states.states import UserState

command = ("custom", "Найти товары в заданном ценовом диапазоне")
base_logger.debug(f"Adding command {command} to the list")
add_command(command)


@bot.message_handler(state="*", commands=["custom"])
async def custom(message: Message) -> None:
    state = UserState.enter_keyword
    bot_logger.info(
        "CUSTOM command from user {user_id}. Setting user state to: '{state}'".format(
            user_id=message.from_user.id, state=state
        )
    )
    await bot.set_state(message.from_user.id, state, message.chat.id)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["price_input"] = True
        data["command"] = "/custom"

    await bot.send_message(
        message.chat.id, "Введите название/ключевые слова для поиска товара"
    )
