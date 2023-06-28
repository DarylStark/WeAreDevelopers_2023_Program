"""Main module.

Contains the main script for the WAD2023 applican.
"""
from enum import Enum

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from .program import get_program


class SortField(str, Enum):
    """The field to sort on.

    Specifies the field to sort on.

    Attributes:
        _start_time: sort on the start time.
        _end_time: sort on the end time.
        _title: sort on the title.
        _speaker: sort on the speakername.
    """
    START_TIME = 'start'
    END_TIME = 'end'
    TITLE = 'title'
    SPEAKER = 'speaker'
    STAGE_NAME = 'stage'

    @property
    def field_name(self) -> str:
        """Return the name of the field.

        We have to add a underscore to the attributes so we can use the `title`
        attribute. This method returns the normalized name.

        Returns:
            The normalized name.
        """
        return self.name.lower()


def main(
        sort: SortField = SortField.START_TIME,
        in_title: str = '',
        in_speaker: str = '',
        stage: str = ''
) -> None:
    """Script function for the program.

    The function that gets called when starting the script.

    Args
        sort: the field on what to sort.
        in_title: filter on words in the title.
    """
    # Get the program
    program = get_program()

    # Sort the program. We always sort on start time first, before sorting on
    # the column given by the user
    program.sort(key=lambda x: x.start_time)
    program.sort(key=lambda x: getattr(x, sort.field_name))

    # Filter
    if len(in_title) > 0:
        program = list(filter(lambda session: in_title.lower()
                              in session.title.lower(), program))
    if len(in_speaker) > 0:
        program = list(filter(lambda session: in_speaker.lower()
                              in session.speaker.lower(), program))
    if len(stage) > 0:
        program = list(filter(lambda session:
                              session.stage_name.lower() == stage.lower(),
                              program))

    # Create a Rich console for a beautiful display
    console = Console()

    # Create a table to display the program
    table = Table(box=box.HORIZONTALS)
    table.add_column('Date')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Stage')
    table.add_column('Title')
    table.add_column('Speakers')

    # Add the rows
    for item in program:
        table.add_row(
            f'{item.start_time:%Y-%m-%d}',
            f'{item.start_time:%H:%M}',
            f'{item.end_time:%H:%M}',
            item.stage_name,
            item.title,
            item.speaker
        )

    # Show the nice table
    console.print(table)


if __name__ == '__main__':
    typer.run(main)
