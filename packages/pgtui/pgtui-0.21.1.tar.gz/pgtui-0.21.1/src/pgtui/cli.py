import logging
import os
from pathlib import Path

import click
from textual.logging import TextualHandler

from pgtui.app import PgTuiApp
from pgtui.entities import DbContext

# Tweak the Click context
# https://click.palletsprojects.com/en/8.1.x/api/#context
CONTEXT = dict(show_default=True)


@click.command(
    context_settings=CONTEXT,
    epilog="https://codeberg.org/ihabunek/pgtui",
)
@click.option(
    "-h",
    "--host",
    help="Database server host",
    envvar="PGHOST",
)
@click.option(
    "-p",
    "--port",
    help="Database server port",
    envvar="PGPORT",
)
@click.option(
    "-U",
    "--username",
    help="Database user name",
    envvar="PGUSER",
)
@click.option(
    "-d",
    "--dbname",
    help="Database name to connect to",
    envvar="PGDATABASE",
)
@click.option(
    "-W",
    "--password",
    "force_password_prompt",
    is_flag=True,
    default=False,
    help="Force password prompt",
)
@click.option(
    "-w",
    "--no-password",
    "never_prompt_password",
    is_flag=True,
    default=False,
    help="Never prompt for password",
)
@click.version_option()
@click.argument(
    "sql_file",
    type=click.Path(dir_okay=False, writable=True),
    required=False,
)
def pgtui(
    host: str,
    port: str,
    username: str,
    dbname: str | None,
    force_password_prompt: bool,
    never_prompt_password: bool,
    sql_file: str | None,
):
    """
    Text based user interface for PostgreSQL.
    """
    # TODO: prompt for password if first connect fails unless never_prompt_password is set
    password = os.environ.get("PGPASSWORD", None)
    if force_password_prompt:
        password = click.prompt("Password", hide_input=True)

    db_context = DbContext(
        host=host,
        port=port,
        dbname=dbname,
        username=username,
        password=password,
    )

    file_path = Path(sql_file) if sql_file is not None else None
    PgTuiApp(db_context, file_path).run()


def main():
    logging.basicConfig(level="NOTSET", handlers=[TextualHandler()])
    pgtui()
