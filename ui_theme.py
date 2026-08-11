"""Shared visual tokens and Tk helpers for the cyber Minesweeper UI."""
from __future__ import annotations

import base64
import tkinter as tk
from tkinter import ttk


COLORS = {
    "bg": "#070b14",
    "surface": "#0d1320",
    "surface_alt": "#111a2c",
    "surface_hover": "#162238",
    "border": "#22314a",
    "text": "#edf3ff",
    "muted": "#8a97b2",
    "subtle": "#5d687f",
    "primary": "#34d6ff",
    "primary_hover": "#67e3ff",
    "primary_pressed": "#179cc2",
    "success": "#35e0a1",
    "warning": "#ffd166",
    "danger": "#ff5c7a",
    "accent": "#9b6dff",
    "input": "#050812",
}

FONT = "Microsoft YaHei UI"


def configure_ttk(root: tk.Misc) -> None:
    """Configure shared ttk styles for the app."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Primary.TButton",
        font=(FONT, 11, "bold"),
        padding=(16, 9),
        background=COLORS["primary"],
        foreground="#08101b",
        borderwidth=0,
        focusthickness=2,
        focuscolor=COLORS["warning"],
    )
    style.map(
        "Primary.TButton",
        background=[("pressed", COLORS["primary_pressed"]), ("active", COLORS["primary_hover"])],
        foreground=[("disabled", COLORS["subtle"])],
    )

    style.configure(
        "Secondary.TButton",
        font=(FONT, 10, "bold"),
        padding=(14, 8),
        background=COLORS["surface_alt"],
        foreground=COLORS["text"],
        borderwidth=1,
        focusthickness=2,
        focuscolor=COLORS["warning"],
    )
    style.map(
        "Secondary.TButton",
        background=[("pressed", COLORS["surface"]), ("active", COLORS["surface_hover"])],
    )

    style.configure(
        "Ghost.TButton",
        font=(FONT, 10),
        padding=(12, 7),
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        borderwidth=0,
        focusthickness=2,
        focuscolor=COLORS["warning"],
    )
    style.map(
        "Ghost.TButton",
        background=[("active", COLORS["surface_hover"])],
        foreground=[("active", COLORS["text"])],
    )

    style.configure("App.TNotebook", background=COLORS["bg"], borderwidth=0, tabmargins=0)
    style.configure(
        "App.TNotebook.Tab",
        font=(FONT, 10, "bold"),
        padding=(16, 9),
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        borderwidth=0,
    )
    style.map(
        "App.TNotebook.Tab",
        background=[("selected", COLORS["surface_alt"]), ("active", COLORS["surface_hover"])],
        foreground=[("selected", COLORS["primary"]), ("active", COLORS["text"])],
    )

    style.configure(
        "App.Treeview",
        font=(FONT, 10),
        rowheight=32,
        background=COLORS["surface"],
        foreground=COLORS["text"],
        fieldbackground=COLORS["surface"],
        borderwidth=0,
    )
    style.configure(
        "App.Treeview.Heading",
        font=(FONT, 10, "bold"),
        padding=(8, 8),
        background=COLORS["surface_alt"],
        foreground=COLORS["muted"],
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "App.Treeview",
        background=[("selected", COLORS["primary"])],
        foreground=[("selected", "#08101b")],
    )


def load_photo(path: str, master: tk.Misc | None = None) -> tk.PhotoImage | None:
    """Load a PNG without passing a non-ASCII Windows path to Tcl."""
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("ascii")
        return tk.PhotoImage(master=master, data=encoded)
    except (OSError, tk.TclError):
        return None


def make_entry(parent: tk.Misc, *, show: str = "") -> tk.Entry:
    return tk.Entry(
        parent,
        font=(FONT, 12),
        show=show,
        bg=COLORS["input"],
        fg=COLORS["text"],
        insertbackground=COLORS["primary"],
        selectbackground=COLORS["primary"],
        selectforeground="#08101b",
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["primary"],
    )


def set_window_geometry(root: tk.Misc, width: int, height: int, min_width: int, min_height: int) -> None:
    root.geometry(f"{width}x{height}")
    root.minsize(min_width, min_height)
    root.configure(bg=COLORS["bg"])
