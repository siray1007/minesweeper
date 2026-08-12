"""Shared visual tokens and Tk helpers for the cyber Minesweeper UI."""
from __future__ import annotations

import base64
import tkinter as tk
from tkinter import ttk


COLORS = {
    "bg": "#070b14",
    "bg_grid": "#0b1728",
    "surface": "#0d1320",
    "surface_alt": "#111a2c",
    "surface_metal": "#172033",
    "surface_hover": "#162238",
    "border": "#22314a",
    "border_hot": "#2ce6ff",
    "border_dim": "#263c5c",
    "tile_border": "#304a70",
    "tile_open_border": "#476487",
    "text": "#edf3ff",
    "muted": "#8a97b2",
    "subtle": "#5d687f",
    "disabled": "#3f4b61",
    "primary": "#34d6ff",
    "primary_hover": "#67e3ff",
    "primary_pressed": "#179cc2",
    "success": "#35e0a1",
    "warning": "#ffd166",
    "danger": "#ff5c7a",
    "danger_dim": "#391320",
    "accent": "#9b6dff",
    "input": "#050812",
    "tile_even": "#1d3150",
    "tile_odd": "#172842",
    "tile_open": "#0b1424",
    "tile_flag": "#401d35",
}

FONT = "Microsoft YaHei UI"
FONT_MONO = "Consolas"

LAYOUT = {
    "auth": (720, 820, 560, 680),
    "lobby": (1360, 860, 1120, 720),
    "game_easy": (980, 840, 760, 700),
    "game_medium": (1180, 880, 920, 740),
    "game_hard": (1440, 920, 1040, 760),
    "ranking": (1280, 820, 1040, 700),
    "profile": (1160, 860, 1020, 760),
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
            bg, fg, active_bg = COLORS["primary"], "#08101b", COLORS["primary_hover"]
            border = COLORS["primary"]
        elif variant == "danger":
            bg, fg, active_bg = COLORS["danger_dim"], COLORS["text"], COLORS["danger"]
            border = COLORS["danger"]
        else:
            bg, fg, active_bg = COLORS["surface_metal"], COLORS["text"], COLORS["surface_hover"]
            border = COLORS["border_hot"]
        font_size, padx, pady = (11, 24, 14) if size == "large" else (10, 16, 9)
        super().__init__(
            parent,
            text=text,
            command=command,
            font=(FONT, font_size, "bold"),
            bg=bg,
            fg=fg,
            activebackground=active_bg,
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
        self._hover_bg = active_bg
        self.bind("<Enter>", lambda _event: self.configure(bg=self._hover_bg))
        self.bind("<Leave>", lambda _event: self.configure(bg=self._normal_bg))


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
            width=14,
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
    frame = tk.Frame(parent, bg=fill)
    tk.Label(frame, text=label.upper(), font=(FONT_MONO, 8), bg=fill, fg=COLORS["subtle"]).pack(
        anchor="w"
    )
    tk.Label(
        frame,
        text=value,
        font=(FONT_MONO, 13, "bold"),
        bg=fill,
        fg=accent or COLORS["text"],
    ).pack(anchor="w", pady=(2, 0))
    return frame


def section_title(
    parent: tk.Misc, kicker: str, title: str, subtitle: str, *, accent: str | None = None, bg: str | None = None
) -> tk.Frame:
    """Large cyber title stack used by command-deck screens."""
    fill = bg or COLORS["surface"]
    glow = accent or COLORS["primary"]
    frame = tk.Frame(parent, bg=fill)
    tk.Label(frame, text=kicker, font=(FONT_MONO, 10, "bold"), bg=fill, fg=glow).pack(anchor="w")
    tk.Label(frame, text=title, font=(FONT, 30, "bold"), bg=fill, fg=COLORS["text"]).pack(anchor="w", pady=(4, 0))
    tk.Frame(frame, bg=glow, height=2).pack(fill=tk.X, pady=(10, 9))
    tk.Label(frame, text=subtitle, font=(FONT, 11), bg=fill, fg=COLORS["muted"]).pack(anchor="w")
    return frame


def draw_grid_background(canvas: tk.Canvas, width: int, height: int, *, step: int = 32) -> None:
    """Draw a restrained cyber grid on a Tk canvas."""
    for x in range(0, width + 1, step):
        canvas.create_line(x, 0, x, height, fill=COLORS["bg_grid"], width=1, tags="grid")
    for y in range(0, height + 1, step):
        canvas.create_line(0, y, width, y, fill=COLORS["bg_grid"], width=1, tags="grid")
    canvas.create_line(0, 0, width, 0, fill=COLORS["border_hot"], width=1, tags="grid")


def install_backdrop(parent: tk.Misc) -> tk.Canvas:
    """Install a lightweight animated cyber grid behind a frame."""
    canvas = tk.Canvas(parent, bg=COLORS["bg"], highlightthickness=0, bd=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)
    canvas.tk.call("lower", canvas._w)
    state = {"scan": 0, "width": 1, "height": 1, "after_id": None}

    def redraw(width: int, height: int) -> None:
        state["width"], state["height"] = max(1, width), max(1, height)
        canvas.delete("grid")
        draw_grid_background(canvas, state["width"], state["height"], step=36)
        for y in range(0, state["height"] + 1, 144):
            canvas.create_line(0, y, state["width"], y, fill=COLORS["border_dim"], tags="grid")

    def on_configure(event) -> None:
        redraw(event.width, event.height)

    def animate() -> None:
        if not canvas.winfo_exists():
            return
        canvas.delete("scan")
        state["scan"] = (state["scan"] + 7) % max(1, state["height"] + 80)
        y = state["scan"] - 40
        canvas.create_rectangle(0, y, state["width"], y + 2, fill=COLORS["primary"], outline="", tags="scan")
        canvas.create_rectangle(
            0, y + 3, state["width"], y + 16, fill=COLORS["bg_grid"], outline="", stipple="gray25", tags="scan"
        )
        state["after_id"] = canvas.after(80, animate)

    def on_destroy(_event) -> None:
        after_id = state.get("after_id")
        if after_id:
            try:
                canvas.after_cancel(after_id)
            except tk.TclError:
                pass
            state["after_id"] = None

    canvas.bind("<Configure>", on_configure)
    canvas.bind("<Destroy>", on_destroy)
    state["after_id"] = canvas.after(120, animate)
    return canvas


def set_window_geometry(root: tk.Misc, width: int, height: int, min_width: int, min_height: int) -> None:
    root.geometry(f"{width}x{height}")
    root.minsize(min_width, min_height)
    root.configure(bg=COLORS["bg"])
