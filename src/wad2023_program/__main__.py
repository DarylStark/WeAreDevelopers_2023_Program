"""Main module.

Contains the CLI script for the `wad23` application.
"""

from typer import Typer

# Create the Typer app
app = Typer(name='WeAreDevelopers 2023 Conference')


@app.command(name='synchronize', help='Synchronize the database')
def synchronize() -> None:
    """Function to synchronize the database.

    Retrieves the sessions from the Sessionize API and updates the local
    database.
    """


@app.command(name='list', help='List sessions')
def list_sessions() -> None:
    """Function ot list a subset or all of the sessions.

    Displays a list of all sessions, or filters the sessions based on given
    criteria.
    """


if __name__ == '__main__':
    app()
