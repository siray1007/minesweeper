"""Local and cloud leaderboard screen."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from database import get_rankings_local, _gitee_fetch_rankings
from lang import t
from ui_theme import COLORS, FONT, configure_ttk


class RankingFrame(tk.Frame):
    def __init__(self, parent, current_user: dict, on_back):
        super().__init__(parent, bg=COLORS['bg'])
        configure_ttk(parent)
        self.current_user = current_user
        self.on_back = on_back
        self._trees: dict[str, ttk.Treeview] = {}
        self._cloud_idx = 0
        self._build_ui()
        self._cloud_job = self.after(250, self._fetch_cloud_step)

    def _build_ui(self) -> None:
        bar = tk.Frame(self, bg=COLORS['surface'], height=64)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        ttk.Button(bar, text=t('btn_back'), style='Ghost.TButton', command=self._back).pack(
            side=tk.LEFT, padx=18, pady=12)
        tk.Label(
            bar, text=t('rank_title'), font=(FONT, 19, 'bold'),
            bg=COLORS['surface'], fg=COLORS['text'],
        ).pack(side=tk.LEFT, padx=10)
        tk.Label(
            bar, text=t('current_user', self.current_user['username']),
            font=(FONT, 9), bg=COLORS['surface'], fg=COLORS['muted'],
        ).pack(side=tk.RIGHT, padx=22)

        self.status_label = tk.Label(
            self, text='本地记录已加载 · 云端同步中…', font=(FONT, 9),
            bg=COLORS['bg'], fg=COLORS['subtle'], anchor='w',
        )
        self.status_label.pack(fill=tk.X, padx=24, pady=(14, 0))

        notebook = ttk.Notebook(self, style='App.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=14)
        for difficulty, label in self._difficulty_labels():
            frame = tk.Frame(notebook, bg=COLORS['surface'])
            notebook.add(frame, text=label)
            self._build_table(frame, difficulty)

        mine_frame = tk.Frame(notebook, bg=COLORS['surface'])
        notebook.add(mine_frame, text=t('my_records'))
        self._build_my_records(mine_frame)

    @staticmethod
    def _difficulty_labels():
        return [
            ('9x9', t('diff_easy')),
            ('27x27', t('diff_medium')),
            ('81x81', t('diff_hard')),
        ]

    @staticmethod
    def _dedup_best(rankings: list[dict]) -> list[dict]:
        best = {}
        for record in rankings:
            username = record.get('username', '—')
            seconds = int(record.get('time_seconds', 99999))
            if username not in best or seconds < best[username].get('time_seconds', 99999):
                best[username] = record
        return sorted(best.values(), key=lambda item: item.get('time_seconds', 99999))

    def _build_table(self, parent, difficulty: str) -> None:
        table = ttk.Treeview(
            parent, columns=('rank', 'username', 'time', 'date'),
            show='headings', style='App.Treeview', selectmode='browse',
        )
        for column, title, width in (
            ('rank', t('rank_col'), 72),
            ('username', t('user_col'), 180),
            ('time', t('time_col'), 140),
            ('date', t('date_col'), 230),
        ):
            table.heading(column, text=title)
            table.column(column, width=width, anchor='center', stretch=True)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0), pady=16)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 16), pady=16)
        table.tag_configure('me', foreground=COLORS['primary'])
        self._trees[difficulty] = table
        self._populate_tree(table, self._dedup_best(get_rankings_local(difficulty)))

    def _populate_tree(self, table: ttk.Treeview, rankings: list[dict]) -> None:
        for item in table.get_children():
            table.delete(item)
        if not rankings:
            table.insert('', tk.END, values=('—', t('no_data'), '—', '—'))
            return
        for rank, record in enumerate(rankings, 1):
            minutes, seconds = divmod(int(record.get('time_seconds', 0)), 60)
            date = record.get('completed_at') or record.get('created_at', '—')
            tags = ('me',) if record.get('username') == self.current_user.get('username') else ()
            table.insert(
                '', tk.END,
                values=(rank, record.get('username', '—'), f'{minutes:02d}:{seconds:02d}', date),
                tags=tags,
            )

    def _build_my_records(self, parent) -> None:
        table = ttk.Treeview(
            parent, columns=('difficulty', 'time', 'date'),
            show='headings', style='App.Treeview', selectmode='browse',
        )
        for column, title, width in (
            ('difficulty', t('difficulty_col'), 190),
            ('time', t('time_col'), 160),
            ('date', t('date_col'), 260),
        ):
            table.heading(column, text=title)
            table.column(column, width=width, anchor='center', stretch=True)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0), pady=16)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 16), pady=16)

        labels = dict(self._difficulty_labels())
        records = []
        for difficulty in labels:
            for record in get_rankings_local(difficulty):
                if record.get('username') == self.current_user.get('username'):
                    records.append((
                        labels[difficulty], int(record.get('time_seconds', 0)),
                        record.get('completed_at') or record.get('created_at', '—'),
                    ))
        records.sort(key=lambda item: item[1])
        if not records:
            table.insert('', tk.END, values=('—', t('no_records'), '—'))
            return
        for label, total_seconds, date in records:
            minutes, seconds = divmod(total_seconds, 60)
            table.insert('', tk.END, values=(label, f'{minutes:02d}:{seconds:02d}', date))

    def _fetch_cloud_step(self) -> None:
        labels = self._difficulty_labels()
        if self._cloud_idx >= len(labels):
            self.status_label.configure(text='本地记录已加载 · 云端同步完成')
            return
        difficulty = labels[self._cloud_idx][0]
        self._cloud_idx += 1

        def fetch() -> None:
            online = _gitee_fetch_rankings(difficulty, 50) or []
            local = get_rankings_local(difficulty)
            merged = self._dedup_best(online + local)
            table = self._trees.get(difficulty)
            if table is not None and table.winfo_exists():
                self._populate_tree(table, merged)

        self.after(50, fetch)
        self._cloud_job = self.after(350, self._fetch_cloud_step)

    def _back(self) -> None:
        if getattr(self, '_cloud_job', None):
            self.after_cancel(self._cloud_job)
        self.on_back()
