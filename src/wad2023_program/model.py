"""Model module.

Contains the models for the application.
"""
from datetime import datetime
from pydantic import BaseModel


class Model(BaseModel):
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

    uid: str
    name: str


class Stage(Model):
    """Model for a stage.

    Class with the attributes for a stage.

    Attributes:
        uid: the ID of the stage.
        name: the name of the stage.
    """

    id: int
    name: str


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

    title: str = ''
    stage: Stage | None = None
    speakers: list[Speaker] = []
    start_time: datetime = datetime.now()
    end_time: datetime = datetime.now()
    tags: list[str] = []

    @property
    def speaker(self) -> str:
        """Get the speaker name.

        Returns the speaker name as a string. Can be useful when sorting a list
        of sessions.

        Returns:
            The speaker name as a string.
        """
        return ', '.join([speaker.name for speaker in self.speakers])
