from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from typer import (
    Argument,
    Option,
    Typer,
)
from yaml import safe_load

from emailer.schemas.specification import Specification

typer = Typer()


@typer.command()
def register(
    spec_file: Annotated[Path, Argument(exists=True, dir_okay=False)],
    env_file: Annotated[Path | None, Option(exists=True, dir_okay=False)] = None,
    interactive: Annotated[bool, Option()] = False,
) -> None:
    load_dotenv(env_file)

    spec_text = spec_file.read_text()
    spec = Specification.model_validate(safe_load(spec_text))
