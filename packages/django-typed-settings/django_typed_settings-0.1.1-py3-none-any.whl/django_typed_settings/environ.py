from collections.abc import Sequence
from decimal import InvalidOperation
from os import environ
from types import EllipsisType
from typing import TYPE_CHECKING, cast

from django_typed_settings.booleans import VALUE_TO_BOOLEAN
from django_typed_settings.exceptions import (
    DjangoSettingsInvalidFlagValueError,
    DjangoSettingsKeyValueError,
    DjangoSettingsMissingRequiredKeyError,
)

if TYPE_CHECKING:
    from decimal import Decimal

# Python currently does not provide (or I not find that) ways to validate not at runtime
# that type acceps atleast 1 argument in constructor.
type INITABLE_TYPES = str | int | float | Decimal


def env_key[T: INITABLE_TYPES, N: None](
    key: str,
    as_type: type[T] = str,
    *,
    default: T | N = None,
    strict: bool = True,
) -> T | N:
    """
    Return raw key from environment variable with casting to type and default fallback.

    :param key: Name of key to load from environment.
    :param as_type: Type which will instantiated with key value in constructor.
    :param default: Value to return when there is no such key.

    :returns: Value from environment of type `as_type` or default one (type same as `as_type`)
    """
    value = environ.get(key, default=Ellipsis)
    if isinstance(value, EllipsisType):
        return default
    return _cast_to_type(key, as_type, value, strict=strict, default=default)


def env_key_required[T: INITABLE_TYPES](
    key: str,
    as_type: type[T] = str,
) -> T:
    """
    Return raw key from environment variable with casting to type or raise exception if not found.

    :param key: Name of key to load from environment.
    :param as_type: Type which will instantiated with key value in constructor.

    :returns: Value from environment of type `as_type`
    :raises DjangoSettingsMissingRequiredKeyError: If key is missing
    """
    value = environ.get(key, default=Ellipsis)
    if isinstance(value, EllipsisType):
        raise DjangoSettingsMissingRequiredKeyError(key, as_type)
    casted_value = _cast_to_type(key, as_type, value, strict=True, default=None)
    assert casted_value is not None, "Probable an bug in `env_key_required`"
    return casted_value


def env_key_sequence[T: INITABLE_TYPES](
    key: str,
    as_type: type[T] = str,
    *,
    required: bool = False,
) -> Sequence[T]:
    """
    Return key from environment variable parsed as sequence (immutable type) and elements casted to type.

    :param key: Name of key to load from environment.
    :param as_type: Type which will instantiated with key value in constructor.

    :returns: Sequence of values from environment of type `as_type`
    """
    raw_value = environ.get(key, default=Ellipsis)
    if isinstance(raw_value, EllipsisType):
        if required:
            raise DjangoSettingsMissingRequiredKeyError(key, as_type, as_sequence=True)
        return []

    def parse_sequence_element(raw_value: str) -> T:
        value = _cast_to_type(
            key, as_type=as_type, value=raw_value, strict=True, default=None
        )

        assert value is not None, "Probable an bug in `env_key_sequence`"
        return value

    generator = map(
        parse_sequence_element,
        map(str.strip, raw_value.removeprefix("[").removesuffix("]").split(",")),
    )
    return tuple(generator)


def env_key_flag(key: str, *, default: bool | None = None) -> bool:
    """
    Return boolean flag key from environment variable, raise exception if default is None and not found.

    :param key: Name of key to load from environment.
    :param default: Default flag value or None if raise on missing.

    :returns: Value of an flag as boolean.
    :raises DjangoSettingsMissingRequiredKeyError: If default is None and key is missing.
    """
    raw_value = env_key(key, as_type=str, default=None)
    if not raw_value:
        if default:
            return default
        raise DjangoSettingsMissingRequiredKeyError(key, bool)

    value = raw_value.lower().strip()
    if value not in VALUE_TO_BOOLEAN:
        raise DjangoSettingsInvalidFlagValueError(key, value)

    return VALUE_TO_BOOLEAN[value]


#####
### Private APIs
#####


def _cast_to_type[T: INITABLE_TYPES, N: None | EllipsisType](
    key: str,
    as_type: type[T],
    value: str,
    strict: bool,
    default: T | N,
) -> T | N:
    """Internal cast to desired type with strict raise"""
    try:
        if as_type is bool:
            return cast("T", env_key_flag(key, default=None))
        return as_type(value)
    except (ValueError, InvalidOperation) as e:
        if strict:
            raise DjangoSettingsKeyValueError(key, value, as_type) from e
        return default
