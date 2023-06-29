"""Module with program functions.

Module that contains all functions to retrieve and parse the program.
"""

from os.path import dirname, expanduser
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dateutil import parser

from .app_config import AppConfig
from .model import Session, Speaker, Stage

# Configuration
config = AppConfig()


def get_program_from_cache() -> str:
    """Get program from cache file.

    Retrieves the program from the saved cache file.

    Returns:
        The HTML for the program in the cache file.
    """
    with open(expanduser(config.cache_file),
              'r',
              encoding='utf-16') as cache_file_handle:
        return cache_file_handle.read()


def download_program() -> str:
    """Get program from the web.

    Retrieves the program from the web URL.

    Returns:
        The HTML for the program on the web.

    Raises:
        ValueError: when a wrong status code is returned.
    """
    program_request = requests.get(
        url=config.program_url,
        params=config.program_params,
        timeout=10)
    if program_request.status_code != 200:
        raise ValueError(
            ('Did not receive responsecode 200; got ' +
             f'responsecode {program_request.status_code}'))
    return program_request.text


def parse_program(program_html: str) -> list[Session]:
    """Parse the HTML for the program.

    Parses the program from the HTML returned by the webpage or from the cache.

    Args:
        program_html: the HTML from cache or from the web that contains the
            program.

    Returns:
        A list with all Sessions.
    """
    # Empty session list
    conference_session_list: list[Session] = []

    # Parse the HTML
    soup = BeautifulSoup(program_html, 'html.parser')
    session_list = soup.find_all('ul', {'class': 'sz-sessions--list'})
    sessions = session_list[0].find_all('li', {'class': 'sz-session--full'})

    # Loop through the session and create the correct objects
    for session in sessions:
        # Create a new session object
        session_object = Session()

        # Get the title
        session_object.title = session.find_all('h3')[0].text.strip()

        # Get the description
        description_tag = session.find_all(
            'p', {'class': 'sz-session__description'})
        if len(description_tag) == 1:
            session_object.description = description_tag[0].text.strip()

        # Get the stage
        stage = session.find_all('div', {'class': 'sz-session__room'})[0]
        session_object.stage = Stage(
            id=stage['data-roomid'],
            name=stage.text
        )

        # Get the speakers
        speakers = session.find_all('ul', {'class': 'sz-session__speakers'})
        for speaker in speakers[0].find_all('li'):
            speaker_object = Speaker(
                uid=speaker['data-speakerid'],
                name=speaker.text.strip())
            session_object.speakers.append(speaker_object)

        # Get the session times
        session_time = session.find_all(
            'div', {'class': 'sz-session__time'})[0]
        time_attribute = session_time['data-sztz'].split('|')
        session_object.start_time = parser.parse(time_attribute[2])
        session_object.end_time = parser.parse(time_attribute[3])

        # Append the session to the list
        conference_session_list.append(session_object)

    return conference_session_list


def get_program(cache: bool = True) -> list[Session]:
    """Get the program.

    Retrieves the program from cache or, if that fails, from the web and
    returns it parsed.

    Args:
        cache: specify if the page can be retrieved from cache.

    Returns:
        The parsed program.
    """
    try:
        if not cache:
            raise FileNotFoundError
        program = get_program_from_cache()
    except FileNotFoundError:
        program = download_program()

        # Create cache directory
        cache_file = expanduser(config.cache_file)
        directory = dirname(cache_file)
        Path(directory).mkdir(parents=True, exist_ok=True)

        # Write to cache
        with open(cache_file,
                  'w',
                  encoding='utf-16') as cache_file_handle:
            cache_file_handle.write(str(program))
    return parse_program(program)
