from collections.abc import Sequence
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from mimetypes import (
    guess_extension,
    guess_file_type,
)
from pathlib import Path
from string import Template
from urllib.parse import quote

from html_to_markdown import convert_to_markdown
from icalendar import (
    Calendar,
    Event,
    vCalAddress,
    vText,
)
from pydantic import FilePath

from ..specification import Specification
from ..specification.message import (
    AttachmentCalendar,
    AttachmentContent,
    AttachmentFile,
    InlineAttachmentContent,
    InlineAttachmentFile,
    TemplateContent,
    TemplateFile,
)


class EmailBuilder:
    message: MIMEMultipart

    def __init__(
        self,
        email_address: str,  # TODO
        specification: Specification,
    ):
        template = specification.message.template

        mixed_message = self.__class__.seal_mixed_message(specification.message.attachments)
        alternative_message = self.__class__.seal_alternative_message(email_address, template)

        mixed_message.attach(alternative_message)

        self.message = mixed_message
        self.specification = specification

    @classmethod
    def seal_related_message(
        cls,
        content: str,
        inline_attachments: Sequence[InlineAttachmentFile | InlineAttachmentContent] | None = None,
    ) -> MIMEMultipart:
        message = MIMEMultipart("related")  # multipart/related
        html = MIMEText(content, "html", "utf-8")

        message.attach(html)

        for inline_attachment in inline_attachments or []:
            file_type = (*inline_attachment.type.split("/", 1), None)[:2] if inline_attachment.type else (None, None)

            if isinstance(inline_attachment, InlineAttachmentFile):
                payload = inline_attachment.file.read_bytes()

                if file_type == (None, None):
                    file_type = guess_file_type(inline_attachment.file)
            else:
                payload = inline_attachment.content.encode("utf-8")

            _type, _subtype = file_type

            if _type is None or _subtype is None:
                _type, _subtype = "application", "octet-stream"

            part = MIMENonMultipart(_type, _subtype)
            part["Content-ID"] = inline_attachment.content_id or make_msgid()  # TODO

            part.set_payload(payload)
            encode_base64(part)
            message.attach(part)

        return message

    @classmethod
    def seal_alternative_message(
        cls,
        email_address: str,
        template: TemplateFile | TemplateContent | FilePath,
    ) -> MIMEMultipart:
        message = MIMEMultipart("alternative")  # multipart/alternative

        if isinstance(template, Path):
            content = template.read_text("utf-8")
            inline_attachments = None
        elif isinstance(template, TemplateFile):
            content = template.file.read_text("utf-8")
            inline_attachments = template.inline_attachments
        else:
            content = template.content
            inline_attachments = template.inline_attachments

        content = Template(content).safe_substitute(dict(email_address=quote(email_address)))  # TODO
        text = MIMEText(convert_to_markdown(content, strip=("table", "tr", "th", "td")), "plain", "utf-8")
        related_message = cls.seal_related_message(
            content,
            inline_attachments,
        )

        message.attach(text)
        message.attach(related_message)

        return message

    @classmethod
    def seal_mixed_message(
        cls,
        attachments: Sequence[AttachmentFile | AttachmentContent | AttachmentCalendar | FilePath] | None = None,
    ) -> MIMEMultipart:
        message = MIMEMultipart("mixed")  # multipart/mixed

        for attachment in attachments or []:
            file_type = None, None

            if isinstance(attachment, Path):
                file_stem = attachment.stem
                file_type = guess_file_type(attachment)
                payload = attachment.read_bytes()
            else:
                file_type = (*attachment.type.split("/", 1), None)[:2] if attachment.type else (None, None)

                if isinstance(attachment, AttachmentFile):
                    file_stem = attachment.file.stem
                    payload = attachment.file.read_bytes()

                    if file_type == (None, None):
                        file_type = guess_file_type(attachment.file)
                elif isinstance(attachment, AttachmentCalendar):
                    organizer = vCalAddress("MAILTO:evs_service@mail.moe.gov.tw")
                    calendar = Calendar()
                    event = Event(
                        summary=attachment.summary,
                        description=attachment.description,
                        organizer=organizer,
                    )

                    organizer.name = vText("教育網站資安弱點掃描防護服務計畫", encoding="utf-8")
                    event.start = attachment.start
                    event.end = attachment.end

                    calendar.add_component(event)

                    file_stem = "115年教育體系資安專業訓練課程_網站應⽤程式安全"  # TODO
                    payload = calendar.to_ical()
                else:
                    file_stem = "noname"
                    payload = attachment.content.encode("utf-8")

            _type, _subtype = file_type

            if _type is None or _subtype is None:
                _type, _subtype = "application", "octet-stream"

            part = MIMENonMultipart(_type, _subtype)
            file_extension = guess_extension(f"{_type}/{_subtype}") or ""
            file_name = f"{file_stem}{file_extension}"

            part.add_header("Content-Disposition", "attachment", filename=file_name)
            part.set_payload(payload)
            encode_base64(part)
            message.attach(part)

        return message
