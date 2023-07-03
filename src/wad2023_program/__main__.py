"""Main module.

Contains the CLI script for the `wad23` application.
"""

from typer import Typer
from .app_config import AppConfig
from .database import get_db_engine, create_tables

from .model import *

# Create the Typer app
app = Typer(name='WeAreDevelopers 2023 Conference')

# Create a instance of the configuration
config = AppConfig()


@app.command(name='sync', help='Synchronize the database')
def sync() -> None:
    """Synchronize the database.

    Retrieves the sessions from the Sessionize API and updates the local
    database.
    """
    # Create a Database Enginer
    engine = get_db_engine(config.db_connection_str)

    # Create the tables. This only creates the tables that don't exist yet, so
    # we can safely execute it.
    create_tables(engine)


@app.command(name='list', help='List sessions')
def list_sessions() -> None:
    """List a subset or all of the sessions.

    Displays a list of all sessions, or filters the sessions based on given
    criteria.
    """


if __name__ == '__main__':
    app()
