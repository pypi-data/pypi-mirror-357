from datetime import timedelta

from django_typed_settings.environ import env_key_required


def env_key_timedelta(key: str) -> timedelta:
    """WARNING. Preview function"""
    raw_value = env_key_required(key=key, as_type=str)
    base = int("".join(v for v in raw_value if v.isdigit()))
    multiplier = str(
        "".join(v for v in raw_value if not v.isdigit() and not v.isspace())
    )
    multiplier_type = {
        "ms": "milliseconds",
        "mcs": "microseconds",
        "w": "weeks",
        "week": "weeks",
        "weeks": "weeks",
        "h": "hours",
        "hour": "hours",
        "hours": "hours",
        "m": "minutes",
        "min": "minutes",
        "minute": "minutes",
        "minutes": "minutes",
        "s": "seconds",
        "sec": "seconds",
        "second": "seconds",
        "seconds": "seconds",
        "d": "days",
        "day": "days",
        "days": "days",
    }[multiplier]
    return timedelta(**{multiplier_type: base})
