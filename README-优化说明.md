# 赛博扫雷重构说明

## 重构重点
- 重建语言资源，清理乱码文案
- 统一深色赛博风主题 token
- 重做登录、大厅、对局和排行榜界面
- 保留原有扫雷规则与本地存档能力
- 清理数据库模块注释和云端同步降级逻辑
- 合并测试 worktree 与主项目，保留玩家档案、HUD、结果面板和大棋盘适配
- 固定账号数据库目录并迁移旧版 `ssr` 数据
- 重新生成无控制台的单文件 `扫雷.exe`

## 文件结构
```text
main.py       应用壳和页面切换
auth.py       登录与注册界面
game.py       扫雷规则与对局界面
ranking.py    排行榜界面
database.py   SQLite 与 Gitee 排行榜同步
lang.py       语言资源
ui_theme.py   主题 token 与 Tk 样式
```

## 验证
```bash
python -m unittest discover -v
python -c "import main, auth, game, ranking, lang, ui_theme, database"
```

## 正式打包
```bash
powershell -ExecutionPolicy Bypass -File .\build_release.ps1
```
