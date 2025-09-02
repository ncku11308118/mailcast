from csv import DictReader
from datetime import datetime
from logging import (
    DEBUG,
    INFO,
    Formatter,
    LogRecord,
    StreamHandler,
    getLogger,
)
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from smtplib import SMTP
from sys import stderr
from typing import (
    Any,
    override,
)
from uuid import uuid4

from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    EmailStr,
)

from emailer.helpers.email_builder import Mailer
from emailer.helpers.mailing_list import MailingList
from emailer.schemas.environment import Environment
from emailer.schemas.specification import Specification as Configuration

logger = getLogger()


class CustomFormatter(Formatter):
    @override
    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created).astimezone()

        return dt.strftime(datefmt) if datefmt else dt.isoformat(timespec="seconds")


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    @override
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.suffix = "%Y%m%d"

    @override
    @staticmethod
    def namer(name: str) -> str:
        return name.replace(".log.", "_") + ".log"

    @override
    @staticmethod
    def rotator(
        source: str,
        destination: str,
    ) -> None:
        try:
            logger.info(
                "Rotated existing log file to %s",
                Path(source).rename(destination).name,
            )
        except OSError as error:
            logger.error(
                "Failed to rotate log file: %s",
                error,
            )


list_id = str(uuid4())

format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
target = Path() / "archive" / "logs" / f"{list_id}.log"

logger.setLevel(DEBUG)

formatter = CustomFormatter(format)
file_handler = CustomTimedRotatingFileHandler(target, when="midnight", backupCount=180)
stream_handler = StreamHandler(stderr)

file_handler.setFormatter(formatter)
file_handler.setLevel(INFO)
logger.addHandler(file_handler)

stream_handler.setFormatter(formatter)
stream_handler.setLevel(DEBUG)
logger.addHandler(stream_handler)


class Recipient(BaseModel):
    personal_name: str
    email_address: EmailStr


def main():
    env = Environment.load()
    config = Configuration.load()

    originator = config.email.originator
    mailing_list = MailingList(
        originator=(None, originator) if isinstance(originator, str) else (originator.name, originator.address),
        phrase=list_id,
        domain="evs.hs.edu.tw",  # TODO
        logger=logger,
    )

    for row in DictReader(Path("list.csv").open("r", encoding="utf-8-sig")):
        recipient = Recipient.model_validate(row)
        mailer = Mailer(recipient.email_address, config)

        mailing_list.register(
            (None, recipient.email_address),
            config.email.subject,
            mailer.message,
        )

    with SMTP(env.smtp_hostname, env.smtp_port) as smtp:
        smtp.ehlo_or_helo_if_needed()
        smtp.starttls()
        smtp.login(env.smtp_username, env.smtp_password.get_secret_value())
        mailing_list.send(smtp)


if __name__ == "__main__":
    load_dotenv()
    main()
