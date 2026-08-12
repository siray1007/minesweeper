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
from ui_theme import COLORS, FONT, LAYOUT, configure_ttk, load_photo, metric_label, section_title, set_window_geometry


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_ICON_PATH = os.path.join(_BASE_DIR, '扫雷图标.png')
_BOMB_ICON = os.path.join(_BASE_DIR, 'bomb32.png')


class MainApp:
    def __init__(self, *, start_loop: bool = True):
        self.root = tk.Tk()
        configure_ttk(self.root)
        self.current_user: dict | None = None
        self.current_frame: tk.Widget | None = None
        self._menu_icon = None
        self._icon = load_photo(_ICON_PATH, master=self.root)
        if self._icon is not None:
            self.root.iconphoto(True, self._icon)

        self.root.title(t('title'))
        auth_width, auth_height, auth_min_w, auth_min_h = LAYOUT['auth']['window']
        set_window_geometry(self.root, auth_width, auth_height, auth_min_w, auth_min_h)
        self.root.resizable(True, True)
        self.root.protocol('WM_DELETE_WINDOW', self._quit)
        self.root.bind('<Escape>', lambda _event: self._handle_escape())
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
        self.root.title(t('title'))
        auth_width, auth_height, auth_min_w, auth_min_h = LAYOUT['auth']['window']
        set_window_geometry(self.root, auth_width, auth_height, auth_min_w, auth_min_h)
        self._swap(AuthFrame, self._on_login)

    def _on_login(self, user: dict) -> None:
        self.current_user = user
        self._show_menu()

    def _panel(self, parent: tk.Misc, title: str, subtitle: str = '') -> tk.Frame:
        panel = tk.Frame(
            parent,
            bg=COLORS['surface'],
            highlightthickness=1,
            highlightbackground=COLORS['border'],
        )
        panel.grid_columnconfigure(0, weight=1)
        header = section_title(panel, title, subtitle)
        header.pack(fill=tk.X, padx=22, pady=(20, 14))
        return panel

    def _show_menu(self) -> None:
        self.root.title(t('menu_title'))
        width, height, min_width, min_height = LAYOUT['lobby']['window']
        set_window_geometry(self.root, width, height, min_width, min_height)
        if self.current_frame is not None:
            self.current_frame.destroy()

        frame = tk.Frame(self.root, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = frame

        header = tk.Frame(frame, bg=COLORS['bg'])
        header.pack(fill=tk.X, padx=40, pady=(28, 14))
        image = load_photo(_BOMB_ICON, master=self.root)
        if image is not None:
            self._menu_icon = image
            tk.Label(header, image=image, bg=COLORS['bg']).pack(side=tk.LEFT, padx=(0, 16))
        title_block = tk.Frame(header, bg=COLORS['bg'])
        title_block.pack(side=tk.LEFT, fill=tk.X, expand=True)
        section_title(title_block, t('menu_title'), t('welcome', self.current_user['username'])).pack(fill=tk.X)
        ttk.Button(
            header, text=t('btn_logout'), style='Ghost.TButton',
            command=self._logout,
        ).pack(side=tk.RIGHT, anchor='n')

        body = tk.Frame(frame, bg=COLORS['bg'])
        body.pack(fill=tk.BOTH, expand=True, padx=40, pady=(10, 24))
        body.grid_columnconfigure(0, weight=1, uniform='lobby')
        body.grid_columnconfigure(1, weight=2, uniform='lobby')
        body.grid_columnconfigure(2, weight=1, uniform='lobby')
        body.grid_rowconfigure(0, weight=1)

        self._lobby_identity_panel(body).grid(row=0, column=0, sticky='nsew', padx=(0, LAYOUT['lobby']['gap']))
        self._lobby_modes_panel(body).grid(row=0, column=1, sticky='nsew', padx=(0, LAYOUT['lobby']['gap']))
        self._lobby_status_panel(body).grid(row=0, column=2, sticky='nsew')

        footer = tk.Frame(frame, bg=COLORS['bg'])
        footer.pack(fill=tk.X, padx=40, pady=(0, 24))
        ttk.Button(
            footer, text=t('btn_ranking'), style='Secondary.TButton',
            command=self._show_ranking,
        ).pack(side=tk.LEFT)
        tk.Label(
            footer,
            text=t('esc_hint'),
            font=(FONT, 9),
            bg=COLORS['bg'],
            fg=COLORS['subtle'],
        ).pack(side=tk.RIGHT)

    def _lobby_identity_panel(self, parent: tk.Misc) -> tk.Frame:
        panel = self._panel(parent, t('lobby_profile_title'), t('lobby_profile_subtitle'))
        panel.grid_propagate(False)
        panel.configure(width=300)

        content = tk.Frame(panel, bg=COLORS['surface'])
        content.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 22))
        tk.Label(
            content,
            text=self.current_user['username'],
            font=(FONT, 22, 'bold'),
            bg=COLORS['surface'],
            fg=COLORS['text'],
            anchor='w',
        ).pack(fill=tk.X)
        tk.Label(
            content,
            text=t('current_user', self.current_user['username']),
            font=(FONT, 10),
            bg=COLORS['surface'],
            fg=COLORS['muted'],
            anchor='w',
        ).pack(fill=tk.X, pady=(4, 0))

        stat_row = tk.Frame(content, bg=COLORS['surface'])
        stat_row.pack(fill=tk.X, pady=(22, 18))
        metric_label(stat_row, 'MODE', t('menu_title'), bg=COLORS['surface'], accent=COLORS['primary']).pack(side=tk.LEFT, expand=True, fill=tk.X)
        metric_label(stat_row, 'STATUS', 'READY', bg=COLORS['surface'], accent=COLORS['success']).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(12, 0))

        tk.Frame(content, bg=COLORS['border'], height=1).pack(fill=tk.X, pady=(2, 14))
        tk.Label(
            content,
            text=t('lobby_status_scan'),
            font=(FONT, 10),
            bg=COLORS['surface'],
            fg=COLORS['text'],
            anchor='w',
            wraplength=250,
            justify='left',
        ).pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            content,
            text=t('lobby_status_record'),
            font=(FONT, 10),
            bg=COLORS['surface'],
            fg=COLORS['muted'],
            anchor='w',
            wraplength=250,
            justify='left',
        ).pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            content,
            text=t('lobby_status_control'),
            font=(FONT, 10),
            bg=COLORS['surface'],
            fg=COLORS['muted'],
            anchor='w',
            wraplength=250,
            justify='left',
        ).pack(fill=tk.X)
        return panel

    def _difficulty_card(self, parent, column: int, key: str, label: str,
                         description: str, accent: str) -> None:
        card = tk.Frame(
            parent,
            bg=COLORS['surface'],
            highlightbackground=COLORS['border'],
            highlightthickness=1,
        )
        card.grid(row=0, column=column, sticky='nsew', padx=(0 if column == 0 else 10, 0 if column == 2 else 10))
        card.grid_rowconfigure(1, weight=1)
        tk.Frame(card, bg=accent, height=6).pack(fill=tk.X)
        content = tk.Frame(card, bg=COLORS['surface'])
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        tk.Label(
            content, text=label, font=(FONT, 18, 'bold'),
            bg=COLORS['surface'], fg=accent, anchor='w',
        ).pack(fill=tk.X)
        cfg = DIFFICULTY_CONFIG[key]
        tk.Label(
            content,
            text=f"{cfg['rows']} x {cfg['cols']}   ·   {cfg['mines']} mines",
            font=(FONT, 10, 'bold'),
            bg=COLORS['surface'],
            fg=COLORS['text'],
            anchor='w',
        ).pack(fill=tk.X, pady=(14, 6))
        tk.Label(
            content,
            text=description,
            wraplength=230,
            justify='left',
            font=(FONT, 10),
            bg=COLORS['surface'],
            fg=COLORS['muted'],
            anchor='w',
        ).pack(fill=tk.X)

        ttk.Button(
            content, text=t('btn_start'), style='Primary.TButton',
            command=lambda selected=key: self._start_game(selected),
        ).pack(fill=tk.X, pady=(24, 0))

    def _lobby_modes_panel(self, parent: tk.Misc) -> tk.Frame:
        panel = self._panel(parent, t('lobby_launch_title'), t('lobby_launch_subtitle'))
        content = tk.Frame(panel, bg=COLORS['surface'])
        content.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 22))
        content.grid_columnconfigure((0, 1, 2), weight=1, uniform='modes')
        content.grid_rowconfigure(0, weight=1)

        difficulties = [
            ('9x9', t('diff_easy'), t('desc_easy'), COLORS['success']),
            ('27x27', t('diff_medium'), t('desc_medium'), COLORS['warning']),
            ('81x81', t('diff_hard'), t('desc_hard'), COLORS['danger']),
        ]
        for column, (key, label, description, accent) in enumerate(difficulties):
            self._difficulty_card(content, column, key, label, description, accent)
        return panel

    def _lobby_status_panel(self, parent: tk.Misc) -> tk.Frame:
        panel = self._panel(parent, t('lobby_status_title'), t('lobby_threat_matrix'))
        content = tk.Frame(panel, bg=COLORS['surface'])
        content.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 22))

        blocks = [
            ('1', t('status_scan_heading'), t('status_scan_desc'), COLORS['primary']),
            ('2', t('status_sync_heading'), t('status_sync_desc'), COLORS['success']),
            ('3', t('status_control_heading'), t('status_control_desc'), COLORS['warning']),
        ]
        for idx, (num, heading, desc, accent) in enumerate(blocks):
            row = tk.Frame(content, bg=COLORS['surface_alt'])
            row.pack(fill=tk.X, pady=(0 if idx == 0 else 12, 0))
            tk.Label(
                row, text=num, font=(FONT, 18, 'bold'),
                bg=COLORS['surface_alt'], fg=accent, width=3,
            ).pack(side=tk.LEFT, padx=(14, 10), pady=16)
            text_block = tk.Frame(row, bg=COLORS['surface_alt'])
            text_block.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=14)
            tk.Label(
                text_block, text=heading, font=(FONT, 11, 'bold'),
                bg=COLORS['surface_alt'], fg=COLORS['text'],
                anchor='w',
            ).pack(fill=tk.X)
            tk.Label(
                text_block, text=desc, font=(FONT, 9),
                bg=COLORS['surface_alt'], fg=COLORS['muted'],
                anchor='w', wraplength=220, justify='left',
            ).pack(fill=tk.X, pady=(4, 0))
        return panel

    def _start_game(self, difficulty: str) -> None:
        self._swap(GameFrame, self.current_user, difficulty, self._show_menu)

    def _show_ranking(self) -> None:
        self._swap(RankingFrame, self.current_user, self._show_menu)

    def _logout(self) -> None:
        if messagebox.askyesno(t('btn_logout'), t('logout_confirm'), parent=self.root):
            self.current_user = None
            self._show_auth()

    def _handle_escape(self) -> None:
        if self.current_user and isinstance(self.current_frame, (GameFrame, RankingFrame)):
            self._show_menu()

    def _quit(self) -> None:
        if self.current_user and not messagebox.askyesno(
            t('title'), t('quit_confirm'), parent=self.root,
        ):
            return
        self.root.destroy()


if __name__ == '__main__':
    MainApp()
