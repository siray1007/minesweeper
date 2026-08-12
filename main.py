"""Application shell and top-level navigation."""
from __future__ import annotations

import os
import queue
import threading
import tkinter as tk
from tkinter import messagebox

from auth import AuthFrame
from database import cloud_connection_status, get_rankings_local, get_user_profile_summary, init_db
from game import DIFFICULTY_CONFIG, GameFrame, board_density
from lang import t
from ranking import RankingFrame
from ui_theme import (
    COLORS,
    FONT,
    FONT_MONO,
    LAYOUT,
    CyberButton,
    configure_ttk,
    install_backdrop,
    load_photo,
    make_panel,
    metric_label,
    section_title,
    set_window_geometry,
)


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_ICON_PATH = os.path.join(_BASE_DIR, "扫雷图标.png")
_BOMB_ICON = os.path.join(_BASE_DIR, "bomb32.png")


def threat_key(difficulty: str) -> str:
    return {"9x9": "threat_low", "27x27": "threat_medium", "81x81": "threat_high"}[difficulty]


def format_duration(seconds: int | None) -> str:
    if seconds is None:
        return t("no_record_short")
    minutes, remain = divmod(int(seconds), 60)
    return f"{minutes:02d}:{remain:02d}"


class MainApp:
    def __init__(self, *, start_loop: bool = True):
        self.root = tk.Tk()
        configure_ttk(self.root)
        self.current_user: dict | None = None
        self.current_frame: tk.Widget | None = None
        self._profile_dialog: tk.Toplevel | None = None
        self._cloud_status_queue: queue.Queue[dict] = queue.Queue()
        self._cloud_probe_job: str | None = None
        self._icon = load_photo(_ICON_PATH, master=self.root)
        if self._icon is not None:
            self.root.iconphoto(True, self._icon)

        self.root.title(t("title"))
        set_window_geometry(self.root, 620, 720, 520, 600)
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.bind("<Escape>", lambda _event: self._handle_escape())
        self.root.bind("<Destroy>", self._on_root_destroy, add="+")
        init_db()
        self._show_auth()
        if start_loop:
            self.root.mainloop()

    def _swap(self, frame_class, *args) -> None:
        self._cancel_cloud_probe()
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.root, *args)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def _show_auth(self) -> None:
        self._close_profile_dialog()
        self.root.title(t("title"))
        set_window_geometry(self.root, *LAYOUT["auth"])
        self._swap(AuthFrame, self._on_login)

    def _on_login(self, user: dict) -> None:
        self.current_user = user
        self._show_menu()

    def _show_menu(self) -> None:
        self._close_profile_dialog()
        self._cancel_cloud_probe()
        self.root.title(t("menu_title"))
        set_window_geometry(self.root, *LAYOUT["lobby"])
        if self.current_frame is not None:
            self.current_frame.destroy()

        frame = tk.Frame(self.root, bg=COLORS["bg"])
        frame.pack(fill=tk.BOTH, expand=True)
        install_backdrop(frame)
        self.current_frame = frame

        header_outer, header = make_panel(frame, bg=COLORS["surface"], border=COLORS["border_hot"])
        header_outer.pack(fill=tk.X, padx=42, pady=(30, 16))
        header.configure(height=116)
        header.pack_propagate(False)
        image = load_photo(_BOMB_ICON, master=self.root)
        if image is not None:
            self._menu_icon = image
            tk.Label(header, image=image, bg=COLORS["surface"]).pack(side=tk.LEFT, padx=(22, 18), pady=24)
        title_block = tk.Frame(header, bg=COLORS["surface"])
        title_block.pack(side=tk.LEFT, anchor="w", fill=tk.X, expand=True, pady=18)
        section_title(title_block, "NEON_SWEEP // MINEFIELD OPS", t("menu_title"), t("menu_subtitle")).pack(
            anchor="w", fill=tk.X
        )
        CyberButton(header, text=t("profile_label"), variant="secondary", command=self._show_profile, size="large").pack(
            side=tk.RIGHT, anchor="n", padx=22, pady=24
        )

        body = tk.Frame(frame, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=42, pady=(18, 26))
        body.grid_columnconfigure(0, weight=0, minsize=248)
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=0, minsize=248)
        body.grid_rowconfigure(0, weight=1)

        self._lobby_identity_panel(body).grid(row=0, column=0, sticky="nsew", padx=(0, 18))

        modules = tk.Frame(body, bg=COLORS["bg"])
        modules.grid(row=0, column=1, sticky="nsew")
        modules.grid_columnconfigure((0, 1, 2), weight=1, uniform="difficulty")
        modules.grid_rowconfigure(0, weight=1)

        difficulties = [
            ("9x9", "TRAINING", t("diff_easy"), t("desc_easy"), COLORS["success"]),
            ("27x27", "ADVANCED", t("diff_medium"), t("desc_medium"), COLORS["warning"]),
            ("81x81", "EXTREME", t("diff_hard"), t("desc_hard"), COLORS["danger"]),
        ]
        for column, (key, code, label, description, accent) in enumerate(difficulties):
            self._difficulty_card(modules, column, key, code, label, description, accent)

        self._lobby_status_panel(body).grid(row=0, column=2, sticky="nsew", padx=(18, 0))

        footer_outer, footer = make_panel(frame, bg=COLORS["surface"], border=COLORS["border"])
        footer_outer.pack(fill=tk.X, padx=42, pady=(0, 30))
        CyberButton(footer, text=t("btn_ranking"), variant="secondary", command=self._show_ranking).pack(
            side=tk.LEFT, padx=16, pady=12, ipadx=12, ipady=4
        )
        tk.Label(
            footer,
            text="NEON_SWEEP // COMMAND DECK",
            font=(FONT_MONO, 9),
            bg=COLORS["surface"],
            fg=COLORS["subtle"],
        ).pack(side=tk.RIGHT, padx=16, pady=12)

    def _lobby_identity_panel(self, parent) -> tk.Frame:
        summary = get_user_profile_summary(self.current_user["id"])
        outer, inner = make_panel(parent, bg=COLORS["surface"], border=COLORS["border"])
        tk.Label(
            inner,
            text=t("lobby_profile_title"),
            font=(FONT_MONO, 9, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(anchor="w", padx=20, pady=(22, 6))
        tk.Label(
            inner,
            text=self.current_user["username"],
            font=(FONT, 21, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(anchor="w", padx=20)
        tk.Label(
            inner,
            text=t("lobby_profile_subtitle"),
            font=(FONT, 9),
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            wraplength=190,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(6, 18))

        for label, value, accent in (
            (t("profile_total_matches"), str(summary["total_matches"]).zfill(2), COLORS["primary"]),
            (t("profile_win_rate"), f"{summary['win_rate']:02d}%", COLORS["warning"]),
            (t("profile_wins"), str(summary["wins"]).zfill(2), COLORS["success"]),
        ):
            metric_label(inner, label, value, accent=accent).pack(fill=tk.X, padx=20, pady=(0, 14))

        return outer

    def _lobby_status_panel(self, parent) -> tk.Frame:
        outer, inner = make_panel(parent, bg=COLORS["surface"], border=COLORS["border"])
        tk.Label(
            inner,
            text=t("cloud_panel_title"),
            font=(FONT_MONO, 9, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(anchor="w", padx=20, pady=(22, 8))
        status_items = [
            (t("cloud_provider"), "GITHUB", COLORS["primary"]),
            (t("cloud_repository"), "siray1007/minesweeper", COLORS["text"]),
        ]
        for label, value, accent in status_items:
            metric_label(inner, label, value, accent=accent).pack(fill=tk.X, padx=20, pady=(0, 18))

        tk.Frame(inner, bg=COLORS["border"], height=1).pack(fill=tk.X, padx=20, pady=(8, 16))
        self._cloud_mode_metric = metric_label(
            inner, t("cloud_access"), t("cloud_checking"), accent=COLORS["warning"]
        )
        self._cloud_mode_metric.pack(fill=tk.X, padx=20, pady=(0, 18))
        self._cloud_mode_value = self._cloud_mode_metric.winfo_children()[-1]
        self._cloud_link_metric = metric_label(
            inner, t("cloud_link"), t("cloud_checking"), accent=COLORS["warning"]
        )
        self._cloud_link_metric.pack(fill=tk.X, padx=20, pady=(0, 18))
        self._cloud_link_value = self._cloud_link_metric.winfo_children()[-1]
        self._start_cloud_probe()
        return outer

    def _start_cloud_probe(self) -> None:
        def probe() -> None:
            self._cloud_status_queue.put(cloud_connection_status())

        threading.Thread(target=probe, daemon=True).start()
        self._cloud_probe_job = self.root.after(100, self._poll_cloud_probe)

    def _poll_cloud_probe(self) -> None:
        self._cloud_probe_job = None
        try:
            status = self._cloud_status_queue.get_nowait()
        except queue.Empty:
            if self.current_user is not None:
                self._cloud_probe_job = self.root.after(100, self._poll_cloud_probe)
            return
        if not hasattr(self, "_cloud_link_value") or not self._cloud_link_value.winfo_exists():
            return
        connected = status["connected"]
        writable = status["writable"]
        self._cloud_link_value.configure(
            text=t("cloud_connected") if connected else t("cloud_offline"),
            fg=COLORS["success"] if connected else COLORS["danger"],
        )
        self._cloud_mode_value.configure(
            text=t("cloud_read_write") if writable else t("cloud_read_only"),
            fg=COLORS["success"] if writable else COLORS["warning"],
        )

    def _cancel_cloud_probe(self) -> None:
        if self._cloud_probe_job is None:
            return
        try:
            self.root.after_cancel(self._cloud_probe_job)
        except tk.TclError:
            pass
        self._cloud_probe_job = None

    def _on_root_destroy(self, event) -> None:
        if event.widget is self.root:
            self._cancel_cloud_probe()

    def _difficulty_card(
        self, parent, column: int, key: str, code: str, label: str, description: str, accent: str
    ) -> None:
        card, content = make_panel(parent, bg=COLORS["surface"], border=accent)
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 8 if column < 2 else 0))
        tk.Frame(content, bg=accent, height=5).pack(fill=tk.X)
        content = tk.Frame(content, bg=COLORS["surface"])
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=28)
        tk.Label(content, text=f"MODE // {code}", font=(FONT_MONO, 10, "bold"), bg=COLORS["surface"], fg=accent).pack(
            anchor="w"
        )
        tk.Label(content, text=label, font=(FONT, 19, "bold"), bg=COLORS["surface"], fg=accent).pack(anchor="w", pady=(2, 0))
        cfg = DIFFICULTY_CONFIG[key]
        metrics = tk.Frame(content, bg=COLORS["surface"])
        metrics.pack(fill=tk.X, pady=(18, 14))
        metric_label(metrics, t("grid_label"), f"{cfg['rows']}x{cfg['cols']}", accent=COLORS["text"]).pack(
            side=tk.LEFT, expand=True, fill=tk.X
        )
        metric_label(metrics, t("mine_density"), board_density(cfg), accent=accent).pack(
            side=tk.LEFT, expand=True, fill=tk.X
        )
        tk.Label(
            content,
            text=f"{t('threat_label')}: {t(threat_key(key))}  /  {t('mine_count_label')}: {cfg['mines']}",
            font=(FONT_MONO, 11, "bold"),
            bg=COLORS["surface"],
            fg=accent,
        ).pack(anchor="w", pady=(2, 8))

        run_count, best_seconds = self._personal_stats(key)
        record_bar = tk.Frame(content, bg=COLORS["surface"])
        record_bar.pack(fill=tk.X, pady=(8, 10))
        metric_label(record_bar, t("best_label"), format_duration(best_seconds), accent=accent).pack(
            side=tk.LEFT, expand=True, fill=tk.X
        )
        metric_label(record_bar, t("ops_label"), str(run_count).zfill(2), accent=COLORS["text"]).pack(
            side=tk.LEFT, expand=True, fill=tk.X
        )

        tk.Label(
            content,
            text=description,
            wraplength=250,
            justify="left",
            font=(FONT, 10),
            bg=COLORS["surface"],
            fg=COLORS["muted"],
        ).pack(anchor="w", pady=(2, 0))
        CyberButton(
            content,
            text=t("btn_start"),
            command=lambda selected=key: self._start_game(selected),
        ).pack(fill=tk.X, pady=(26, 0))

    def _personal_stats(self, difficulty: str) -> tuple[int, int | None]:
        records = [
            record
            for record in get_rankings_local(difficulty, 1000)
            if record.get("user_id") == self.current_user.get("id")
            or record.get("username") == self.current_user.get("username")
        ]
        if not records:
            return 0, None
        best = min(int(record.get("time_seconds", 0)) for record in records)
        return len(records), best

    def _close_profile_dialog(self) -> None:
        dialog = self._profile_dialog
        if dialog is not None and dialog.winfo_exists():
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            dialog.destroy()
        self._profile_dialog = None

    def _show_profile(self) -> None:
        if self.current_user is None:
            self._show_auth()
            return
        self._cancel_cloud_probe()

        dialog = self._profile_dialog
        if dialog is not None and dialog.winfo_exists():
            dialog.deiconify()
            dialog.lift()
            dialog.focus_set()
            return

        summary = get_user_profile_summary(self.current_user["id"])
        self._profile_summary = summary

        dialog = tk.Toplevel(self.root)
        self._profile_dialog = dialog
        dialog.title(t("profile_label"))
        dialog.configure(bg=COLORS["bg"])
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.protocol("WM_DELETE_WINDOW", self._close_profile_dialog)
        dialog.bind("<Escape>", lambda _event: self._close_profile_dialog())
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)

        outer, inner = make_panel(dialog, bg=COLORS["surface"], border=COLORS["border_hot"])
        outer.grid(row=0, column=0, sticky="nsew", padx=14, pady=(14, 8))

        header = tk.Frame(inner, bg=COLORS["surface"])
        header.pack(fill=tk.X, padx=24, pady=(20, 8))
        header_left = tk.Frame(header, bg=COLORS["surface"])
        header_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            header_left,
            text=t("profile_label"),
            font=(FONT_MONO, 9, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(anchor="w")
        tk.Label(
            header_left,
            text=self.current_user["username"],
            font=(FONT, 22, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(anchor="w", pady=(4, 0))
        tk.Label(
            header_left,
            text=t("profile_subtitle"),
            font=(FONT, 10),
            bg=COLORS["surface"],
            fg=COLORS["muted"],
        ).pack(anchor="w", pady=(4, 0))
        CyberButton(header, text=t("btn_close"), variant="secondary", command=self._close_profile_dialog).pack(
            side=tk.RIGHT, padx=(12, 0), pady=2
        )

        stats = tk.Frame(inner, bg=COLORS["surface"])
        stats.pack(fill=tk.X, padx=24, pady=(8, 0))
        for index in range(4):
            stats.grid_columnconfigure(index, weight=1, uniform="profile_stats")
        metric_label(stats, t("profile_total_matches"), str(summary["total_matches"]).zfill(2), accent=COLORS["primary"]).grid(
            row=0, column=0, sticky="ew", padx=(0, 10)
        )
        metric_label(stats, t("profile_wins"), str(summary["wins"]).zfill(2), accent=COLORS["success"]).grid(
            row=0, column=1, sticky="ew", padx=(0, 10)
        )
        metric_label(stats, t("profile_losses"), str(summary["losses"]).zfill(2), accent=COLORS["danger"]).grid(
            row=0, column=2, sticky="ew", padx=(0, 10)
        )
        metric_label(stats, t("profile_win_rate"), f"{summary['win_rate']:02d}%", accent=COLORS["warning"]).grid(
            row=0, column=3, sticky="ew"
        )

        best_section = tk.Frame(inner, bg=COLORS["surface"])
        best_section.pack(fill=tk.X, padx=24, pady=(18, 0))
        tk.Label(
            best_section,
            text=t("personal_best_title"),
            font=(FONT_MONO, 9, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(anchor="w", pady=(0, 10))
        best_cards = tk.Frame(best_section, bg=COLORS["surface"])
        best_cards.pack(fill=tk.X)
        for index in range(3):
            best_cards.grid_columnconfigure(index, weight=1, uniform="profile_best")

        for column, (difficulty, label, accent) in enumerate(
            [
                ("9x9", t("diff_easy"), COLORS["success"]),
                ("27x27", t("diff_medium"), COLORS["warning"]),
                ("81x81", t("diff_hard"), COLORS["danger"]),
            ]
        ):
            outer_card, inner_card = make_panel(best_cards, bg=COLORS["surface_alt"], border=accent)
            outer_card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 8 if column < 2 else 0))
            tk.Label(
                inner_card,
                text=label,
                font=(FONT, 10, "bold"),
                bg=COLORS["surface_alt"],
                fg=accent,
            ).pack(anchor="w", padx=16, pady=(14, 2))
            tk.Label(
                inner_card,
                text=format_duration(summary["best_by_difficulty"].get(difficulty)),
                font=(FONT_MONO, 18, "bold"),
                bg=COLORS["surface_alt"],
                fg=COLORS["text"] if summary["best_by_difficulty"].get(difficulty) is not None else COLORS["disabled"],
            ).pack(anchor="w", padx=16)
            tk.Label(
                inner_card,
                text=f"{summary['run_counts'].get(difficulty, 0):02d} {t('ops_label')}",
                font=(FONT_MONO, 8),
                bg=COLORS["surface_alt"],
                fg=COLORS["muted"],
            ).pack(anchor="w", padx=16, pady=(6, 14))

        recent_section = tk.Frame(inner, bg=COLORS["surface"])
        recent_section.pack(fill=tk.BOTH, expand=True, padx=24, pady=(18, 0))
        tk.Label(
            recent_section,
            text=t("profile_recent_title"),
            font=(FONT_MONO, 9, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).pack(anchor="w", pady=(0, 10))
        recent_outer, recent_inner = make_panel(recent_section, bg=COLORS["surface"], border=COLORS["border"])
        recent_outer.pack(fill=tk.BOTH, expand=True)
        rows = summary["recent_matches"]
        if not rows:
            tk.Label(
                recent_inner,
                text=t("profile_no_recent"),
                font=(FONT, 10),
                bg=COLORS["surface"],
                fg=COLORS["disabled"],
            ).pack(anchor="w", padx=18, pady=16)
        else:
            for index, record in enumerate(rows):
                row_bg = COLORS["surface_alt"] if index % 2 else COLORS["surface"]
                row = tk.Frame(recent_inner, bg=row_bg)
                row.pack(fill=tk.X, padx=1, pady=(1 if index == 0 else 0, 0))
                difficulty = record.get("difficulty", "")
                accent = {
                    "9x9": COLORS["success"],
                    "27x27": COLORS["warning"],
                    "81x81": COLORS["danger"],
                }.get(difficulty, COLORS["primary"])
                left = tk.Frame(row, bg=row_bg)
                left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=16, pady=10)
                tk.Label(
                    left,
                    text=DIFFICULTY_CONFIG.get(difficulty, {}).get("title", difficulty),
                    font=(FONT, 10, "bold"),
                    bg=row_bg,
                    fg=accent,
                ).pack(anchor="w")
                tk.Label(
                    left,
                    text=t("match_win") if record.get("result") == "win" else t("match_fail"),
                    font=(FONT_MONO, 8),
                    bg=row_bg,
                    fg=COLORS["success"] if record.get("result") == "win" else COLORS["danger"],
                ).pack(anchor="w", pady=(4, 0))
                right = tk.Frame(row, bg=row_bg)
                right.pack(side=tk.RIGHT, padx=16, pady=10)
                tk.Label(
                    right,
                    text=format_duration(record.get("time_seconds")),
                    font=(FONT_MONO, 11, "bold"),
                    bg=row_bg,
                    fg=COLORS["text"],
                ).pack(anchor="e")
                tk.Label(
                    right,
                    text=record.get("completed_at", "--"),
                    font=(FONT_MONO, 8),
                    bg=row_bg,
                    fg=COLORS["muted"],
                ).pack(anchor="e", pady=(4, 0))

        actions = tk.Frame(dialog, bg=COLORS["surface"])
        actions.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14), ipady=11)
        actions.configure(padx=24)
        actions.grid_columnconfigure((0, 1), weight=1, uniform="profile_actions")
        actions.grid_rowconfigure(0, minsize=62)
        self._profile_switch_button = CyberButton(
            actions,
            text=t("profile_switch_account"),
            variant="secondary",
            command=self._switch_account,
            size="large",
        )
        self._profile_switch_button.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._profile_logout_button = CyberButton(
            actions,
            text=t("btn_logout"),
            variant="danger",
            command=self._logout,
            size="large",
        )
        self._profile_logout_button.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        actions.tkraise()

        dialog.update_idletasks()
        width, height, min_width, min_height = LAYOUT["profile"]
        width = min(width, max(min_width, dialog.winfo_screenwidth() - 80))
        height = min(height, max(680, dialog.winfo_screenheight() - 180))
        x = self.root.winfo_rootx() + max(0, (self.root.winfo_width() - width) // 2)
        y = self.root.winfo_rooty() + max(0, (self.root.winfo_height() - height) // 2)
        y = max(20, min(y, dialog.winfo_screenheight() - height - 20))
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.minsize(min(min_width, width), min(680, height))
        dialog.grab_set()
        dialog.focus_set()

    def _start_game(self, difficulty: str) -> None:
        self._swap(GameFrame, self.current_user, difficulty, self._show_menu, self._show_ranking)

    def _show_ranking(self) -> None:
        self._swap(RankingFrame, self.current_user, self._show_menu)

    def _switch_account(self) -> None:
        self.current_user = None
        self._close_profile_dialog()
        self._show_auth()

    def _logout(self) -> None:
        if messagebox.askyesno(t("btn_account"), t("logout_confirm"), parent=self.root):
            self.current_user = None
            self._close_profile_dialog()
            self._show_auth()

    def _handle_escape(self) -> None:
        if self._profile_dialog is not None and self._profile_dialog.winfo_exists():
            self._close_profile_dialog()
            return
        if self.current_user and isinstance(self.current_frame, (GameFrame, RankingFrame)):
            self._show_menu()

    def _quit(self) -> None:
        self._cancel_cloud_probe()
        self._close_profile_dialog()
        if self.current_user and not messagebox.askyesno(t("title"), t("quit_confirm"), parent=self.root):
            return
        self.root.destroy()


if __name__ == "__main__":
    MainApp()
