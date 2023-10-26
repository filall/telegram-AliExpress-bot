import logging.config

from config_data.logging_config import config

logging.config.dictConfig(config)
base_logger = logging.getLogger("app")
bot_logger = logging.getLogger("app.bot")
