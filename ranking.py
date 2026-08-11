"""Local and cloud leaderboard screen."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from database import _gitee_fetch_rankings, get_rankings_local
from lang import t
from ui_theme import COLORS, FONT, FONT_MONO, CyberButton, configure_ttk, install_backdrop, make_panel


def format_duration(seconds: int | None) -> str:
    if seconds is None:
        return t("no_record_short")
    minutes, remain = divmod(int(seconds), 60)
    return f"{minutes:02d}:{remain:02d}"


class RankingFrame(tk.Frame):
    def __init__(self, parent, current_user: dict, on_back):
        super().__init__(parent, bg=COLORS["bg"])
        configure_ttk(parent)
        install_backdrop(self)
        self.current_user = current_user
        self.on_back = on_back
        self._trees: dict[str, ttk.Treeview] = {}
        self._cloud_idx = 0
        self._build_ui()
        self._cloud_job = self.after(250, self._fetch_cloud_step)

    def _build_ui(self) -> None:
        bar_outer, bar = make_panel(self, bg=COLORS["surface"], border=COLORS["border_hot"])
        bar_outer.pack(fill=tk.X, padx=16, pady=(16, 0))
        bar.configure(height=74)
        bar.pack_propagate(False)
        CyberButton(bar, text=t("btn_back"), variant="secondary", command=self._back).pack(
            side=tk.LEFT, padx=18, pady=12
        )
        title_stack = tk.Frame(bar, bg=COLORS["surface"])
        title_stack.pack(side=tk.LEFT, padx=10, pady=12)
        tk.Label(
            title_stack, text=t("rank_title"), font=(FONT, 20, "bold"), bg=COLORS["surface"], fg=COLORS["text"]
        ).pack(anchor="w")
        tk.Label(
            title_stack,
            text=t("rank_subtitle"),
            font=(FONT_MONO, 8),
            bg=COLORS["surface"],
            fg=COLORS["muted"],
        ).pack(anchor="w", pady=(4, 0))
        tk.Label(
            bar,
            text=t("current_user", self.current_user["username"]),
            font=(FONT_MONO, 9, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(side=tk.RIGHT, padx=22)

        self.status_label = tk.Label(
            self,
            text=t("status_local_loaded"),
            font=(FONT, 9),
            bg=COLORS["bg"],
            fg=COLORS["subtle"],
            anchor="w",
        )
        self.status_label.pack(fill=tk.X, padx=24, pady=(14, 0))

        self._build_personal_summary()

        notebook = ttk.Notebook(self, style="App.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=14)
        for difficulty, label in self._difficulty_labels():
            frame = tk.Frame(notebook, bg=COLORS["surface"])
            notebook.add(frame, text=label)
            self._build_table(frame, difficulty)

        mine_frame = tk.Frame(notebook, bg=COLORS["surface"])
        notebook.add(mine_frame, text=t("my_records"))
        self._build_my_records(mine_frame)

    @staticmethod
    def _difficulty_labels():
        return [
            ("9x9", t("diff_easy")),
            ("27x27", t("diff_medium")),
            ("81x81", t("diff_hard")),
        ]

    def _build_personal_summary(self) -> None:
        outer, inner = make_panel(self, bg=COLORS["surface"], border=COLORS["border"])
        outer.pack(fill=tk.X, padx=20, pady=(12, 0))
        tk.Label(
            inner,
            text=t("personal_best_title"),
            font=(FONT_MONO, 9, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(side=tk.LEFT, padx=(16, 18), pady=12)
        for difficulty, label in self._difficulty_labels():
            best = self._best_for_user(difficulty)
            block = tk.Frame(inner, bg=COLORS["surface"])
            block.pack(side=tk.LEFT, expand=True, fill=tk.X, pady=10)
            tk.Label(block, text=label, font=(FONT, 8), bg=COLORS["surface"], fg=COLORS["subtle"]).pack(anchor="w")
            tk.Label(
                block,
                text=format_duration(best),
                font=(FONT_MONO, 12, "bold"),
                bg=COLORS["surface"],
                fg=COLORS["text"] if best is not None else COLORS["disabled"],
            ).pack(anchor="w")

    def _best_for_user(self, difficulty: str) -> int | None:
        records = [
            int(record.get("time_seconds", 0))
            for record in get_rankings_local(difficulty, 1000)
            if record.get("user_id") == self.current_user.get("id")
            or record.get("username") == self.current_user.get("username")
        ]
        return min(records) if records else None

    @staticmethod
    def _dedup_best(rankings: list[dict]) -> list[dict]:
        best = {}
        for record in rankings:
            username = record.get("username", "—")
            seconds = int(record.get("time_seconds", 99999))
            if username not in best or seconds < best[username].get("time_seconds", 99999):
                best[username] = record
        return sorted(best.values(), key=lambda item: item.get("time_seconds", 99999))

    def _build_table(self, parent, difficulty: str) -> None:
        table = ttk.Treeview(
            parent,
            columns=("rank", "username", "time", "date"),
            show="headings",
            style="App.Treeview",
            selectmode="browse",
        )
        for column, title, width in (
            ("rank", t("rank_col"), 72),
            ("username", t("user_col"), 180),
            ("time", t("time_col"), 140),
            ("date", t("date_col"), 230),
        ):
            table.heading(column, text=title)
            table.column(column, width=width, anchor="center", stretch=True)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=table.yview, style="Cyber.Vertical.TScrollbar")
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0), pady=16)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 16), pady=16)
        table.tag_configure("me", foreground=COLORS["primary"])
        table.tag_configure("top", foreground=COLORS["warning"])
        table.tag_configure("empty", foreground=COLORS["disabled"])
        self._trees[difficulty] = table
        self._populate_tree(table, self._dedup_best(get_rankings_local(difficulty)))

    def _populate_tree(self, table: ttk.Treeview, rankings: list[dict]) -> None:
        for item in table.get_children():
            table.delete(item)
        if not rankings:
            table.insert("", tk.END, values=("--", t("rank_empty_marker"), t("no_data"), "--"), tags=("empty",))
            return
        for rank, record in enumerate(rankings, 1):
            minutes, seconds = divmod(int(record.get("time_seconds", 0)), 60)
            date = record.get("completed_at") or record.get("created_at", "—")
            tags = ("me",) if record.get("username") == self.current_user.get("username") else ()
            if rank <= 3 and not tags:
                tags = ("top",)
            table.insert(
                "",
                tk.END,
                values=(rank, record.get("username", "—"), f"{minutes:02d}:{seconds:02d}", date),
                tags=tags,
            )

    def _build_my_records(self, parent) -> None:
        table = ttk.Treeview(
            parent, columns=("difficulty", "time", "date"), show="headings", style="App.Treeview", selectmode="browse"
        )
        for column, title, width in (
            ("difficulty", t("difficulty_col"), 190),
            ("time", t("time_col"), 160),
            ("date", t("date_col"), 260),
        ):
            table.heading(column, text=title)
            table.column(column, width=width, anchor="center", stretch=True)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=table.yview, style="Cyber.Vertical.TScrollbar")
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0), pady=16)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 16), pady=16)

        labels = dict(self._difficulty_labels())
        records = []
        for difficulty in labels:
            for record in get_rankings_local(difficulty, 1000):
                if record.get("username") == self.current_user.get("username"):
                    records.append(
                        (
                            labels[difficulty],
                            int(record.get("time_seconds", 0)),
                            record.get("completed_at") or record.get("created_at", "—"),
                        )
                    )
        records.sort(key=lambda item: item[1])
        table.tag_configure("empty", foreground=COLORS["disabled"])
        if not records:
            table.insert("", tk.END, values=("--", t("no_records"), "--"), tags=("empty",))
            return
        for label, total_seconds, date in records:
            minutes, seconds = divmod(total_seconds, 60)
            table.insert("", tk.END, values=(label, f"{minutes:02d}:{seconds:02d}", date))

    def _fetch_cloud_step(self) -> None:
        labels = self._difficulty_labels()
        if self._cloud_idx >= len(labels):
            self.status_label.configure(text=t("status_cloud_done"))
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
        self._cancel_cloud_job()
        self.on_back()

    def _cancel_cloud_job(self) -> None:
        if getattr(self, "_cloud_job", None):
            try:
                self.after_cancel(self._cloud_job)
            except tk.TclError:
                pass
            self._cloud_job = None

    def destroy(self) -> None:
        self._cancel_cloud_job()
        super().destroy()
