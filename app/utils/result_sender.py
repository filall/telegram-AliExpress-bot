from typing import Dict, List, Optional, Tuple

from app.loader import bot
from app.logger import bot_logger as logger
from app.utils.picture_loader import get_pictures

TELEGRAM_MESSAGE_LENGTH = 4096


async def send_result_to_user(request_data: Dict, result: Dict) -> None:
    """Возврат результата запроса пользователю"""
    user_id, chat_id = request_data["user_id"], request_data["chat_id"]
    # Иногда api возвращает ошибку в теле ответа, несмотря на код 200
    if error := result.get("error"):
        logger.info(
            "Request for user {user_id} returned an error: '{error}'".format(
                user_id=user_id, error=error
            )
        )
        await send_error_report_to_user(request_data)
        return

    items: List[Dict] = result["body"][: request_data["quantity"]]
    idx = 1
    result_strings: List[str] = []
    picture_uris = []
    for item in items:
        parsed_values = get_item_string_and_picture_uri(item)
        if not parsed_values:
            continue

        item_string, picture_uri = parsed_values[0], parsed_values[1]

        item_string = "{index}) ".format(index=idx) + item_string
        result_strings.append(item_string)
        picture_uris.append(picture_uri)
        idx += 1

    # Помимо отсутствия результата, проверяем экстремальный случай,
    # когда все объекты вернулись с пустыми элементами
    if len(items) == 0 or not result_strings:
        logger.info(
            "Request for user {user_id} returned no items. Informing user".format(
                user_id=user_id
            )
        )
        await bot.send_message(
            chat_id,
            "К сожалению, по вашему запросу ничего не найдено :-("
            "\nПопробуйте поискать что-нибудь еще.",
        )
        return

    logger.info(
        "Received response for request from user {user_id}. "
        "Fetching pictures.".format(user_id=user_id)
    )

    pictures = await get_pictures(picture_uris)

    logger.info(
        "Received pictures for request from user {user_id}. "
        "Sending {count} result(s) to the user .".format(
            user_id=user_id, count=len(result_strings)
        )
    )

    msg = "По вашему запросу '{keyword}' найдено:\n\n".format(
        keyword=request_data["keyword"]
    )
    await bot.send_message(chat_id, msg)
    for idx in range(len(result_strings)):
        await bot.send_photo(chat_id, pictures[idx], result_strings[idx])
    await bot.send_message(chat_id, "Я готов принять Ваш следующий запрос.")


def get_item_string_and_picture_uri(item: Dict) -> Optional[Tuple[str, str]]:
    """Преобразование объекта результата поиска в строку"""
    title = item.get("title")
    item_uri = item.get("link")
    # Оборачиваем в блок Try на случай если поле prices есть, но его значение None
    try:
        price = item.get("prices", {}).get("salePrice", {}).get("formattedPrice")
        picture_uri = item.get("image", {}).get("imgUrl")
    except AttributeError:
        price = None
        picture_uri = None
    # Иногда среди результатов попадаются объекты, у которых все элементы являются None,
    # поэтому делаем проверку
    if title and item_uri and price and picture_uri:
        return (
            "{title}\n{price}\n{uri}\n\n".format(
                title=title, price=price, uri=item_uri
            ),
            picture_uri,
        )
    else:
        return None


async def send_error_report_to_user(request_data: Dict) -> None:
    """Отправка уведомления о неуспешной попытке запроса"""
    user_id, chat_id = request_data["user_id"], request_data["chat_id"]
    logger.info(
        "Informing user {user_id} about unsuccessful result".format(user_id=user_id)
    )
    await bot.send_message(
        chat_id,
        "К сожалению, "
        "в данный момент мне не удалось получить результат по вашему запросу."
        "\nПожалуйста, попробуйте повторить запрос позже "
        "или попробуйте поискать-то-нибудь еще.",
    )
