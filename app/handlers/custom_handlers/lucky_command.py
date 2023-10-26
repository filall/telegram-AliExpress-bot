import random
import string

from telebot.types import Message

from app.config_data.config import add_command
from app.loader import bot
from app.logger import base_logger, bot_logger
from app.states.states import UserState
from app.utils.api_caller import fetch_data_for_user

AMOUNT = 5

command = ("lucky", f"Испытать удачу, найти {AMOUNT} случайных товаров")
base_logger.debug(f"Adding command {command} to the list")
add_command(command)


@bot.message_handler(state="*", commands=["lucky"])
async def low(message: Message) -> None:
    state = UserState.lucky

    bot_logger.info(
        "LUCKY command from user {user_id}. Setting user state to: '{state}'".format(
            user_id=message.from_user.id, state=state
        )
    )
    print("KBA")
    await bot.set_state(message.from_user.id, state, message.chat.id)
    print("KPR")
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["command"] = "/lucky"
        data["quantity"] = AMOUNT
        data["keyword"] = random.choice(string.ascii_letters)
    print("MYY")
    bot_logger.info(
        "LUCKY state. Calling for random API request for user {user_id}.".format(
            user_id=message.from_user.id
        )
    )
    await fetch_data_for_user(message.from_user.id, message.chat.id)
    await bot.delete_state(message.from_user.id, message.chat.id)
