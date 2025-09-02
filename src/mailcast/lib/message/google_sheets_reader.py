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

        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}"
        request = Request(url=url, method=HTTPMethod.GET)
        response = opener.open(request)

        if response.status == HTTPStatus.FOUND:
            raise Exception("The spreadsheet is not public")

        if response.status == HTTPStatus.NOT_FOUND:
            raise Exception("The spreadsheet does not exist")

        new_url = response.getheader("Location")

        if response.status != HTTPStatus.TEMPORARY_REDIRECT or new_url is None:
            raise Exception("The spreadsheet is not available")

        new_request = Request(url=new_url, method=HTTPMethod.GET)
        new_response = opener.open(new_request)

        super().__init__(new_response.read())
