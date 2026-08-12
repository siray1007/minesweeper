"""Minesweeper rules and the responsive Tk game screen."""
from __future__ import annotations

import os
import random
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from database import _gitee_append_ranking, save_ranking
from lang import t
from ui_theme import COLORS, FONT, LAYOUT, configure_ttk, load_photo, metric_label, set_window_geometry


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_BOMB_PNG = os.path.join(_BASE_DIR, 'bomb16.png')

NUM_COLORS = {
    1: '#7cc7ff',
    2: '#67d39b',
    3: '#ff7b7b',
    4: '#c59bff',
    5: '#ffc26b',
    6: '#63d9dd',
    7: '#e6ecf7',
    8: '#a9b6c9',
}

BOARD_COLORS = {
    'closed': '#102235',
    'closed_alt': '#132940',
    'open': '#09121f',
    'grid': '#203a54',
    'grid_major': '#2b5872',
    'flag': '#123a43',
    'hover': '#34d5ff',
}

DIFFICULTY_CONFIG = {
    '9x9': {'rows': 9, 'cols': 9, 'mines': 10, 'cell': 56, 'title_key': 'easy_title'},
    '27x27': {'rows': 27, 'cols': 27, 'mines': 100, 'cell': 24, 'title_key': 'medium_title'},
    '81x81': {'rows': 81, 'cols': 81, 'mines': 800, 'cell': 16, 'title_key': 'hard_title'},
}


def calculate_fit_zoom(view_width: int, view_height: int, rows: int, cols: int,
                       cell_size: int) -> float:
    """Return a supported zoom that fits the whole board in the viewport."""
    if min(view_width, view_height, rows, cols, cell_size) <= 0:
        return 1.0
    zoom = min(view_width / (cols * cell_size), view_height / (rows * cell_size))
    return round(max(0.25, min(3.0, zoom)), 2)


class MinesweeperGame:
    """Pure game state and rules; no Tk dependencies."""

    def __init__(self, difficulty: str, rng=None):
        if difficulty not in DIFFICULTY_CONFIG:
            raise ValueError(f'Unknown difficulty: {difficulty!r}')
        config = DIFFICULTY_CONFIG[difficulty]
        self.difficulty = difficulty
        self._rng = rng or random
        self.rows = config['rows']
        self.cols = config['cols']
        self.total_mines = config['mines']
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
            raise ValueError('Safe cell is outside the board')
        safe = {(safe_row, safe_col)}
        if self.rows * self.cols > self.total_mines + 9:
            safe.update(self._neighbors(safe_row, safe_col))
        candidates = [
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if (row, col) not in safe
        ]
        self.mine_positions = set(self._rng.sample(candidates, min(self.total_mines, len(candidates))))
        for row, col in self.mine_positions:
            self.board[row][col] = -1
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1:
                    self.board[row][col] = sum(
                        self.board[nr][nc] == -1 for nr, nc in self._neighbors(row, col)
                    )
        self.mines_generated = True

    def reveal(self, row: int, col: int) -> str:
        if self.game_over or self.game_won:
            return 'continue'
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return 'continue'
        if self.revealed[row][col] or self.flagged[row][col]:
            return 'continue'
        if self.first_click:
            self.generate_mines(row, col)
            self.first_click = False
        if self.board[row][col] == -1:
            self.game_over = True
            self.revealed[row][col] = True
            return 'game_over'
        self._flood_fill(row, col)
        if self.revealed_count >= self.total_safe_cells:
            self.game_won = True
            return 'win'
        return 'continue'

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
            return 'continue'
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return 'continue'
        if not self.revealed[row][col] or self.board[row][col] <= 0:
            return 'continue'
        flag_count = sum(self.flagged[nr][nc] for nr, nc in self._neighbors(row, col))
        if flag_count != self.board[row][col]:
            return 'continue'
        result = 'continue'
        for nr, nc in self._neighbors(row, col):
            if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                current = self.reveal(nr, nc)
                if current == 'game_over':
                    result = current
                elif current == 'win' and result != 'game_over':
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
    def __init__(self, parent, user: dict, difficulty: str, on_back):
        super().__init__(parent, bg=COLORS['bg'])
        configure_ttk(parent)
        self.user = user
        self.difficulty = difficulty
        self.on_back = on_back
        self.cfg = DIFFICULTY_CONFIG[difficulty]
        self.difficulty_title = t(self.cfg['title_key'])
        self.game = MinesweeperGame(difficulty)
        self.cell_size = self.cfg['cell']
        self.timer_running = False
        self.timer_seconds = 0
        self._after_id = None
        self._fit_after_id = None
        self.zoom = 1.0
        self._hover_cell = None
        self._auto_fit_pending = difficulty == '81x81'
        self._build_ui()
        self._apply_window_size()

    @staticmethod
    def _closed_color(row: int, col: int) -> str:
        return BOARD_COLORS['closed_alt'] if (row + col) % 2 else BOARD_COLORS['closed']

    def _apply_window_size(self) -> None:
        root = self.winfo_toplevel()
        if self.difficulty == '81x81':
            width, height, min_width, min_height = LAYOUT['game_hard']['window']
        elif self.difficulty == '27x27':
            width, height, min_width, min_height = LAYOUT['game_medium']['window']
        else:
            width, height, min_width, min_height = LAYOUT['game_easy']['window']
        set_window_geometry(root, width, height, min_width, min_height)
        root.title(f"{t('title')} · {self.difficulty_title} · {self.user['username']}")

    def _build_ui(self) -> None:
        bar = tk.Frame(self, bg=COLORS['surface'], height=78)
        bar.pack(fill=tk.X, padx=12, pady=(12, 0))
        bar.pack_propagate(False)
        ttk.Button(bar, text=t('btn_back'), style='Ghost.TButton', command=self._back).pack(
            side=tk.LEFT, padx=8, pady=12)
        image = load_photo(_BOMB_PNG, master=self)
        if image is not None:
            self._bomb_image = image
            tk.Label(bar, image=image, bg=COLORS['surface']).pack(side=tk.LEFT, padx=(10, 6))
        mine_box = metric_label(bar, t('mines'), f'{self.game.remaining_mines:02d}', bg=COLORS['surface'], accent=COLORS['text'])
        mine_box.pack(side=tk.LEFT, padx=(8, 18), pady=10)
        tk.Label(
            bar,
            text=self.difficulty_title,
            font=(FONT, 15, 'bold'),
            bg=COLORS['surface'],
            fg=COLORS['text'],
        ).pack(side=tk.LEFT, expand=True)
        timer_box = metric_label(bar, 'TIME', '00:00', bg=COLORS['surface'], accent=COLORS['text'])
        timer_box.pack(side=tk.RIGHT, padx=14, pady=10)
        self.timer_label = timer_box.winfo_children()[1]
        self.mine_label = mine_box.winfo_children()[1]
        self._update_mine_label()
        if self.difficulty == '81x81':
            self._build_large_board()
        else:
            self._build_small_board()
        bottom = tk.Frame(self, bg=COLORS['bg'])
        bottom.pack(fill=tk.X, padx=20, pady=(0, 16))
        ttk.Button(bottom, text=t('btn_restart'), style='Secondary.TButton', command=self.restart).pack(side=tk.LEFT, padx=5)
        tk.Label(
            bottom,
            text=t('game_hint'),
            font=(FONT, 9),
            bg=COLORS['bg'],
            fg=COLORS['subtle'],
        ).pack(side=tk.RIGHT, padx=6)

    def _bind_canvas(self, canvas):
        canvas.bind('<Button-1>', self._left_click)
        canvas.bind('<Double-Button-1>', self._double_click)
        canvas.bind('<Button-3>', self._right_click)
        canvas.bind('<Button-2>', self._right_click)
        canvas.bind('<Motion>', self._hover_move)
        canvas.bind('<Leave>', self._hover_leave)

    def _build_small_board(self) -> None:
        width = self.cfg['cols'] * self.cell_size
        height = self.cfg['rows'] * self.cell_size
        shell = tk.Frame(
            self,
            bg=COLORS['primary'],
            highlightthickness=1,
            highlightbackground=BOARD_COLORS['grid_major'],
        )
        shell.pack(padx=20, pady=20, expand=True)
        self.canvas = tk.Canvas(
            shell,
            width=width,
            height=height,
            bg=COLORS['input'],
            highlightthickness=0,
            cursor='crosshair',
        )
        self.canvas.pack(padx=2, pady=2)
        self._bind_canvas(self.canvas)
        self._draw_small()

    def _draw_small(self) -> None:
        self.canvas.delete('all')
        size = self.cell_size
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                x1, y1 = col * size, row * size
                x2, y2 = x1 + size, y1 + size
                center_x, center_y = x1 + size // 2, y1 + size // 2
                if self.game.revealed[row][col]:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=BOARD_COLORS['open'], outline=BOARD_COLORS['grid'],
                    )
                    value = self.game.board[row][col]
                    if value == -1:
                        self.canvas.create_text(center_x, center_y, text='✖', font=('Arial', size // 2), fill=COLORS['danger'])
                    elif value > 0:
                        self.canvas.create_text(center_x, center_y, text=str(value), font=('Arial', size // 2, 'bold'), fill=NUM_COLORS.get(value, COLORS['text']))
                elif self.game.flagged[row][col]:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=BOARD_COLORS['flag'], outline=COLORS['warning'], width=2,
                    )
                    self.canvas.create_text(center_x, center_y, text='⚑', font=('Arial', size // 2), fill=COLORS['warning'])
                else:
                    outline = BOARD_COLORS['grid_major'] if row % 3 == 0 and col % 3 == 0 else BOARD_COLORS['grid']
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self._closed_color(row, col), outline=outline,
                    )

    def _build_large_board(self) -> None:
        outer = tk.Frame(
            self,
            bg=COLORS['surface'],
            highlightthickness=1,
            highlightbackground=BOARD_COLORS['grid_major'],
        )
        outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)
        self.scroll_canvas = tk.Canvas(outer, width=980, height=680, bg=COLORS['input'], highlightthickness=0)
        self.h_bar = ttk.Scrollbar(outer, orient=tk.HORIZONTAL, command=self.scroll_canvas.xview)
        self.v_bar = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(xscrollcommand=self.h_bar.set, yscrollcommand=self.v_bar.set)
        self.scroll_canvas.bind('<Configure>', self._viewport_resized)
        self.scroll_canvas.grid(row=0, column=0, sticky='nsew')
        self.h_bar.grid(row=1, column=0, sticky='ew')
        self.v_bar.grid(row=0, column=1, sticky='ns')
        self.canvas = tk.Canvas(self.scroll_canvas, bg=COLORS['input'], highlightthickness=0)
        self._canvas_window = self.scroll_canvas.create_window(
            0, 0, window=self.canvas, anchor='nw',
        )
        self._bind_canvas(self.canvas)
        zoom_bar = tk.Frame(self, bg=COLORS['bg'])
        zoom_bar.pack(fill=tk.X, padx=20, pady=(0, 8))
        ttk.Button(zoom_bar, text='-', style='Secondary.TButton', command=self._zoom_out, width=4).pack(side=tk.LEFT, padx=2)
        self.zoom_label = tk.Label(zoom_bar, text='100%', font=(FONT, 9, 'bold'), bg=COLORS['bg'], fg=COLORS['muted'], width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=4)
        ttk.Button(zoom_bar, text='+', style='Secondary.TButton', command=self._zoom_in, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_bar, text=t('zoom_fit'), style='Ghost.TButton', command=self._zoom_reset).pack(side=tk.LEFT, padx=10)
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self._draw_large()

    def _draw_large(self) -> None:
        self.canvas.delete('all')
        size = max(4.0, self.cell_size * self.zoom)
        self._actual_cs = size
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                x1, y1 = col * size + 1, row * size + 1
                x2, y2 = x1 + size - 2, y1 + size - 2
                center_x, center_y = x1 + max(size - 2, 0) // 2, y1 + max(size - 2, 0) // 2
                if self.game.revealed[row][col]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=BOARD_COLORS['open'], outline='')
                    value = self.game.board[row][col]
                    if value == -1 and size >= 10:
                        self.canvas.create_text(center_x, center_y, text='✖', font=('Arial', max(8, int(size // 2))), fill=COLORS['danger'])
                    elif value > 0 and size >= 10:
                        self.canvas.create_text(center_x, center_y, text=str(value), font=('Arial', max(8, int(size // 2)), 'bold'), fill=NUM_COLORS.get(value, COLORS['text']))
                elif self.game.flagged[row][col]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=BOARD_COLORS['flag'], outline=COLORS['warning'])
                    if size >= 12:
                        self.canvas.create_text(center_x, center_y, text='⚑', font=('Arial', max(8, int(size // 2))), fill=COLORS['warning'])
                else:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self._closed_color(row, col), outline='',
                    )
        width, height = self.game.cols * size, self.game.rows * size
        canvas_width, canvas_height = int(round(width)), int(round(height))
        self.canvas.configure(width=canvas_width, height=canvas_height)
        viewport_width = max(1, self.scroll_canvas.winfo_width())
        viewport_height = max(1, self.scroll_canvas.winfo_height())
        origin_x = max(0, (viewport_width - canvas_width) // 2)
        origin_y = max(0, (viewport_height - canvas_height) // 2)
        self.scroll_canvas.coords(self._canvas_window, origin_x, origin_y)
        self.scroll_canvas.configure(scrollregion=(
            0, 0, max(viewport_width, canvas_width), max(viewport_height, canvas_height),
        ))

    def _zoom_in(self):
        self.zoom = min(3.0, self.zoom + 0.25)
        self.zoom_label.configure(text=f'{int(self.zoom * 100)}%')
        self._draw_large()

    def _zoom_out(self):
        self.zoom = max(0.25, self.zoom - 0.25)
        self.zoom_label.configure(text=f'{int(self.zoom * 100)}%')
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
        )
        self.zoom_label.configure(text=f'{int(self.zoom * 100)}%')
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

    def _hover_move(self, event):
        row, col = self._get_cell(event.x, event.y)
        cell = None if row is None else (row, col)
        if cell == self._hover_cell:
            return
        self._hover_cell = cell
        self.canvas.delete('hover')
        if cell is None or self.game.game_over or self.game.game_won:
            return
        size = getattr(self, '_actual_cs', self.cell_size)
        x1, y1 = col * size + 1, row * size + 1
        x2, y2 = x1 + size - 2, y1 + size - 2
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=BOARD_COLORS['hover'], width=2, tags='hover',
        )

    def _hover_leave(self, _event=None):
        self._hover_cell = None
        self.canvas.delete('hover')

    def _on_mousewheel(self, event):
        if event.state & 0x4:
            self._zoom_in() if event.delta > 0 else self._zoom_out()
        else:
            self.scroll_canvas.yview_scroll(-1 * (event.delta // 120), 'units')

    def _get_cell(self, x: int, y: int):
        size = getattr(self, '_actual_cs', self.cell_size)
        row, col = int(y // size), int(x // size)
        return (row, col) if 0 <= row < self.game.rows and 0 <= col < self.game.cols else (None, None)

    def _handle_result(self, result: str) -> None:
        self._redraw()
        self._update_mine_label()
        if result == 'game_over':
            self._stop_timer()
            self._reveal_all_mines()
            self.after(180, lambda: messagebox.showinfo(t('game_over'), t('game_over_msg'), parent=self))
        elif result == 'win':
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
        self._handle_result(self.game.reveal(row, col))

    def _right_click(self, event):
        if self.game.game_over or self.game.game_won:
            return
        row, col = self._get_cell(event.x, event.y)
        if row is None:
            return
        if not self.timer_running:
            self._start_timer()
        self.game.toggle_flag(row, col)
        self._redraw()
        self._update_mine_label()

    def _double_click(self, event):
        if self.game.game_over or self.game.game_won:
            return
        row, col = self._get_cell(event.x, event.y)
        if row is None or not self.game.revealed[row][col]:
            return
        self._handle_result(self.game.chord(row, col))

    def _redraw(self):
        self._draw_large() if self.difficulty == '81x81' else self._draw_small()

    def _start_timer(self):
        self.timer_running = True
        self.timer_seconds = 0
        self.timer_label.configure(text='00:00')
        self._after_id = self.after(1000, self._tick)

    def _tick(self):
        if not self.timer_running:
            return
        self.timer_seconds += 1
        minutes, seconds = divmod(self.timer_seconds, 60)
        self.timer_label.configure(text=f'{minutes:02d}:{seconds:02d}')
        self._after_id = self.after(1000, self._tick)

    def _stop_timer(self):
        self.timer_running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _update_mine_label(self):
        self.mine_label.configure(text=f'{self.game.remaining_mines:02d}')

    def _reveal_all_mines(self):
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.board[row][col] == -1 and not self.game.flagged[row][col]:
                    self.game.revealed[row][col] = True
        self._redraw()

    def _on_win(self):
        save_ranking(self.user['id'], self.difficulty, self.timer_seconds)
        minutes, seconds = divmod(self.timer_seconds, 60)
        messagebox.showinfo(t('win_title'), t('win_msg', self.difficulty_title, f'{minutes:02d}:{seconds:02d}'), parent=self)
        threading.Thread(target=_gitee_append_ranking, args=(self.user['username'], self.difficulty, self.timer_seconds), daemon=True).start()

    def _back(self):
        self._stop_timer()
        if self._fit_after_id is not None:
            self.after_cancel(self._fit_after_id)
            self._fit_after_id = None
        self.on_back()

    def destroy(self):
        self._stop_timer()
        if self._fit_after_id is not None:
            try:
                self.after_cancel(self._fit_after_id)
            except tk.TclError:
                pass
            self._fit_after_id = None
        super().destroy()

    def restart(self):
        self._stop_timer()
        self.timer_seconds = 0
        self.timer_label.configure(text='00:00')
        self.game = MinesweeperGame(self.difficulty)
        self._hover_cell = None
        self._redraw()
        self._update_mine_label()
