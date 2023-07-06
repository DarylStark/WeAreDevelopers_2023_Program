"""Main module.

Contains the CLI script for the `wad23` application.
"""

from datetime import datetime
from logging import INFO, basicConfig, getLogger

from sqlmodel import Session as DBSession
from sqlmodel import select
from typer import Typer

from .app_config import AppConfig
from .database import create_tables, get_db_engine
from .model import Session, Speaker, SpeakerLink, Stage
from .sessionize_parser import SessionizeParser

# Create the Typer app
app = Typer(name='WeAreDevelopers 2023 Conference')

# Create a instance of the configuration
config = AppConfig()

# Configure logging
basicConfig(level=INFO)


@app.command(name='sync', help='Synchronize the database')
def sync() -> None:
    """Synchronize the database.

    Retrieves the sessions from the Sessionize API and updates the local
    database.
    """
    # Create a logger
    logger = getLogger('sync')

    # Create a Database Engine
    engine = get_db_engine(config.db_connection_str)

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


@app.command(name='list', help='List sessions')
def list_sessions() -> None:
    """List a subset or all of the sessions.

    Displays a list of all sessions, or filters the sessions based on given
    criteria.
    """


if __name__ == '__main__':
    app()
