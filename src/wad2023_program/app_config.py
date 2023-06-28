from pydantic import BaseSettings


class AppConfig(BaseSettings):
    cache_file: str = '~/.cache/program.html'
    program_url: str = 'https://sessionize.com/api/v2/tx3wi18f/view/Sessions'
    program_params: dict = {'under': True}
