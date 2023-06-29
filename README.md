# WeAreDevelopers 2023 - Program CLI

In less then a month, the [WeAreDevelopers 2023](https://www.wearedevelopers.com/world-congress) conference is finally starting! Two days of being with like-minded people, talking about code and infrastructure! If you're like me, you're very excited about this, but a bit overwhelmed by the 236 session that are planned. It's difficult to pick the sessions that are right for me. The [programpage](https://www.wearedevelopers.com/world-congress/program) on the website is not really to my liking, so I decided to create a small CLI script to browse through the sessions.

# Installation

Installation can be done using `pip`:

```bash
pip install wad2023-program
```

## Usage

After installing, the CLI script can be executed by executing the `wad23` command in your browser. By executing it without arguments, you get a complete list of all sessions. the first time you run the script, it will download these sessions from the program page (from [Sessionize](https://sessionize.com/api/v2/tx3wi18f/view/Sessions) to be precise) and save the page to your `.cache` folder in your homefolder (the folder will be created if it doesn't exist). All subsequent requests will be done using the cache the original page is not flooded with requests.

The script has a few command line arguments you can use to sort and filter the list. You can use `--help` to see these. Here is a list of the command line options:

-   `--sort=<sort_field>`: specify a field to sort on. Can be `start`, `end`, `title`, `speaker` or `stage`.
-   `--in-title=<text>`: shows only session with a specific word in the title field. For example, the command line argument `--in-title=python` will only display sessions with the word Python in it.
-   `--in-speaker=<text>`: shows only sessions with a specific word in the speaker field.
-   `--in-description=<text>`: shows only sessions with a specific word in the description field.
-   `--stage=<stage_name>`: filters on stage. The stage has to match exactly, like `--stage="Stage 2"`, for instance.
-   `--output=<output_format>`: let's you specify a output format. Can be either `table` (default), `csv` for CSV output or `details` for detailed output. The detailed output will also display the description.
-   `--cache` and `--no-cache`: specifies if the script should use the cache. By default, it uses the cache file, but if you want to skip that, you can specify `--no-cache`. Be warned though: do _not_ flood the webserver of Sessionize with requests!

## Configuration

There is not much to configure for the application, but there are a few configuration options you have. These configuration options are set with environment variables:

-   `CACHE_FILE`: specifies where the cache file should be placed. Default: `~/.cache/program.html`
-   `PROGRAM_URL`: specifies where to download the program from. Default: `https://sessionize.com/api/v2/tx3wi18f/view/Sessions`
-   `PROGRAM_PARAMS`: dictionary that sets specific parameters to the web URL. Default: `dict = {'under': True}`