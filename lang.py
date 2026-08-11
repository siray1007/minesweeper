"""Localization resources for the Minesweeper client."""
from __future__ import annotations

import os


_LANG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lang_pref.txt")

_ZH = {
    "title": "赛博扫雷",
    "login": "登录账号",
    "register": "创建账号",
    "username": "用户名",
    "password": "密码",
    "confirm_pwd": "确认密码",
    "btn_login": "进入大厅",
    "btn_quick_start": "快速进入本地作战",
    "btn_register": "创建账号",
    "no_account": "还没有账号？",
    "has_account": "已有账号？",
    "to_register": "创建新账号",
    "to_login": "返回登录",
    "warn_empty": "请输入用户名和密码。",
    "login_fail": "登录失败",
    "reg_fail": "注册失败",
    "reg_ok": "注册成功",
    "pwd_mismatch": "两次输入的密码不一致。",
    "user_exists": "用户名已存在。",
    "pwd_short": "密码至少需要 4 个字符。",
    "user_short": "用户名至少需要 2 个字符。",
    "pwd_hint": "密码（至少 4 位）",
    "menu_title": "作战大厅",
    "welcome": "欢迎，{}",
    "diff_easy": "训练 9x9",
    "diff_medium": "进阶 27x27",
    "diff_hard": "极限 81x81",
    "desc_easy": "10 雷 / 入门热身",
    "desc_medium": "100 雷 / 高压推进",
    "desc_hard": "800 雷 / 长线作战",
    "btn_start": "启动作战",
    "btn_ranking": "战绩榜",
    "btn_logout": "退出登录",
    "btn_back": "返回",
    "btn_restart": "重开",
    "game_over": "任务失败",
    "game_over_msg": "你触发了地雷，任务终止。",
    "win_title": "任务完成",
    "win_msg": "清扫完成。\n\n模式：{}\n用时：{}\n\n成绩已写入战绩榜。",
    "rank_title": "战绩榜",
    "my_records": "我的记录",
    "rank_col": "排名",
    "user_col": "玩家",
    "time_col": "用时",
    "date_col": "完成时间",
    "no_data": "暂无记录",
    "no_records": "暂无个人记录",
    "difficulty_col": "模式",
    "current_user": "当前玩家：{}",
    "logout_confirm": "确定退出当前账号？",
    "quit_confirm": "确定退出游戏？",
    "easy_title": "训练 9x9",
    "medium_title": "进阶 27x27",
    "hard_title": "极限 81x81",
    "mines": "剩余雷数",
    "btn_close": "关闭",
    "language": "语言",
    "time_label": "计时",
    "status_local_loaded": "本地战绩已加载 / 云端同步中",
    "status_cloud_done": "本地战绩已加载 / 云端同步完成",
    "mode_hint": "选择一个作战模式开始清扫",
    "control_hint": "左键翻开 / 右键标记 / 双击数字快速展开",
    "zoom_fit": "重置缩放",
    "profile_label": "玩家档案",
    "records_label": "战绩同步",
    "auth_kicker": "NEON_SWEEP / ACCESS NODE",
    "auth_status": "本地档案在线 / 离线排行可用",
    "system_ready": "系统待命",
    "menu_subtitle": "选择作战模块，进入雷区扫描。",
    "operator_label": "OPERATOR",
    "grid_label": "GRID",
    "mine_density": "DENSITY",
    "threat_label": "THREAT",
    "threat_low": "LOW",
    "threat_medium": "HIGH",
    "threat_high": "EXTREME",
    "sector_label": "SECTOR",
    "board_status_ready": "雷区未激活",
    "board_status_live": "扫描进行中",
    "board_status_failed": "任务失败",
    "board_status_clear": "区域清空",
    "rank_subtitle": "本地战绩优先显示，云端数据后台合并。",
    "rank_empty_marker": "NO SIGNAL",
}

_EN = {
    "title": "Cyber Minesweeper",
    "login": "Sign In",
    "register": "Create Account",
    "username": "Username",
    "password": "Password",
    "confirm_pwd": "Confirm Password",
    "btn_login": "Enter Lobby",
    "btn_quick_start": "Quick Local Start",
    "btn_register": "Create Account",
    "no_account": "No account yet?",
    "has_account": "Already have an account?",
    "to_register": "Create Account",
    "to_login": "Back to Sign In",
    "warn_empty": "Please enter a username and password.",
    "login_fail": "Sign In Failed",
    "reg_fail": "Registration Failed",
    "reg_ok": "Registration Complete",
    "pwd_mismatch": "Passwords do not match.",
    "user_exists": "Username already exists.",
    "pwd_short": "Password must be at least 4 characters.",
    "user_short": "Username must be at least 2 characters.",
    "pwd_hint": "Password (min 4 chars)",
    "menu_title": "Operations Lobby",
    "welcome": "Welcome, {}",
    "diff_easy": "Training 9x9",
    "diff_medium": "Advanced 27x27",
    "diff_hard": "Extreme 81x81",
    "desc_easy": "10 mines / warm-up run",
    "desc_medium": "100 mines / high pressure",
    "desc_hard": "800 mines / long operation",
    "btn_start": "Launch",
    "btn_ranking": "Records",
    "btn_logout": "Logout",
    "btn_back": "Back",
    "btn_restart": "Restart",
    "game_over": "Mission Failed",
    "game_over_msg": "You triggered a mine. Mission terminated.",
    "win_title": "Mission Complete",
    "win_msg": "Clear complete.\n\nMode: {}\nTime: {}\n\nScore saved to records.",
    "rank_title": "Records",
    "my_records": "My Records",
    "rank_col": "Rank",
    "user_col": "Player",
    "time_col": "Time",
    "date_col": "Completed",
    "no_data": "No records",
    "no_records": "No personal records",
    "difficulty_col": "Mode",
    "current_user": "Current player: {}",
    "logout_confirm": "Log out of this account?",
    "quit_confirm": "Quit the game?",
    "easy_title": "Training 9x9",
    "medium_title": "Advanced 27x27",
    "hard_title": "Extreme 81x81",
    "mines": "Mines",
    "btn_close": "Close",
    "language": "Language",
    "time_label": "Time",
    "status_local_loaded": "Local records loaded / cloud sync running",
    "status_cloud_done": "Local records loaded / cloud sync complete",
    "mode_hint": "Select an operation mode to begin.",
    "control_hint": "Left reveal / Right flag / Double-click number to expand",
    "zoom_fit": "Reset zoom",
    "profile_label": "Profile",
    "records_label": "Record Sync",
    "auth_kicker": "NEON_SWEEP / ACCESS NODE",
    "auth_status": "Local profile online / offline records enabled",
    "system_ready": "System Ready",
    "menu_subtitle": "Choose an operation module and enter the minefield.",
    "operator_label": "OPERATOR",
    "grid_label": "GRID",
    "mine_density": "DENSITY",
    "threat_label": "THREAT",
    "threat_low": "LOW",
    "threat_medium": "HIGH",
    "threat_high": "EXTREME",
    "sector_label": "SECTOR",
    "board_status_ready": "Minefield idle",
    "board_status_live": "Scan active",
    "board_status_failed": "Mission failed",
    "board_status_clear": "Sector clear",
    "rank_subtitle": "Local records show first while cloud data merges in the background.",
    "rank_empty_marker": "NO SIGNAL",
}

TEXTS = {
    "zh": _ZH,
    "en": _EN,
    "zt": {**_ZH, "title": "賽博掃雷", "language": "語言"},
    "de": _EN,
    "fr": _EN,
    "ru": _EN,
    "ja": _EN,
    "ko": _EN,
    "wy": _ZH,
}

LANG_OPTIONS = [
    ("zh", "中文"),
    ("en", "English"),
    ("zt", "繁體中文"),
    ("de", "Deutsch"),
    ("fr", "Français"),
    ("ru", "Русский"),
    ("ja", "日本語"),
    ("ko", "한국어"),
    ("wy", "文言"),
]

_current_lang = "zh"


def load_lang() -> None:
    global _current_lang
    try:
        if os.path.exists(_LANG_FILE):
            with open(_LANG_FILE, "r", encoding="utf-8") as lang_file:
                lang = lang_file.read().strip()
            if lang in TEXTS:
                _current_lang = lang
    except OSError:
        _current_lang = "zh"


def save_lang(lang: str) -> None:
    global _current_lang
    if lang not in TEXTS:
        lang = "zh"
    _current_lang = lang
    with open(_LANG_FILE, "w", encoding="utf-8") as lang_file:
        lang_file.write(lang)


def t(key: str, *args) -> str:
    text = TEXTS.get(_current_lang, TEXTS["zh"]).get(key, TEXTS["zh"].get(key, key))
    return text.format(*args) if args else text


def get_lang() -> str:
    return _current_lang


load_lang()
