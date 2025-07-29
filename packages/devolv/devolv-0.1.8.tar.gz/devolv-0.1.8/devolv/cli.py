import typer
from devolv import __version__

from devolv.iam.validator.cli import validate
app = typer.Typer(help="Devolv CLI - Modular DevOps Toolkit")

@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show Devolv version and exit.",
        callback=lambda value: print_version(value),
        is_eager=True,
    )
):
    pass

def print_version(value: bool):
    if value:
        typer.echo(f"Devolv version: {__version__}")
        raise typer.Exit()


app.command()(validate)

if __name__ == "__main__":
    app()
