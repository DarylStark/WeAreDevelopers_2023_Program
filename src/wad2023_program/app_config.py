"""Module with the config model.

Contains the model for the configuration of the application.
"""
from pydantic import BaseSettings


class AppConfig(BaseSettings):
    """Application config model.

    Class with the attributes for the configuration of the application.

    Attributes:
        program_id: the Sessionize ID for the session program.
        workshops_id: the Sessionize ID for the workshop program.
        db_connection_str: the connection string for the SQL database.
    """

    program_id: str = 'tx3wi18f'
    workshops_id: str = 'txhel6oq'
    db_connection_str: str = 'sqlite:///:memory:'
