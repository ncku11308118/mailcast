from codecs import getreader
from collections.abc import Mapping, Sequence
from enum import Enum
from csv import DictReader
from http import (
    HTTPMethod)
from typing import Any
from urllib.request import (
    Request,
    build_opener,
)
from yaml import safe_load_all

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
    def stream(self):
        if isinstance(self.file, AnyHttpUrl):
            opener = build_opener()
            request = Request(url=self.file.encoded_string(), method=HTTPMethod.GET)

            with opener.open(request) as response:
                yield getreader("utf-8")(response)
        else:
            with self.file.open() as file:
                yield file

    @computed_field
    @property
    def output(self):
        match self.type:
            case MailingListType.CSV:
                for row in DictReader(self.stream):
                    yield row

            case MailingListType.JSON:


            case MailingListType.YAML:
                data = [
                    item
                    for document in safe_load_all(text)
                    for item in (document if isinstance(document, Sequence) else [document])
                ]
