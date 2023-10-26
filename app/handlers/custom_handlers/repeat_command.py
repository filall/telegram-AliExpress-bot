from telebot.types import Message

from app.config_data.config import add_command
from app.database.models import get_user_by_id
from app.loader import bot
from app.logger import base_logger, bot_logger
from app.states.states import UserState

command = ("repeat", "Повтор ранее совершенного поискового запроса")
base_logger.debug(f"Adding command {command} to the list")
add_command(command)


@bot.message_handler(state="*", commands=["repeat"])
async def repeat(message: Message) -> None:
    user = await get_user_by_id(message.from_user.id)

    if not user or not user.requests:
        bot_logger.info(
            "REPEAT command from user {user_id}. No requests in history. "
            "Informing user".format(
                user_id=message.from_user.id,
            )
        )

        await bot.send_message(
            message.chat.id,
            "Вы еще ничего не искали. Попробуйте прямо сейчас!\n"
            "Используйте команду /help, чтобы узнать как.",
        )
        return

    state = UserState.enter_history_number

    bot_logger.info(
        "REPEAT command from user {user_id}. Setting user state to: '{state}'".format(
            user_id=message.from_user.id, state=state
        )
    )
    await bot.set_state(message.from_user.id, state, message.chat.id)

    await bot.send_message(
        message.chat.id,
        "Введите номер запроса из истории для повторного поиска.\n"
        "Историю запросов можно посмотреть командой /history",
    )
