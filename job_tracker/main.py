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
        default="example.init.sql",
    )
    args = parser.parse_args()

    schema = _read_schema_from_file(args.schema)

    with keyboard.GlobalHotKeys(
        {
            SAVE_JOB_DESCRIPTION_HOTKEY: lambda: _save_job_description(schema),
            QUIT_HOTKEY: _quit_program,
        },
    ) as listener:
        listener.join()


if __name__ == "__main__":
    main()
