from typing import Any, Literal, NotRequired, TypedDict, Unpack

from django_typed_settings.environ import env_key, env_key_required

type KNOWN_ENGINES = Literal[
    "django.db.backends.postgresql",
    "django.db.backends.mysql",
    "django.db.backends.sqlite3",
    "django.db.backends.oracle",
]


class DjangoDatabaseOptions(TypedDict):
    isolation_level: NotRequired[Any]


class DjangoDatabaseConfiguration(TypedDict):
    ENGINE: NotRequired[KNOWN_ENGINES | str]
    HOST: NotRequired[str]
    NAME: NotRequired[str]
    PORT: NotRequired[str]
    CONN_MAX_AGE: NotRequired[int]
    CONN_HEALTH_CHECKS: NotRequired[bool]
    PASSWORD: NotRequired[str]
    USER: NotRequired[str]
    OPTIONS: NotRequired[DjangoDatabaseOptions]


def env_key_database(
    prefix: str = "DJANGO_DATABASE",
    always_use_engine: KNOWN_ENGINES | None = None,
    **kwargs: Unpack[DjangoDatabaseConfiguration],
) -> DjangoDatabaseConfiguration:
    engine = always_use_engine or env_key_required(
        key=f"{prefix}_ENGINE",
        as_type=str,
    )
    return {
        "ENGINE": engine,
        "PASSWORD": env_key(f"{prefix}_PASSWORD", default=""),
        "HOST": env_key(f"{prefix}_HOST", default=""),
        "NAME": env_key(f"{prefix}_NAME", default=""),
        "PORT": env_key(f"{prefix}_PORT", as_type=str, default=""),
        "USER": env_key(f"{prefix}_USER", as_type=str, default=""),
        "CONN_MAX_AGE": env_key(f"{prefix}_CONN_MAX_AGE", as_type=int, default=0),
        "CONN_HEALTH_CHECKS": env_key(
            f"{prefix}_CONN_HEALTH_CHECKS",
            as_type=bool,
            default=False,
        ),
        **kwargs,
    }
