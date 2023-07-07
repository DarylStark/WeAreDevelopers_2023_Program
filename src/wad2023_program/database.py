"""Module that contains the functions to interact with the database.

This module contains the functions to create a database engine.
"""

from sqlmodel import create_engine, SQLModel
from sqlalchemy.future import Engine


def get_db_engine(conntection_str: str) -> Engine:
    """Create a database engine and return it.

    Function to create a database engine and return the engine so the calling
    application can use it.

    Args:
        conntection_str: a SQLalchemy connection string.

    Returns:
        A database engine object.
    """
    return create_engine(conntection_str)


def create_tables(engine: Engine) -> None:
    """Create the tables.

    Function to create non-existing tables.

    Args:
        engine: the database engine.
    """
    SQLModel.metadata.create_all(
        bind=engine,
        checkfirst=True)
