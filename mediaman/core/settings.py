"""
Settings and constants.
"""

LOGGER_NAME_PREFIX = "mattccs"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)s - %(funcName)s() - %(message)s"
EXTRA_LOG_LEVELS = [("TRACE", 5)]
BASE_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG_LEVELS = [e[0] for e in EXTRA_LOG_LEVELS] + BASE_LOG_LEVELS
DEFAULT_LOG_LEVEL = "WARNING"

VERSION = 2
