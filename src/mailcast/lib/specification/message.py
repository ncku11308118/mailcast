from abc import ABC
from collections.abc import Sequence
from datetime import datetime
from email.utils import formataddr
from typing import (
    Annotated,
    Literal,
    override,
)

from jsonpath_rfc9535 import (
    JSONPathQuery,
    compile,
)
from pydantic import (
    BaseModel,
    Field,
    InstanceOf,
    PlainSerializer,
    PlainValidator,
)
from pydantic.networks import (
    EmailStr,
    NameEmail,
)
from pydantic.types import (
    Base64UrlStr,
    FilePath,
)

from .rfc import (
    ListIdentifier,
    MIMEEntity,
)

# https://datatracker.ietf.org/doc/html/rfc9535
type JSONPath = Annotated[
    InstanceOf[JSONPathQuery],
    PlainValidator(compile, json_schema_input_type=str),
    PlainSerializer(str, return_type=str),
]
type Address = EmailStr
type Mailbox = Participant | EmailStr | NameEmail
type MailboxList = Sequence[Mailbox]
type AddressList = Sequence[Address]
type GroupList = MailboxList
type DynamicMailbox = Mailbox | JSONPath
type ListID = Annotated[
    ListIdentifier,
    PlainValidator(
        ListIdentifier.transform,
        json_schema_input_type=ListIdentifier | str,
    ),
]


# mailbox: https://datatracker.ietf.org/doc/html/rfc822#section-6.1
# mailbox: https://datatracker.ietf.org/doc/html/rfc2822#section-3.4
# mailbox: https://datatracker.ietf.org/doc/html/rfc5322#section-3.4
# https://datatracker.ietf.org/doc/html/rfc6854#section-3
class Participant(BaseModel):
    name: str | None = Field(default=None)
    address: EmailStr

    @override
    def __str__(self) -> str:
        pair = self.name, self.address

        return formataddr(pair)


class MessageHeaders(BaseModel, extra="allow"):
    # https://datatracker.ietf.org/doc/html/rfc2822#section-3.6.2
    # https://datatracker.ietf.org/doc/html/rfc5322#section-3.6.2
    # https://datatracker.ietf.org/doc/html/rfc6854#section-2.1
    from_: DynamicMailbox | Sequence[DynamicMailbox] = Field(validation_alias="from")
    sender: DynamicMailbox | None = Field(default=None)
    reply_to: DynamicMailbox | Sequence[DynamicMailbox] | None = Field(default=None)
    return_path: DynamicMailbox | None = Field(default=None)
    to: DynamicMailbox | Sequence[DynamicMailbox] | None = Field(default=None)
    cc: DynamicMailbox | Sequence[DynamicMailbox] | None = Field(default=None)
    bcc: DynamicMailbox | Sequence[DynamicMailbox] | None = Field(default=None)
    subject: str | None = Field(default=None)
    list_id: ListID | None = Field(default=None)
    message_id: JSONPath | None = Field(default=None)


class Attachment[T: str | None](MIMEEntity[T], ABC):
    name: str


class AttachmentFile(Attachment[str | None]):
    file: FilePath


class AttachmentContent(Attachment[str | None]):
    content: Base64UrlStr | str


class InlineAttachment(Attachment[str | None]):
    content_id: str | None


class InlineAttachmentFile(AttachmentFile, InlineAttachment): ...


class InlineAttachmentContent(AttachmentContent, InlineAttachment): ...


class Template(MIMEEntity[Literal["text/html", "text/plain"]], ABC):
    inline_attachments: Sequence[InlineAttachmentFile | InlineAttachmentContent] | None = Field(default=None)


class TemplateFile(Template):
    file: FilePath


class TemplateContent(Template):
    content: Base64UrlStr | str


class AttachmentCalendar(Attachment[Literal["text/calendar"]]):
    summary: str
    description: str | None = Field(default=None)
    start: datetime
    end: datetime | None = Field(default=None)
    organizer: Participant | str | None = Field(default=None)


class Message(BaseModel):
    headers: MessageHeaders
    template: TemplateFile | TemplateContent | FilePath
    attachments: Sequence[AttachmentFile | AttachmentContent | AttachmentCalendar | FilePath] | None = Field(
        default=None
    )
