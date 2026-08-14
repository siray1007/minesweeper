# 扫雷

深色硬朗、赛博朋克风格的 Tkinter 扫雷客户端。项目正式名称就是“扫雷”，赛博朋克只作为视觉风格，不作为产品名。

## 功能

- 三种难度：9x9 训练、27x27 进阶、81x81 极限
- 本地账号登录、注册和战绩保存
- 大厅展示个人最佳成绩、作战次数和玩家档案
- 对局 HUD 展示剩余雷数、计时、雷区密度和清扫进度
- 右键标记、双击数字展开、`R` 重开、`Esc` 返回
- 排行榜优先显示本地战绩，并可在后台合并在线榜单
- 左上角语言模块提供多语言下拉选择

## 正式版

直接双击项目根目录的 `扫雷.exe`。它是无控制台窗口的单文件版本，不会弹出“请按任意键继续”。

账号与战绩统一保存在：

```text
%LOCALAPPDATA%\CyberMinesweeper\minesweeper.db
```

这个目录名是历史兼容路径，用来保留已有账号和战绩；它不会显示在游戏界面里。首次启动会自动迁移项目目录中的旧数据库，原有 `ssr` 账号和战绩不会因 exe 位置变化而丢失。

## 源码运行

```bash
python main.py
```

也可以双击 `run.bat`，脚本使用 `pythonw`，不会保留命令行窗口。

## 构建 exe

```powershell
powershell -ExecutionPolicy Bypass -File .\build_release.ps1
```

构建完成后根目录只生成 `扫雷.exe`。

## 开发验证

```bash
python -m unittest discover -v
python -m py_compile auth.py database.py game.py lang.py main.py ranking.py ui_theme.py
```

核心玩法逻辑在 `game.py` 的 `MinesweeperGame` 中，界面主题和通用控件在 `ui_theme.py` 中。

## 在线战绩同步

在线榜单读取公开的 `rankings.json`。读取榜单不需要令牌；如需让客户端自动写回新纪录，请设置：

```text
MINESWEEPER_GITHUB_TOKEN
```

未配置令牌时，本地账号和战绩仍会正常保存，界面显示为只读/离线可用状态。
