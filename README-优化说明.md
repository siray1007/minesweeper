# 扫雷重构说明

## 重构重点

- 统一项目名称为“扫雷”，赛博朋克只作为页面风格
- 重建语言资源，清理乱码文案
- 将语言选择恢复为左上角多语言下拉模块
- 统一深色硬朗的竞技视觉 token
- 重做登录、大厅、玩家档案、对局和排行榜界面
- 强化棋盘格子边界的高亮和对比，不改变扫雷规则
- 保留本地账号、战绩迁移和在线榜单降级能力
- 清理旧版发布名、旧 exe 和临时构建目录
- 重新生成无控制台的单文件 `扫雷.exe`

## 文件结构

```text
main.py       应用壳和页面切换
auth.py       登录与注册界面
game.py       扫雷规则与对局界面
ranking.py    排行榜界面
database.py   SQLite 与在线排行榜同步
lang.py       语言资源
ui_theme.py   主题 token 与 Tk 样式
```

## 验证

```bash
python -m unittest discover -v
python -m py_compile auth.py database.py game.py lang.py main.py ranking.py ui_theme.py
```

## 正式打包

```bash
powershell -ExecutionPolicy Bypass -File .\build_release.ps1
```
