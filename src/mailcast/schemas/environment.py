from functools import cache
from os import getenv
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    NonNegativeInt,
    SecretStr,
)
from pydantic_extra_types.timezone_name import TimeZoneName


class Environment(BaseModel, frozen=True):
    time_zone: TimeZoneName = Field(alias="TZ")

    smtp_hostname: str
    smtp_port: NonNegativeInt = Field(le=65535)
    smtp_username: str
    smtp_password: SecretStr

    @classmethod
    @cache
    def load(cls) -> Self:
        result: dict[str, str | None] = dict()

        for name, field in cls.model_fields.items():
            if field.exclude:
                continue

            value = getenv(field.alias or name.upper())

            if value is None or value == "":
                continue

            result[name] = value

        return cls.model_validate(result, by_name=True)
