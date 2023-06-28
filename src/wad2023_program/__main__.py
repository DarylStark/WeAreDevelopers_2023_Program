"""Main module.

Contains the main script for the WAD2023 applican.
"""
from rich import box
from rich.console import Console
from rich.table import Table
import typer

from .program import get_program


def main(sort_field: str = 'start_time') -> None:
    """Script function for the program.

    The function that gets called when starting the script.
    """
    # Get the program
    program = get_program()

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
            ','.join([speaker.name for speaker in item.speakers])
        )

    # Show the nice table
    console.print(table)


if __name__ == '__main__':
    typer.run(main)
