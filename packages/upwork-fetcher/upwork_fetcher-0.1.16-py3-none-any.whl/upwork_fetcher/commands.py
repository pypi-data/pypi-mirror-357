from typing import Tuple
import click
from pydantic import PostgresDsn, ValidationError
from rich.console import Console

from upwork_fetcher.config import load_config, save_config
from upwork_fetcher.services.upwork_service import UpworkService


console = Console()


def validate_db_url(db_url: str):
    try:
        # Validate database URL using PostgresDsn
        db_url_validated = PostgresDsn(db_url)
    except ValidationError:
        console.print(f"[bold red]Invalid database URL format.")
        raise click.Abort()

    if not db_url_validated.path or len(db_url_validated.path) <= 1:
        console.print(f"[bold red]database must be provided")
        raise click.Abort()

    return db_url


@click.command()
@click.option(
    "--search-expression",
    "-s",
    multiple=True,
    help="Generic search filter supports partial Lucene syntax",
)
@click.option("--offset", prompt=False, default=0, help="The offset of the jobs")
@click.option("--limit", prompt=False, default=50, help="The limit of the jobs")
@click.option("--db-url", help="The database url")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Verbose mode")
@click.pass_context
def fetch(
    ctx: click.Context,
    search_expression: Tuple[str],
    db_url: str | None,
    offset: int,
    limit: int,
    verbose: bool,
):
    """
    Fetch the jobs from the Upwork API
    """
    if not search_expression:
        console.print(
            "[bold red]You must specify at least one search expression. Run `upwork-fetcher --help`"
        )
        raise click.Abort()
    if db_url:
        validate_db_url(db_url)
        ctx.obj["db_url"] = db_url
        save_config(ctx.obj)

    if db_url is None and ctx.obj.get("db_url") is None:
        database_url: str = click.prompt("Enter the database url")
        db_url = validate_db_url(database_url)

    config = load_config()
    if (
        config.get("client_id") is None
        or config.get("client_secret") is None
        or config.get("redirect_uri") is None
        or config.get("code") is None
    ):
        console.print(
            "[bold red]You must setup the Upwork API Credentials first. Run `upwork-fetcher setup`"
        )
        raise click.Abort()

    upwork_service = UpworkService(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        redirect_uri=config["redirect_uri"],
    )

    upwork_service.fetch(
        search_expression,
        str(db_url),
        offset,
        limit,
        verbose,
    )


@click.command()
@click.option("--client_id", help="The client id")
@click.option("--client_secret", help="The client secret")
@click.option("--redirect_uri", help="The redirect uri")
def setup(client_id: str, client_secret: str, redirect_uri: str):
    """
    Setup the Upwork API Credentials
    """

    upwork_service = UpworkService(
        client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri
    )
    url = upwork_service.get_authorization_url()

    save_config(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }
    )

    console.print(
        f"\n\nGo to this url and copy the code from the query params: [underline blue]{url}\n\n"
    )
    code = click.prompt("Enter the code")

    tokens = upwork_service.get_access_token(code)

    save_config(tokens)
    save_config({"code": code})
