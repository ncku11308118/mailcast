from typer import Typer

from .registration import typer as registration_typer

typer = Typer()

typer.add_typer(registration_typer)


def main() -> None:
    typer()
