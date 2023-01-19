"""
Tools for caching values in Redis, if it's configured and available.
"""

import json
import typing

from mediaman import config
from mediaman.core import logtools


REDIS = None
logger = logtools.new_logger(__name__)

if (USE_REDIS := bool(config.load("redis-cache", default=False))):
    try:
        import redis
        REDIS = redis.Redis()
    except ImportError:
        logger.warning("[!] Failed to import redis even though it was configured!", exc_info=True)
    except Exception:
        logger.error("[!] Something went wrong while initializing Redis!", exc_info=True)


# TODO(mcotton): hash code, hash config file, prefix all keys with that


def put_in_cache(key, value) -> None:
    global REDIS
    if not REDIS:
        logger.debug("[.] Cache disabled or not available; won't put.")
        return

    try:
        json_value = json.dumps(value)
    except (TypeError, ValueError):
        logger.error(f"[!] Failed to serialize redis value ({value}) as JSON -- something bad is happening!", exc_info=True)

    try:
        REDIS.setex(name=key, time=60, value=json_value)
        logger.debug(f"[+] Set value for {repr(key)} in cache")
    except Exception:
        logger.warning("[!] Failed to put in redis even though it was configured!", exc_info=True)


def get_from_cache(key) -> typing.Optional[typing.Any]:
    global REDIS
    if not REDIS:
        logger.debug("[.] Cache disabled or not available; won't get.")
        return None

    try:
        json_value = REDIS.get(name=key)
    except Exception:
        logger.warning("[!] Failed to get from redis even though it was configured!", exc_info=True)
        return None

    if not json_value:
        return None

    try:
        value = json.loads(json_value)
        logger.debug(f"[+] Cache hit for {repr(key)}")
        return value
    except (TypeError, ValueError):
        logger.error(f"[!] Failed to deserialize redis value ({json_value}) as JSON -- something bad is happening!", exc_info=True)
