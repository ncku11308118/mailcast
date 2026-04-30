from collections.abc import Generator, Mapping, Sequence
from csv import DictReader
from enum import Enum
from http import HTTPMethod
from io import TextIOWrapper
from typing import Any
from urllib.request import (
    Request,
    build_opener,
)

from pydantic import (
    computed_field,
)
from pydantic.networks import AnyHttpUrl
from pydantic.types import FilePath

from mailcast.lib.specification.rfc import MIMEEntity

type MailingListOutput = Sequence[Mapping[str, Any]]


class MailingListType(str, Enum):
    CSV = "text/csv"
    JSON = "application/json"
    YAML = "application/yaml"


class MailingList(MIMEEntity[MailingListType]):
    file: FilePath | AnyHttpUrl

    @computed_field
    @property
    def stream(self) -> Generator[str]:
        if isinstance(self.file, AnyHttpUrl):
            opener = build_opener()
            request = Request(url=self.file.encoded_string(), method=HTTPMethod.GET)

            with opener.open(request) as response:
                yield from TextIOWrapper(response, encoding="utf-8", newline="")
        else:
            with self.file.open() as file:
                yield from file

    @computed_field
    @property
    def output(self) -> Generator[dict[str | Any, str | Any]]:
        match self.type:
            case MailingListType.CSV:
                yield from DictReader(self.stream)

            case _:
                pass

            # case MailingListType.JSON:
            #     ...

            # case MailingListType.YAML:
            #     for document in safe_load_all(text):
            #         for item in document if isinstance(document, Sequence) else [document]:
            #             yield item
