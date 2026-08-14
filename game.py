"""Minesweeper rules and the responsive Tk game screen."""
from __future__ import annotations

import os
import random
import threading
import tkinter as tk
from tkinter import ttk

from database import _github_append_ranking, save_match_result, save_ranking
from lang import t
from sound import play_explosion, play_flag, play_reveal, play_win
from solver import is_no_guess
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
    set_window_geometry,
)


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_BOMB_PNG = os.path.join(_BASE_DIR, "bomb16.png")

NUM_COLORS = {
    1: "#0b6cbf",
    2: "#0a7d4f",
    3: "#d62a4c",
    4: "#6a3fc0",
    5: "#b85c00",
    6: "#0a8a8a",
    7: "#1f2937",
    8: "#64748b",
}

BOARD_GRADIENTS = (
    ("#33bfe4", "#64dfb8"),
    ("#45aaf2", "#9d8cff"),
    ("#2fb4d0", "#50d6a4"),
    ("#5a9cf0", "#e17ca8"),
)


def interpolate_hex(start: str, end: str, amount: float) -> str:
    """Interpolate two RGB hex colors with a clamped amount."""
    amount = max(0.0, min(1.0, float(amount)))
    first = tuple(int(start[index:index + 2], 16) for index in (1, 3, 5))
    second = tuple(int(end[index:index + 2], 16) for index in (1, 3, 5))
    mixed = tuple(round(left + (right - left) * amount) for left, right in zip(first, second))
    return "#" + "".join(f"{channel:02x}" for channel in mixed)


def board_gradient_color(start: str, end: str, row: int, col: int, rows: int, cols: int) -> str:
    denominator = max(1, rows + cols - 2)
    return interpolate_hex(start, end, (row + col) / denominator)

DIFFICULTY_CONFIG = {
    "9x9": {"rows": 9, "cols": 9, "mines": 10, "cell": 48, "title_key": "easy_title"},
    "27x27": {"rows": 27, "cols": 27, "mines": 100, "cell": 20, "title_key": "medium_title"},
    "81x81": {"rows": 81, "cols": 81, "mines": 800, "cell": 14, "title_key": "hard_title"},
}


def calculate_fit_zoom(view_width: int, view_height: int, rows: int, cols: int,
                       cell_size: int, *, minimum: float = 0.25) -> float:
    if min(view_width, view_height, rows, cols, cell_size) <= 0:
        return 1.0
    zoom = min(view_width / (cols * cell_size), view_height / (rows * cell_size))
    return round(max(minimum, min(3.0, zoom)), 2)


def board_density(config: dict) -> str:
    cells = max(1, int(config["rows"]) * int(config["cols"]))
    return f"{int(config['mines']) / cells * 100:.1f}%"


def clearance_percent(game: "MinesweeperGame") -> int:
    if game.total_safe_cells <= 0:
        return 100
    return min(100, int(game.revealed_count / game.total_safe_cells * 100))


def flag_count(game: "MinesweeperGame") -> int:
    return sum(game.flagged[row][col] for row in range(game.rows) for col in range(game.cols))


class MinesweeperGame:
    """Pure game state and rules; no Tk dependencies."""

    def __init__(self, difficulty: str, rng=None):
        if difficulty not in DIFFICULTY_CONFIG:
            raise ValueError(f"Unknown difficulty: {difficulty!r}")
        config = DIFFICULTY_CONFIG[difficulty]
        self.difficulty = difficulty
        self._rng = rng or random
        self.rows = config["rows"]
        self.cols = config["cols"]
        self.total_mines = config["mines"]
        self.board = [[0] * self.cols for _ in range(self.rows)]
        self.revealed = [[False] * self.cols for _ in range(self.rows)]
        self.flagged = [[False] * self.cols for _ in range(self.rows)]
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.mines_generated = False
        self.mine_positions: set[tuple[int, int]] = set()
        self.revealed_count = 0
        self.total_safe_cells = self.rows * self.cols - self.total_mines

    def _neighbors(self, row: int, col: int):
        for row_delta in (-1, 0, 1):
            for col_delta in (-1, 0, 1):
                if not row_delta and not col_delta:
                    continue
                neighbor = row + row_delta, col + col_delta
                if 0 <= neighbor[0] < self.rows and 0 <= neighbor[1] < self.cols:
                    yield neighbor

    def generate_mines(self, safe_row: int, safe_col: int) -> None:
        if self.mines_generated:
            return
        if not (0 <= safe_row < self.rows and 0 <= safe_col < self.cols):
            raise ValueError("Safe cell is outside the board")
        safe = {(safe_row, safe_col)}
        if self.rows * self.cols > self.total_mines + 9:
            safe.update(self._neighbors(safe_row, safe_col))
        candidates = [
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if (row, col) not in safe
        ]
        mine_count = min(self.total_mines, len(candidates))
        # 无猜重布：约束传播解不开就重布，超过上限则接受当前布局
        max_retries = 60 if self.rows * self.cols <= 27 * 27 else 6
        for _ in range(max_retries):
            self.mine_positions = set(self._rng.sample(candidates, mine_count))
            self._compute_numbers()
            if is_no_guess(self.rows, self.cols, self.board, self.mine_positions, safe_row, safe_col):
                break
        self.mines_generated = True

    def _compute_numbers(self) -> None:
        for row in range(self.rows):
            for col in range(self.cols):
                self.board[row][col] = -1 if (row, col) in self.mine_positions else 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1:
                    self.board[row][col] = sum(self.board[nr][nc] == -1 for nr, nc in self._neighbors(row, col))

    def reveal(self, row: int, col: int) -> str:
        if self.game_over or self.game_won:
            return "continue"
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return "continue"
        if self.revealed[row][col] or self.flagged[row][col]:
            return "continue"
        if self.first_click:
            self.generate_mines(row, col)
            self.first_click = False
        if self.board[row][col] == -1:
            self.game_over = True
            self.revealed[row][col] = True
            return "game_over"
        self._flood_fill(row, col)
        if self.revealed_count >= self.total_safe_cells:
            self.game_won = True
            return "win"
        return "continue"

    def _flood_fill(self, start_row: int, start_col: int) -> None:
        stack = [(start_row, start_col)]
        while stack:
            row, col = stack.pop()
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                continue
            if self.revealed[row][col] or self.flagged[row][col] or self.board[row][col] == -1:
                continue
            self.revealed[row][col] = True
            self.revealed_count += 1
            if self.board[row][col] == 0:
                stack.extend(self._neighbors(row, col))

    def chord(self, row: int, col: int) -> str:
        if self.game_over or self.game_won:
            return "continue"
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return "continue"
        if not self.revealed[row][col] or self.board[row][col] <= 0:
            return "continue"
        flag_count = sum(self.flagged[nr][nc] for nr, nc in self._neighbors(row, col))
        if flag_count != self.board[row][col]:
            return "continue"
        result = "continue"
        for nr, nc in self._neighbors(row, col):
            if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                current = self.reveal(nr, nc)
                if current == "game_over":
                    result = current
                elif current == "win" and result != "game_over":
                    result = current
        return result

    def toggle_flag(self, row: int, col: int) -> None:
        if self.game_over or self.game_won:
            return
        if 0 <= row < self.rows and 0 <= col < self.cols and not self.revealed[row][col]:
            self.flagged[row][col] = not self.flagged[row][col]

    @property
    def remaining_mines(self) -> int:
        flagged_count = sum(self.flagged[row][col] for row in range(self.rows) for col in range(self.cols))
        return self.total_mines - flagged_count


class GameFrame(tk.Frame):
    def __init__(self, parent, user: dict, difficulty: str, on_back, on_ranking=None):
        super().__init__(parent, bg=COLORS["bg"])
        configure_ttk(parent)
        install_backdrop(self)
        self.user = user
        self.difficulty = difficulty
        self.on_back = on_back
        self.on_ranking = on_ranking
        self.cfg = DIFFICULTY_CONFIG[difficulty]
        self.game = MinesweeperGame(difficulty)
        self.cell_size = self.cfg["cell"]
        self.timer_running = False
        self.timer_seconds = 0
        self._after_id = None
        self._fit_after_id = None
        self.zoom = 1.0
        self._auto_fit_pending = difficulty == "81x81"
        self.hover_cell: tuple[int, int] | None = None
        self._result_panel: tk.Frame | None = None
        self._board_bg = COLORS["input"]
        self._gradient = random.choice(BOARD_GRADIENTS)
        self._tile_fills = self._build_tile_fills()
        self._cell_items: dict[tuple[int, int], list[int]] = {}
        self._rendered_revealed = [[False] * self.game.cols for _ in range(self.game.rows)]
        self._rendered_flagged = [[False] * self.game.cols for _ in range(self.game.rows)]
        self._wrong_flags: set[tuple[int, int]] = set()
        self._build_ui()
        self._bind_shortcuts()
        self._apply_window_size()

    def _apply_window_size(self) -> None:
        root = self.winfo_toplevel()
        if self.difficulty == "81x81":
            set_window_geometry(root, *LAYOUT["game_hard"])
        elif self.difficulty == "27x27":
            set_window_geometry(root, *LAYOUT["game_medium"])
        else:
            set_window_geometry(root, *LAYOUT["game_easy"])
        root.title(t("window_title", t("title"), t(self.cfg["title_key"]), self.user["username"]))

    def _build_ui(self) -> None:
        bar_outer, bar = make_panel(self, bg=COLORS["surface"], border=COLORS["border_hot"])
        bar_outer.pack(fill=tk.X, padx=16, pady=(14, 0))
        bar.configure(height=78)
        bar.pack_propagate(False)

        CyberButton(bar, text=t("btn_back"), variant="secondary", command=self._back).pack(side=tk.LEFT, padx=10, pady=12)
        image = load_photo(_BOMB_PNG, master=self)
        if image is not None:
            self._bomb_image = image
            tk.Label(bar, image=image, bg=COLORS["surface"]).pack(side=tk.LEFT, padx=(10, 6))

        mine_box = tk.Frame(bar, bg=COLORS["surface"])
        mine_box.pack(side=tk.LEFT, pady=10)
        tk.Label(mine_box, text=t("mines"), font=(FONT_MONO, 9), bg=COLORS["surface"], fg=COLORS["subtle"]).pack(anchor="w")
        self.mine_label = tk.Label(mine_box, font=(FONT_MONO, 16, "bold"), bg=COLORS["surface"], fg=COLORS["text"])
        self.mine_label.pack(anchor="w")

        title_stack = tk.Frame(bar, bg=COLORS["surface"])
        title_stack.pack(side=tk.LEFT, padx=20, pady=10)
        tk.Label(title_stack, text=t(self.cfg["title_key"]), font=(FONT, 13, "bold"), bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(title_stack, text=t("control_hint"), font=(FONT, 9), bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", pady=(4, 0))
        self.status_label = tk.Label(title_stack, text=self._status_text(), font=(FONT_MONO, 9, "bold"), bg=COLORS["surface"], fg=COLORS["primary"])
        self.status_label.pack(anchor="w", pady=(4, 0))

        density_box = tk.Frame(bar, bg=COLORS["surface"])
        density_box.pack(side=tk.RIGHT, padx=14, pady=10)
        tk.Label(density_box, text=t("mine_density"), font=(FONT_MONO, 9), bg=COLORS["surface"], fg=COLORS["subtle"]).pack(anchor="e")
        tk.Label(density_box, text=board_density(self.cfg), font=(FONT_MONO, 16, "bold"), bg=COLORS["surface"], fg=COLORS["warning"]).pack(anchor="e")

        progress_box = tk.Frame(bar, bg=COLORS["surface"])
        progress_box.pack(side=tk.RIGHT, padx=14, pady=10)
        tk.Label(progress_box, text=t("clearance_label"), font=(FONT_MONO, 9), bg=COLORS["surface"], fg=COLORS["subtle"]).pack(anchor="e")
        self.progress_label = tk.Label(progress_box, text="000%", font=(FONT_MONO, 16, "bold"), bg=COLORS["surface"], fg=COLORS["primary"])
        self.progress_label.pack(anchor="e")

        timer_box = tk.Frame(bar, bg=COLORS["surface"])
        timer_box.pack(side=tk.RIGHT, padx=16, pady=10)
        tk.Label(timer_box, text=t("time_label"), font=(FONT_MONO, 9), bg=COLORS["surface"], fg=COLORS["subtle"]).pack(anchor="e")
        self.timer_label = tk.Label(timer_box, text="00:00", font=(FONT_MONO, 16, "bold"), bg=COLORS["surface"], fg=COLORS["text"])
        self.timer_label.pack(anchor="e")

        self._update_mine_label()
        self._update_progress_label()
        if self.difficulty == "81x81":
            self._build_large_board()
        else:
            self._build_small_board()

        bottom = tk.Frame(self, bg=COLORS["bg"])
        self._bottom_bar = bottom
        bottom.pack(fill=tk.X, padx=24, pady=(0, 18))
        CyberButton(bottom, text=t("btn_restart"), variant="secondary", command=self.restart).pack(side=tk.LEFT, padx=6)
        tk.Label(bottom, text=t("quick_controls"), font=(FONT_MONO, 10), bg=COLORS["bg"], fg=COLORS["subtle"]).pack(side=tk.RIGHT, padx=6)

    def _bind_canvas(self, canvas):
        canvas.bind("<Button-1>", self._left_click)
        canvas.bind("<Double-Button-1>", self._double_click)
        canvas.bind("<Button-3>", self._right_click)
        canvas.bind("<Button-2>", self._double_click)  # 中键 = chord 快速展开
        canvas.bind("<Leave>", self._clear_hover)

    def _build_small_board(self) -> None:
        width = self.cfg["cols"] * self.cell_size
        height = self.cfg["rows"] * self.cell_size
        outer, inner = make_panel(self, bg=self._board_bg, border=COLORS["border"])
        outer.pack(padx=24, pady=24, expand=True)
        self.canvas = tk.Canvas(inner, width=width, height=height, bg=self._board_bg, highlightthickness=0, cursor="crosshair")
        self.canvas.pack(padx=2, pady=2)
        self._bind_canvas(self.canvas)
        self.canvas.bind("<Motion>", self._track_hover)
        self._draw_small()

    def _build_tile_fills(self) -> list[list[str]]:
        return [
            [
                board_gradient_color(*self._gradient, row, col, self.game.rows, self.game.cols)
                for col in range(self.game.cols)
            ]
            for row in range(self.game.rows)
        ]

    def _tile_colors(self, row: int, col: int) -> tuple[str, str]:
        return self._tile_fills[row][col], COLORS["tile_border"]

    def _draw_unrevealed_tile(
        self, canvas, x1: float, y1: float, x2: float, y2: float, fill: str, outline: str, *, detailed: bool
    ) -> list[int]:
        edge = COLORS["tile_edge_shadow"] if detailed else COLORS["tile_border"]
        ids = [canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=edge, width=1)]
        if not detailed:
            return ids
        ids.append(canvas.create_line(x1 + 1, y1 + 1, x2 - 1, y1 + 1, fill=COLORS["tile_edge_light"], width=1))
        ids.append(canvas.create_line(x1 + 1, y1 + 1, x1 + 1, y2 - 1, fill=outline, width=1))
        ids.append(canvas.create_line(x1 + 1, y2 - 1, x2 - 1, y2 - 1, fill=COLORS["tile_edge_shadow"], width=1))
        ids.append(canvas.create_line(x2 - 1, y1 + 1, x2 - 1, y2 - 1, fill=COLORS["tile_edge_shadow"], width=1))
        return ids

    def _draw_revealed_tile(
        self, canvas, x1: float, y1: float, x2: float, y2: float, row: int, col: int, *, detailed: bool = True
    ) -> list[int]:
        fill = COLORS["tile_open_alt"] if (row + col) % 2 else COLORS["tile_open"]
        ids = [canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=COLORS["tile_open_border"], width=1)]
        if not detailed:
            return ids
        inset = 1
        ids.append(canvas.create_line(x1 + inset, y1 + inset, x2 - inset, y1 + inset, fill=COLORS["tile_open_highlight"], width=1))
        ids.append(canvas.create_line(x1 + inset, y1 + inset, x1 + inset, y2 - inset, fill=COLORS["tile_open_highlight"], width=1))
        ids.append(canvas.create_line(x1 + inset, y2 - inset, x2 - inset, y2 - inset, fill=COLORS["tile_open_shadow"], width=1))
        ids.append(canvas.create_line(x2 - inset, y1 + inset, x2 - inset, y2 - inset, fill=COLORS["tile_open_shadow"], width=1))
        return ids

    def _draw_cell(self, canvas, row: int, col: int, size: int, *, small: bool) -> None:
        x1, y1 = col * size, row * size
        x2, y2 = x1 + size, y1 + size
        center_x, center_y = x1 + size // 2, y1 + size // 2
        if self.game.revealed[row][col]:
            self._draw_revealed_tile(canvas, x1, y1, x2, y2, row, col)
            value = self.game.board[row][col]
            if value == -1:
                canvas.create_rectangle(x1 + 4, y1 + 4, x2 - 4, y2 - 4, fill=COLORS["danger_dim"], outline=COLORS["danger"])
                canvas.create_text(
                    center_x,
                    center_y,
                    text="X",
                    font=("Consolas", max(8, size // 2), "bold"),
                    fill=COLORS["danger"],
                )
            elif value > 0:
                canvas.create_text(
                    center_x,
                    center_y,
                    text=str(value),
                    font=("Consolas", max(8, size // 2), "bold"),
                    fill=NUM_COLORS.get(value, COLORS["text"]),
                )
        elif self.game.flagged[row][col]:
            canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["tile_flag"], outline=COLORS["danger"], width=2)
            wrong = (row, col) in self._wrong_flags
            canvas.create_text(
                center_x,
                center_y,
                text="X" if wrong else "⚑",
                font=(FONT, max(8, size // 2), "bold"),
                fill=COLORS["text"],
            )
        else:
            fill, outline = self._tile_colors(row, col)
            self._draw_unrevealed_tile(canvas, x1, y1, x2, y2, fill, outline, detailed=small)

    def _draw_small(self) -> None:
        self.canvas.delete("all")
        self._hover_item = self.canvas.create_rectangle(
            0, 0, 0, 0, outline=COLORS["border_hot"], width=2, state="hidden"
        )
        size = self.cell_size
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                self._draw_cell(self.canvas, row, col, size, small=True)
        self._update_hover_item()

    def _build_large_board(self) -> None:
        outer, inner = make_panel(self, bg=COLORS["surface"], border=COLORS["border"])
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)
        self.scroll_canvas = tk.Canvas(inner, width=780, height=560, bg=self._board_bg, highlightthickness=0)
        self.h_bar = ttk.Scrollbar(inner, orient=tk.HORIZONTAL, command=self.scroll_canvas.xview, style="Cyber.Horizontal.TScrollbar")
        self.v_bar = ttk.Scrollbar(inner, orient=tk.VERTICAL, command=self.scroll_canvas.yview, style="Cyber.Vertical.TScrollbar")
        self.scroll_canvas.configure(xscrollcommand=self.h_bar.set, yscrollcommand=self.v_bar.set)
        self.scroll_canvas.bind("<Configure>", self._viewport_resized)
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")
        self.h_bar.grid(row=1, column=0, sticky="ew")
        self.v_bar.grid(row=0, column=1, sticky="ns")
        self.canvas = tk.Canvas(self.scroll_canvas, bg=self._board_bg, highlightthickness=0)
        self._canvas_window = self.scroll_canvas.create_window(0, 0, window=self.canvas, anchor="nw")
        self._bind_canvas(self.canvas)

        zoom_bar = tk.Frame(self, bg=COLORS["bg"])
        zoom_bar.pack(fill=tk.X, padx=24, pady=(0, 10))
        CyberButton(zoom_bar, text="-", variant="secondary", command=self._zoom_out, width=4).pack(side=tk.LEFT, padx=2)
        self.zoom_label = tk.Label(zoom_bar, text="100%", font=(FONT, 10, "bold"), bg=COLORS["bg"], fg=COLORS["muted"], width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=4)
        CyberButton(zoom_bar, text="+", variant="secondary", command=self._zoom_in, width=4).pack(side=tk.LEFT, padx=2)
        CyberButton(zoom_bar, text=t("zoom_fit"), variant="secondary", command=self._zoom_reset).pack(side=tk.LEFT, padx=10)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._draw_large()
    def _glyph_font(self) -> tuple:
        glyph_pixels = max(5, int(self._actual_cs - 2))
        return ("Consolas", -glyph_pixels, "bold")

    def _draw_cell_large(self, row: int, col: int) -> list[int]:
        """Draw one large-board cell and return its canvas item ids."""
        size = self._actual_cs
        x1, y1 = col * size, row * size
        x2, y2 = x1 + size, y1 + size
        center_x = x1 + max(size - 2, 0) // 2
        center_y = y1 + max(size - 2, 0) // 2
        glyph_font = self._glyph_font()
        if self.game.revealed[row][col]:
            ids = self._draw_revealed_tile(self.canvas, x1, y1, x2, y2, row, col, detailed=False)
            value = self.game.board[row][col]
            if value == -1 and size >= 6:
                ids.append(self.canvas.create_rectangle(
                    x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=COLORS["danger_dim"], outline=COLORS["danger"]
                ))
                ids.append(self.canvas.create_text(center_x, center_y, text="X", font=glyph_font, fill=COLORS["danger"]))
            elif value > 0 and size >= 6:
                ids.append(self.canvas.create_text(
                    center_x, center_y, text=str(value), font=glyph_font,
                    fill=NUM_COLORS.get(value, COLORS["text"]),
                ))
            return ids
        if self.game.flagged[row][col]:
            ids = [self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=COLORS["tile_flag"], outline=COLORS["danger"], width=1
            )]
            if size >= 6:
                wrong = (row, col) in self._wrong_flags
                ids.append(self.canvas.create_text(
                    center_x, center_y, text="X" if wrong else "⚑",
                    font=(FONT, -max(5, int(size - 2)), "bold"), fill=COLORS["text"]
                ))
            return ids
        fill, outline = self._tile_colors(row, col)
        return self._draw_unrevealed_tile(self.canvas, x1, y1, x2, y2, fill, outline, detailed=False)

    def _sync_rendered_state(self) -> None:
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                self._rendered_revealed[row][col] = self.game.revealed[row][col]
                self._rendered_flagged[row][col] = self.game.flagged[row][col]

    def _draw_large(self) -> None:
        self.canvas.delete("all")
        size = max(4.0, self.cell_size * self.zoom)
        self._actual_cs = size
        self._cell_items = {}
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                self._cell_items[(row, col)] = self._draw_cell_large(row, col)
        self._sync_rendered_state()
        width, height = self.game.cols * size, self.game.rows * size
        canvas_width, canvas_height = int(round(width)), int(round(height))
        self.canvas.configure(width=canvas_width, height=canvas_height)
        viewport_width = max(1, self.scroll_canvas.winfo_width())
        viewport_height = max(1, self.scroll_canvas.winfo_height())
        origin_x = max(0, (viewport_width - canvas_width) // 2)
        origin_y = max(0, (viewport_height - canvas_height) // 2)
        self.scroll_canvas.coords(self._canvas_window, origin_x, origin_y)
        self.scroll_canvas.configure(scrollregion=(0, 0, max(viewport_width, canvas_width), max(viewport_height, canvas_height)))

    def _redraw_cell(self, row: int, col: int) -> None:
        for item_id in self._cell_items.get((row, col), ()):
            self.canvas.delete(item_id)
        self._cell_items[(row, col)] = self._draw_cell_large(row, col)

    def _redraw_incremental(self) -> None:
        """Redraw only cells whose revealed/flagged state changed."""
        changed = []
        for row in range(self.game.rows):
            game_revealed = self.game.revealed[row]
            game_flagged = self.game.flagged[row]
            rendered_revealed = self._rendered_revealed[row]
            rendered_flagged = self._rendered_flagged[row]
            for col in range(self.game.cols):
                if game_revealed[col] != rendered_revealed[col] or game_flagged[col] != rendered_flagged[col]:
                    changed.append((row, col))
                    rendered_revealed[col] = game_revealed[col]
                    rendered_flagged[col] = game_flagged[col]
        for row, col in changed:
            self._redraw_cell(row, col)

    def _zoom_in(self):
        self.zoom = min(3.0, self.zoom + 0.25)
        self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")
        self._draw_large()

    def _zoom_out(self):
        self.zoom = max(0.25, self.zoom - 0.25)
        self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")
        self._draw_large()

    def _zoom_reset(self):
        self._zoom_fit()

    def _zoom_fit(self):
        self.update_idletasks()
        self.zoom = calculate_fit_zoom(
            max(1, self.scroll_canvas.winfo_width() - 8),
            max(1, self.scroll_canvas.winfo_height() - 8),
            self.game.rows,
            self.game.cols,
            self.cell_size,
            minimum=0.75,
        )
        self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")
        self._draw_large()

    def _viewport_resized(self, event):
        if not self._auto_fit_pending or event.width <= 1 or event.height <= 1:
            return
        if self._fit_after_id is not None:
            self.after_cancel(self._fit_after_id)
        self._fit_after_id = self.after(40, self._finish_initial_fit)

    def _finish_initial_fit(self):
        self._fit_after_id = None
        self._auto_fit_pending = False
        self._zoom_fit()

    def _on_mousewheel(self, event):
        if event.state & 0x4:
            self._zoom_in() if event.delta > 0 else self._zoom_out()
        else:
            self.scroll_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _get_cell(self, x: int, y: int):
        size = getattr(self, "_actual_cs", self.cell_size)
        row, col = int(y // size), int(x // size)
        return (row, col) if 0 <= row < self.game.rows and 0 <= col < self.game.cols else (None, None)

    def _update_hover_item(self) -> None:
        if self.difficulty == "81x81":
            return
        item = getattr(self, "_hover_item", None)
        if item is None:
            return
        row, col = self.hover_cell or (None, None)
        if row is None or col is None or self.game.revealed[row][col] or self.game.flagged[row][col]:
            self.canvas.itemconfigure(item, state="hidden")
            return
        size = self.cell_size
        x1, y1 = col * size + 1, row * size + 1
        self.canvas.coords(item, x1, y1, x1 + size - 2, y1 + size - 2)
        self.canvas.itemconfigure(item, state="normal")
        self.canvas.tag_raise(item)

    def _track_hover(self, event):
        row, col = self._get_cell(event.x, event.y)
        next_cell = None if row is None else (row, col)
        if next_cell != self.hover_cell:
            self.hover_cell = next_cell
            self._update_hover_item()

    def _clear_hover(self, _event=None):
        if self.hover_cell is not None:
            self.hover_cell = None
            self._update_hover_item()

    def _handle_result(self, result: str) -> None:
        self._redraw()
        self._update_mine_label()
        self._update_progress_label()
        self._update_status()
        if result == "game_over":
            play_explosion()
            self._stop_timer()
            save_match_result(self.user["id"], self.difficulty, "game_over", self.timer_seconds)
            triggered = self._find_triggered_mine()
            self._reveal_all_mines()
            self.after(180, lambda: self._show_result_panel("game_over"))
            if triggered is not None:
                self.after(180, lambda: self._flash_mine(*triggered))
        elif result == "win":
            play_win()
            self._stop_timer()
            self.after(180, self._on_win)

    def _left_click(self, event):
        if self.game.game_over or self.game.game_won:
            return
        row, col = self._get_cell(event.x, event.y)
        if row is None:
            return
        if not self.timer_running:
            self._start_timer()
        before = self.game.revealed_count
        result = self.game.reveal(row, col)
        self._handle_result(result)
        if result == "continue" and self.game.revealed_count > before:
            play_reveal()

    def _right_click(self, event):
        if self.game.game_over or self.game.game_won:
            return
        row, col = self._get_cell(event.x, event.y)
        if row is None:
            return
        if not self.timer_running:
            self._start_timer()
        before = self.game.flagged[row][col]
        self.game.toggle_flag(row, col)
        if self.game.flagged[row][col] != before:
            play_flag()
        self._redraw()
        self._update_mine_label()
        self._update_progress_label()

    def _double_click(self, event):
        if self.game.game_over or self.game.game_won:
            return
        row, col = self._get_cell(event.x, event.y)
        if row is None or not self.game.revealed[row][col]:
            return
        self._handle_result(self.game.chord(row, col))

    def _redraw(self):
        if self.difficulty == "81x81":
            self._redraw_incremental()
        else:
            self._draw_small()

    def _full_redraw(self):
        self._draw_large() if self.difficulty == "81x81" else self._draw_small()

    def _start_timer(self):
        self.timer_running = True
        self.timer_seconds = 0
        self.timer_label.configure(text="00:00")
        self._update_status()
        self._after_id = self.after(1000, self._tick)

    def _tick(self):
        if not self.timer_running:
            return
        self.timer_seconds += 1
        minutes, seconds = divmod(self.timer_seconds, 60)
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")
        self._after_id = self.after(1000, self._tick)

    def _stop_timer(self):
        self.timer_running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self._update_status()

    def _update_mine_label(self):
        self.mine_label.configure(text=f"{self.game.remaining_mines:02d}")

    def _update_progress_label(self):
        if hasattr(self, "progress_label") and self.progress_label.winfo_exists():
            self.progress_label.configure(text=f"{clearance_percent(self.game):03d}%")

    def _status_text(self) -> str:
        if self.game.game_won:
            return f"{t('sector_label')}: {t('board_status_clear')}"
        if self.game.game_over:
            return f"{t('sector_label')}: {t('board_status_failed')}"
        if self.timer_running:
            return f"{t('sector_label')}: {t('board_status_live')}"
        return f"{t('sector_label')}: {t('board_status_ready')}"

    def _update_status(self) -> None:
        if hasattr(self, "status_label") and self.status_label.winfo_exists():
            color = COLORS["primary"]
            if self.game.game_over:
                color = COLORS["danger"]
            elif self.game.game_won:
                color = COLORS["success"]
            self.status_label.configure(text=self._status_text(), fg=color)

    def _reveal_all_mines(self):
        self._wrong_flags = set()
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.board[row][col] == -1:
                    if not self.game.flagged[row][col]:
                        self.game.revealed[row][col] = True
                elif self.game.flagged[row][col]:
                    self._wrong_flags.add((row, col))
        self._redraw()

    def _find_triggered_mine(self):
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.board[row][col] == -1 and self.game.revealed[row][col]:
                    return (row, col)
        return None

    def _flash_mine(self, row: int, col: int, times: int = 3, interval: int = 140) -> None:
        """Briefly pulse the triggered mine cell in red."""
        if not self.winfo_exists():
            return
        size = self._actual_cs if self.difficulty == "81x81" else self.cell_size
        x1, y1 = col * size, row * size
        x2, y2 = x1 + size, y1 + size
        overlay = self.canvas.create_rectangle(
            x1, y1, x2, y2, fill=COLORS["danger"], outline=COLORS["danger"], width=2, stipple="gray50"
        )

        def blink(count: int) -> None:
            if count <= 0 or not self.winfo_exists():
                self.canvas.delete(overlay)
                return
            self.canvas.itemconfigure(overlay, state="hidden" if count % 2 == 0 else "normal")
            self.after(interval, lambda: blink(count - 1))

        blink(times * 2)

    def _close_result_dialog(self) -> None:
        panel = self._result_panel
        if panel is not None and panel.winfo_exists():
            panel.destroy()
        self._result_panel = None

    def _show_result_panel(self, result: str) -> None:
        if not self.winfo_exists():
            return
        self._close_result_dialog()
        is_win = result == "win"
        title = t("win_title") if is_win else t("game_over")
        accent = COLORS["success"] if is_win else COLORS["danger"]
        minutes, seconds = divmod(self.timer_seconds, 60)
        mode_label = t("mode_label")
        mode_name = t(self.cfg["title_key"])
        if is_win:
            message = t("win_msg_with_mode", mode_label, mode_name, f"{minutes:02d}:{seconds:02d}")
        else:
            message = t("result_failed_tip")

        outer, inner = make_panel(self, bg=COLORS["surface"], border=accent)
        self._result_panel = outer
        # 浮层覆盖在棋盘上方，避免与棋盘的 pack 空间竞争导致文字被压缩
        outer.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82)

        header = tk.Frame(inner, bg=COLORS["surface"])
        header.pack(fill=tk.X, padx=28, pady=(20, 6))
        left = tk.Frame(header, bg=COLORS["surface"])
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(left, text=t("result_summary"), font=(FONT_MONO, 10, "bold"), bg=COLORS["surface"], fg=accent).pack(anchor="w")
        tk.Label(left, text=title, font=(FONT, 24, "bold"), bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", pady=(4, 0))
        CyberButton(header, text=t("btn_close"), variant="secondary", command=self._close_result_dialog).pack(side=tk.RIGHT, anchor="n", padx=(16, 0))

        tk.Label(
            inner, text=message, font=(FONT, 11), bg=COLORS["surface"], fg=COLORS["muted"],
            wraplength=620, justify="left", anchor="w",
        ).pack(fill=tk.X, padx=28, pady=(8, 0))

        stats = tk.Frame(inner, bg=COLORS["surface"])
        stats.pack(fill=tk.X, padx=28, pady=(16, 0))
        metric_label(stats, t("time_label"), f"{minutes:02d}:{seconds:02d}", accent=accent).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        metric_label(stats, t("clearance_label"), f"{clearance_percent(self.game):03d}%", accent=COLORS["primary"]).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))
        metric_label(stats, t("flags_label"), str(flag_count(self.game)).zfill(2), accent=COLORS["text"]).pack(side=tk.LEFT, expand=True, fill=tk.X)

        footer = tk.Frame(inner, bg=COLORS["surface"])
        footer.pack(fill=tk.X, padx=28, pady=(14, 20))
        tip = tk.Frame(footer, bg=COLORS["surface"])
        tip.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        if is_win:
            tk.Label(tip, text=t("result_saved"), font=(FONT_MONO, 10, "bold"), bg=COLORS["surface"], fg=COLORS["success"]).pack(anchor="w")
        tk.Label(tip, text=t("result_retry_tip"), font=(FONT, 10), bg=COLORS["surface"], fg=COLORS["subtle"], wraplength=300, justify="left").pack(anchor="w", pady=(4, 0))

        actions = tk.Frame(footer, bg=COLORS["surface"])
        actions.pack(side=tk.RIGHT)

        def restart_from_dialog() -> None:
            self._close_result_dialog()
            self.restart()

        def lobby_from_dialog() -> None:
            self._close_result_dialog()
            self._back()

        def records_from_dialog() -> None:
            self._close_result_dialog()
            self._stop_timer()
            self._unbind_shortcuts()
            if self.on_ranking is not None:
                self.on_ranking()
            else:
                self.on_back()

        CyberButton(actions, text=t("btn_restart"), command=restart_from_dialog, size="large").pack(side=tk.LEFT, padx=(0, 6))
        CyberButton(actions, text=t("btn_lobby"), variant="secondary", command=lobby_from_dialog).pack(side=tk.LEFT, padx=(0, 6))
        CyberButton(actions, text=t("btn_result_records"), variant="secondary", command=records_from_dialog).pack(side=tk.LEFT)
    def _on_win(self):
        save_ranking(self.user["id"], self.difficulty, self.timer_seconds)
        save_match_result(self.user["id"], self.difficulty, "win", self.timer_seconds)
        self._show_result_panel("win")
        threading.Thread(
            target=_github_append_ranking,
            args=(self.user["username"], self.difficulty, self.timer_seconds),
            daemon=True,
        ).start()

    def _back(self):
        self._close_result_dialog()
        self._stop_timer()
        self._unbind_shortcuts()
        self.on_back()

    def restart(self):
        self._close_result_dialog()
        self._stop_timer()
        self.timer_seconds = 0
        self.timer_label.configure(text="00:00")
        self.game = MinesweeperGame(self.difficulty)
        self._gradient = random.choice(BOARD_GRADIENTS)
        self._tile_fills = self._build_tile_fills()
        self._wrong_flags = set()
        self._full_redraw()
        self._update_mine_label()
        self._update_progress_label()
        self._update_status()

    def _bind_shortcuts(self):
        root = self.winfo_toplevel()
        root.bind("r", self._restart_shortcut)
        root.bind("R", self._restart_shortcut)

    def _unbind_shortcuts(self):
        root = self.winfo_toplevel()
        root.unbind("r")
        root.unbind("R")

    def _restart_shortcut(self, _event=None):
        self.restart()

    def destroy(self):
        self._close_result_dialog()
        self._stop_timer()
        if self._fit_after_id is not None:
            try:
                self.after_cancel(self._fit_after_id)
            except tk.TclError:
                pass
            self._fit_after_id = None
        self._unbind_shortcuts()
        super().destroy()
