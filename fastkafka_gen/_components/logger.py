# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Logger.ipynb.

# %% auto 0
__all__ = ['should_suppress_timestamps', 'logger_spaces_added', 'suppress_timestamps', 'get_default_logger_configuration',
           'get_logger', 'set_level']

# %% ../../nbs/Logger.ipynb 2
import logging
import logging.config
from typing import *

# %% ../../nbs/Logger.ipynb 4
# Logger Levels
# CRITICAL = 50
# ERROR = 40
# WARNING = 30
# INFO = 20
# DEBUG = 10
# NOTSET = 0

should_suppress_timestamps: bool = False


def suppress_timestamps(flag: bool = True) -> None:
    """Suppress logger timestamp

    Args:
        flag: If not set, then the default value **True** will be used to suppress the timestamp
            from the logger messages
    """
    global should_suppress_timestamps
    should_suppress_timestamps = flag


def get_default_logger_configuration(level: int = logging.INFO) -> Dict[str, Any]:
    """Return the common configurations for the logger

    Args:
        level: Logger level to set

    Returns:
        A dict with default logger configuration

    """
    global should_suppress_timestamps

    if should_suppress_timestamps:
        FORMAT = "[%(levelname)s] %(name)s: %(message)s"
    else:
        FORMAT = "%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s"

    DATE_FMT = "%y-%m-%d %H:%M:%S"

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": FORMAT, "datefmt": DATE_FMT},
        },
        "handlers": {
            "default": {
                "level": level,
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Default is stderr
            },
        },
        "loggers": {
            "": {"handlers": ["default"], "level": level},  # root logger
        },
    }
    return LOGGING_CONFIG

# %% ../../nbs/Logger.ipynb 8
logger_spaces_added: List[str] = []


def get_logger(
    name: str, *, level: int = logging.INFO, add_spaces: bool = True
) -> logging.Logger:
    """Return the logger class with default logging configuration.

    Args:
        name: Pass the __name__ variable as name while calling
        level: Used to configure logging, default value `logging.INFO` logs
            info messages and up.
        add_spaces:

    Returns:
        The logging.Logger class with default/custom logging configuration

    """
    config = get_default_logger_configuration(level=level)
    logging.config.dictConfig(config)

    logger = logging.getLogger(name)
    return logger

# %% ../../nbs/Logger.ipynb 14
def set_level(level: int) -> None:
    """Set logger level

    Args:
        level: Logger level to set
    """

    # Getting all loggers that has either fastkafka_gen or __main__ in the name
    loggers = [
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if ("fastkafka_gen" in name) or ("__main__" in name)
    ]

    for logger in loggers:
        logger.setLevel(level)
