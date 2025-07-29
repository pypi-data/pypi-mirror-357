from typing import Literal

from django_typed_settings.environ import env_key, env_key_required
from django_typed_settings.exceptions import DjangoSettingsInvalidLoggingLevelError

type LOGGING_LEVELS_T = Literal[
    "CRITICAL", "FATAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG", "NOTSET"
]
LOGGING_LEVELS = (
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
    "NOTSET",
)


def env_key_logging_level(
    key: str,
    default: LOGGING_LEVELS_T | None = None,
) -> LOGGING_LEVELS_T:
    """
    Return logging level key from environment variable and optional default fallback.

    :param key: Name of key to load from environment.
    :param default: Value to return when there is no such key or None if strict.

    :returns: Value from environment as valid logging level.

    :raises DjangoSettingsMissingRequiredKeyError: If key is missing and default is None
    """
    raw_level = (
        env_key_required(key, as_type=str)
        if default is None
        else env_key(key, as_type=str, default=default)
    )
    if raw_level not in LOGGING_LEVELS:
        if default:
            return default
        raise DjangoSettingsInvalidLoggingLevelError(key, raw_level)
    return raw_level
