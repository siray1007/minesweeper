"""Application shell and top-level navigation."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox, ttk

from auth import AuthFrame
from database import init_db
from game import DIFFICULTY_CONFIG, GameFrame
from lang import t
from ranking import RankingFrame
from ui_theme import COLORS, FONT, configure_ttk, load_photo, set_window_geometry


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_ICON_PATH = os.path.join(_BASE_DIR, "扫雷图标.png")
_BOMB_ICON = os.path.join(_BASE_DIR, "bomb32.png")


class MainApp:
    def __init__(self, *, start_loop: bool = True):
        self.root = tk.Tk()
        configure_ttk(self.root)
        self.current_user: dict | None = None
        self.current_frame: tk.Widget | None = None
        self._icon = load_photo(_ICON_PATH, master=self.root)
        if self._icon is not None:
            self.root.iconphoto(True, self._icon)

        self.root.title(t("title"))
        set_window_geometry(self.root, 620, 720, 520, 600)
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.bind("<Escape>", lambda _event: self._handle_escape())
        init_db()
        self._show_auth()
        if start_loop:
            self.root.mainloop()

    def _swap(self, frame_class, *args) -> None:
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.root, *args)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def _show_auth(self) -> None:
        self.root.title(t("title"))
        set_window_geometry(self.root, 620, 720, 520, 600)
        self._swap(AuthFrame, self._on_login)

    def _on_login(self, user: dict) -> None:
        self.current_user = user
        self._show_menu()

    def _show_menu(self) -> None:
        self.root.title(t("menu_title"))
        set_window_geometry(self.root, 1080, 720, 920, 620)
        if self.current_frame is not None:
            self.current_frame.destroy()

        frame = tk.Frame(self.root, bg=COLORS["bg"])
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = frame

        header = tk.Frame(frame, bg=COLORS["bg"])
        header.pack(fill=tk.X, padx=32, pady=(24, 12))
        image = load_photo(_BOMB_ICON, master=self.root)
        if image is not None:
            self._menu_icon = image
            tk.Label(header, image=image, bg=COLORS["bg"]).pack(side=tk.LEFT, padx=(0, 14))
        title_block = tk.Frame(header, bg=COLORS["bg"])
        title_block.pack(side=tk.LEFT, anchor="w")
        tk.Label(
            title_block,
            text=t("menu_title"),
            font=(FONT, 24, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor="w")
        tk.Label(
            title_block,
            text=t("welcome", self.current_user["username"]),
            font=(FONT, 10),
            bg=COLORS["bg"],
            fg=COLORS["muted"],
        ).pack(anchor="w", pady=(4, 0))
        ttk.Button(header, text=t("btn_logout"), style="Ghost.TButton", command=self._logout).pack(
            side=tk.RIGHT, anchor="n"
        )

        body = tk.Frame(frame, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=32, pady=(18, 24))
        body.grid_columnconfigure((0, 1, 2), weight=1, uniform="difficulty")
        body.grid_rowconfigure(0, weight=1)

        difficulties = [
            ("9x9", t("diff_easy"), t("desc_easy"), COLORS["success"]),
            ("27x27", t("diff_medium"), t("desc_medium"), COLORS["warning"]),
            ("81x81", t("diff_hard"), t("desc_hard"), COLORS["danger"]),
        ]
        for column, (key, label, description, accent) in enumerate(difficulties):
            self._difficulty_card(body, column, key, label, description, accent)

        footer = tk.Frame(frame, bg=COLORS["bg"])
        footer.pack(fill=tk.X, padx=32, pady=(0, 24))
        ttk.Button(footer, text=t("btn_ranking"), style="Secondary.TButton", command=self._show_ranking).pack(
            side=tk.LEFT
        )
        tk.Label(
            footer,
            text=t("mode_hint"),
            font=(FONT, 9),
            bg=COLORS["bg"],
            fg=COLORS["subtle"],
        ).pack(side=tk.RIGHT)

    def _difficulty_card(self, parent, column: int, key: str, label: str, description: str, accent: str) -> None:
        card = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 8 if column < 2 else 0))
        tk.Frame(card, bg=accent, height=4).pack(fill=tk.X)
        content = tk.Frame(card, bg=COLORS["surface"])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=22)
        tk.Label(content, text=label, font=(FONT, 16, "bold"), bg=COLORS["surface"], fg=accent).pack(anchor="w")
        cfg = DIFFICULTY_CONFIG[key]
        tk.Label(
            content,
            text=f"{cfg['rows']} x {cfg['cols']}   |   {cfg['mines']} mines",
            font=(FONT, 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(anchor="w", pady=(10, 4))
        tk.Label(
            content,
            text=description,
            wraplength=210,
            justify="left",
            font=(FONT, 9),
            bg=COLORS["surface"],
            fg=COLORS["muted"],
        ).pack(anchor="w")
        ttk.Button(
            content,
            text=t("btn_start"),
            style="Primary.TButton",
            command=lambda selected=key: self._start_game(selected),
        ).pack(fill=tk.X, pady=(24, 0))

    def _start_game(self, difficulty: str) -> None:
        self._swap(GameFrame, self.current_user, difficulty, self._show_menu)

    def _show_ranking(self) -> None:
        self._swap(RankingFrame, self.current_user, self._show_menu)

    def _logout(self) -> None:
        if messagebox.askyesno(t("btn_logout"), t("logout_confirm"), parent=self.root):
            self.current_user = None
            self._show_auth()

    def _handle_escape(self) -> None:
        if self.current_user and isinstance(self.current_frame, (GameFrame, RankingFrame)):
            self._show_menu()

    def _quit(self) -> None:
        if self.current_user and not messagebox.askyesno(t("title"), t("quit_confirm"), parent=self.root):
            return
        self.root.destroy()


if __name__ == "__main__":
    MainApp()
