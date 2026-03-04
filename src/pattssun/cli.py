import asyncio

import typer

from pattssun.config import Settings
from pattssun.steps.fetch_bookmarks import fetch_bookmarks, save_bookmarks

app = typer.Typer(help="pattssun — creative pipeline toolkit")


@app.command()
def bookmarks(
    save: bool = typer.Option(False, "--save", "-s", help="Save bookmarks to output directory"),
) -> None:
    """Fetch bookmarked tweets from X."""
    settings = Settings()
    tweets = asyncio.run(fetch_bookmarks(settings))

    print(f"\nFetched {len(tweets)} bookmarks\n")
    for t in tweets:
        preview = t.text[:120].replace("\n", " ")
        print(f"  @{t.author_username}: {preview}")

    if save:
        save_bookmarks(settings, tweets)
