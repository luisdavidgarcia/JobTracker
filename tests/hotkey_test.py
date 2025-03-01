"""Test for hotkey functionality."""

from pynput import keyboard


def _on_activate() -> None:
    print("Hotkey pressed!")


with keyboard.GlobalHotKeys(
    {
        "<ctrl>+<alt>+s": _on_activate,
    },
) as h:
    h.join()
