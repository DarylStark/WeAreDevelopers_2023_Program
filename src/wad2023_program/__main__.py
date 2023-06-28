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

    @property
    def field_name(self) -> str:
        """Return the name of the field.

        We have to add a underscore to the attributes so we can use the `title`
        attribute. This method returns the normalized name.

        Returns:
            The normalized name.
        """
        return self.name.lower()


def start(sort: SortField = SortField.START_TIME) -> None:
    """Script function for the program.

    The function that gets called when starting the script.

    Args:
        sort: the field on what to sort
    """
    # Get the program
    program = get_program()

    # Sort the program. We always sort on start time first, before sorting on
    # the column given by the user
    program.sort(key=lambda x: x.start_time)
    program.sort(key=lambda x: getattr(x, sort.field_name))

    # Create a Rich console for a beautiful display
    console = Console()

    # Create a table to display the program
    table = Table(box=box.HORIZONTALS)
    table.add_column('Date')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Title')
    table.add_column('Speakers')

    # Add the rows
    for item in program:
        table.add_row(
            f'{item.start_time:%Y-%m-%d}',
            f'{item.start_time:%H:%M}',
            f'{item.end_time:%H:%M}',
            item.title,
            item.speaker
        )

    # Show the nice table
    console.print(table)


def main() -> None:
    """Start the script as a Typer app."""
    typer.run(start)


if __name__ == '__main__':
    main()
