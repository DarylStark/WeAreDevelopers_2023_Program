"""Model module.

Contains the models for the application.
"""
from datetime import datetime

import pytz
from sqlmodel import SQLModel, Field, Relationship


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
        speaker_id: the uid for the speaker.
    """

    session_id: int | None = Field(
        default=None, foreign_key='sessions.id', primary_key=True)
    speaker_id: int | None = Field(
        default=None, foreign_key='speakers.uid', primary_key=True)


class Speaker(Model, table=True):
    """Model for a speaker.

    Class with the attributes for a speaker.

    Attributes:
        uid: the ID of the speaker.
        name: the name of the speaker.
    """

    __tablename__: str = 'speakers'  # type: ignore

    uid: str = Field(default='', primary_key=True)
    name: str = ''
    tagline: str = ''
    bio: str = ''
    links: dict[str, str] = {}
    img_url: str = ''

    # Relationships
    sessions: list['Session'] = Relationship(
        back_populates="speakers", link_model=SessionSpeakerLink)


class Stage(Model, table=True):
    """Model for a stage.

    Class with the attributes for a stage.

    Attributes:
        uid: the ID of the stage.
        name: the name of the stage.
    """

    __tablename__: str = 'stages'  # type: ignore

    id: int = Field(default=0, primary_key=True)
    name: str = ''

    # Relationships
    sessions: list['Session'] = Relationship(back_populates='stage')


class Session(Model, table=True):
    """Model for a session.

    Class with the attributes for a session.

    Attributes:
        title: the title of the session.
        stage: the stage where the session is hold.
        speakers: a list with speakers for the session.
        start_time: when the session starts.
        end_time: when the session ends
        tags: a list with tags.
    """

    __tablename__: str = 'sessions'  # type: ignore

    id: int = Field(default=0, primary_key=True)
    title: str = ''
    start_time: datetime = datetime.now()
    end_time: datetime = datetime.now()
    tags: list[str] = []
    description: str = ''

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
