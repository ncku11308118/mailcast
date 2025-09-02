from typer import Typer

typer = Typer(name="schema")


@typer.command()
def generate(indent: int | None = None):
    from json import dump
    from sys import stdout

    from mailcast.lib.specification import Specification

    dump(
        Specification.model_json_schema(mode="validation"),
        stdout,
        indent=indent,
        separators=(",", ":"),
    )
