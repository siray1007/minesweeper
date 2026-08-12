"""Shared visual tokens and Tk helpers for the Minesweeper UI."""
from __future__ import annotations

import base64
import tkinter as tk
from tkinter import ttk


COLORS = {
    'bg': '#060b14',
    'surface': '#0d1422',
    'surface_alt': '#111b2e',
    'surface_hover': '#18253a',
    'border': '#22324a',
    'text': '#edf3ff',
    'muted': '#9aa8c0',
    'subtle': '#647189',
    'primary': '#34d5ff',
    'primary_hover': '#6be5ff',
    'primary_pressed': '#1a9cc4',
    'success': '#35e0a1',
    'warning': '#ffd166',
    'danger': '#ff5c7a',
    'input': '#050912',
}

LAYOUT = {
    'auth': {
        'window': (760, 820, 620, 720),
        'card': (520, 620),
        'field': 13,
    },
    'lobby': {
        'window': (1280, 840, 1120, 760),
        'gap': 18,
        'header_height': 120,
    },
    'ranking': {
        'window': (1220, 820, 1080, 720),
    },
    'game_easy': {
        'window': (860, 860, 760, 760),
    },
    'game_medium': {
        'window': (1280, 980, 1120, 860),
    },
    'game_hard': {
        'window': (1440, 1060, 1280, 920),
    },
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
        padding=(20, 11),
        background=COLORS['primary'],
        foreground='#ffffff',
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
        padding=(16, 9),
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
        padding=(14, 8),
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
        'App.TNotebook',
        background=COLORS['bg'],
        borderwidth=0,
        tabmargins=0,
    )
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
        padding=(8, 10),
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


def metric_label(parent: tk.Misc, title: str, value: str, *, bg: str | None = None,
                 accent: str = COLORS['primary']) -> tk.Frame:
    container = tk.Frame(parent, bg=bg or COLORS['surface'])
    tk.Label(
        container, text=title, font=(FONT, 9),
        bg=container['bg'], fg=COLORS['muted'],
    ).pack(anchor='w')
    tk.Label(
        container, text=value, font=(FONT, 17, 'bold'),
        bg=container['bg'], fg=accent,
    ).pack(anchor='w', pady=(3, 0))
    return container


def section_title(parent: tk.Misc, title: str, subtitle: str = '') -> tk.Frame:
    block = tk.Frame(parent, bg=parent['bg'])
    tk.Label(
        block, text=title, font=(FONT, 24, 'bold'),
        bg=block['bg'], fg=COLORS['text'],
    ).pack(anchor='w')
    if subtitle:
        tk.Label(
            block, text=subtitle, font=(FONT, 10),
            bg=block['bg'], fg=COLORS['muted'],
        ).pack(anchor='w', pady=(4, 0))
    return block


def set_window_geometry(root: tk.Misc, width: int, height: int,
                        min_width: int, min_height: int) -> None:
    root.geometry(f'{width}x{height}')
    root.minsize(min_width, min_height)
    root.configure(bg=COLORS['bg'])
