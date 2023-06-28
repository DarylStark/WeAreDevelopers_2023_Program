"""Module with the config model.

Contains the model for the configuration of the application.
"""
from pydantic import BaseSettings


class AppConfig(BaseSettings):
    """Application config model.

    Class with the attributes for the configuration of the application.

    Attributes:
        cache_file: the location for the cache file.
        program_url: the URL for the program.
        program_params: the params for the URL.
    """

    cache_file: str = '~/.cache/program.html'
    program_url: str = 'https://sessionize.com/api/v2/tx3wi18f/view/Sessions'
    program_params: dict = {'under': True}
