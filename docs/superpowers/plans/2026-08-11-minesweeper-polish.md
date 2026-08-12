# Minesweeper Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for this tightly coupled visual polish pass. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Push the existing Minesweeper redesign from functional to sharply polished, using a cyberpunk visual style.

**Architecture:** Keep Tkinter, SQLite, and the existing view split. Extend shared visual tokens first, then apply them to auth, lobby, ranking, and game rendering without changing game rules.

**Tech Stack:** Python, Tkinter, ttk, SQLite, unittest.

## Global Constraints

- Keep the core Minesweeper rules stable.
- Do not add network, UI framework, or rendering dependencies.
- Keep UTF-8 text resources clean.
- Cyberpunk style should be dark, hard-edged, youthful, and readable.
- Large boards must remain scrollable and performant.

---

### Task 1: Theme Refinement

**Files:**
- Modify: `ui_theme.py`
- Test: `test_lang_theme.py`

**Interfaces:**
- Consumes: existing `COLORS`, `FONT`, `configure_ttk`, `make_entry`, `set_window_geometry`
- Produces: reusable cyber styling helpers and extra tokens

- [x] Add tokens for panel borders, grid lines, glow accents, metal surfaces, and disabled text.
- [x] Add ttk scrollbar and label frame styling.
- [x] Add helpers for compact labels, panel borders, and canvas grid backgrounds.
- [x] Extend theme tests to assert the new tokens and helpers exist.

### Task 2: Shell And Menu Polish

**Files:**
- Modify: `main.py`
- Modify: `auth.py`
- Modify: `lang.py`

**Interfaces:**
- Consumes: theme helpers and localization
- Produces: stronger login and lobby presentation

- [x] Add cyber status marks and system-style copy to the login form.
- [x] Make the lobby header feel like an operation console.
- [x] Make difficulty cards show mode code, board metrics, mine density, and threat labels.
- [x] Keep all visible copy localized.

### Task 3: Game And Ranking Polish

**Files:**
- Modify: `game.py`
- Modify: `ranking.py`
- Modify: `lang.py`
- Test: `test_game.py`

**Interfaces:**
- Consumes: existing rules API and database ranking API
- Produces: stronger board rendering and leaderboard states

- [x] Add board border, sector status text, and compact combat HUD labels.
- [x] Improve hidden, revealed, flagged, mine, and hover/readability states.
- [x] Make leaderboard empty rows and current-player rows more deliberate.
- [x] Add tests for density/risk display helpers and keep existing rule tests passing.

### Task 4: Verification

**Files:**
- Test: all unittest files

- [x] Run `python -m unittest discover -v`.
- [x] Run `python -c "from main import MainApp; app = MainApp(start_loop=False); app.root.destroy()"`.
- [x] Scan for obvious mojibake patterns in tracked Python and Markdown files using Python-level string reads if terminal encoding is unreliable.
