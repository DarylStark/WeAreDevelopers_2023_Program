"""Model module.

Contains the models for the application.
"""
import re
from datetime import datetime

import pytz
from sqlmodel import SQLModel


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


class Speaker(Model):
    """Model for a speaker.

    Class with the attributes for a speaker.

    Attributes:
        uid: the ID of the speaker.
        name: the name of the speaker.
    """

    uid: str = ''
    name: str = ''
    tagline: str = ''
    bio: str = ''
    links: dict[str, str] = {}
    img_url: str = ''


class Stage(Model):
    """Model for a stage.

    Class with the attributes for a stage.

    Attributes:
        uid: the ID of the stage.
        name: the name of the stage.
    """

    id: int = 0
    name: str = ''


class Session(Model):
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

    id: int = 0
    title: str = ''
    stage: Stage = Stage()
    speakers: list[Speaker] = []
    start_time: datetime = datetime.now()
    end_time: datetime = datetime.now()
    tags: list[str] = []
    description: str = ''

    @property
    def speaker(self) -> str:
        """Get the speaker name.

        Returns the speaker name as a string. Can be useful when sorting a list
        of sessions.

        Returns:
            The speaker name as a string.
        """
        return ', '.join([speaker.name for speaker in self.speakers])

    @property
    def stage_name(self) -> str:
        """Get the stage name.

        Returns the name of the stage as a string. The API for the program adds
        a number to the stage. We filter this out.

        Returns:
            The name of the stage.
        """
        stage_name = re.findall(r'^[A-Za-z0-9\ ]+', self.stage.name)
        return stage_name[0].strip()

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
