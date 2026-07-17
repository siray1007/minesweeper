"""
扫雷游戏 - 数据库模块
本地 SQLite：用户认证
云端 Gitee：排行榜（rankings.json）
"""
import sqlite3
import hashlib
import os
import sys
import json
import base64
import urllib.request
import urllib.error
from datetime import datetime

if getattr(sys, 'frozen', False):
    _APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_APP_DIR, 'minesweeper.db')

GITEE_USER = 'siray-07'
GITEE_REPO = 'minesweeper'
GITEE_API  = f'https://gitee.com/api/v5/repos/{GITEE_USER}/{GITEE_REPO}/contents/rankings.json'
GITEE_RAW  = f'https://gitee.com/{GITEE_USER}/{GITEE_REPO}/raw/master/rankings.json'
GITEE_TOKEN = '7d6da7d260950ee67775f83242ac6564'
MAX_RANKINGS = 100


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        difficulty TEXT NOT NULL,
        time_seconds INTEGER NOT NULL,
        completed_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def register_user(username: str, password: str) -> tuple:
    username = username.strip()
    if not username or not password:
        return False, "用户名和密码不能为空！"
    if len(username) < 2:
        return False, "用户名至少需要 2 个字符！"
    if len(password) < 4:
        return False, "密码至少需要 4 个字符！"
    conn = get_db()
    c = conn.cursor()
    try:
        pwd_hash = hash_password(password)
        c.execute('INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)',
                  (username, pwd_hash, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return True, "注册成功！"
    except sqlite3.IntegrityError:
        return False, "用户名已存在！"
    finally:
        conn.close()


def login_user(username: str, password: str) -> tuple:
    conn = get_db()
    c = conn.cursor()
    pwd_hash = hash_password(password)
    c.execute('SELECT id, username FROM users WHERE username = ? AND password_hash = ?',
              (username.strip(), pwd_hash))
    user = c.fetchone()
    conn.close()
    if user:
        return True, dict(user)
    return False, "用户名或密码错误！"


def save_ranking(user_id: int, difficulty: str, time_seconds: int, username: str = ''):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO rankings (user_id, difficulty, time_seconds, completed_at) VALUES (?, ?, ?, ?)',
              (user_id, difficulty, time_seconds, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    if username:
        _gitee_append_ranking(username, difficulty, time_seconds)


def get_rankings_local(difficulty: str, limit: int = 50) -> list:
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT u.username, r.time_seconds, r.completed_at, r.user_id
        FROM rankings r JOIN users u ON r.user_id = u.id
        WHERE r.difficulty = ? ORDER BY r.time_seconds ASC LIMIT ?''',
              (difficulty, limit))
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results


def get_rankings(difficulty: str, limit: int = 50) -> list:
    online = _gitee_fetch_rankings(difficulty, limit) or []
    local = get_rankings_local(difficulty, limit)
    seen = set()
    merged = []
    for r in online:
        key = (r['username'], r['time_seconds'])
        seen.add(key)
        merged.append(r)
    for r in local:
        key = (r['username'], r['time_seconds'])
        if key not in seen:
            seen.add(key)
            merged.append(r)
    merged.sort(key=lambda x: x.get('time_seconds', 99999))
    return merged[:limit]


def _gitee_fetch_rankings(difficulty: str, limit: int) -> list | None:
    try:
        req = urllib.request.Request(GITEE_RAW)
        with urllib.request.urlopen(req, timeout=8) as resp:
            all_rankings = json.loads(resp.read().decode())
    except Exception:
        return None
    filtered = [r for r in all_rankings if r.get('difficulty') == difficulty]
    filtered.sort(key=lambda x: x.get('time_seconds', 99999))
    return filtered[:limit]


def _gitee_append_ranking(username: str, difficulty: str, time_seconds: int):
    try:
        get_url = f'{GITEE_API}?access_token={GITEE_TOKEN}'
        req = urllib.request.Request(get_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            info = json.loads(resp.read().decode())
        sha = info['sha']
        content = base64.b64decode(info['content']).decode()
        rankings = json.loads(content) if content.strip() else []
    except Exception:
        return
    rankings.append({
        'username': username,
        'difficulty': difficulty,
        'time_seconds': time_seconds,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })
    best = {}
    for r in rankings:
        key = (r['username'], r['difficulty'])
        if key not in best or r['time_seconds'] < best[key]['time_seconds']:
            best[key] = r
    trimmed = sorted(best.values(), key=lambda x: x.get('time_seconds', 99999))
    trimmed = trimmed[:MAX_RANKINGS]
    new_content = json.dumps(trimmed, ensure_ascii=False, indent=2)
    body = json.dumps({
        'access_token': GITEE_TOKEN,
        'content': base64.b64encode(new_content.encode()).decode(),
        'sha': sha,
        'message': f'📊 {username} {difficulty} {time_seconds}s',
    }).encode()
    try:
        put_req = urllib.request.Request(GITEE_API, data=body, method='PUT',
                                          headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(put_req, timeout=10)
    except Exception:
        pass
