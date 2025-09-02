from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Sequence
from datetime import datetime
from email.utils import formataddr
from typing import (
    Annotated,
    Any,
    Literal,
    Self,
)

from jsonpath_rfc9535 import (
    JSONPathQuery,
    compile,
)
from pydantic import (
    Base64UrlStr,
    BeforeValidator,
    EmailStr,
    Field,
    FilePath,
    InstanceOf,
    IPvAnyAddress,
    computed_field,
    model_validator,
)
from pydantic_extra_types.domain import DomainStr

from . import (
    HardSchema,
    SoftSchema,
)

JSONPath = Annotated[
    InstanceOf[JSONPathQuery],
    BeforeValidator(compile),
]


class Participant(HardSchema):
    name: str | None = None
    address: EmailStr

    # mailbox: https://datatracker.ietf.org/doc/html/rfc6854#section-3
    # mailbox: https://datatracker.ietf.org/doc/html/rfc5322#section-3.4
    # mailbox: https://datatracker.ietf.org/doc/html/rfc2822#section-3.4
    @computed_field
    @property
    def mailbox(self) -> str:
        pair = self.name, self.address

        return formataddr(pair)


Recipient = Participant | JSONPath | EmailStr | None


class Identifier(ABC, HardSchema):
    label: str | None = None

    @property
    @abstractmethod
    def identifier(self) -> str: ...


# https://datatracker.ietf.org/doc/html/rfc4021#section-2.2.2
class ContentID(Identifier):
    # domain: https://datatracker.ietf.org/doc/html/rfc822#section-6.1
    namespace: EmailStr | None = None

    # content-id: https://datatracker.ietf.org/doc/html/rfc2392#section-2
    # content-id: https://datatracker.ietf.org/doc/html/rfc2111#section-2
    @computed_field
    @property
    def identifier(self) -> str:
        return f"{self.label}.{self.namespace}"


# https://datatracker.ietf.org/doc/html/rfc4021#section-2.1.33
# https://datatracker.ietf.org/doc/html/rfc6783
# https://datatracker.ietf.org/doc/html/rfc5983
class ListID(Identifier):
    # dot-atom-text: https://datatracker.ietf.org/doc/html/rfc5322#section-3.2.3
    # dot-atom-text: https://datatracker.ietf.org/doc/html/rfc2822#section-3.2.4
    # localhost: https://datatracker.ietf.org/doc/html/rfc6761#section-6.3
    # localhost: https://datatracker.ietf.org/doc/html/rfc2606#section-2
    namespace: DomainStr | IPvAnyAddress | Literal["localhost"] = "localhost"

    # list-id: https://datatracker.ietf.org/doc/html/rfc2919#section-2
    @computed_field
    @property
    def identifier(self) -> str:
        if isinstance(self.namespace, IPvAnyAddress):
            return f"{self.label}.{self.namespace}"

        return f"{self.label}.{self.namespace}"


class Attachment(ABC, HardSchema):
    type: str | None = None
    name: str


class AttachmentFile(Attachment):
    file: FilePath


class AttachmentContent(Attachment):
    content: Base64UrlStr | str


class InlineAttachment(Attachment):
    content_id: ContentID | str

    @computed_field
    @property
    def identifier(self) -> str:
        if isinstance(self.content_id, str):
            return self.content_id

        return f"{self.content_id.label}.{self.content_id.namespace}"


class InlineAttachmentFile(InlineAttachment, AttachmentFile): ...


class InlineAttachmentContent(InlineAttachment, AttachmentContent): ...


class Calendar(HardSchema):
    type: Literal["text/calendar"]
    name: str
    summary: str
    description: str | None = None
    start: datetime
    end: datetime | None = None
    organizer: Participant | str | None = None


class Template(ABC, HardSchema):
    type: Literal["text/html", "text/plain"] = Field(default="text/html")
    inline_attachments: Sequence[InlineAttachmentFile | InlineAttachmentContent] | None = None


class TemplateFile(Template):
    file: FilePath


class TemplateContent(Template):
    content: Base64UrlStr | str


class Email(HardSchema):
    # from: https://datatracker.ietf.org/doc/html/rfc6854#section-2.1
    originator: Participant | EmailStr
    author: Participant | EmailStr | None = None
    sender: Participant | EmailStr | None = None
    contact: Participant | EmailStr | None = None
    subject: str | None = None
    template: TemplateFile | TemplateContent | FilePath
    attachments: Sequence[AttachmentFile | AttachmentContent | Calendar | FilePath] | None = None


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
    message_id: str | None = Field(default=None)

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if all(field is None for field in (self.destination, self.carbon_copy, self.blind_carbon_copy)):
            raise ValueError("At least one of destination, carbon_copy, or blind_carbon_copy is required.")

        return self


class MailingList(HardSchema):
    list_id: ListID | str
    file: FilePath
    context: MailingListContext = Field(json_schema_extra=json_schema_extra)

    @computed_field
    @property
    def identifier(self) -> str:
        if isinstance(self.list_id, str):
            return self.list_id

        return self.list_id.identifier


class LogContext(SoftSchema): ...


class Logging(HardSchema):
    file: FilePath
    format: str = ""
    context: LogContext


class MultiThread(HardSchema): ...


class Specification(HardSchema):
    email: Email
    mailing_list: MailingList
    logging: Logging | None = None
    multithread: MultiThread | None = None


if __name__ == "__main__":
    from json import dump
    from sys import stdout

    dump(
        Specification.model_json_schema(mode="validation"),
        stdout,
        separators=(",", ":"),
    )
