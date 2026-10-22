"""Start the FitFor command-line application."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from fitfor.cli import Menu
from fitfor.storage import DEFAULT_DATA_PATH, Storage


def main(argv: Sequence[str] | None = None) -> None:
    """Select the local data file and start the interactive menu."""
    parser = argparse.ArgumentParser(description="FitFor workout and meal log")
    parser.add_argument(
        "--data-file", type=Path, default=DEFAULT_DATA_PATH,
        help="JSON storage path (default: data/fitfor_data.json in the project)",
    )
    arguments = parser.parse_args(argv)
    Menu(Storage(arguments.data_file)).run()


if __name__ == "__main__":
    main()
