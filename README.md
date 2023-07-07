# WeAreDevelopers 2023 - Program CLI

In less then a month, the [WeAreDevelopers 2023](https://www.wearedevelopers.com/world-congress) conference is finally starting! Two days of being with like-minded people, talking about code and infrastructure! If you're like me, you're very excited about this, but a bit overwhelmed by the 236 session that are planned. It's difficult to pick the sessions that are right for me. The [programpage](https://www.wearedevelopers.com/world-congress/program) on the website is not really to my liking, so I decided to create a small CLI script to browse through the sessions.

# Installation

Installation can be done using `pip`:

```bash
pip install wad2023-program
```

## Usage

After installing, the CLI script can be executed by executing the `wad23` command in your browser. The CLI arguments contain two groups. The syntax is `wad23 <group> [optional argument]`

-   `wad23 sync`: syncs the database with the sessions on the website of the conference. This should be done before using the command.
-   `wad23 sessions`: lists the sessions in the database.
    -   You can filter the sessions with the following optional arguments:
        -   `--title`: filter on specific words in the title.
        -   `--description`: filter on specific words in the description.
        -   `--find`: filter on specific words in the description and the title.
        -   `--speaker`: filter on specific words in the names of the speakers.
        -   `--speaker-tagline`: filter on specific words in the tagline of the speakers.
        -   `--speakers-bio`: filter on specific words in the bio of the speakers.
        -   `--only-favourite`: display only sessions that you marked as favourite.
        -   `--no-only-favourite`: display only sessions that you not marked as favourite.
    -   You can also specify how to output the file:
        -   `--output=table`: the default; displays a table with the sessions
        -   `--output=details`: displays the sessions with extra details, like the speakers and the description.
        -   `--output=csv`: displays the sessions in CSV format.
    -   And you can mark sessions as favourite:
        -   `--set-as-favourite`: set the selected sessions as favourite.
        -   `--no-set-as-favourite`: set the selected sessions as not favourite.

## Configuration

There is not much to configure for the application, but there are a few configuration options you have. These configuration options are set with environment variables:

-   `DB_CONNECTION_STR`: set the connection string for the database. By default it uses a `SQLite` database in the local directory, but you can, for instance, use a PostgreSQL database by specifing `postgresql+pg8000://<username:<password>@<server>/<database-name>`.
-   `PROGRAM_ID` and `WORKSHOPS_ID`: the ID for Sessionize for the program and the workshops. The defaults are good for WeAreDevelopers 2023.