"""Module that contains functions to sync the database.

Contains functions to sync the database for sessions and speakers.
"""

from datetime import datetime
from logging import getLogger
from typing import Any

from sqlalchemy.future import Engine
from sqlmodel import Session as DBSession
from sqlmodel import select

from .model import Session, Speaker, SpeakerLink, Stage


def sync_sessions(db_engine: Engine,
                  sessions: list[dict[str, Any]],
                  speakers_by_uid: dict[str, Speaker]) -> None:
    """Sync sessions with the database.

    Function to sync sessions with the database, based on the given sessions
    in the argument.

    Args:
        db_engine: the DB engine to use.
        sessions: the sessions as retrieved from SessionizeParser.
        speakers_by_uid: a dict with speakers sorted by UID.
    """
    logger = getLogger('sync_sessions')

    with DBSession(db_engine, expire_on_commit=False) as session:
        for sess in sessions:
            sess_statement = select(Session).where(Session.uid == sess['uid'])
            result_sessions = session.exec(sess_statement).all()
            if len(result_sessions) != 1:
                # Speaker is new, add it
                logger.info('Session "%s" is new, adding it', sess['title'])
                session_object = Session()
                session_object.uid = int(sess.get('uid', 0))
                session_object.title = str(sess.get('title', ''))
                session_object.start_time = sess.get('start_time', '')
                session_object.end_time = sess.get('end_time', '')
                session_object.description = sess.get('description', '')
                session_object.session_type = sess.get('type', 'session')

                # Loop through the speakers
                for speaker in sess['speakers']:
                    # pylint: disable=no-member
                    if speaker['uid'] in speakers_by_uid:
                        session_object.speakers.append(
                            speakers_by_uid[speaker['uid']])
                    else:
                        session_object.speakers.append(
                            Speaker(uid=speaker['uid'],
                                    name=speaker['name']))

                # Get the stage
                stage_statement = select(Stage).where(
                    Stage.uid == int(sess['stage']['uid']))
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


def sync_speakers(db_engine: Engine,
                  speakers: list[dict[str, Any]]) -> dict[str, Speaker]:
    """Sync speakers with the database.

    Function to sync speakers with the database, based on the given speakers
    in the argument.

    Args:
        db_engine: the DB engine to use.
        speakers: the speakers as retrieved from SessionzizeParser.

    Returns:
        A dict with speakers where the UID of the speaker is the key. This can
        be used by the syncing of sessions to speed up this syncing.
    """
    logger = getLogger('sync_speakers')

    # Empty dict for speakers. We will return this eventually
    speakers_by_uid: dict[str, Speaker] = {}

    with DBSession(db_engine, expire_on_commit=False) as session:
        for speaker in speakers:
            # Check if the speaker is already in the database
            statement = select(Speaker).where(Speaker.uid == speaker['uid'])
            results = session.exec(statement).all()
            if len(results) == 0:
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
                    # pylint: disable=no-member
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

    return speakers_by_uid
