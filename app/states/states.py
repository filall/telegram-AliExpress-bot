from telebot.asyncio_handler_backends import State, StatesGroup


class UserState(StatesGroup):
    enter_keyword = State()
    enter_quantity = State()
    enter_min_price = State()
    enter_max_price = State()
    enter_history_number = State()
    lucky = State()
