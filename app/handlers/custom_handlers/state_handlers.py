from typing import List

from telebot import asyncio_filters
from telebot.types import Message

from app.config_data.config import MAX_QUERY_RESULTS
from app.database.models import UserRequest, get_user_by_id
from app.loader import bot
from app.logger import bot_logger as logger
from app.states.states import UserState
from app.utils.api_caller import fetch_data_for_user


@bot.message_handler(state=UserState.enter_keyword)
async def enter_keyword(message: Message) -> None:
    """Ввод ключевого слова для поиска"""
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["keyword"] = message.text
        try:
            is_price_input_required = data["price_input"]
        except KeyError:
            is_price_input_required = False
    state = (
        UserState.enter_min_price
        if is_price_input_required
        else UserState.enter_quantity
    )
    logger.info(
        "ENTER KEYWORD state. Received keyword from user {user_id}. "
        "Setting user state to: '{state}'".format(
            user_id=message.from_user.id, state=state
        )
    )
    await bot.set_state(message.from_user.id, state, message.chat.id)
    msg = (
        "Введите минимальную цену (USD)"
        if is_price_input_required
        else "Введите желаемое количество результатов.\nМаксимум {max}".format(
            max=MAX_QUERY_RESULTS
        )
    )
    await bot.send_message(message.chat.id, msg)


@bot.message_handler(state=UserState.enter_min_price)
async def enter_min_price(message: Message):
    """Ввод минимальной цены для поиска"""
    try:
        price = float(message.text.replace(",", "."))
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["min_price"] = price
    except ValueError:
        logger.info(
            "MIN PRICE state. Received incorrect value from user {user_id}. "
            "Asking to repeat".format(user_id=message.from_user.id)
        )
        bot.send_message(
            message.chat.id,
            "Некорректное значение.\n"
            "Пожалуйста, введите минимальную цену еще раз (USD)",
        )
        return

    state = UserState.enter_max_price
    logger.info(
        "MIN PRICE state. Received MIN price from user {user_id}. "
        "Setting user state to: '{state}'".format(
            user_id=message.from_user.id, state=state
        )
    )
    await bot.set_state(message.from_user.id, state, message.chat.id)
    await bot.send_message(message.chat.id, "Введите максимальную цену (USD)")


@bot.message_handler(state=UserState.enter_max_price)
async def enter_max_price(message: Message):
    """Ввод максимальной цены для поиска"""
    try:
        price = float(message.text.replace(",", "."))
        is_value_correct = True
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            is_price_correct = price > data["min_price"]
            if is_price_correct:
                data["max_price"] = price
    except ValueError:
        is_value_correct = False

    if all((is_value_correct, is_price_correct)):
        state = UserState.enter_quantity
        logger.info(
            "MAX PRICE state. Received MAX price from user {user_id}. "
            "Setting user state to: '{state}'".format(
                user_id=message.from_user.id, state=state
            )
        )
        await bot.set_state(message.from_user.id, state, message.chat.id)
        msg = "Введите желаемое количество результатов.\nМаксимум {max}".format(
            max=MAX_QUERY_RESULTS
        )
        await bot.send_message(message.chat.id, msg)
    else:
        msg = (
            "Некорректное значение."
            if not is_value_correct
            else "Максимальная цена должна быть выше минимальной."
        )
        msg += "\nПожалуйста, введите максимальную цену еще раз (USD)"
        logger.info(
            "MAX PRICE state. Received incorrect value from user {user_id}. "
            "Asking to repeat".format(user_id=message.from_user.id)
        )
        await bot.send_message(message.chat.id, msg)


@bot.message_handler(state=UserState.enter_quantity, is_digit=True)
async def enter_quantity(message: Message):
    """Ввод желаемого количества результатов для поиска"""
    quantity = int(message.text)
    if 0 < quantity <= MAX_QUERY_RESULTS:
        user_id = message.from_user.id
        chat_id = message.chat.id
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["quantity"] = quantity

        logger.info(
            "ENTER QUANTITY state. Received quantity from user {user_id}. "
            "Calling for API request.".format(user_id=message.from_user.id)
        )
        await fetch_data_for_user(user_id, chat_id)
        await bot.delete_state(user_id, chat_id)
    else:
        logger.info(
            "ENTER QUANTITY state. Received incorrect value from user {user_id}. "
            "Asking to repeat".format(user_id=message.from_user.id)
        )
        msg = (
            "Указанное количество превышает максимально допустимое значение."
            if quantity > MAX_QUERY_RESULTS
            else "Количество должно быть не менее 1"
        )
        msg += (
            "\nПожалуйста, введите желаемое количество результатов еще раз."
            "\nМаксимум {max}".format(max=MAX_QUERY_RESULTS)
        )
        await bot.send_message(message.chat.id, msg)


@bot.message_handler(state=UserState.enter_quantity, is_digit=False)
async def incorrect_quantity(message: Message):
    """Обработка ввода некорректного ввода количества результатов для поиска"""
    logger.info(
        "ENTER QUANTITY state. Received incorrect value from user {user_id}. "
        "Asking to repeat".format(user_id=message.from_user.id)
    )
    msg = (
        "Некорректное значение. Количество должно быть целым числом.\n"
        "Пожалуйста, повторно введите желаемое количество результатов.\n"
        "Максимум {max}".format(max=MAX_QUERY_RESULTS)
    )
    await bot.send_message(message.chat.id, msg)


@bot.message_handler(state=UserState.enter_history_number, is_digit=True)
async def enter_quantity(message: Message):
    """Обработка ввода номера запроса из истории"""
    number = int(message.text)
    user = await get_user_by_id(message.from_user.id)

    if not user or not user.requests:
        logger.info(
            "HISTORY NUMBER state. Received number from user {user_id},"
            "but no requests in history. Informing user".format(
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

    if 0 < number <= len(user_requests):
        request_to_repeat = user_requests[number - 1]
        user_id = message.from_user.id
        chat_id = message.chat.id
        async with bot.retrieve_data(user_id, chat_id) as data:
            data["quantity"] = request_to_repeat.quantity
            data["keyword"] = request_to_repeat.keyword
            if request_to_repeat.sort:
                data["sort"] = request_to_repeat.sort
            if request_to_repeat.min_price and request_to_repeat.max_price:
                data["min_price"] = request_to_repeat.min_price
                data["max_price"] = request_to_repeat.max_price

        logger.info(
            "HISTORY NUMBER state. Received number from user {user_id}. "
            "Calling for API request.".format(user_id=message.from_user.id)
        )
        await fetch_data_for_user(user_id, chat_id, is_repeat=True)
        await bot.delete_state(user_id, chat_id)
    else:
        logger.info(
            "HISTORY NUMBER state. Received incorrect number from user {user_id}. "
            "Asking to repeat".format(user_id=message.from_user.id)
        )
        msg = (
            "В истории нет запроса с таким номером."
            "\nПожалуйста, введите желаемое количество результатов еще раз."
            "\nИсторию запросов можно посмотреть командой /history"
        )
        await bot.send_message(message.chat.id, msg)


@bot.message_handler(state=UserState.enter_history_number, is_digit=False)
async def incorrect_quantity(message: Message):
    """Обработка ввода некорректного номера запроса из истории"""
    logger.info(
        "HISTORY NUMBER state. Received incorrect value from user {user_id}. "
        "Asking to repeat".format(user_id=message.from_user.id)
    )
    msg = (
        "Некорректное значение. Номер должно быть целым числом.\n"
        "Историю запросов можно посмотреть командой /history"
    )
    await bot.send_message(message.chat.id, msg)


bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())
