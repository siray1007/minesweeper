"""
扫雷游戏 - 数据库模块
SQLite 数据库：用户表 + 排行榜表
"""
import sqlite3
import hashlib
import os
import sys
from datetime import datetime

if getattr(sys, 'frozen', False):
    _APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(_APP_DIR, 'minesweeper.db')


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


def save_ranking(user_id: int, difficulty: str, time_seconds: int):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO rankings (user_id, difficulty, time_seconds, completed_at) VALUES (?, ?, ?, ?)',
              (user_id, difficulty, time_seconds, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()


def get_rankings(difficulty: str, limit: int = 50) -> list:
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT u.username, r.time_seconds, r.completed_at, r.user_id
        FROM rankings r JOIN users u ON r.user_id = u.id
        WHERE r.difficulty = ? ORDER BY r.time_seconds ASC LIMIT ?''',
              (difficulty, limit))
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results
