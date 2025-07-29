from django_typed_settings.booleans import VALUE_TO_BOOLEAN


class DjangoSettingsMissingRequiredKeyError(Exception):
    def __init__(
        self,
        key: str,
        as_type: type,
        as_sequence: bool = False,
    ) -> None:
        expected_type = (
            f"Sequence[of `{as_type.__name__}`]" if as_sequence else as_type.__name__
        )
        super().__init__(
            f"Missing required environment key `{key}` (of type: `{expected_type}`)!"
        )


class DjangoSettingsInvalidFlagValueError(Exception):
    def __init__(self, key: str, value: str) -> None:
        possible_flags = ", ".join(VALUE_TO_BOOLEAN.keys())
        super().__init__(
            f"Expected environment key `{key}` will be an flag but got `{value}`. Possible values: `{possible_flags}`"
        )


class DjangoSettingsKeyValueError(Exception):
    def __init__(
        self,
        key: str,
        value: str,
        as_type: type,
    ) -> None:
        super().__init__(
            f"Value error for environment key `{key}` with value `{value}` while tried to cast to `{as_type.__name__}`!"
        )


class DjangoSettingsInvalidLoggingLevelError(Exception):
    def __init__(
        self,
        key: str,
        value: str,
    ) -> None:
        super().__init__(
            f"Value error for environment key `{key}` with value `{value}` expected it to be an logging level!"
        )
