"""扫雷 - 多语言模块"""
from __future__ import annotations

import os


_LANG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lang_pref.txt')

TEXTS = {
    'zh': {
        'title': '扫雷',
        'login': '登录账号',
        'register': '注册新账号',
        'username': '用户名',
        'password': '密码',
        'confirm_pwd': '确认密码',
        'btn_login': '登录',
        'btn_register': '注册',
        'no_account': '还没有账号？',
        'has_account': '已有账号？',
        'to_register': '立即注册',
        'to_login': '返回登录',
        'warn_empty': '请输入用户名和密码！',
        'login_fail': '登录失败',
        'reg_fail': '注册失败',
        'reg_ok': '注册成功！',
        'pwd_mismatch': '两次密码输入不一致！',
        'user_exists': '用户名已存在！',
        'pwd_short': '密码至少需要 4 个字符！',
        'user_short': '用户名至少需要 2 个字符！',
        'pwd_hint': '密码（至少 4 位）',
        'menu_title': '选择难度',
        'welcome': '欢迎，{}！',
        'diff_easy': '简单 9x9',
        'diff_medium': '进阶 27x27',
        'diff_hard': '困难 81x81',
        'desc_easy': '10 个地雷，适合快速开局',
        'desc_medium': '100 个地雷，适合中段挑战',
        'desc_hard': '800 个地雷，极限战场',
        'btn_start': '开始游戏',
        'btn_ranking': '排行榜',
        'btn_logout': '退出登录',
        'btn_back': '返回',
        'btn_restart': '重新开始',
        'game_over': '游戏结束',
        'game_over_msg': '你踩到地雷了，游戏结束。',
        'win_title': '胜利',
        'win_msg': '你赢了！\n\n难度：{}\n用时：{}\n\n成绩已记录到排行榜！',
        'rank_title': '排行榜',
        'my_records': '我的战绩',
        'rank_col': '排名',
        'user_col': '用户名',
        'time_col': '用时',
        'date_col': '完成日期',
        'no_data': '暂无记录',
        'no_records': '暂无战绩',
        'difficulty_col': '难度',
        'current_user': '当前用户：{}',
        'logout_confirm': '确定要退出登录吗？',
        'quit_confirm': '确定要退出游戏吗？',
        'easy_title': '简单 9x9',
        'medium_title': '进阶 27x27',
        'hard_title': '困难 81x81',
        'mines': '地雷',
        'btn_close': '关闭',
        'lobby_profile_title': '战斗档案',
        'lobby_profile_subtitle': '账号状态 / 记录 / 赛况概览',
        'lobby_status_title': '系统状态',
        'lobby_status_scan': '扫描中：准备进入战场',
        'lobby_status_record': '记录：本地 + 云端同步',
        'lobby_status_control': '控制：选择一项难度开始',
        'lobby_threat_matrix': '威胁矩阵',
        'lobby_launch_title': '三条战线',
        'lobby_launch_subtitle': '从轻量局到极限局，窗口会随战场放大',
        'language': '语言',
        'esc_hint': '按住 Esc 可返回大厅',
        'rank_syncing': '本地记录已加载，云端同步中…',
        'rank_synced': '本地记录已加载，云端同步完成。',
        'zoom_fit': '适应窗口',
        'game_hint': '左键翻开 · 右键标记 · 双击数字快速扩展',
        'status_scan_heading': 'SCAN',
        'status_sync_heading': 'SYNC',
        'status_control_heading': 'CONTROL',
        'status_scan_desc': '实时记录与本地进度同步。',
        'status_sync_desc': '战绩保留在本地与云端。',
        'status_control_desc': '进入战场后继续保留返回路径。',
    },
    'en': {
        'title': 'Minesweeper',
        'login': 'Sign In',
        'register': 'Sign Up',
        'username': 'Username',
        'password': 'Password',
        'confirm_pwd': 'Confirm Password',
        'btn_login': 'Sign In',
        'btn_register': 'Sign Up',
        'no_account': "Don't have an account?",
        'has_account': 'Already have an account?',
        'to_register': 'Create Account',
        'to_login': 'Back to Sign In',
        'warn_empty': 'Please enter username and password!',
        'login_fail': 'Login Failed',
        'reg_fail': 'Registration Failed',
        'reg_ok': 'Registration Successful!',
        'pwd_mismatch': 'Passwords do not match!',
        'user_exists': 'Username already exists!',
        'pwd_short': 'Password must be at least 4 characters!',
        'user_short': 'Username must be at least 2 characters!',
        'pwd_hint': 'Password (min 4 chars)',
        'menu_title': 'Choose Difficulty',
        'welcome': 'Welcome, {}!',
        'diff_easy': 'Easy 9x9',
        'diff_medium': 'Medium 27x27',
        'diff_hard': 'Hard 81x81',
        'desc_easy': '10 mines, quick warm-up',
        'desc_medium': '100 mines, mid-tier pressure',
        'desc_hard': '800 mines, extreme arena',
        'btn_start': 'Start Game',
        'btn_ranking': 'Leaderboard',
        'btn_logout': 'Logout',
        'btn_back': 'Back',
        'btn_restart': 'Restart',
        'game_over': 'Game Over',
        'game_over_msg': 'You hit a mine. Game over.',
        'win_title': 'You Win',
        'win_msg': 'You win!\n\nDifficulty: {}\nTime: {}\n\nScore recorded!',
        'rank_title': 'Leaderboard',
        'my_records': 'My Records',
        'rank_col': 'Rank',
        'user_col': 'Username',
        'time_col': 'Time',
        'date_col': 'Completed',
        'no_data': 'No Records',
        'no_records': 'No Records',
        'difficulty_col': 'Difficulty',
        'current_user': 'Current User: {}',
        'logout_confirm': 'Are you sure you want to logout?',
        'quit_confirm': 'Are you sure you want to quit?',
        'easy_title': 'Easy 9x9',
        'medium_title': 'Medium 27x27',
        'hard_title': 'Hard 81x81',
        'mines': 'Mines',
        'btn_close': 'Close',
        'lobby_profile_title': 'Profile',
        'lobby_profile_subtitle': 'Account, match history, and status',
        'lobby_status_title': 'System Status',
        'lobby_status_scan': 'Scan: ready for deployment',
        'lobby_status_record': 'Record: local plus cloud sync',
        'lobby_status_control': 'Control: pick a difficulty to launch',
        'lobby_threat_matrix': 'Threat Matrix',
        'lobby_launch_title': 'Three Fronts',
        'lobby_launch_subtitle': 'From quick runs to extreme boards, the window scales with the battlefield',
        'language': 'Language',
        'esc_hint': 'Hold Esc to return to lobby',
        'rank_syncing': 'Local records loaded. Cloud sync in progress…',
        'rank_synced': 'Local records loaded. Cloud sync complete.',
        'zoom_fit': 'Fit Window',
        'game_hint': 'Left click reveal · Right click flag · Double click number to chord',
        'status_scan_heading': 'SCAN',
        'status_sync_heading': 'SYNC',
        'status_control_heading': 'CONTROL',
        'status_scan_desc': 'Match state and local progress stay live.',
        'status_sync_desc': 'Records are kept locally and synced to cloud when available.',
        'status_control_desc': 'The lobby path remains available after deployment.',
    },
}

_current_lang = 'zh'


def load_lang() -> None:
    global _current_lang
    try:
        if os.path.exists(_LANG_FILE):
            with open(_LANG_FILE, 'r', encoding='utf-8') as handle:
                lang = handle.read().strip()
                if lang in TEXTS:
                    _current_lang = lang
    except OSError:
        pass


def save_lang(lang: str) -> None:
    global _current_lang
    _current_lang = lang
    with open(_LANG_FILE, 'w', encoding='utf-8') as handle:
        handle.write(lang)


def t(key: str, *args) -> str:
    text = TEXTS.get(_current_lang, TEXTS['zh']).get(key, key)
    return text.format(*args) if args else text


def get_lang() -> str:
    return _current_lang


LANG_OPTIONS = [
    ('en', 'English'),
    ('zh', '简体中文'),
]


load_lang()
