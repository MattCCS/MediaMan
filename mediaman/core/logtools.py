"""
Useful logging utilities.
"""

import logging

from mediaman.core import settings

logging.basicConfig(format=settings.LOG_FORMAT)


__all__ = [
    "new_logger",
    "get_logger",
    "set_level",
]


# TODO: surely there's a cleaner way to add extra log levels...
for (name, level) in settings.EXTRA_LOG_LEVELS:
    logging.addLevelName(level, name)
    setattr(logging.Logger, name.lower(), lambda self, *args, **kwargs: self.log(level, *args, **kwargs))



def prefixed(name=None):
    if name is None:
        return settings.LOGGER_NAME_PREFIX
    else:
        return "{}.{}".format(settings.LOGGER_NAME_PREFIX, name)


def get_logger(name=None):
    """
    Equivalent to new_logger(), but doesn't reset its log level.
    """
    logger = logging.getLogger(prefixed(name=name))
    return logger


def new_logger(name):
    """
    Returns the requested logger, with the log level set to 'NOTSET'.
    """
    logger = get_logger(name=name)
    logger.setLevel(logging.NOTSET)  # Allows log level inheritance
    return logger


def set_level(level_or_name, logger=None):
    """
    Sets the level of the given logger to the given level (e.g. 10)
    or the level defined by the given name (e.g., "DEBUG").

    If no logger is provided, the root logger's level is set.

    For reference, check mediaman.settings.LOG_LEVELS,
    or https://docs.python.org/3/library/logging.html#levels.
    """
    # NOTE: Python's logging.getLevelName is perhaps
    #       the most confused function of all time.
    if logger is None:
        logger = get_logger()
    logger.setLevel(logging.getLevelName(level_or_name))


def add_log_parser(parser, logger=None):
    """
    Adds an optional flag to the given parser to set the
    given logger's initial log level based on user input.

    If no logger is provided, the root logger's level is set.
    """

    def set_level_on_parse(level):
        if level in settings.LOG_LEVELS:
            set_level(level, logger=logger)
        return level

    parser.add_argument("--log",
                        dest="log-level",
                        default=settings.DEFAULT_LOG_LEVEL,
                        type=set_level_on_parse,
                        choices=settings.LOG_LEVELS,
                        help="Set the logging level (default: %(default)s)")
