from pydantic import BaseModel

from .mailing_list import MailingList
from .message import Message


class Specification(BaseModel):
    mailing_list: MailingList
    message: Message
