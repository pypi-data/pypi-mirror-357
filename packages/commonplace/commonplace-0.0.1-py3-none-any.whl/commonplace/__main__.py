import logging
from pathlib import Path

import typer
from rich.progress import track

from commonplace._claude import ClaudeImporter
from commonplace._gemini import GeminiImporter
from commonplace._store import ActivityLogDirectoryStore

logger = logging.getLogger("melange")
app = typer.Typer(
    help="melange: AI-powered journaling tool", pretty_exceptions_enable=False
)


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v")):
    lvl = logging.INFO
    if verbose:
        lvl = logging.DEBUG
    logging.basicConfig(level=lvl)


@app.command(name="import")
def import_(path: Path):
    """Import activity logs from a file."""

    if not path.exists():
        logger.error(f"The file {path} does not exist.")
        raise typer.Exit(code=1)
    if not path.is_file():
        logger.error(f"The path {path} is not a file.")
        raise typer.Exit(code=1)

    importers = [GeminiImporter(), ClaudeImporter()]
    importer = next((imp for imp in importers if imp.can_import(path)), None)
    if importer is None:
        logger.error(
            f"The file {path} is not supported by any available importer."
        )
        raise typer.Exit(code=1)
    logger.info(f"Using {importer.source} importer for {path}.")

    logs = importer.import_(path)
    logger.info(f"Imported {len(logs)} activity logs from {path}.")

    store = ActivityLogDirectoryStore(root=Path("output"))
    for log in track(logs):
        store.store(log)


@app.command()
def journal():
    """Generate a journal entry."""
    logger.info("Journal command is not yet implemented.")
