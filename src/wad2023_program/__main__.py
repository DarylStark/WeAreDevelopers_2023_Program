"""Main module.

Contains the CLI script for the `wad23` application.
"""

from datetime import datetime
from logging import INFO, basicConfig, getLogger

from sqlmodel import Session as DBSession
from sqlmodel import select, or_
from typer import Typer

from .app_config import AppConfig
from .database import create_tables, get_db_engine
from .model import Session, Speaker, SpeakerLink, Stage, SessionType
from .sessionize_parser import SessionizeParser

from enum import Enum
from rich import box
from rich.console import Console
from rich.table import Table

# Create the Typer app
app = Typer(name='WeAreDevelopers 2023 Conference')

# Create a instance of the configuration
config = AppConfig()

# Configure logging
basicConfig(level=INFO)

# Create a Database Engine
engine = get_db_engine(config.db_connection_str)


class SessionTypeCLI(str, Enum):
    ALL = 'all'
    SESSION = 'session'
    WORKSHOP = 'workshop'


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
        sessionize_id=config.program_id, cache_dir=config.cache_dir)
    sessions.update()

    logger.info('Retrieving workshops')
    workshops = SessionizeParser(
        sessionize_id=config.workshops_id, cache_dir=config.cache_dir)
    workshops.update()

    # Empty dict for speakers; will come in handy later
    speakers_by_uid = {}

    # Synchronize the speakers
    logger.info('Starting to sync speakers')
    all_speakers = []
    if sessions.speakers:
        all_speakers += sessions.speakers
    if workshops.speakers:
        all_speakers += workshops.speakers

    with DBSession(engine, expire_on_commit=False) as session:
        for speaker in all_speakers:
            # Check if the speaker is already in the database
            statement = select(Speaker).where(Speaker.uid == speaker['uid'])
            results = session.exec(statement).all()
            if len(results) != 1:
                # Speaker is new, add it
                logger.info('Speaker "%s" is new, adding it', speaker['name'])
                speaker_object = Speaker()
                speaker_object.uid = str(speaker.get('uid', ''))
                speaker_object.name = str(speaker.get('name', ''))
                speaker_object.tagline = str(speaker.get('tagline', ''))
                speaker_object.bio = str(speaker.get('bio', ''))
                speaker_object.img_url = str(speaker.get('img_url', ''))

                # Add the links
                for name, url in speaker['links'].items():
                    speaker_object.links.append(SpeakerLink(
                        name=name,
                        url=url
                    ))
            else:
                speaker_object = results[0]
                speaker_object.update = datetime.now()

            session.add(speaker_object)
            speakers_by_uid[speaker_object.uid] = speaker_object
        session.commit()

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

    with DBSession(engine, expire_on_commit=False) as session:
        for sess in all_sessions:
            statement = select(Session).where(Session.uid == sess['uid'])
            result_sessions = session.exec(statement).all()
            if len(result_sessions) != 1:
                # Speaker is new, add it
                logger.info('Session "%s" is new, adding it', sess['title'])
                session_object = Session()
                session_object.uid = int(sess.get('uid', 0))
                session_object.title = str(sess.get('title', ''))
                session_object.start_time = sess.get('start_time')
                session_object.end_time = sess.get('end_time', '')
                session_object.description = sess.get('description', '')
                session_object.session_type = sess.get('type', 'session')

                # Loop through the speakers
                for speaker in sess['speakers']:
                    if speaker['uid'] in speakers_by_uid.keys():
                        session_object.speakers.append(
                            speakers_by_uid[speaker['uid']])
                    else:
                        session_object.speakers.append(
                            Speaker(uid=speaker['uid'],
                                    name=speaker['name']))

                # Get the stage
                stage_statement = select(Stage).where(
                    Stage.uid == sess['stage']['uid'])
                result_stages = session.exec(stage_statement).all()
                if len(result_stages) != 1:
                    session_object.stage = Stage(**sess['stage'])
                else:
                    session_object.stage = result_stages[0]
            else:
                session_object = result_sessions[0]
                session_object.update = datetime.now()

            session.add(session_object)
        session.commit()


@app.command(name='sessions', help='List sessions')
def list_sessions(
    session_type: SessionTypeCLI = SessionTypeCLI.ALL,
    title: str | None = None,
    description: str | None = None,
    find: str | None = None,
    only_favourite: bool | None = None,
) -> None:
    """List a subset or all of the sessions.

    Displays a list of all sessions, or filters the sessions based on given
    criteria.

    Args:
        session_type: filter on a specific session type.
        title: filter on a specific string in the title.
        description: filter on a specific string in the description.
        find: search in title and description.
        only_favourite: display only favourites
    """
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
            statement = statement.where(Session.title.ilike(f'%{title}%'))
        if description:
            statement = statement.where(
                Session.description.ilike(f'%{description}%'))
        if find:
            statement = statement.where(or_(Session.title.ilike(
                f'%{find}%'), Session.description.ilike(f'%{find}%')))
        if only_favourite is not None:
            statement = statement.where(Session.favourite == only_favourite)

        # Get the selected sessions
        all_sessions = session.exec(statement).all()

        # Display the sessions
        console = Console()
        table = Table(box=box.HORIZONTALS)
        table.add_column('*')
        table.add_column('Type')
        table.add_column('Date')
        table.add_column('Start')
        table.add_column('End')
        table.add_column('Stage')
        table.add_column('Title')
        table.add_column('Speakers')
        for sess in all_sessions:
            table.add_row(
                '*' if sess.favourite else '',
                sess.session_type.capitalize(),
                f'{sess.start_time_berlin:%Y-%m-%d}',
                f'{sess.start_time_berlin:%H:%M}',
                f'{sess.end_time_berlin:%H:%M}',
                sess.stage.name,
                sess.title,
                ', '.join([speaker.name for speaker in sess.speakers])
            )
        console.print(table)


if __name__ == '__main__':
    app()
