# 赛博扫雷

深色硬朗风格的 Tkinter 扫雷客户端。正式版从登录页进入，使用统一的本地账号与战绩目录。

## 功能

- 三种难度：9x9 训练、27x27 进阶、81x81 极限
- 本地 SQLite 档案和战绩保存
- 大厅显示每个模式的个人最佳成绩和作战次数
- 对局 HUD 显示剩余雷数、计时、雷区密度和清扫进度
- 右键标记、双击数字展开、`R` 重开、`Esc` 返回大厅
- 胜负结算使用赛博操作面板，可重开、回大厅或查看战绩
- 排行榜优先显示本地战绩，并在后台合并 GitHub 云端数据
- 大厅显示真实 GitHub 连接状态；未配置令牌时为云端只读模式
- 支持语言切换，主要界面文案集中在 `lang.py`

## 正式版

直接双击项目根目录的 `扫雷.exe`。它是无控制台窗口的单文件版本，不会弹出“请按任意键继续”。

账号与战绩统一保存在：

```text
%LOCALAPPDATA%\CyberMinesweeper\minesweeper.db
```

首次启动会自动迁移项目目录中的旧数据库，原有 `ssr` 账号和战绩不会因源码目录、worktree 或 exe 位置变化而丢失。

## 源码运行

```bash
python main.py
```

也可以双击 `run.bat`，脚本使用 `pythonw`，不会保留命令行窗口。

## 构建 exe

```powershell
powershell -ExecutionPolicy Bypass -File .\build_release.ps1
```

## 开发验证

```bash
python -m unittest discover -v
```

核心玩法逻辑在 `game.py` 的 `MinesweeperGame` 中，界面主题和通用控件在 `ui_theme.py` 中。

## GitHub 战绩同步

云端榜单读取自 `siray1007/minesweeper` 的 `main/rankings.json`。读取公开榜单不需要令牌。

如需让客户端自动把新纪录写回 GitHub，请设置具有该仓库 Contents 写权限的环境变量：

```text
MINESWEEPER_GITHUB_TOKEN
```

未配置令牌时，本地账号和战绩仍会正常保存，界面会明确显示“云端只读”。
