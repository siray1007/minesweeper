# 扫雷重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把当前偏儿童化且乱码严重的扫雷项目重构成一款深色、硬朗、带赛博朋克气质的桌面客户端，同时保留扫雷、登录、排行榜和语言切换的完整可用性。

**Architecture:** 保留 Tkinter 和 SQLite，把规则层、主题层、语言层、存储层和视图层拆开。先修复资源和文案，再统一视觉系统，随后分视图重做布局，最后收口测试与清理。

**Tech Stack:** Python 3, Tkinter, SQLite, urllib, unittest

## Global Constraints

- 不更换技术栈，仍然使用 Tkinter
- 不把项目改成网页或 3D 游戏
- 不新增复杂社交、商店、任务系统
- 不重写扫雷规则，只做界面与结构升级
- 所有文案、图标与资源读取保持 UTF-8
- 默认深色，强调色少而准，不使用大面积糖果感配色

---

### Task 1: Repair text resources and resource naming

**Files:**
- Modify: `lang.py`
- Modify: `main.py`
- Modify: `auth.py`
- Modify: `game.py`
- Modify: `ranking.py`
- Modify: `README.md`
- Modify: `README-使用说明.md`
- Modify: `README-优化说明.md`

**Interfaces:**
- Consumes: existing `t(key, *args)`, `LANG_OPTIONS`, `get_lang()`, `save_lang()`
- Produces: clean UTF-8 language tables, stable keys for all visible text, valid icon/resource paths

- [ ] **Step 1: Write a failing regression test for language keys**

```python
from lang import TEXTS

def test_core_language_keys_exist():
    required = {
        "title", "login", "register", "menu_title", "rank_title",
        "btn_start", "btn_restart", "btn_ranking", "btn_logout",
    }
    for lang, mapping in TEXTS.items():
        assert required.issubset(mapping.keys()), lang
```

- [ ] **Step 2: Run the test to see the current resource damage**

Run: `python -m unittest tests.test_lang_keys -v`
Expected: fail if keys are missing or malformed

- [ ] **Step 3: Rewrite `lang.py` as a clean UTF-8 table**

```python
TEXTS = {
    "zh": {
        "title": "扫雷",
        "login": "登录",
        "register": "注册",
        "menu_title": "选择模式",
        "rank_title": "排行榜",
        "btn_start": "开始游戏",
        "btn_restart": "重新开始",
        "btn_ranking": "排行榜",
        "btn_logout": "退出登录",
    },
    "en": {
        "title": "Minesweeper",
        "login": "Sign In",
        "register": "Sign Up",
        "menu_title": "Select Mode",
        "rank_title": "Leaderboard",
        "btn_start": "Start Game",
        "btn_restart": "Restart",
        "btn_ranking": "Leaderboard",
        "btn_logout": "Logout",
    },
}
```

- [ ] **Step 4: Fix all UI resource references to use the real filenames**

Use the existing `扫雷图标.png`, `扫雷图标.ico`, `bomb32.png`, `bomb24.png`, `bomb16.png`, and remove any string literals that point at broken mojibake names.

- [ ] **Step 5: Run the language test and a quick import check**

Run:
`python -m unittest tests.test_lang_keys -v`
`python -c "import lang, main, auth, game, ranking"`

Expected: pass without Unicode or import errors

### Task 2: Rebuild the theme layer for the cyber look

**Files:**
- Modify: `ui_theme.py`
- Modify: `main.py`
- Modify: `auth.py`
- Modify: `game.py`
- Modify: `ranking.py`

**Interfaces:**
- Consumes: `COLORS`, `FONT`, `configure_ttk()`, `load_photo()`, `make_entry()`, `set_window_geometry()`
- Produces: darker token palette, sharper ttk styles, reusable panel/button/input styles

- [ ] **Step 1: Add a theme snapshot test**

```python
from ui_theme import COLORS

def test_theme_has_core_tokens():
    for key in ["bg", "surface", "surface_alt", "border", "text", "muted", "primary", "danger"]:
        assert key in COLORS
```

- [ ] **Step 2: Replace the palette with a hard-edged cyber palette**

```python
COLORS = {
    "bg": "#070b14",
    "surface": "#0d1320",
    "surface_alt": "#111a2c",
    "surface_hover": "#162238",
    "border": "#22314a",
    "text": "#edf3ff",
    "muted": "#8a97b2",
    "subtle": "#5d687f",
    "primary": "#34d6ff",
    "primary_hover": "#67e3ff",
    "primary_pressed": "#179cc2",
    "success": "#35e0a1",
    "warning": "#ffd166",
    "danger": "#ff5c7a",
    "accent": "#9b6dff",
    "input": "#050812",
}
```

- [ ] **Step 3: Restyle ttk buttons, notebook tabs, treeview, and entries**

Keep flat shapes, subtle borders, small radii, and strong focus states. Avoid friendly pastel surfaces and oversized padding.

- [ ] **Step 4: Run the theme snapshot and import checks**

Run:
`python -m unittest tests.test_theme_tokens -v`
`python -c "from ui_theme import configure_ttk"`

Expected: pass and no Tcl style errors

### Task 3: Rework auth and lobby into a real client shell

**Files:**
- Modify: `auth.py`
- Modify: `main.py`
- Add: `tests/test_auth_layout.py`
- Add: `tests/test_main_shell.py`

**Interfaces:**
- Consumes: `AuthFrame(parent, on_login)`, `MainApp._show_auth()`, `MainApp._show_menu()`
- Produces: compact login/register shell, cyber lobby header, difficulty cards with clear mode entry points

- [ ] **Step 1: Write layout tests for auth and lobby framing**

```python
def test_auth_register_button_stays_inside_card():
    ...

def test_menu_has_three_mode_cards():
    ...
```

- [ ] **Step 2: Run them and confirm the current layout is the thing being fixed**

Run: `python -m unittest tests.test_auth_layout tests.test_main_shell -v`

- [ ] **Step 3: Refactor `AuthFrame` into a compact two-state shell**

Use a left-aligned language switcher, smaller card spacing, sharper buttons, and a more serious header treatment. Keep the login/register flow unchanged.

- [ ] **Step 4: Refactor the main menu into a cyber lobby**

Replace the current playful title block with a status-driven header, turn difficulty cards into mode panels, and remove decorative clutter.

- [ ] **Step 5: Run UI smoke tests**

Run:
`python -m unittest tests.test_auth_layout tests.test_main_shell -v`
`python -c "from main import MainApp; app = MainApp(start_loop=False); app.root.destroy()"`

Expected: pass and render without overlap

### Task 4: Rebuild the game screen and board renderer

**Files:**
- Modify: `game.py`
- Add: `tests/test_game.py`

**Interfaces:**
- Consumes: `MinesweeperGame`, `GameFrame`, `DIFFICULTY_CONFIG`
- Produces: cleaner board rendering, cyber-styled status bar, stable click handling, zoom and scroll behavior for large boards

- [ ] **Step 1: Add or tighten rule tests around the game model**

```python
def test_first_click_safe_zone_is_preserved():
    ...

def test_chord_reveals_when_flags_match():
    ...
```

- [ ] **Step 2: Run the game tests before changing rendering**

Run: `python -m unittest tests.test_game -v`

- [ ] **Step 3: Split the view logic from the render logic inside `GameFrame`**

Keep `MinesweeperGame` untouched except for rule fixes. Move rendering details into dedicated helper methods for the top bar, small board, large board, and status updates.

- [ ] **Step 4: Replace pastel gradients with a hard-edged board palette**

Use dark unrevealed tiles, crisp revealed tiles, stronger number colors, and a restrained highlight for flags and mines. Preserve the existing zoom/scroll mechanics for the big board.

- [ ] **Step 5: Run board interaction smoke checks**

Run:
`python -m unittest tests.test_game -v`
`python -c "from game import GameFrame"`

Expected: pass with no click-coordinate regressions

### Task 5: Make the leaderboard feel like a battle record screen

**Files:**
- Modify: `ranking.py`
- Modify: `database.py`

**Interfaces:**
- Consumes: `get_rankings_local()`, `_gitee_fetch_rankings()`, `save_ranking()`
- Produces: ranked tables with clear local/cloud blending, stable fallback behavior, current-user highlighting

- [ ] **Step 1: Add a leaderboard merge test**

```python
def test_dedup_keeps_best_time_per_user():
    ...
```

- [ ] **Step 2: Run the leaderboard-related tests**

Run: `python -m unittest tests.test_ranking_merge -v`

- [ ] **Step 3: Simplify and harden the ranking merge path**

Keep local records authoritative when cloud data is unavailable. Ensure merges remain sorted by time and the current user remains highlighted.

- [ ] **Step 4: Rework the ranking view into a battle-record panel**

Use the cyber theme tokens, tighten table spacing, make empty states explicit, and keep the local/cloud sync status visible without clutter.

- [ ] **Step 5: Run the ranking smoke test**

Run: `python -m unittest tests.test_ranking_layout -v`

Expected: render cleanly and merge data without exceptions

### Task 6: Clean up documentation and verify the full app

**Files:**
- Modify: `README.md`
- Modify: `README-使用说明.md`
- Modify: `README-优化说明.md`
- Modify: any remaining touched source file if a stale string or path remains

**Interfaces:**
- Consumes: the new app structure and final visible copy
- Produces: accurate docs, no stale screenshots or broken paths, no orphaned mojibake

- [ ] **Step 1: Update the README copy to match the cyber redesign**

Describe the app as a dark cyber-style desktop Minesweeper client with login, modes, leaderboard, and local save support.

- [ ] **Step 2: Search the tree for leftover mojibake and dead resource paths**

Run a mojibake scan across tracked Python and Markdown files.

Expected: only intentional Chinese text remains, no broken encoding artifacts

- [ ] **Step 3: Run the full Python test suite**

Run: `python -m unittest discover -v`

Expected: all tests pass

- [ ] **Step 4: Launch the app and inspect the final layout**

Run:
`python main.py`

Check:
- login card fits the window
- lobby cards do not overlap
- game board renders and responds
- ranking table loads and highlights correctly

- [ ] **Step 5: Commit the completed refactor**

```bash
git add .
git commit -m "refactor: cyber theme minesweeper redesign"
```
