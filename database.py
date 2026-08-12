"""Local SQLite storage and optional GitHub leaderboard sync."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import urllib.request
from datetime import datetime

from lang import t


_SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
_EXECUTABLE_DIR = os.path.dirname(os.path.abspath(sys.executable))
_DATA_ROOT = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or os.path.expanduser("~")
_DATA_DIR = os.path.join(_DATA_ROOT, "CyberMinesweeper")
_DEFAULT_DB_PATH = os.path.join(_DATA_DIR, "minesweeper.db")
DB_PATH = _DEFAULT_DB_PATH

GITHUB_USER = "siray1007"
GITHUB_REPO = "minesweeper"
GITHUB_BRANCH = "main"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/rankings.json"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/rankings.json"
GITHUB_TOKEN = os.getenv("MINESWEEPER_GITHUB_TOKEN", "")
MAX_RANKINGS = 100


def get_db():
    parent = os.path.dirname(os.path.abspath(DB_PATH))
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def migrate_legacy_database(target_path: str, candidates: list[str]) -> str | None:
    """Copy the first existing legacy database when the formal data store is empty."""
    if os.path.exists(target_path):
        return None
    target_abs = os.path.abspath(target_path)
    for candidate in candidates:
        candidate_abs = os.path.abspath(candidate)
        if candidate_abs == target_abs or not os.path.isfile(candidate_abs):
            continue
        os.makedirs(os.path.dirname(target_abs), exist_ok=True)
        try:
            legacy = sqlite3.connect(candidate_abs)
            legacy.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            legacy.close()
        except sqlite3.Error:
            pass
        shutil.copy2(candidate_abs, target_abs)
        return candidate_abs
    return None


def _prepare_database_path() -> None:
    if os.path.abspath(DB_PATH) != os.path.abspath(_DEFAULT_DB_PATH):
        return
    candidates = [
        os.path.join(_SOURCE_DIR, "minesweeper.db"),
        os.path.join(_EXECUTABLE_DIR, "minesweeper.db"),
    ]
    migrate_legacy_database(DB_PATH, candidates)


def init_db():
    _prepare_database_path()
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        difficulty TEXT NOT NULL,
        time_seconds INTEGER NOT NULL,
        completed_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id))"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        difficulty TEXT NOT NULL,
        result TEXT NOT NULL,
        time_seconds INTEGER,
        completed_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id))"""
    )
    c.execute("CREATE INDEX IF NOT EXISTS idx_matches_user_completed ON matches (user_id, completed_at DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_matches_user_difficulty ON matches (user_id, difficulty)")
    conn.commit()
    _seed_match_history(conn)
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username: str, password: str) -> tuple:
    username = username.strip()
    if not username or not password:
        return False, t("warn_empty")
    if len(username) < 2:
        return False, t("user_short")
    if len(password) < 4:
        return False, t("pwd_short")
    conn = get_db()
    c = conn.cursor()
    try:
        pwd_hash = hash_password(password)
        c.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, pwd_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return True, t("reg_ok")
    except sqlite3.IntegrityError:
        return False, t("user_exists")
    finally:
        conn.close()


def login_user(username: str, password: str) -> tuple:
    username = username.strip()
    conn = get_db()
    c = conn.cursor()
    pwd_hash = hash_password(password)
    c.execute(
        "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
        (username, pwd_hash),
    )
    user = c.fetchone()
    if not user:
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        username_exists = c.fetchone() is not None
    else:
        username_exists = True
    conn.close()
    if user:
        return True, dict(user)
    if username_exists:
        return False, t("login_password_wrong")
    return False, t("login_user_missing")


def save_ranking(user_id: int, difficulty: str, time_seconds: int, username: str = ""):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO rankings (user_id, difficulty, time_seconds, completed_at) VALUES (?, ?, ?, ?)",
        (user_id, difficulty, time_seconds, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()
    if username:
        _github_append_ranking(username, difficulty, time_seconds)


def save_match_result(user_id: int, difficulty: str, result: str, time_seconds: int | None = None) -> None:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO matches (user_id, difficulty, result, time_seconds, completed_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, difficulty, result, time_seconds, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_rankings_local(difficulty: str, limit: int = 50) -> list:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """SELECT u.username, r.time_seconds, r.completed_at, r.user_id
        FROM rankings r JOIN users u ON r.user_id = u.id
        WHERE r.difficulty = ? ORDER BY r.time_seconds ASC LIMIT ?""",
        (difficulty, limit),
    )
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results


def get_user_profile_summary(user_id: int) -> dict:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """SELECT
            COUNT(*) AS total_matches,
            COALESCE(SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END), 0) AS wins,
            COALESCE(SUM(CASE WHEN result = 'game_over' THEN 1 ELSE 0 END), 0) AS losses
        FROM matches
        WHERE user_id = ?""",
        (user_id,),
    )
    totals = dict(c.fetchone() or {})

    c.execute(
        """SELECT difficulty, MIN(time_seconds) AS best_seconds
        FROM rankings
        WHERE user_id = ?
        GROUP BY difficulty""",
        (user_id,),
    )
    best_by_difficulty = {}
    for row in c.fetchall():
        row = dict(row)
        best_by_difficulty[row["difficulty"]] = row["best_seconds"]

    c.execute(
        """SELECT difficulty, COUNT(*) AS runs
        FROM matches
        WHERE user_id = ?
        GROUP BY difficulty""",
        (user_id,),
    )
    run_counts = {}
    for row in c.fetchall():
        row = dict(row)
        run_counts[row["difficulty"]] = row["runs"]

    c.execute(
        """SELECT difficulty, result, time_seconds, completed_at
        FROM matches
        WHERE user_id = ?
        ORDER BY completed_at DESC, id DESC
        LIMIT 5""",
        (user_id,),
    )
    recent_matches = [dict(row) for row in c.fetchall()]
    conn.close()

    total_matches = int(totals.get("total_matches") or 0)
    wins = int(totals.get("wins") or 0)
    losses = int(totals.get("losses") or 0)
    win_rate = int(round(wins / total_matches * 100)) if total_matches else 0
    return {
        "total_matches": total_matches,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "best_by_difficulty": best_by_difficulty,
        "run_counts": run_counts,
        "recent_matches": recent_matches,
    }


def _seed_match_history(conn) -> None:
    c = conn.cursor()
    c.execute("SELECT COUNT(*) AS total FROM matches")
    row = c.fetchone()
    if row and int(row["total"] or 0) > 0:
        return
    c.execute("SELECT COUNT(*) AS total FROM rankings")
    row = c.fetchone()
    if not row or int(row["total"] or 0) == 0:
        return
    c.execute(
        """INSERT INTO matches (user_id, difficulty, result, time_seconds, completed_at)
        SELECT user_id, difficulty, 'win', time_seconds, completed_at
        FROM rankings"""
    )
    conn.commit()


def get_rankings(difficulty: str, limit: int = 50) -> list:
    online = fetch_cloud_rankings(difficulty, limit) or []
    local = get_rankings_local(difficulty, limit)
    seen = set()
    merged = []
    for r in online:
        key = (r["username"], r["time_seconds"])
        seen.add(key)
        merged.append(r)
    for r in local:
        key = (r["username"], r["time_seconds"])
        if key not in seen:
            seen.add(key)
            merged.append(r)
    merged.sort(key=lambda x: x.get("time_seconds", 99999))
    return merged[:limit]


def fetch_cloud_rankings(difficulty: str, limit: int) -> list | None:
    try:
        req = urllib.request.Request(
            GITHUB_RAW,
            headers={"Accept": "application/vnd.github.raw+json", "User-Agent": "Minesweeper"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            all_rankings = json.loads(resp.read().decode())
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    filtered = [r for r in all_rankings if r.get("difficulty") == difficulty]
    filtered.sort(key=lambda x: x.get("time_seconds", 99999))
    return filtered[:limit]


def cloud_connection_status() -> dict:
    """Return the leaderboard connection and access mode without exposing the backing sync target."""
    rankings = fetch_cloud_rankings("9x9", MAX_RANKINGS)
    return {
        "connected": rankings is not None,
        "writable": bool(GITHUB_TOKEN),
        "provider": "GITHUB",
    }


def _github_append_ranking(username: str, difficulty: str, time_seconds: int):
    if not GITHUB_TOKEN:
        return
    try:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "User-Agent": "Minesweeper",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        get_url = f"{GITHUB_API}?ref={GITHUB_BRANCH}"
        req = urllib.request.Request(get_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            info = json.loads(resp.read().decode())
        sha = info["sha"]
        content = base64.b64decode(info["content"]).decode()
        rankings = json.loads(content) if content.strip() else []
    except Exception:
        return

    rankings.append(
        {
            "username": username,
            "difficulty": difficulty,
            "time_seconds": time_seconds,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    best = {}
    for r in rankings:
        key = (r["username"], r["difficulty"])
        if key not in best or r["time_seconds"] < best[key]["time_seconds"]:
            best[key] = r
    trimmed = sorted(best.values(), key=lambda x: x.get("time_seconds", 99999))
    trimmed = trimmed[:MAX_RANKINGS]

    new_content = json.dumps(trimmed, ensure_ascii=False, indent=2)
    body = json.dumps(
        {
            "message": f"records: update {username} {difficulty} {time_seconds}s",
            "content": base64.b64encode(new_content.encode()).decode(),
            "sha": sha,
            "branch": GITHUB_BRANCH,
        }
    ).encode()
    try:
        put_req = urllib.request.Request(
            GITHUB_API,
            data=body,
            method="PUT",
            headers={**headers, "Content-Type": "application/json"},
        )
        urllib.request.urlopen(put_req, timeout=10)
    except OSError:
        pass
