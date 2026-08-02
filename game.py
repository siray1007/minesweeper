"""Minesweeper rules and the responsive Tk game screen."""
from __future__ import annotations

import colorsys
import os
import random
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from database import _gitee_append_ranking, save_ranking
from lang import t
from ui_theme import COLORS, FONT, configure_ttk, load_photo, set_window_geometry


_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_BOMB_PNG = os.path.join(_BASE_DIR, 'bomb16.png')

NUM_COLORS = {
    1: '#7cc7ff', 2: '#67d39b', 3: '#ff7b7b', 4: '#c59bff',
    5: '#ffc26b', 6: '#63d9dd', 7: '#e6ecf7', 8: '#a9b6c9',
}

DIFFICULTY_CONFIG = {
    '9x9': {'rows': 9, 'cols': 9, 'mines': 10, 'cell': 48, 'title': '简单 9×9'},
    '27x27': {'rows': 27, 'cols': 27, 'mines': 100, 'cell': 20, 'title': '进阶 27×27'},
    '81x81': {'rows': 81, 'cols': 81, 'mines': 800, 'cell': 14, 'title': '困难 81×81'},
}


def _pastel_pair() -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    colors = []
    for _ in range(2):
        hue = random.random()
        red, green, blue = colorsys.hsv_to_rgb(hue, 0.30, 0.88)
        colors.append((int(red * 255), int(green * 255), int(blue * 255)))
    return colors[0], colors[1]


def _mix(c1, c2, ratio: float) -> str:
    ratio = max(0.0, min(1.0, ratio))
    channels = [int(a + (b - a) * ratio) for a, b in zip(c1, c2)]
    return '#{:02x}{:02x}{:02x}'.format(*channels)


def _lighten(color: str, amount: float) -> str:
    rgb = [int(color[offset:offset + 2], 16) for offset in (1, 3, 5)]
    rgb = [min(255, int(channel + 255 * amount)) for channel in rgb]
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


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
        self.game = MinesweeperGame(difficulty)
        self.cell_size = self.cfg['cell']
        self.timer_running = False
        self.timer_seconds = 0
        self._after_id = None
        self.zoom = 1.0
        self._gradient_start, self._gradient_end = _pastel_pair()
        self._gradient_max = max(self.cfg['rows'] + self.cfg['cols'] - 2, 1)
        self._build_ui()
        self._apply_window_size()

    def _gradient(self, row: int, col: int) -> str:
        return _mix(self._gradient_start, self._gradient_end, (row + col) / self._gradient_max)

    def _apply_window_size(self) -> None:
        root = self.winfo_toplevel()
        if self.difficulty == '81x81':
            set_window_geometry(root, 1040, 760, 760, 560)
        elif self.difficulty == '27x27':
            set_window_geometry(root, 760, 760, 620, 620)
        else:
            set_window_geometry(root, 620, 700, 520, 580)
        root.title(f"{t('title')} · {self.cfg['title']} · {self.user['username']}")

    def _build_ui(self) -> None:
        bar = tk.Frame(self, bg=COLORS['surface'], height=64)
        bar.pack(fill=tk.X, padx=12, pady=(12, 0))
        bar.pack_propagate(False)
        ttk.Button(bar, text=t('btn_back'), style='Ghost.TButton', command=self._back).pack(
            side=tk.LEFT, padx=8, pady=10)
        image = load_photo(_BOMB_PNG, master=self)
        if image is not None:
            self._bomb_image = image
            tk.Label(bar, image=image, bg=COLORS['surface']).pack(side=tk.LEFT, padx=(10, 5))
        mine_box = tk.Frame(bar, bg=COLORS['surface'])
        mine_box.pack(side=tk.LEFT, pady=8)
        tk.Label(mine_box, text=t('mines'), font=(FONT, 8), bg=COLORS['surface'], fg=COLORS['subtle']).pack(anchor='w')
        self.mine_label = tk.Label(mine_box, font=('Consolas', 15, 'bold'), bg=COLORS['surface'], fg=COLORS['text'])
        self.mine_label.pack(anchor='w')
        tk.Label(bar, text=self.cfg['title'], font=(FONT, 12, 'bold'), bg=COLORS['surface'], fg=COLORS['text']).pack(side=tk.LEFT, expand=True)
        timer_box = tk.Frame(bar, bg=COLORS['surface'])
        timer_box.pack(side=tk.RIGHT, padx=14, pady=8)
        tk.Label(timer_box, text='TIME', font=(FONT, 8), bg=COLORS['surface'], fg=COLORS['subtle']).pack(anchor='e')
        self.timer_label = tk.Label(timer_box, text='00:00', font=('Consolas', 15, 'bold'), bg=COLORS['surface'], fg=COLORS['text'])
        self.timer_label.pack(anchor='e')
        self._update_mine_label()
        if self.difficulty == '81x81':
            self._build_large_board()
        else:
            self._build_small_board()
        bottom = tk.Frame(self, bg=COLORS['bg'])
        bottom.pack(fill=tk.X, padx=20, pady=(0, 14))
        ttk.Button(bottom, text=t('btn_restart'), style='Secondary.TButton', command=self.restart).pack(side=tk.LEFT, padx=5)
        tk.Label(bottom, text='左键翻开 · 右键标记 · 双击数字格快速展开', font=(FONT, 9), bg=COLORS['bg'], fg=COLORS['subtle']).pack(side=tk.RIGHT, padx=6)

    def _bind_canvas(self, canvas):
        canvas.bind('<Button-1>', self._left_click)
        canvas.bind('<Double-Button-1>', self._double_click)
        canvas.bind('<Button-3>', self._right_click)
        canvas.bind('<Button-2>', self._right_click)

    def _build_small_board(self) -> None:
        width = self.cfg['cols'] * self.cell_size
        height = self.cfg['rows'] * self.cell_size
        self.canvas = tk.Canvas(self, width=width, height=height, bg=COLORS['input'], highlightthickness=0, cursor='crosshair')
        self.canvas.pack(padx=20, pady=20, expand=True)
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
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS['surface_alt'], outline=COLORS['border'])
                    value = self.game.board[row][col]
                    if value == -1:
                        self.canvas.create_text(center_x, center_y, text='✹', font=('Arial', size // 2), fill=COLORS['danger'])
                    elif value > 0:
                        self.canvas.create_text(center_x, center_y, text=str(value), font=('Arial', size // 2, 'bold'), fill=NUM_COLORS.get(value, COLORS['text']))
                elif self.game.flagged[row][col]:
                    color = self._gradient(row, col)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=COLORS['border'])
                    self.canvas.create_text(center_x, center_y, text='⚑', font=('Arial', size // 2), fill=COLORS['danger'])
                else:
                    color = self._gradient(row, col)
                    if (row + col) % 2:
                        color = _lighten(color, 0.06)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=COLORS['border'])

    def _build_large_board(self) -> None:
        outer = tk.Frame(self, bg=COLORS['surface'])
        outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)
        self.scroll_canvas = tk.Canvas(outer, width=780, height=560, bg=COLORS['input'], highlightthickness=0)
        self.h_bar = ttk.Scrollbar(outer, orient=tk.HORIZONTAL, command=self.scroll_canvas.xview)
        self.v_bar = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(xscrollcommand=self.h_bar.set, yscrollcommand=self.v_bar.set)
        self.scroll_canvas.grid(row=0, column=0, sticky='nsew')
        self.h_bar.grid(row=1, column=0, sticky='ew')
        self.v_bar.grid(row=0, column=1, sticky='ns')
        self.canvas = tk.Canvas(self.scroll_canvas, bg=COLORS['input'], highlightthickness=0)
        self.scroll_canvas.create_window(0, 0, window=self.canvas, anchor='nw')
        self._bind_canvas(self.canvas)
        zoom_bar = tk.Frame(self, bg=COLORS['bg'])
        zoom_bar.pack(fill=tk.X, padx=20, pady=(0, 8))
        ttk.Button(zoom_bar, text='−', style='Secondary.TButton', command=self._zoom_out, width=4).pack(side=tk.LEFT, padx=2)
        self.zoom_label = tk.Label(zoom_bar, text='100%', font=(FONT, 9, 'bold'), bg=COLORS['bg'], fg=COLORS['muted'], width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=4)
        ttk.Button(zoom_bar, text='+', style='Secondary.TButton', command=self._zoom_in, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_bar, text='适应窗口', style='Ghost.TButton', command=self._zoom_reset).pack(side=tk.LEFT, padx=10)
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self._draw_large()

    def _draw_large(self) -> None:
        self.canvas.delete('all')
        size = max(2, int(self.cell_size * self.zoom))
        self._actual_cs = size
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                x1, y1 = col * size + 1, row * size + 1
                x2, y2 = x1 + size - 2, y1 + size - 2
                center_x, center_y = x1 + max(size - 2, 0) // 2, y1 + max(size - 2, 0) // 2
                if self.game.revealed[row][col]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS['surface_alt'], outline='')
                    value = self.game.board[row][col]
                    if value == -1 and size >= 10:
                        self.canvas.create_text(center_x, center_y, text='✹', font=('Arial', max(8, size // 2)), fill=COLORS['danger'])
                    elif value > 0 and size >= 10:
                        self.canvas.create_text(center_x, center_y, text=str(value), font=('Arial', max(8, size // 2), 'bold'), fill=NUM_COLORS.get(value, COLORS['text']))
                elif self.game.flagged[row][col]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=self._gradient(row, col), outline='')
                    if size >= 12:
                        self.canvas.create_text(center_x, center_y, text='⚑', font=('Arial', max(8, size // 2)), fill=COLORS['danger'])
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=self._gradient(row, col), outline='')
        width, height = self.game.cols * size, self.game.rows * size
        self.canvas.configure(width=width, height=height)
        self.scroll_canvas.configure(scrollregion=(0, 0, width, height))

    def _zoom_in(self):
        self.zoom = min(3.0, self.zoom + 0.25)
        self.zoom_label.configure(text=f'{int(self.zoom * 100)}%')
        self._draw_large()

    def _zoom_out(self):
        self.zoom = max(0.25, self.zoom - 0.25)
        self.zoom_label.configure(text=f'{int(self.zoom * 100)}%')
        self._draw_large()

    def _zoom_reset(self):
        self.zoom = 1.0
        self.zoom_label.configure(text='100%')
        self._draw_large()

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
        messagebox.showinfo(t('win_title'), t('win_msg', self.cfg['title'], f'{minutes:02d}:{seconds:02d}'), parent=self)
        threading.Thread(target=_gitee_append_ranking, args=(self.user['username'], self.difficulty, self.timer_seconds), daemon=True).start()

    def _back(self):
        self._stop_timer()
        self.on_back()

    def restart(self):
        self._stop_timer()
        self.timer_seconds = 0
        self.timer_label.configure(text='00:00')
        self.game = MinesweeperGame(self.difficulty)
        self._gradient_start, self._gradient_end = _pastel_pair()
        self._redraw()
        self._update_mine_label()
