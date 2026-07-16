"""
扫雷游戏 - 数据库模块
SQLite 数据库：用户表 + 排行榜表
"""
import sqlite3
import hashlib
import os
import sys
from datetime import datetime

# PyInstaller 打包后 __file__ 指向临时目录，需用 sys.executable 定位 exe 所在目录
if getattr(sys, 'frozen', False):
    _APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(_APP_DIR, 'minesweeper.db')


def get_db():
    """获取数据库连接（WAL 模式，支持并发读）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            password_hash TEXT  NOT NULL,
            created_at  TEXT    NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rankings (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            difficulty   TEXT    NOT NULL,
            time_seconds INTEGER NOT NULL,
            completed_at TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """SHA-256 密码哈希"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def register_user(username: str, password: str) -> tuple:
    """注册新用户，返回 (成功, 消息)"""
    username = username.strip()
    if not username or not password:
        return False, "用户名和密码不能为空！"
    if len(username) < 2:
        return False, "用户名至少需要 2 个字符！"
    if len(password) < 4:
        return False, "密码至少需要 4 个字符！"

    conn = get_db()
    cursor = conn.cursor()
    try:
        pwd_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)',
            (username, pwd_hash, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        return True, "注册成功！"
    except sqlite3.IntegrityError:
        return False, "用户名已存在，请换一个！"
    finally:
        conn.close()


def login_user(username: str, password: str) -> tuple:
    """登录验证，返回 (成功, 用户信息或错误消息)"""
    conn = get_db()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    cursor.execute(
        'SELECT id, username FROM users WHERE username = ? AND password_hash = ?',
        (username.strip(), pwd_hash)
    )
    user = cursor.fetchone()
    conn.close()
    if user:
        return True, dict(user)
    return False, "用户名或密码错误！"


def save_ranking(user_id: int, difficulty: str, time_seconds: int):
    """保存游戏成绩"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO rankings (user_id, difficulty, time_seconds, completed_at) '
        'VALUES (?, ?, ?, ?)',
        (user_id, difficulty, time_seconds, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    conn.commit()
    conn.close()


def get_rankings(difficulty: str, limit: int = 50) -> list:
    """获取指定难度的排行榜（按用时升序）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, r.time_seconds, r.completed_at, r.user_id
        FROM rankings r
        JOIN users u ON r.user_id = u.id
        WHERE r.difficulty = ?
        ORDER BY r.time_seconds ASC
        LIMIT ?
    ''', (difficulty, limit))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results
