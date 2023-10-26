from typing import List

from telebot.types import Message

from app.config_data.config import add_command
from app.database.models import UserRequest, get_user_by_id
from app.loader import bot
from app.logger import base_logger, bot_logger
from app.states.states import UserState

TELEGRAM_MESSAGE_LENGTH = 4096

command = ("history", "Просмотр истории поиска")
base_logger.debug(f"Adding command {command} to the list")
add_command(command)


@bot.message_handler(state=UserState.enter_history_number, commands=["history"])
@bot.message_handler(state="*", commands=["history"])
async def custom(message: Message) -> None:
    user = await get_user_by_id(message.from_user.id)

    if not user or not user.requests:
        bot_logger.info(
            "HISTORY command from user {user_id}. No requests in history. "
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

    user_requests: List[UserRequest] = user.requests
    user_requests.sort(reverse=True)

    history_strings = []
    history_string = ""
    idx = 1
    for user_request in user_requests:
        history_request = "{idx}) {request}\n".format(request=user_request, idx=idx)
        if len(history_string) + len(history_request) > TELEGRAM_MESSAGE_LENGTH:
            history_strings.append(history_string)
            history_string = ""
        history_string += history_request
        idx += 1
    history_strings.append(history_string)

    bot_logger.info(
        "HISTORY command from user {user_id}. "
        "Sending history to the user in {count} message(s)".format(
            user_id=message.from_user.id, count=len(history_strings)
        )
    )
    msg = "Ранее вы искали:\n\n"
    msg += history_strings[0]
    await bot.send_message(message.chat.id, msg)
    for hist_str in history_strings[1:]:
        await bot.send_message(message.chat.id, hist_str)

    current_state = await bot.get_state(message.from_user.id, message.chat.id)
    if str(current_state) == str(UserState.enter_history_number):
        await bot.send_message(
            message.chat.id, "Введите номер запроса из истории для повторного поиска."
        )
    else:
        await bot.send_message(
            message.chat.id, "Вы можете повторить поиск с помощью команды /repeat"
        )
