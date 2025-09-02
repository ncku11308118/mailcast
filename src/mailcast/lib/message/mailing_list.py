from collections.abc import Sequence
from email import message_from_bytes
from email.message import Message
from email.utils import (
    formataddr,
    make_msgid,
)
from smtplib import (
    SMTP,
    SMTPException,
)
from typing import (
    Literal,
    Self,
)
from uuid import uuid4

AddressPair = tuple[str | None, str]
Importance = Literal["low", "normal", "high"]
Priority = Literal["non-urgent", "normal", "urgent"]
Sensitivity = Literal["personal", "private", "company confidential"]


class MailingList:
    collection: list[Message]

    originator: AddressPair
    author: AddressPair
    sender: AddressPair
    contact: AddressPair | None
    identifier: AddressPair
    namespace: str

    def __init__(
        self,
        originator: AddressPair,
        *,
        author: AddressPair | None = None,
        sender: AddressPair | None = None,
        contact: AddressPair | None = None,
        namespace: str | None = None,
        identifier: AddressPair | None = None,
    ):
        self.collection = []

        self.originator = originator
        self.author = author or originator
        self.sender = sender or originator
        self.contact = contact
        self.namespace = namespace or originator[1].rsplit("@", 1)[0]
        self.identifier = identifier or (None, f"{uuid4().hex}.")

    def __iter__(self):
        return iter(self.collection)

    def seal(
        self,
        subject: str,
        message: Message,
        original: Sequence[AddressPair] | None = None,
        carbon_copy: Sequence[AddressPair] | None = None,
        blind_carbon_copy: Sequence[AddressPair] | None = None,
        *,
        importance: Importance = "normal",
        priority: Priority = "normal",
        sensitivity: Sensitivity = "personal",
    ) -> Self:
        if (original or carbon_copy or blind_carbon_copy) is None:
            raise ValueError("At least one recipient must be specified")

        copy = message_from_bytes(message.as_bytes())

        copy.add_header("From", formataddr(self.author))
        copy.add_header("Sender", formataddr(self.sender))
        copy.add_header("Return-Path", formataddr(self.originator))

        if original:
            copy.add_header("To", formataddr(original))

        if carbon_copy:
            copy.add_header("Cc", formataddr(original))

        if blind_carbon_copy:
            copy.add_header("Bcc", formataddr(original))

        copy.add_header("Subject", subject)
        copy.add_header("List-ID", formataddr(self.identifier))
        copy.add_header("Message-ID", make_msgid(domain=self.domain))
        copy.add_header("Importance", importance)
        copy.add_header("Priority", priority)
        copy.add_header("Sensitivity", sensitivity)

        if self.contact:
            copy.add_header("Reply-To", formataddr(self.contact))

        self.collection.append(copy)

        return self

    def send(self, smtp: SMTP) -> None:
        if len(self.collection) < 1:
            logger.warning("No message was sent due to empty message queue")

            return

        smtp.ehlo_or_helo_if_needed()

        for message in self.collection:
            recipient = message["To"]  # TODO

            try:
                smtp.rset()
                smtp.send_message(message)
                logger.info("Sent message successfully", recipient=recipient)
            except SMTPException as exception:
                logger.error("Failed to send message", recipient=recipient, exception=exception)
