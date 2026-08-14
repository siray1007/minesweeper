"""Shared visual tokens and Tk helpers for the cyber Minesweeper UI."""
from __future__ import annotations

import base64
import os
import tkinter as tk
from tkinter import ttk


_DATA_ROOT = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or os.path.expanduser("~")
_DATA_DIR = os.path.join(_DATA_ROOT, "CyberMinesweeper")
_GEOM_FILE = os.path.join(_DATA_DIR, "window_geometry.txt")


DARK_COLORS = {
    "bg": "#102a43",
    "bg_grid": "#183a56",
    "surface": "#173b57",
    "surface_alt": "#214c69",
    "surface_metal": "#2b5873",
    "surface_hover": "#356983",
    "surface_pressed": "#1f4257",
    "border": "#5c7f96",
    "border_hot": "#64ddf2",
    "border_dim": "#345b73",
    "tile_border": "#6f91a6",
    "tile_open_border": "#9db5c4",
    "text": "#f5fbff",
    "muted": "#c4d7e2",
    "subtle": "#9bb7c8",
    "disabled": "#8fb3c6",
    "primary": "#55d8ee",
    "primary_hover": "#7ae6f5",
    "primary_pressed": "#31b8d1",
    "success": "#6ee7b7",
    "warning": "#ffd166",
    "danger": "#ff6f91",
    "danger_dim": "#6b2944",
    "danger_pressed": "#4d1f33",
    "accent": "#a99cff",
    "input": "#0e314c",
    "tile_even": "#39bde0",
    "tile_odd": "#62d8c7",
    "tile_open": "#d7e6ec",
    "tile_open_alt": "#cfdee5",
    "tile_open_highlight": "#f6fbfd",
    "tile_open_shadow": "#9db4c1",
    "tile_flag": "#a83f62",
    "tile_edge_light": "#c5f6ff",
    "tile_edge_shadow": "#28718c",
}


LIGHT_COLORS = {
    "bg": "#eef2f7",
    "bg_grid": "#e2e8f0",
    "surface": "#ffffff",
    "surface_alt": "#f4f7fb",
    "surface_metal": "#e8eef5",
    "surface_hover": "#dbe6f0",
    "surface_pressed": "#c9d9e8",
    "border": "#b8c7d8",
    "border_hot": "#0aa2c0",
    "border_dim": "#d5dee8",
    "tile_border": "#9db5c8",
    "tile_open_border": "#c3d0dc",
    "text": "#10263a",
    "muted": "#4a5f73",
    "subtle": "#6b7f92",
    "disabled": "#94a7b8",
    "primary": "#0a9bb8",
    "primary_hover": "#0bb0d0",
    "primary_pressed": "#087f99",
    "success": "#0e9f6e",
    "warning": "#d97706",
    "danger": "#e0446c",
    "danger_dim": "#f7d5de",
    "danger_pressed": "#f0b8c8",
    "accent": "#7c5cff",
    "input": "#ffffff",
    "tile_even": "#4a9bd8",
    "tile_odd": "#43b8a0",
    "tile_open": "#f8fafc",
    "tile_open_alt": "#f0f4f8",
    "tile_open_highlight": "#ffffff",
    "tile_open_shadow": "#cbd6e0",
    "tile_flag": "#f4c7d1",
    "tile_edge_light": "#eaf6ff",
    "tile_edge_shadow": "#9fb6c8",
}


COLORS = dict(DARK_COLORS)

FONT = "Microsoft YaHei UI"
FONT_MONO = "Consolas"

LAYOUT = {
    "auth": (720, 780, 620, 680),
    "lobby": (1280, 800, 1080, 680),
    "game_easy": (960, 720, 820, 620),
    "game_medium": (1180, 780, 1000, 680),
    "game_hard": (1360, 820, 1100, 700),
    "ranking": (1260, 800, 1080, 680),
    "profile": (1200, 760, 1040, 680),
}


class CyberButton(tk.Button):
    """A hard-edged Tk button that does not inherit platform ttk softness."""

    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command=None,
        *,
        variant: str = "primary",
        width: int = 0,
        size: str = "normal",
    ):
        if variant == "primary":
            bg, hover_bg, pressed_bg = COLORS["primary"], COLORS["primary_hover"], COLORS["primary_pressed"]
            fg, border = "#071019", COLORS["primary"]
        elif variant == "danger":
            bg, hover_bg, pressed_bg = COLORS["danger_dim"], COLORS["danger"], COLORS["danger_pressed"]
            fg, border = COLORS["text"], COLORS["danger"]
        else:
            bg, hover_bg, pressed_bg = COLORS["surface_metal"], COLORS["surface_hover"], COLORS["surface_pressed"]
            fg, border = COLORS["text"], COLORS["border_hot"] if size == "large" else COLORS["border"]
        font_size, padx, pady = (12, 22, 12) if size == "large" else (10, 18, 9)
        super().__init__(
            parent,
            text=text,
            command=command,
            font=(FONT, font_size, "bold"),
            bg=bg,
            fg=fg,
            activebackground=pressed_bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=border,
            highlightcolor=border,
            padx=padx,
            pady=pady,
            cursor="hand2",
            width=width,
        )
        self._normal_bg = bg
        self._hover_bg = hover_bg
        self.bind("<Enter>", lambda _event: self.configure(bg=self._hover_bg))
        self.bind("<Leave>", lambda _event: self.configure(bg=self._normal_bg))


def configure_ttk(root: tk.Misc) -> None:
    """Configure shared ttk styles for the app."""
    root.option_add("*TCombobox*Listbox.background", COLORS["surface_metal"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["primary"])
    root.option_add("*TCombobox*Listbox.selectForeground", "#08101b")
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Primary.TButton", font=(FONT, 11, "bold"), padding=(16, 9), background=COLORS["primary"], foreground="#071019", borderwidth=0, focusthickness=2, focuscolor=COLORS["warning"])
    style.map(
        "Primary.TButton",
        background=[("pressed", COLORS["primary_pressed"]), ("active", COLORS["primary_hover"])],
        foreground=[("disabled", COLORS["subtle"])],
    )

    style.configure("Secondary.TButton", font=(FONT, 10, "bold"), padding=(14, 8), background=COLORS["surface_alt"], foreground=COLORS["text"], borderwidth=1, focusthickness=2, focuscolor=COLORS["warning"])
    style.map(
        "Secondary.TButton",
        background=[("pressed", COLORS["surface"]), ("active", COLORS["surface_hover"])],
    )

    style.configure("Ghost.TButton", font=(FONT, 9), padding=(10, 6), background=COLORS["surface"], foreground=COLORS["muted"], borderwidth=0, focusthickness=2, focuscolor=COLORS["warning"])
    style.map(
        "Ghost.TButton",
        background=[("active", COLORS["surface_hover"])],
        foreground=[("active", COLORS["text"])],
    )

    style.configure(
        "Language.TCombobox",
        font=(FONT, 10, "bold"),
        padding=(10, 6),
        fieldbackground=COLORS["surface_metal"],
        background=COLORS["surface_metal"],
        foreground=COLORS["text"],
        arrowcolor=COLORS["primary"],
        bordercolor=COLORS["border_dim"],
        lightcolor=COLORS["border_dim"],
        darkcolor=COLORS["border_dim"],
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Language.TCombobox",
        fieldbackground=[("readonly", COLORS["surface_alt"]), ("focus", COLORS["surface_hover"])],
        foreground=[("readonly", COLORS["text"])],
        selectbackground=[("readonly", COLORS["surface_metal"])],
        selectforeground=[("readonly", COLORS["text"])],
        bordercolor=[("focus", COLORS["border_hot"])],
        lightcolor=[("focus", COLORS["border_hot"])],
        darkcolor=[("focus", COLORS["border_hot"])],
    )

    style.configure("App.TNotebook", background=COLORS["bg"], borderwidth=0, tabmargins=0)
    style.configure(
        "App.TNotebook.Tab",
        font=(FONT, 10, "bold"),
        padding=(14, 9),
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
        rowheight=30,
        background=COLORS["surface"],
        foreground=COLORS["text"],
        fieldbackground=COLORS["surface"],
        borderwidth=0,
    )
    style.configure(
        "App.Treeview.Heading",
        font=(FONT, 10, "bold"),
        padding=(8, 7),
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

    for orientation in ("Vertical", "Horizontal"):
        style.configure(
            f"Cyber.{orientation}.TScrollbar",
            gripcount=0,
            background=COLORS["surface_metal"],
            darkcolor=COLORS["surface"],
            lightcolor=COLORS["surface_hover"],
            troughcolor=COLORS["input"],
            bordercolor=COLORS["border"],
            arrowcolor=COLORS["primary"],
            relief="flat",
            width=13,
        )
        style.map(
            f"Cyber.{orientation}.TScrollbar",
            background=[("active", COLORS["surface_hover"]), ("pressed", COLORS["primary_pressed"])],
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


def make_panel(parent: tk.Misc, *, bg: str | None = None, border: str | None = None) -> tuple[tk.Frame, tk.Frame]:
    """Create a crisp one-pixel bordered panel and return (outer, inner)."""
    outer = tk.Frame(parent, bg=border or COLORS["border"], bd=0, highlightthickness=0)
    inner = tk.Frame(outer, bg=bg or COLORS["surface"], bd=0, highlightthickness=0)
    inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    return outer, inner


def metric_label(
    parent: tk.Misc, label: str, value: str, *, accent: str | None = None, bg: str | None = None
) -> tk.Frame:
    """Small terminal-style metric block."""
    fill = bg or COLORS["surface"]
    frame = tk.Frame(
        parent,
        bg=fill,
        highlightthickness=1,
        highlightbackground=COLORS["border_dim"],
        highlightcolor=COLORS["border_hot"],
        padx=12,
        pady=9,
    )
    tk.Label(frame, text=label.upper(), font=(FONT_MONO, 9), bg=fill, fg=COLORS["muted"]).pack(anchor="w")
    tk.Label(
        frame,
        text=value,
        font=(FONT_MONO, 13, "bold"),
        bg=fill,
        fg=accent or COLORS["text"],
    ).pack(anchor="w", pady=(3, 0))
    return frame


def section_title(
    parent: tk.Misc, kicker: str, title: str, subtitle: str, *, accent: str | None = None, bg: str | None = None
) -> tk.Frame:
    """Large cyber title stack used by command-deck screens."""
    fill = bg or COLORS["surface"]
    glow = accent or COLORS["primary"]
    frame = tk.Frame(parent, bg=fill)
    tk.Label(frame, text=kicker, font=(FONT_MONO, 10, "bold"), bg=fill, fg=glow).pack(anchor="w")
    tk.Label(frame, text=title, font=(FONT, 30, "bold"), bg=fill, fg=COLORS["text"]).pack(anchor="w", pady=(3, 0))
    tk.Frame(frame, bg=glow, height=2).pack(fill=tk.X, pady=(10, 8))
    tk.Label(frame, text=subtitle, font=(FONT, 11), bg=fill, fg=COLORS["muted"]).pack(anchor="w")
    return frame


def draw_grid_background(canvas: tk.Canvas, width: int, height: int, *, step: int = 48) -> None:
    """Draw a restrained cyber grid on a Tk canvas."""
    for x in range(0, width + 1, step):
        canvas.create_line(x, 0, x, height, fill=COLORS["bg_grid"], width=1, tags="grid")
    for y in range(0, height + 1, step):
        canvas.create_line(0, y, width, y, fill=COLORS["bg_grid"], width=1, tags="grid")
    canvas.create_line(0, 0, width, 0, fill=COLORS["border"], width=1, tags="grid")


def install_backdrop(parent: tk.Misc) -> tk.Canvas:
    """Install a static cyber grid behind a frame."""
    canvas = tk.Canvas(parent, bg=COLORS["bg"], highlightthickness=0, bd=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)
    canvas.tk.call("lower", canvas._w)
    def redraw(width: int, height: int) -> None:
        canvas.delete("grid")
        width, height = max(1, width), max(1, height)
        draw_grid_background(canvas, width, height, step=48)
        for y in range(0, height + 1, 192):
            canvas.create_line(0, y, width, y, fill=COLORS["border_dim"], tags="grid")

    def on_configure(event) -> None:
        redraw(event.width, event.height)

    canvas.bind("<Configure>", on_configure)
    return canvas


def load_window_geometry() -> str | None:
    """Return the persisted window geometry, or None if unavailable."""
    try:
        with open(_GEOM_FILE, "r", encoding="utf-8") as geom_file:
            geometry = geom_file.read().strip()
        return geometry or None
    except OSError:
        return None


def save_window_geometry(geometry: str) -> None:
    """Persist the window geometry across sessions."""
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(_GEOM_FILE, "w", encoding="utf-8") as geom_file:
            geom_file.write(geometry)
    except OSError:
        pass


def fit_window(root: tk.Misc, width: int, height: int, min_width: int, min_height: int) -> None:
    """Clamp the requested size to the screen, then center or restore position."""
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    avail_h = max(480, screen_h - 60)
    width = max(320, min(int(width), screen_w - 40))
    height = max(240, min(int(height), avail_h))
    min_width = min(int(min_width), width)
    min_height = min(int(min_height), height)

    # Restore the last position when it still fits on screen; otherwise center.
    x = y = None
    saved = load_window_geometry()
    if saved:
        parts = saved.split("+")
        if len(parts) >= 3:
            try:
                x, y = int(parts[1]), int(parts[2])
            except ValueError:
                x = y = None
    if x is None or y is None or x < 0 or y < 0 or x + width > screen_w or y + height > screen_h:
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2 - 20)

    root.geometry(f"{width}x{height}+{x}+{y}")
    root.minsize(min_width, min_height)
    root.configure(bg=COLORS["bg"])


def set_window_geometry(root: tk.Misc, width: int, height: int, min_width: int, min_height: int) -> None:
    fit_window(root, width, height, min_width, min_height)


_THEME_FILE = os.path.join(_DATA_DIR, "theme_pref.txt")
_current_theme = "dark"


def apply_theme(theme: str) -> None:
    global _current_theme
    _current_theme = "light" if theme == "light" else "dark"
    COLORS.clear()
    COLORS.update(LIGHT_COLORS if _current_theme == "light" else DARK_COLORS)


def get_theme() -> str:
    return _current_theme


def set_theme(theme: str) -> None:
    apply_theme(theme)
    try:
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(_THEME_FILE, "w", encoding="utf-8") as theme_file:
            theme_file.write(_current_theme)
    except OSError:
        pass


def load_theme() -> None:
    try:
        with open(_THEME_FILE, "r", encoding="utf-8") as theme_file:
            theme = theme_file.read().strip()
    except OSError:
        theme = "dark"
    apply_theme(theme)
