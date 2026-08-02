"""Shared visual tokens and Tk helpers for the Minesweeper UI."""
from __future__ import annotations

import base64
import tkinter as tk
from tkinter import ttk


COLORS = {
    'bg': '#0b1020',
    'surface': '#121a2f',
    'surface_alt': '#182440',
    'surface_hover': '#213154',
    'border': '#2a3b61',
    'text': '#f4f7ff',
    'muted': '#9aa8c2',
    'subtle': '#6f7d99',
    'primary': '#ff4d6d',
    'primary_hover': '#ff6b85',
    'primary_pressed': '#dc3657',
    'success': '#2ed5a1',
    'warning': '#ffc857',
    'danger': '#ff6b6b',
    'input': '#080d1b',
}

FONT = 'Microsoft YaHei UI'


def configure_ttk(root: tk.Misc) -> None:
    """Configure the shared ttk component styles once per Tk interpreter."""
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass

    style.configure(
        'Primary.TButton',
        font=(FONT, 11, 'bold'),
        padding=(18, 10),
        background=COLORS['primary'],
        foreground='white',
        borderwidth=0,
        focusthickness=2,
        focuscolor=COLORS['warning'],
    )
    style.map(
        'Primary.TButton',
        background=[('pressed', COLORS['primary_pressed']),
                    ('active', COLORS['primary_hover'])],
        foreground=[('disabled', COLORS['subtle'])],
    )

    style.configure(
        'Secondary.TButton',
        font=(FONT, 10, 'bold'),
        padding=(14, 8),
        background=COLORS['surface_alt'],
        foreground=COLORS['text'],
        borderwidth=1,
        focusthickness=2,
        focuscolor=COLORS['warning'],
    )
    style.map(
        'Secondary.TButton',
        background=[('pressed', COLORS['surface']),
                    ('active', COLORS['surface_hover'])],
    )

    style.configure(
        'Ghost.TButton',
        font=(FONT, 10),
        padding=(12, 7),
        background=COLORS['surface'],
        foreground=COLORS['muted'],
        borderwidth=0,
        focusthickness=2,
        focuscolor=COLORS['warning'],
    )
    style.map(
        'Ghost.TButton',
        background=[('active', COLORS['surface_hover'])],
        foreground=[('active', COLORS['text'])],
    )

    style.configure(
        'App.TNotebook', background=COLORS['bg'], borderwidth=0, tabmargins=0)
    style.configure(
        'App.TNotebook.Tab',
        font=(FONT, 10, 'bold'),
        padding=(18, 10),
        background=COLORS['surface'],
        foreground=COLORS['muted'],
        borderwidth=0,
    )
    style.map(
        'App.TNotebook.Tab',
        background=[('selected', COLORS['surface_alt']),
                    ('active', COLORS['surface_hover'])],
        foreground=[('selected', COLORS['primary']),
                    ('active', COLORS['text'])],
    )

    style.configure(
        'App.Treeview',
        font=(FONT, 10),
        rowheight=34,
        background=COLORS['surface'],
        foreground=COLORS['text'],
        fieldbackground=COLORS['surface'],
        borderwidth=0,
    )
    style.configure(
        'App.Treeview.Heading',
        font=(FONT, 10, 'bold'),
        padding=(8, 9),
        background=COLORS['surface_alt'],
        foreground=COLORS['muted'],
        relief='flat',
        borderwidth=0,
    )
    style.map(
        'App.Treeview',
        background=[('selected', COLORS['primary'])],
        foreground=[('selected', 'white')],
    )


def load_photo(path: str, master: tk.Misc | None = None) -> tk.PhotoImage | None:
    """Load a PNG without passing a non-ASCII Windows path to Tcl."""
    try:
        with open(path, 'rb') as image_file:
            encoded = base64.b64encode(image_file.read()).decode('ascii')
        return tk.PhotoImage(master=master, data=encoded)
    except (OSError, tk.TclError):
        return None


def make_entry(parent: tk.Misc, *, show: str = '') -> tk.Entry:
    return tk.Entry(
        parent,
        font=(FONT, 12),
        show=show,
        bg=COLORS['input'],
        fg=COLORS['text'],
        insertbackground=COLORS['primary'],
        selectbackground=COLORS['primary'],
        selectforeground='white',
        relief='flat',
        bd=0,
        highlightthickness=1,
        highlightbackground=COLORS['border'],
        highlightcolor=COLORS['primary'],
    )


def set_window_geometry(root: tk.Misc, width: int, height: int,
                        min_width: int, min_height: int) -> None:
    root.geometry(f'{width}x{height}')
    root.minsize(min_width, min_height)
    root.configure(bg=COLORS['bg'])
