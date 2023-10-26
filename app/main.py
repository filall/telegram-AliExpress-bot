import asyncio

import handlers  # noqa
from utils.set_bot_commands import set_bot_commands

from app.database.database import create_models, shutdown
from app.loader import bot
from app.logger import base_logger as logger


async def main():
    logger.debug("Calling DB models creation")
    await create_models()
    logger.debug("Calling bot commands setup")
    await set_bot_commands(bot)
    logger.debug("Starting bot")
    await bot.infinity_polling()
    await shutdown()
    logger.debug("Bot has been stopped")


if __name__ == "__main__":
    asyncio.run(main())
