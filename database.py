"""Local SQLite storage and optional Gitee leaderboard sync."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import sys
import urllib.request
from datetime import datetime

from lang import t


if getattr(sys, "frozen", False):
    _APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(_APP_DIR, "minesweeper.db")

GITEE_USER = "siray-07"
GITEE_REPO = "minesweeper"
GITEE_API = f"https://gitee.com/api/v5/repos/{GITEE_USER}/{GITEE_REPO}/contents/rankings.json"
GITEE_RAW = f"https://gitee.com/{GITEE_USER}/{GITEE_REPO}/raw/master/rankings.json"
GITEE_TOKEN = os.getenv("MINESWEEPER_GITEE_TOKEN", "")
MAX_RANKINGS = 100


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
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


def get_or_create_local_user(username: str = "CyberPilot") -> dict:
    """Return a local no-password pilot account for quick private play."""
    username = username.strip() or "CyberPilot"
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user:
        conn.close()
        return dict(user)

    pwd_hash = hash_password(f"local::{username}")
    c.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, pwd_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    c.execute("SELECT id, username FROM users WHERE username = ?", (username,))
    created = c.fetchone()
    conn.close()
    return dict(created)


def login_user(username: str, password: str) -> tuple:
    conn = get_db()
    c = conn.cursor()
    pwd_hash = hash_password(password)
    c.execute(
        "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
        (username.strip(), pwd_hash),
    )
    user = c.fetchone()
    conn.close()
    if user:
        return True, dict(user)
    return False, t("login_fail")


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
        _gitee_append_ranking(username, difficulty, time_seconds)


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
    online = _gitee_fetch_rankings(difficulty, limit) or []
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


def _gitee_fetch_rankings(difficulty: str, limit: int) -> list | None:
    try:
        req = urllib.request.Request(GITEE_RAW)
        with urllib.request.urlopen(req, timeout=8) as resp:
            all_rankings = json.loads(resp.read().decode())
    except Exception:
        return None
    filtered = [r for r in all_rankings if r.get("difficulty") == difficulty]
    filtered.sort(key=lambda x: x.get("time_seconds", 99999))
    return filtered[:limit]


def _gitee_append_ranking(username: str, difficulty: str, time_seconds: int):
    if not GITEE_TOKEN:
        return
    try:
        get_url = f"{GITEE_API}?access_token={GITEE_TOKEN}"
        req = urllib.request.Request(get_url)
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
            "access_token": GITEE_TOKEN,
            "content": base64.b64encode(new_content.encode()).decode(),
            "sha": sha,
            "message": f"更新战绩：{username} {difficulty} {time_seconds}s",
        }
    ).encode()
    try:
        put_req = urllib.request.Request(
            GITEE_API, data=body, method="PUT", headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(put_req, timeout=10)
    except Exception:
        pass
