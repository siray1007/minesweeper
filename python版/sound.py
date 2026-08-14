"""Sound effects for the Minesweeper client (Windows only)."""
from __future__ import annotations

import os
import threading


_DATA_ROOT = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or os.path.expanduser("~")
_DATA_DIR = os.path.join(_DATA_ROOT, "CyberMinesweeper")
_SOUND_FILE = os.path.join(_DATA_DIR, "sound_pref.txt")

_enabled = True


def is_enabled() -> bool:
    return _enabled


def set_enabled(value: bool) -> None:
    global _enabled
    _enabled = value
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(_SOUND_FILE, "w", encoding="utf-8") as sound_file:
            sound_file.write("on" if value else "off")
    except OSError:
        pass


def _play(frequencies: list[int], durations: list[int]) -> None:
    """Play tones off the main thread so the UI never blocks."""
    if not _enabled:
        return

    def run() -> None:
        try:
            import winsound
        except ImportError:
            return
        try:
            for freq, dur in zip(frequencies, durations):
                winsound.Beep(freq, dur)
        except RuntimeError:
            pass

    threading.Thread(target=run, daemon=True).start()


def play_reveal() -> None:
    _play([880], [40])


def play_flag() -> None:
    _play([660], [60])


def play_explosion() -> None:
    _play([200, 150], [180, 200])


def play_win() -> None:
    _play([523, 659, 784, 1047], [120, 120, 120, 220])


def _load_enabled() -> None:
    global _enabled
    try:
        with open(_SOUND_FILE, "r", encoding="utf-8") as sound_file:
            _enabled = sound_file.read().strip() != "off"
    except OSError:
        _enabled = True


_load_enabled()
