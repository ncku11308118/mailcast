from pathlib import Path
from typing import Annotated

from typer import (
    Argument,
    Option,
    Typer,
)

from .schema import typer as schema_typer

typer = Typer()

typer.add_typer(schema_typer)


@typer.command()
def register(
    specification_file: Annotated[Path, Argument(exists=True, dir_okay=False)],
    interactive: Annotated[bool, Option()] = False,
) -> None:
    from email.mime.text import MIMEText
    from os import getenv
    from smtplib import (
        SMTP,
        SMTPException,
    )

    from pydantic import TypeAdapter
    from pydantic.types import (
        NonNegativeInt,
        SecretStr,
    )
    from pydantic_extra_types.domain import DomainStr
    from yaml import safe_load

    from mailcast.lib.message.mailing_list import MailingList
    from mailcast.lib.specification import Specification

    specification_text = specification_file.read_text()
    specification = Specification.model_validate(safe_load(specification_text))

    SMTP_HOSTNAME = TypeAdapter(DomainStr).validate_python(getenv("SMTP_HOSTNAME"))
    SMTP_PORT = TypeAdapter(NonNegativeInt).validate_python(getenv("SMTP_PORT"))
    SMTP_USERNAME = TypeAdapter(str).validate_python(getenv("SMTP_USERNAME"))
    SMTP_PASSWORD = TypeAdapter(SecretStr).validate_python(getenv("SMTP_PASSWORD"))

    mailing_list = MailingList(originator=(None, "evs_service@mail.moe.gov.tw"))

    specification.mailing_list.file

    mailing_list.seal(
        (None, "11308118@gs.ncku.edu.tw"),
        "Test",
        MIMEText("Test"),
    )

    with SMTP(SMTP_HOSTNAME, SMTP_PORT) as smtp:
        smtp.ehlo_or_helo_if_needed()
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD.get_secret_value())
        mailing_list.send(smtp)


@typer.callback()
def _(
    env_file: Annotated[Path | None, Option(exists=True, dir_okay=False)] = None,
    verbose: Annotated[bool, Option("-v", "--verbose")] = False,  # TODO
) -> None:
    from sys import stderr

    from dotenv import load_dotenv
    from loguru import logger

    load_dotenv(env_file)

    logger.remove()
    logger.add(
        sink=stderr,
        diagnose=False,
        enqueue=True,
    )


if __name__ == "__main__":
    typer()
