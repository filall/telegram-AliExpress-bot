config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "%(levelname)s | %(name)s | %(asctime)s | %(pathname)s | %(lineno)d | %(message)s"  # noqa
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "base",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
        "rotating_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "H",
            "interval": 12,
            "backupCount": 3,
            "level": "DEBUG",
            "formatter": "base",
            "filename": "app.log",
        },
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "rotating_file"],
        },
        "app.bot": {
            "level": "INFO",
            "handlers": ["console", "rotating_file"],
            "propagate": False,
        },
    },
}
