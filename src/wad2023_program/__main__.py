import requests
from dateutil import parser

from bs4 import BeautifulSoup

from .app_config import AppConfig
from .model import Session, Speaker, Stage

# Configuration
config = AppConfig()


def get_program_from_cache() -> str:
    with open(config.cache_file, 'r', encoding='utf-16') as cache_file_handle:
        return cache_file_handle.read()


def download_program() -> str:
    print('downloading_program')
    # Download program
    program_request = requests.get(config.program_url, config.program_params)
    if program_request.status_code != 200:
        raise ValueError(
            ('Did not receive responsecode 200; got ' +
             f'responsecode {program_request.status_code}'))
    return program_request.text


def parse_program(program_html) -> list[Session]:
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


def get_program() -> list[Session]:
    try:
        program = get_program_from_cache()
    except FileNotFoundError:
        program = download_program()
        with open(config.cache_file, 'w', encoding='utf-16') as cache_file_handle:
            cache_file_handle.write(str(program))
    return parse_program(program)


def main() -> None:

    # Get the program
    program = get_program()

    pass


if __name__ == '__main__':
    main()
