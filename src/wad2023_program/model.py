from datetime import datetime
from pydantic import BaseModel


class Model(BaseModel):
    class Config:
        """Config for the models.

        Attributes:
            validate_assignment: specifies if assigned values should be
                validated by Pydantic. If this is set to False, only
                assignments in the constructor are validated.
        """

        validate_assignment = True


class Speaker(Model):
    uid: str
    name: str


class Stage(Model):
    id: int
    name: str


class Session(Model):
    title: str | None = None
    stage: Stage | None = None
    speakers: list[Speaker] = []
    start_time: datetime | None = None
    end_time: datetime | None = None
    tags: list[str] = []
