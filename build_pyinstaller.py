"""Run the user-installed PyInstaller from restricted Python environments."""
from __future__ import annotations

import sys


if len(sys.argv) < 2 or not sys.argv[1].startswith("--pyinstaller-path="):
    raise SystemExit("Missing --pyinstaller-path")
pyinstaller_path = sys.argv.pop(1).split("=", 1)[1]
sys.path.insert(0, pyinstaller_path)

from PyInstaller.__main__ import run


if __name__ == "__main__":
    run(sys.argv[1:])
