from typing import (
    Any,
    Self,
)

from pydantic import (
    EmailStr,
    Field,
    FilePath,
    model_validator,
)

from . import (
    HardSchema,
)


class Message(HardSchema):
    # from: https://datatracker.ietf.org/doc/html/rfc6854#section-2.1
    originator: Participant | EmailStr
    author: Participant | EmailStr | None = None
    sender: Participant | EmailStr | None = None
    contact: Participant | EmailStr | None = None


def json_schema_extra(json_schema: dict[str, Any]) -> None:
    extra = {
        "anyOf": [
            {"required": ["destination"]},
            {"required": ["carbon_copy"]},
            {"required": ["blind_carbon_copy"]},
        ]
    }

    json_schema.update(extra)


class MailingListContext(HardSchema):
    destination: Recipient = Field(default=None)
    carbon_copy: Recipient = Field(default=None)
    blind_carbon_copy: Recipient = Field(default=None)

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if all(field is None for field in (self.destination, self.carbon_copy, self.blind_carbon_copy)):
            raise ValueError("At least one of destination, carbon_copy, or blind_carbon_copy is required.")

        return self


class Logging(HardSchema):
    file: FilePath
    format: str = ""
    context: LogContext
