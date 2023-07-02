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

    cache_dir: str = '~/.cache/wad2023/'
    program_id: str = 'tx3wi18f'
    workshops_id: str = 'tx3wi18f'
