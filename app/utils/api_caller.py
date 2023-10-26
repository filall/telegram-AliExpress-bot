import random
import time

import aiohttp

from app.config_data.config import (FACTOR, HEADERS, MAX_ATTEMPTS, MAX_DELAY,
                                    MIN_DELAY, RANDOMNESS, RAPID_API_URI)
from app.database.models import create_user_request_history
from app.loader import bot
from app.logger import base_logger as logger
from app.utils.result_sender import (send_error_report_to_user,
                                     send_result_to_user)


async def fetch_data_for_user(
    user_id: int, chat_id: int, is_repeat: bool = False
) -> None:
    request_data = {"user_id": user_id, "chat_id": chat_id}
    history_request_data = {"user_id": user_id}
    async with bot.retrieve_data(user_id, chat_id) as data:
        query_params = {"search": data["keyword"]}
        request_data["keyword"] = data["keyword"]
        history_request_data["keyword"] = data["keyword"]
        try:
            query_params["sort"] = data["sort"]
            history_request_data["sort"] = data["sort"]
        except KeyError:
            pass

        try:
            query_params["minPrice"] = data["min_price"]
            query_params["maxPrice"] = data["max_price"]
            history_request_data["min_price"] = data["min_price"]
            history_request_data["max_price"] = data["max_price"]
        except KeyError:
            pass

        request_data["quantity"] = data["quantity"]
        history_request_data["quantity"] = data["quantity"]

        if not is_repeat:
            history_request_data["command"] = data["command"]
            logger.info(
                "Adding request from user {user_id} to history".format(
                    user_id=user_id,
                )
            )
            await create_user_request_history(**history_request_data)

    delay = MIN_DELAY
    attempt = 1
    while True:
        logger.info(
            "Calling API for user {user_id}. Attempt №{attempt}".format(
                user_id=user_id, attempt=attempt
            )
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(
                RAPID_API_URI, headers=HEADERS, params=query_params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    await send_result_to_user(request_data, result)
                    break
                else:
                    logger.info(
                        "Request №{attempt} for user {user_id} "
                        "has returned code {code}".format(
                            user_id=user_id, attempt=attempt, code=response.status
                        )
                    )
                    if attempt < MAX_ATTEMPTS:
                        time.sleep(delay + random.uniform(-RANDOMNESS, RANDOMNESS))
                        delay = min(delay * FACTOR, MAX_DELAY)
                        attempt += 1
                    else:
                        logger.info(
                            "Request for user {user_id} has reached maximum "
                            "amount of attempts "
                            "and was unsuccessfull".format(user_id=user_id)
                        )
                        await send_error_report_to_user(request_data)
                        break
