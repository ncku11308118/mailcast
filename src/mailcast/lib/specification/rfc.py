from abc import ABC
from email.utils import formataddr, parseaddr
from typing import (
    Any,
    Literal,
    Self,
)
from uuid import uuid4

from pydantic import (
    BaseModel,
    Field,
    RootModel,
)
from pydantic.networks import EmailStr
from pydantic_extra_types.domain import DomainStr


# https://datatracker.ietf.org/doc/html/rfc2045#section-2.4
class MIMEEntity[T](BaseModel, ABC):
    type: T


# https://datatracker.ietf.org/doc/html/rfc2919
# https://datatracker.ietf.org/doc/html/rfc4021#section-2.1.33
# https://datatracker.ietf.org/doc/html/rfc5983
# https://datatracker.ietf.org/doc/html/rfc6783
class ListIdentifier(BaseModel):
    # phrase: https://datatracker.ietf.org/doc/html/rfc822#section-3.3
    # phrase: https://datatracker.ietf.org/doc/html/rfc2822#section-3.2.6
    # phrase: https://datatracker.ietf.org/doc/html/rfc5322#section-3.2.5
    phrase: str | None = Field(default=None)
    # list-label: https://datatracker.ietf.org/doc/html/rfc2919#section-2
    label: str = Field(default_factory=lambda: str(uuid4()))
    # localhost: https://datatracker.ietf.org/doc/html/rfc2606#section-2
    # localhost: https://datatracker.ietf.org/doc/html/rfc6761#section-6.3
    # dot-atom-text: https://datatracker.ietf.org/doc/html/rfc2822#section-3.2.4
    # dot-atom-text: https://datatracker.ietf.org/doc/html/rfc5322#section-3.2.3
    # list-id-namespace: https://datatracker.ietf.org/doc/html/rfc2919#section-2
    namespace: DomainStr | Literal["localhost"] = Field(default="localhost")

    # list-id: https://datatracker.ietf.org/doc/html/rfc2919#section-2
    # list-id-header: https://datatracker.ietf.org/doc/html/rfc2919#section-3
    def __str__(self) -> str:
        pair = self.phrase, f"{self.label}.{self.namespace}"

        return formataddr(pair)

    @classmethod
    def transform(cls, data: Any) -> Self:
        if not isinstance(data, str):
            return cls.model_validate(data)

        phrase, list_id = parseaddr(data)
        list_label, list_id_namespace = list_id.split(".", 1)

        return cls(
            phrase=phrase,
            label=list_label,
            namespace=(
                list_id_namespace
                if list_id_namespace == "localhost"
                else RootModel[DomainStr].model_validate(list_id_namespace).root
            ),
        )


# https://datatracker.ietf.org/doc/html/rfc4021#section-2.1.8
# https://datatracker.ietf.org/doc/html/rfc4021#section-2.2.2
class ContentIdentifier(BaseModel):
    local_part: str
    domain: EmailStr | None = Field(default=None)

    # id: https://datatracker.ietf.org/doc/html/rfc2045#section-7
    # addr-spec: https://datatracker.ietf.org/doc/html/rfc822#section-6.1
    # addr-spec: https://datatracker.ietf.org/doc/html/rfc2822#section-3.4.1
    # addr-spec: https://datatracker.ietf.org/doc/html/rfc5322#section-3.4.1
    # content-id: https://datatracker.ietf.org/doc/html/rfc2111#section-2
    # content-id: https://datatracker.ietf.org/doc/html/rfc2392#section-2
    # message-id: https://datatracker.ietf.org/doc/html/rfc2111#section-2
    # message-id: https://datatracker.ietf.org/doc/html/rfc2392#section-2
    # message-id: https://datatracker.ietf.org/doc/html/rfc5322#section-3.6.4
    def __str__(self) -> str:
        return f"{self.local_part}@{self.domain}"
