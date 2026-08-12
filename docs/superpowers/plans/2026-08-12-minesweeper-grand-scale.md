# Minesweeper Grand Scale Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Minesweeper client feel larger, more cinematic, and more like a serious competitive desktop game.

**Architecture:** Keep Tkinter, SQLite, and the existing app split. Add shared layout-scale helpers first, then apply them to the lobby, game frame, ranking view, and player profile without changing Minesweeper rules.

**Tech Stack:** Python, Tkinter, ttk, SQLite, unittest.

## Global Constraints

- Keep the core Minesweeper rules stable.
- Do not add new UI frameworks or runtime dependencies.
- Keep the dark cyberpunk visual language: hard edges, neon accents, readable data.
- Use real player data for summaries; do not invent decorative metrics.
- Preserve keyboard flows: Escape returns/closes, R restarts in-game.

---

### Task 1: Shared Scale Tokens

**Files:**
- Modify: `ui_theme.py`
- Test: `test_lang_theme.py`

**Interfaces:**
- Consumes: existing `COLORS`, `FONT`, `FONT_MONO`, `CyberButton`, `make_panel`, `metric_label`
- Produces: `LAYOUT`, `section_title(parent, kicker, title, subtitle, accent=None)`

- [ ] Add a `LAYOUT` dict with window sizes for auth, lobby, game modes, ranking, and profile.
- [ ] Add `section_title` for large cyber section headers.
- [ ] Extend theme tests to assert `LAYOUT` and `section_title`.

### Task 2: Lobby As Grand Command Deck

**Files:**
- Modify: `main.py`
- Modify: `lang.py`
- Test: `test_main_flow.py`

**Interfaces:**
- Consumes: `LAYOUT`, `section_title`, `metric_label`, `get_user_profile_summary`
- Produces: larger lobby shell, wider difficulty modules, profile summary strip

- [ ] Increase default lobby window and minimum sizes.
- [ ] Add a wide command deck body with left identity panel, center difficulty modules, and right readiness/status panel.
- [ ] Make difficulty cards taller and more commanding.
- [ ] Add tests that lobby geometry is large and profile entry still opens.

### Task 3: Larger Game, Ranking, And Profile Surfaces

**Files:**
- Modify: `game.py`
- Modify: `ranking.py`
- Modify: `main.py`
- Test: `test_main_flow.py`

**Interfaces:**
- Consumes: shared `LAYOUT` values and existing view callbacks
- Produces: larger in-game windows, broader ranking header/table, wider profile dialog

- [ ] Increase game window sizes per difficulty while keeping large boards scrollable.
- [ ] Increase ranking default window and header scale.
- [ ] Increase profile dialog size and spacing so it reads as a proper player center.
- [ ] Add smoke tests for profile and ranking creation.

### Task 4: Verification And Commit

**Files:**
- Test: all unittest files

- [ ] Run `python -m unittest discover -v`.
- [ ] Run `python -m py_compile auth.py database.py game.py lang.py main.py ranking.py ui_theme.py`.
- [ ] Run `python -c "from main import MainApp; app = MainApp(start_loop=False); app.root.update(); app.root.destroy()"`.
- [ ] Commit the plan and implementation.
