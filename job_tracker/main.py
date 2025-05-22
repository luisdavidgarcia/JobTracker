"""Main Module for Job Tracker."""

import argparse

from pynput import keyboard
from utils.database_helpers import _quit_program, _read_schema_from_file, _save_job_description

SAVE_JOB_DESCRIPTION_HOTKEY = "<ctrl>+<alt>+s"
QUIT_HOTKEY = "<ctrl>+<alt>+x"


def main() -> None:
    """Main function to parse job description and add to database."""
    parser = argparse.ArgumentParser(
        description="Parse job description and add to database",
    )
    parser.add_argument(
        "--schema",
        type=str,
        help="Path to the database schema file",
        default="init.sql",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model to use for parsing",
        default="llama3.2",
    )
    args = parser.parse_args()

    schema = _read_schema_from_file(args.schema)

    with keyboard.GlobalHotKeys(
        {
            SAVE_JOB_DESCRIPTION_HOTKEY: lambda: _save_job_description(schema, args.model),
            QUIT_HOTKEY: _quit_program,
        },
    ) as listener:
        print("Listening for hotkeys...\n")
        listener.join()


if __name__ == "__main__":
    main()
