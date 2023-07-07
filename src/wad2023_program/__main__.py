"""Main module.

Contains the CLI script for the `wad23` application.
"""

from enum import Enum
from logging import INFO, basicConfig, getLogger
from sqlite3 import OperationalError

from sqlmodel import Session as DBSession
from sqlmodel import or_, select
from typer import Typer

from wad2023_program.sync import sync_sessions, sync_speakers

from .app_config import AppConfig
from .database import create_tables, get_db_engine
from .model import Session, SessionType
from .sessionize_parser import SessionizeParser
from .view import (view_sessions_as_csv, view_sessions_as_details,
                   view_sessions_as_table)

from sqlalchemy.exc import OperationalError

# Create the Typer app
app = Typer(name='WeAreDevelopers 2023 Conference')

# Create a instance of the configuration
config = AppConfig()

# Configure logging
basicConfig(level=INFO)

# Create a Database Engine
engine = get_db_engine(config.db_connection_str)


class SessionTypeCLI(str, Enum):
    """Enum for the session types.

    Specifies the types of session to filter on.
    """

    ALL = 'all'
    SESSION = 'session'
    WORKSHOP = 'workshop'


class OutputType(str, Enum):
    """The choosable output.

    Specifies what output modes are choosable.
    """

    TABLE = 'table'
    CSV = 'csv'
    DETAILS = 'details'


@app.command(name='sync', help='Synchronize the database')
def sync() -> None:
    """Synchronize the database.

    Retrieves the sessions from the Sessionize API and updates the local
    database.
    """
    # Create a logger
    logger = getLogger('sync')

    # Create the tables. This only creates the tables that don't exist yet, so
    # we can safely execute it.
    create_tables(engine)

    # Get the sessions from Sessionize
    logger.info('Retrieving sessions')
    sessions = SessionizeParser(
        sessionize_id=config.program_id)
    sessions.update()

    logger.info('Retrieving workshops')
    workshops = SessionizeParser(
        sessionize_id=config.workshops_id)
    workshops.update()

    # Synchronize the speakers
    logger.info('Starting to sync speakers')
    all_speakers = []
    if sessions.speakers:
        all_speakers += sessions.speakers
    if workshops.speakers:
        all_speakers += workshops.speakers

    speakers_by_uid = sync_speakers(engine, all_speakers)

    # Synchronize the sessions
    logger.info('Starting to sync sessions')
    all_sessions = []
    if sessions.sessions:
        for sess in sessions.sessions:
            sess['type'] = 'session'
        all_sessions += sessions.sessions
    if workshops.sessions:
        for sess in workshops.sessions:
            sess['type'] = 'workshop'
        all_sessions += workshops.sessions

    sync_sessions(engine, all_sessions, speakers_by_uid)


@app.command(name='sessions', help='List sessions')
def list_sessions(
    session_type: SessionTypeCLI = SessionTypeCLI.ALL,
    title: str | None = None,
    description: str | None = None,
    find: str | None = None,
    speaker: str | None = None,
    speaker_tagline: str | None = None,
    speaker_bio: str | None = None,
    only_favourite: bool | None = None,
    set_as_favourite: bool | None = None,
    output: OutputType = OutputType.TABLE
) -> None:
    """List a subset or all of the sessions.

    Displays a list of all sessions, or filters the sessions based on given
    criteria.

    Args:
        session_type: filter on a specific session type.
        title: filter on a specific string in the title.
        description: filter on a specific string in the description.
        find: search in title and description.
        speaker: filter on speaker name.
        speaker_tagline: filter on speaker tagline.
        speaker_bio: filter on speaker biography.
        only_favourite: display only favourites.
        set_as_favourite: set the selected sessions as favourite.
        output: the type of output.
    """
    # pylint: disable=too-many-branches
    # Filter on sessions
    with DBSession(engine, expire_on_commit=False) as session:
        # Base statement
        statement = select(Session).order_by(Session.start_time)

        # Apply filters
        if session_type == SessionTypeCLI.SESSION:
            statement = statement.where(
                Session.session_type == SessionType.SESSION)
        elif session_type == SessionTypeCLI.WORKSHOP:
            statement = statement.where(
                Session.session_type == SessionType.WORKSHOP)
        if title:
            # pylint: disable=no-member
            statement = statement.where(
                Session.title.ilike(f'%{title}%'))  # type:ignore
        if description:
            # pylint: disable=no-member
            statement = statement.where(
                Session.description.ilike(f'%{description}%'))  # type:ignore
        if find:
            # pylint: disable=no-member
            # type:ignore
            statement = statement.where(or_(Session.title.ilike(  # type:ignore
                f'%{find}%'),
                Session.description.ilike(f'%{find}%')))  # type:ignore
        if only_favourite is not None:
            statement = statement.where(Session.favourite == only_favourite)

        # Get the selected sessions
        try:
            all_sessions = session.exec(statement).all()
        except OperationalError:
            print('Looks like there are some tables missing. ' +
                  'Please run `wad23` sync first')
            return

        # Extra filters
        if speaker:
            all_sessions = list(filter(lambda x: len(
                [a for a in x.speakers
                 if a.name and speaker and
                 speaker.lower() in a.name.lower()]) > 0,
                all_sessions))
        if speaker_tagline:
            all_sessions = list(filter(lambda x: len(
                [a for a in x.speakers
                 if a.tagline and speaker_tagline and
                 speaker_tagline.lower() in a.tagline.lower()]) > 0,
                all_sessions))
        if speaker_bio:
            all_sessions = list(filter(lambda x: len(
                [a for a in x.speakers
                 if a.bio and speaker_bio and
                 speaker_bio.lower() in a.bio.lower()]) > 0,
                all_sessions))

        # Set as favourite, if that is set
        if set_as_favourite is not None:
            for sess in all_sessions:
                sess.favourite = set_as_favourite

        if output == OutputType.TABLE:
            view_sessions_as_table(all_sessions)

        if output == OutputType.CSV:
            view_sessions_as_csv(all_sessions)

        if output == OutputType.DETAILS:
            view_sessions_as_details(all_sessions)

        session.commit()


if __name__ == '__main__':
    app()
