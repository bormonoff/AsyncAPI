import logging.config

LOGGER_NAME = "etl_logger"
LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {
            "format": "[%(levelname)s:%(asctime)s | %(module)s:%(funcName)s:%(lineno)s:%(name)s] %(message)s"
        },
    },
    "handlers": {
        "stream_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default_formatter",
        },
    },
    "loggers": {
        LOGGER_NAME: {
            "handlers": ["stream_handler"],
            "level": "DEBUG",
            "propagate": True,
        }
    },
}

logging.config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger(LOGGER_NAME)
