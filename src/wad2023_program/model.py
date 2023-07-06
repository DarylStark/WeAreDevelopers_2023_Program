"""Model module.

Contains the models for the application.
"""
from datetime import datetime
from enum import Enum

import pytz
from sqlmodel import Field, Relationship, SQLModel


def to_timezone(datetime_utc: datetime, timezone: str) -> datetime:
    """Convert a UTC time to a specific timezone.

    Args:
        datetime_utc: the datetime object to convert.
        timezone: the timezone to convert to. Example: "Europe/Amsterdam.

    Returns:
        A datetime-object with the time in the set Timezone.
    """
    new_timezone = pytz.timezone(timezone)
    return datetime_utc.replace(tzinfo=pytz.utc).astimezone(tz=new_timezone)


class Model(SQLModel):
    """Base model for all models.

    Contains the main attributes for Model classes.
    """

    class Config:
        """Config for the models.

        Attributes:
            validate_assignment: specifies if assigned values should be
                validated by Pydantic. If this is set to False, only
                assignments in the constructor are validated.
        """

        validate_assignment = True


class SessionSpeakerLink(Model, table=True):
    """Connection class for sessions and speakers.

    Connects sessions and speakers to each-other in a many-to-many model.

    Attributes:
        session_id: the id for the session.
        speaker_id: the id for the speaker.
    """

    session_id: int | None = Field(
        default=None, foreign_key='sessions.id', primary_key=True)
    speaker_id: int | None = Field(
        default=None, foreign_key='speakers.id', primary_key=True)


class SpeakerLink(Model, table=True):
    """Model for a link for a speaker.

    Class with the attributes for a link that is connected to a speaker.

    Attributes:
        id: the ID of the link.
        name: the name of the link.
        url: the URL of the link.
        speaker: the ID of the speaker
    """

    __tablename__: str = 'speaker_links'  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str
    url: str
    speaker_id: int | None = Field(default=None, foreign_key='speakers.id')

    # Relationships
    speaker: 'Speaker' = Relationship(back_populates='links')


class Speaker(Model, table=True):
    """Model for a speaker.

    Class with the attributes for a speaker.

    Attributes:
        id: the ID of the speaker.
        uid: the UID of the speaker.
        name: the name of the speaker.
        tagline: the tagline for the speaker.
        bio: the biography of the speaker.
        img_url: a image URL for the speaker.
        favourite: if the speaker is a favourite.
        creation: the datetime of the object creation.
        updated: the datetime of the object update.
    """

    __tablename__: str = 'speakers'  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    uid: str = ''
    name: str = ''
    tagline: str = ''
    bio: str = ''
    img_url: str = ''
    favourite: bool = False
    creation: datetime = Field(default_factory=datetime.now)
    update: datetime = Field(default_factory=datetime.now)

    # Relationships
    sessions: list['Session'] = Relationship(
        back_populates="speakers", link_model=SessionSpeakerLink)
    links: list[SpeakerLink] = Relationship(back_populates='speaker')


class Stage(Model, table=True):
    """Model for a stage.

    Class with the attributes for a stage.

    Attributes:
        id: the ID of the stage.
        uid: the UID of the object.
        name: the name of the stage.
    """

    __tablename__: str = 'stages'  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    uid: int = 0
    name: str = ''

    # Relationships
    sessions: list['Session'] = Relationship(back_populates='stage')


class SessionType(str, Enum):
    """Model for session-types.

    Can be either `session` or `worshop`, depending on the type of session.

    Attributes:
        SESSION: the sessions is a normal conference session.
        WORKSHOP: the session is a workshop.
    """

    SESSION = 'session'
    WORKSHOP = 'workshop'


class Session(Model, table=True):
    """Model for a session.

    Class with the attributes for a session.

    Attributes:
        id: the unique ID of the object.
        uid: the UID of the object.
        session_type: the session type.
        title: the title of the session.
        stage: the stage where the session is hold.
        speakers: a list with speakers for the session.
        start_time: when the session starts.
        end_time: when the session ends
        tags: a list with tags.
        favourite: if the speaker is a favourite.
        creation: the datetime of the object creation.
        updated: the datetime of the object update.
    """

    __tablename__: str = 'sessions'  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    uid: int = 0
    session_type: SessionType = SessionType.SESSION
    title: str = ''
    start_time: datetime = datetime.now()
    end_time: datetime = datetime.now()
    description: str = ''
    stage_id: int | None = Field(default=None, foreign_key='stages.id')
    favourite: bool = False
    creation: datetime = Field(default_factory=datetime.now)
    update: datetime = Field(default_factory=datetime.now)

    # Relationships
    stage: Stage = Relationship(back_populates='sessions')
    speakers: list[Speaker] = Relationship(
        back_populates="sessions", link_model=SessionSpeakerLink)

    @property
    def start_time_berlin(self) -> datetime:
        """Get the start time in Berlin timezone.

        Returns the start time in Berlin timezone instead of UTC.

        Returns:
            The start time in Berlin timezone.
        """
        return to_timezone(self.start_time, "Europe/Amsterdam")

    @property
    def end_time_berlin(self) -> datetime:
        """Get the end time in Berlin timezone.

        Returns the end time in Berlin timezone instead of UTC.

        Returns:
            The end time in Berlin timezone.
        """
        return to_timezone(self.end_time, "Europe/Amsterdam")
