"""Module with the functions to display information.

Tihs module contains function to display information in the correct way.
"""
from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

from .model import Session, Speaker


def speaker_text(speaker: Speaker) -> str:
    """Create a text for a speaker.

    Returns a string in a default format for a speaker.

    Args:
        speaker: the speaker object.

    Returns:
        The format for the speaker.
    """
    output_text = f'\n[yellow][b]{speaker.name}[/b][/yellow]'

    if len(speaker.tagline) > 0:
        output_text += f'\n[orange][i]{speaker.tagline}[/i][/orange]'

    if len(speaker.bio) > 0:
        output_text += '\n\n' + speaker.bio

    return output_text


def view_sessions_as_table(sessions: list[Session]) -> None:
    """View Sessions in a table.

    Prints the sessions in a `rich` table.

    Args:
        sessions: a list with Session objects to view.
    """
    console = Console()
    table = Table(box=box.HORIZONTALS)
    table.add_column('*')
    table.add_column('Type')
    table.add_column('Date')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Stage')
    table.add_column('Title')
    table.add_column('Speakers')
    for sess in sessions:
        table.add_row(
            '*' if sess.favourite else '',
            sess.session_type.capitalize(),
            f'{sess.start_time_berlin:%Y-%m-%d}',
            f'{sess.start_time_berlin:%H:%M}',
            f'{sess.end_time_berlin:%H:%M}',
            sess.stage.name,
            sess.title,
            ', '.join([speaker.name for speaker in sess.speakers])
        )
    console.print(table)


def view_sessions_as_csv(sessions: list[Session]) -> None:
    """View Sessions in a csv.

    Prints the sessions in a CSV output.

    Args:
        sessions: a list with Session objects to view.
    """
    columns = ('Favourite', 'Type', 'Date', 'Start',
               'End', 'Stage', 'Title', 'Speakers')
    print(';'.join([f'"{column}"' for column in columns]))
    for sess in sessions:
        row = ['*' if sess.favourite else '',
               sess.session_type.capitalize(),
               f'{sess.start_time_berlin:%Y-%m-%d}',
               f'{sess.start_time_berlin:%H:%M}',
               f'{sess.end_time_berlin:%H:%M}',
               sess.stage.name,
               sess.title,
               ', '.join([speaker.name for speaker in sess.speakers])]
        print(';'.join([f'"{row_data}"' for row_data in row]))


def view_sessions_as_details(sessions: list[Session]) -> None:
    """View Sessions with details.

    Prints the sessions in a CSV output.

    Args:
        sessions: a list with Session objects to view.
    """
    console = Console()
    for sess in sessions:
        table = Table(box=box.MINIMAL, show_header=False)
        table.add_column('Field')
        table.add_column('Information')
        table.add_row('Title', sess.title)
        table.add_row('Session ID', str(sess.id))
        table.add_row(
            'Date', (f'{sess.start_time_berlin:%Y-%m-%d} ' +
                     f'({sess.start_time_berlin:%H:%M} - ' +
                     f'{sess.end_time_berlin:%H:%M})'))
        table.add_row('Stage', sess.stage.name)

        output_parts: list[str | Table] = [table]
        if len(sess.description) > 0:
            output_parts.append(sess.description + '\n')

        output_parts.append('[green][b]## Speakers[/b][/green]')

        for speaker in sess.speakers:
            output_parts.append(speaker_text(speaker))

        console.print(
            Panel(
                Group(*output_parts)
            ))
