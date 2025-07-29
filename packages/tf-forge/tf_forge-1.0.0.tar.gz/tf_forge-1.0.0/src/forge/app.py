import typer
from rich.console import Console

app = typer.Typer(
    name="forge",
    help="CLI to help you forge Terraform modules with best practices.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()

from .commands import new, docs, publish, lint


@app.callback()
def main():
    """
    Forge: A CLI to help you forge Terraform modules with best practices.
    """
    pass