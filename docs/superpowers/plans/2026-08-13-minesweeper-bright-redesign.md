# 扫雷明亮竞技科技风 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将整个 Tkinter 扫雷重构为明亮、健康、年轻且具有竞技科技感的统一界面，并发布新的根目录 `扫雷.exe`。

**Architecture:** 以 `ui_theme.py` 的语义 token 和共享构件作为唯一视觉基础，页面模块只负责布局与信息层级；`game.py` 独立负责受控渐变、状态色与多尺寸棋盘绘制。保留现有账号、数据库和云排行榜数据流，在当前未提交优化上增量实现。

**Tech Stack:** Python 3、Tkinter/ttk、Pillow（现有资源检查）、unittest、PyInstaller/现有 `build_release.ps1`。

## Global Constraints

- 产品名称始终为“扫雷”，赛博朋克仅是视觉风格。
- 不显示 GitHub、代码仓库、开发者信息或其他隐私内容。
- 不删除、迁移或重建 `%LOCALAPPDATA%\CyberMinesweeper\minesweeper.db`。
- 不改变注册、登录、成绩写入、云排行拉取和本地/云端合并的数据契约。
- 语言选择固定在左上角，维持现有全部语言、简体中文、繁體中文和文言文。
- 格子连续排列、边界清楚，不使用粗缝硬切开。
- 完成后必须重新生成根目录 `扫雷.exe` 并完成启动检查。

---

### Task 1: 全局明亮主题系统

**Files:**
- Modify: `ui_theme.py`
- Test: `test_lang_theme.py`

**Interfaces:**
- Produces: `COLORS` 语义 token、`CyberButton`、`make_entry()`、`make_panel()`、`metric_label()`、`section_title()`、`install_backdrop()`。
- Consumes: Tkinter 与现有页面调用约定。

- [ ] **Step 1: 为背景、表面、边界、文字、状态和棋盘 token 增加亮度与对比测试**
- [ ] **Step 2: 运行 `python -m unittest test_lang_theme -v`，确认新约束先失败**
- [ ] **Step 3: 将近黑色板替换为明亮深蓝、银蓝和冰灰体系，并统一 ttk、按钮、输入框、面板及背景纹理**
- [ ] **Step 4: 运行 `python -m unittest test_lang_theme -v`，确认主题约束通过**

### Task 2: 连续渐变棋盘与清晰状态

**Files:**
- Modify: `game.py`
- Modify: `ui_theme.py`
- Test: `test_game.py`

**Interfaces:**
- Produces: 受控渐变色组、RGB 插值函数、位置色函数，以及未打开、已打开、旗帜、悬停、爆雷绘制。
- Consumes: `COLORS` 棋盘语义 token 和 `MinesweeperGame` 状态矩阵。

- [ ] **Step 1: 增加端点插值、对角连续性、色组范围及打开/未打开感知差异测试**
- [ ] **Step 2: 运行 `python -m unittest test_game -v`，确认测试失败**
- [ ] **Step 3: 恢复 `t=(row+col)/(rows+cols-2)` 渐变并实现精选色组，已打开格使用独立低彩度扫描面**
- [ ] **Step 4: 统一 9x9、27x27、81x81 的旗帜、数字、悬停和危险态绘制**
- [ ] **Step 5: 运行 `python -m unittest test_game -v`，确认棋盘测试通过**

### Task 3: 登录、注册与语言模块

**Files:**
- Modify: `auth.py`
- Modify: `lang.py`
- Test: `test_auth_layout.py`
- Test: `test_lang_theme.py`

**Interfaces:**
- Produces: 左上角单一语言模块、同尺寸登录/注册操作、页面内错误反馈。
- Consumes: 现有 `login_user()`、`register_user()`、`LANG_OPTIONS`、`set_lang()`。

- [ ] **Step 1: 增加语言模块整体性、主操作等尺寸和产品名约束测试**
- [ ] **Step 2: 运行 `python -m unittest test_auth_layout test_lang_theme -v`，确认失败项**
- [ ] **Step 3: 扩大登录内容区，统一语言模块和操作按钮，清除弹窗式可恢复反馈**
- [ ] **Step 4: 运行登录布局与语言测试，确认通过**

### Task 4: 大厅与个人档案统一重构

**Files:**
- Modify: `main.py`
- Modify: `ui_theme.py`
- Test: `test_lang_theme.py`

**Interfaces:**
- Produces: 以难度入口为中心的大厅、无重复内容的档案、统一完整边框和等尺寸操作区。
- Consumes: 现有用户对象、统计查询、页面导航回调。

- [ ] **Step 1: 增加隐私词、重复信息和关键布局约束测试**
- [ ] **Step 2: 运行相关测试并记录失败**
- [ ] **Step 3: 重排大厅视觉层级，扩大难度入口和有效内容区**
- [ ] **Step 4: 重排档案概览、统计与操作区，统一边框并移除重复内容**
- [ ] **Step 5: 运行相关测试确认通过**

### Task 5: 排行榜、HUD 与结算统一

**Files:**
- Modify: `ranking.py`
- Modify: `game.py`
- Modify: `lang.py`
- Test: `test_game.py`
- Test: `test_lang_theme.py`

**Interfaces:**
- Produces: 清晰榜单层级、非阻塞云状态、统一 HUD 和页内结算区。
- Consumes: `fetch_cloud_rankings()`、`get_rankings_local()`、现有计时与导航回调。

- [ ] **Step 1: 增加联网降级、HUD 文案和页内结算约束测试**
- [ ] **Step 2: 运行测试确认失败项**
- [ ] **Step 3: 统一个人最佳、榜单、联网状态和空状态的容器与颜色语义**
- [ ] **Step 4: 重排 HUD 与结算操作优先级，保持后台任务可取消**
- [ ] **Step 5: 运行相关测试确认通过**

### Task 6: 实际窗口视觉验收与修正

**Files:**
- Modify: `auth.py`
- Modify: `main.py`
- Modify: `game.py`
- Modify: `ranking.py`
- Modify: `ui_theme.py`
- Test: `test_auth_layout.py`
- Test: `test_game.py`
- Test: `test_lang_theme.py`

**Interfaces:**
- Produces: 登录、注册、大厅、档案、排行、结算及三种棋盘的实际截图证据。
- Consumes: 应用启动入口与固定棋盘状态注入方式。

- [ ] **Step 1: 启动实际 Tk 窗口并截取各核心页面**
- [ ] **Step 2: 检查文字截断、控件重叠、边框不一致、过暗区域和状态混淆**
- [ ] **Step 3: 固定生成包含未打开、已打开、数字、旗帜与雷的 9x9、27x27、81x81 状态**
- [ ] **Step 4: 修正发现的问题并重复截图，直至各状态一眼可辨且棋盘连续**
- [ ] **Step 5: 清理临时预览与截图辅助文件**

### Task 7: 全量验证与 Windows 发布

**Files:**
- Modify: `扫雷.exe`（由构建脚本生成）
- Verify: `build_release.ps1`

**Interfaces:**
- Produces: 通过验证的源码和根目录可启动 `扫雷.exe`。
- Consumes: 现有发布脚本及项目图标资源。

- [ ] **Step 1: 运行 `python -m unittest discover -v`**
- [ ] **Step 2: 运行 `python -m py_compile auth.py database.py game.py lang.py main.py ranking.py ui_theme.py test_auth_layout.py test_game.py test_lang_theme.py`**
- [ ] **Step 3: 运行 `git diff --check`**
- [ ] **Step 4: 运行 `powershell.exe -ExecutionPolicy Bypass -File .\build_release.ps1`**
- [ ] **Step 5: 启动根目录 `扫雷.exe`，检查进程、窗口和登录页后正常退出**
- [ ] **Step 6: 核对 `扫雷.exe` 的修改时间与文件大小，并汇总所有验证结果**
