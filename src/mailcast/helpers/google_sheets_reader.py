from csv import DictReader
from http import (
    HTTPMethod,
    HTTPStatus,
)
from typing import ClassVar
from urllib.request import (
    Request,
    build_opener,
)


class GoogleSheetsReader(DictReader):
    # https://developers.google.com/workspace/drive/api/guides/mime-types
    T: ClassVar[str] = "application/vnd.google-apps.spreadsheet"

    def __init__(
        self,
        spreadsheet_id: str,
        sheet_id: str | None = None,
    ) -> None:
        opener = build_opener()
        request = Request(
            url=f"docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}",
            method=HTTPMethod.GET,
        )
        response = opener.open(request)

        if response == HTTPStatus.NOT_FOUND:
            raise Exception("The spreadsheet does not exist")

        if response.status == HTTPStatus.FOUND:
            raise Exception("The spreadsheet is not public")

        if response.status == HTTPStatus.TEMPORARY_REDIRECT:
            return cls.retrieve()

        super().__init__(response.read())
