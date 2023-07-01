"""Module with the SessionizeParser.

Class that can be used to initiate a parser for Sessionize pages. Because the
organization of WeAreDevlopers 2023 have decided to turn off the REST API on
Sessionize, we have to parse the page using BeautifulSoup 4.
"""

from os.path import expanduser, isfile
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dateutil import parser

from .model import Session, Speaker, Stage
from .exceptions import HTMLNotDownloadedException


class SessionizeParser:
    """Parser for Sessionize pages.

    Parses Sessionize pages using BeautifulSoup 4.

    Attributes:
        sessionize_id: the ID for the meeting at sessionize.
        cache_dir: the directory where pages can be cached.
        session: a list with the session for this program.
        speakers: a list with the speakers for this program.
    """

    def __init__(self, sessionize_id: str, cache_dir: str) -> None:
        """Initiator for the object.

        Sets the sessionize ID that is used later to parse the page.

        Args:
            sessionize_id: the ID for the meeting at sessionize. Is used in the
                URL to download the meetings.
            cache_dir: the directory where cache files can be saved.
        """
        self.session_id = sessionize_id
        self.cache_dir = expanduser(cache_dir)

        # Sessions and speakers
        self.sessions: list[Session] | None = None
        self.speakers: list[Speaker] | None = None

        # Cache for the HTML
        self.cache: dict[str, str | None] = {
            'program': None,
            'speakers': None
        }

    @property
    def cache_file_program(self) -> str:
        """Return the cache file for this program.

        Returns the cache file for this program.

        Returns:
            A string for the cache file.
        """
        return expanduser(f'{self.cache_dir}/{self.session_id}.program.html')

    @property
    def cache_file_speakers(self) -> str:
        """Return the cache file for the speakers.

        Returns the cache file for the speakers.

        Returns:
            A string for the cache file.
        """
        return expanduser(f'{self.cache_dir}/{self.session_id}.speakers.html')

    @property
    def program_url(self) -> str:
        """Return the program URL from Sessionize for this program.

        Returns the URL to use when downloading the file from Sessionize.

        Returns:
            A string with the URL from Sessionize for the program.
        """
        return f'https://sessionize.com/api/v2/{self.session_id}/view/Sessions'

    @property
    def speakers_url(self) -> str:
        """Return the speakers URL from Sessionize for this program.

        Returns the URL to use when downloading the file from Sessionize.

        Returns:
            A string with the URL from Sessionize for speakers.
        """
        return f'https://sessionize.com/api/v2/{self.session_id}/view/Speakers'

    def get_files_from_cache(self) -> None:
        """Get the files for the program and speakers from the cache.

        Retrieves the files for the program and for speakers from the cache
        files. The output gets saved in the object so it can be parsed later.
        """
        for cache_file in [
                ('program', self.cache_file_program),
                ('speakers', self.cache_file_speakers)]:
            with open(cache_file[1],
                      'r',
                      encoding='utf-16') as cache_file_handle:
                self.cache[cache_file[0]] = cache_file_handle.read()

    def save_files_in_cache(self) -> None:
        """Save files in the cache.

        Saves the HTML to the cache.
        """
        # Create the directories
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

        # Save the HTML to the cache
        for page in [
                ('program', self.cache_file_program),
                ('speakers', self.cache_file_speakers)]:
            if self.cache[page[0]] is not None:
                with open(page[1],
                          'w',
                          encoding='utf-16') as outfile:
                    outfile.write(self.cache[page[0]])

    def download_session(self) -> None:
        """Get HTML for the program and the speakers from the web.

        Retrieves the HTML for the program and the speakers from the web and
        saves them in the object cache.

        Raises:
            ValueError: when a wrong status code is returned.
        """
        for url in [
                ('program', self.program_url),
                ('speakers', self.speakers_url)]:
            download_request = requests.get(
                url=url[1],
                params={'under': True},
                timeout=10)
            if download_request.status_code != 200:
                raise ValueError(
                    ('Did not receive responsecode 200; got ' +
                     f'responsecode {download_request.status_code}'))
            self.cache[url[0]] = download_request.text

    def get_html(self, cache: bool = True) -> None:
        """Get the HTML for the program and the speakers.

        Retrieves the HTML for this Sessionize event. Retrieves it from the
        cache if it exists. Otherwise it retrieves it from the web.

        Args:
            cache: specify if the cache file should be used. Warning: if no
                cache file exists and `cache` is set to True, the files will
                still be downloaded.
        """
        download = False
        if (not cache or
                not isfile(self.cache_file_program) or
                not isfile(self.cache_file_speakers)):
            download = True

        # Downloa the program
        if download:
            self.download_session()
            self.save_files_in_cache()
            return

        # Get the program from cache
        self.get_files_from_cache()

    def parse_program_html(self) -> None:
        """Parse the HTML for the program.

        Parses the program from the HTML returned by the webpage or from the
        cache. Saves it in the `sessions` attribute of the object.

        Raises:
            HTMLNotDownloadedException: when the HTML for the program page has
                not been downloaded yet.
        """

        # Local variable for the HTML
        if self.cache['program'] is None:
            raise HTMLNotDownloadedException('HTML for the program is not' +
                                             'downloaded yet')

        program_html = self.cache['program']
        self.sessions = []

        # Parse the HTML
        soup = BeautifulSoup(program_html, 'html.parser')
        session_list = soup.find_all('ul', {'class': 'sz-sessions--list'})
        sessions = session_list[0].find_all(
            'li', {'class': 'sz-session--full'})

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
            speakers = session.find_all(
                'ul', {'class': 'sz-session__speakers'})
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
            self.sessions.append(session_object)

    def parse_speakers_html(self) -> None:
        pass

    def update(self, cache: bool = True) -> None:
        """Update the sessions and speakers.

        Updates the sessions and speakers for this event.

        Args:
            cache: specify if the cache file should be used. Warning: if no
                cache file exists and `cache` is set to True, the files will
                still be downloaded.
        """
        self.get_html(cache)
        self.parse_speakers_html()
        self.parse_program_html()
