<div align="center">

# 五子棋 · Gomoku

**基于 Pygame-CE 的五子棋对弈游戏，内置 Minimax + Alpha-Beta 剪枝 AI、经典棋谱回放、窗口缩放与完整的对局管理系统。**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame-CE](https://img.shields.io/badge/Pygame--CE-2.5.7+-00979D?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge)

</div>

---

## 核心功能

### 🎮 三种对弈模式

| 模式 | 说明 |
|------|------|
| **双人对弈** | 本地双人轮流落子，支持悔棋 |
| **人机对战** | 对抗 AI，三档难度可选 |
| **棋谱回放** | 内置 3 局经典棋谱 + 自定义保存，支持逐步回放与中途接管 |

### 🪟 可缩放窗口

- 使用 `pygame.RESIZABLE` 创建窗口，支持拖拽改变窗口大小
- 棋盘、棋子、按钮、字体与提示栏会按窗口比例整体缩放
- 鼠标点击会自动映射到缩放后的棋盘坐标，避免窗口变化后落子偏移

### 🧠 AI 引擎

```
┌─────────────────────────────────────────────────────┐
│                  AI 决策流水线                        │
│                                                     │
│  棋盘状态 ──▶ 候选点生成 ──▶ 紧急着法检测            │
│                                    │                │
│                    ┌───────────────┤                │
│                    ▼               ▼                │
│              必胜/必防?        Minimax 搜索          │
│              直接返回          + Alpha-Beta 剪枝     │
│                                    │                │
│                                    ▼                │
│                             局面评估函数             │
│                             返回最优着法             │
└─────────────────────────────────────────────────────┘
```

- **Minimax 搜索** + **Alpha-Beta 剪枝**，搜索深度可配置
- **棋型识别**：连五 / 活四 / 冲四 / 活三 / 眠三 / 活二 / 眠二
- **紧急着法优先**：能赢直接赢，能防立刻防
- **候选点裁剪**：仅评估棋子周围 2 格内的有效空位，大幅提升性能

| 难度 | 搜索深度 | 候选点数 | 特点 |
|:----:|:--------:|:--------:|------|
| 简单 | 2 | 5 | 加入随机性，适合新手 |
| 中等 | 3 | 8 | 稳扎稳打，有一定挑战 |
| 困难 | 4 | 10 | 全力计算，需要认真应对 |

### 📜 经典棋谱

内置 3 局精选对局，每局最后一步均形成五连：

| 棋谱 | 结果 | 亮点 |
|------|:----:|------|
| `斜线妙杀——五十三手经典长局.json` | 黑胜 | 对角线五连，53 手长局攻防 |
| `白棋逆袭——斜线绝杀.json` | 白胜 | 白棋后发制人，38 手绝杀 |
| `快刀斩乱麻——二十一手速胜.json` | 黑胜 | 21 手速胜，凌厉攻势 |

棋谱回放支持 **逐步播放**、**自动播放**、**中途接管** 继续对弈。

---

## 快速开始

### 方式一：Windows 启动脚本

```bat
run.bat
```

脚本会自动查找 `.venv\Scripts\python.exe` 或系统 `python`，并检查 Python 版本与 Pygame 依赖。

### 方式二：命令行启动

```bash
# 克隆项目
git clone https://github.com/lanmao657/WZQ.git
cd WZQ

# 创建虚拟环境 & 安装依赖
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 启动游戏
python main.py
```

> 运行环境要求 Python 3.10+；依赖包含 `pygame-ce>=2.5.7` 与用于打包的 `pyinstaller>=6.13`。

---

## 打包为 Windows 可执行文件

```bat
build.bat
```

构建完成后会生成：

```text
dist\gomoku.exe
```

打包配置位于 `gomoku.spec`，会把 `records/classic` 内置棋谱一起打入程序。运行打包后的 `gomoku.exe` 时，用户保存的棋谱会写入可执行文件所在目录下的 `records/saved/`，便于后续继续回放或备份。

---

## 操作指南

```
┌───────────────────────────────────────────┐
│            主菜单                         │
│  ┌─────────────┐                         │
│  │  双人对弈    │  ──▶  PVP 模式         │
│  │  人机对战    │  ──▶  选择难度 ▶ PVE   │
│  │  棋谱回放    │  ──▶  选择棋谱 ▶ 回放  │
│  └─────────────┘                         │
└───────────────────────────────────────────┘
```

| 操作 | 说明 |
|------|------|
| **鼠标左键** | 落子 / 点击按钮 |
| 拖拽窗口边缘 | 调整游戏窗口大小 |
| **R** | 游戏结束后重新开始 |
| **M** | 游戏结束后返回菜单 |
| 侧边栏 **悔棋** | 撤回上一步（人机模式撤回两步） |
| 侧边栏 **保存棋谱** | 将当前对局保存为 JSON 文件 |

---

## 项目架构

```
WZQ/
├── main.py          # 程序入口
├── game.py          # 游戏状态机与调度核心
├── board.py         # 15×15 棋盘数据结构
├── rules.py         # 胜负判定（五连/平局）
├── ai.py            # AI 引擎（Minimax + α-β 剪枝）
├── renderer.py      # Pygame 渲染器（棋盘、棋子、UI）
├── history.py       # 棋谱系统（保存/加载/回放控制）
├── paths.py         # 开发环境与 PyInstaller 环境的资源路径处理
├── requirements.txt # 依赖声明
├── run.bat          # Windows 启动脚本
├── build.bat        # Windows 打包脚本
├── gomoku.spec      # PyInstaller 打包配置
└── records/
    ├── classic/     # 内置经典棋谱
    │   ├── 斜线妙杀——五十三手经典长局.json
    │   ├── 白棋逆袭——斜线绝杀.json
    │   └── 快刀斩乱麻——二十一手速胜.json
    └── saved/       # 用户保存的棋谱（自动创建）
```

### 模块职责

```
main.py ──▶ game.py (状态机)
               │
               ├──▶ board.py    棋盘数据（落子/悔棋/重置）
               ├──▶ rules.py    胜负判定
               ├──▶ ai.py       AI 对手
               ├──▶ renderer.py 界面渲染
               ├──▶ history.py  棋谱管理
               └──▶ paths.py    资源/用户数据路径
```

**`game.py` 状态机**：

```
         ┌──────────┐
         │   MENU   │
         └────┬─────┘
    ┌─────────┼──────────┐
    ▼         ▼          ▼
 PVP/PVE  DIFFICULTY   REPLAY_SELECT
    │         │          │
    ▼         ▼          ▼
 PLAYING ◀───┘      REPLAY ◀──▶ PLAYING (接管)
    │
    ▼
 GAME_OVER ──▶ MENU / PLAYING
```

---

## 棋谱格式

棋谱以 JSON 格式存储，结构清晰，易于编辑与分享：

```json
{
  "meta": {
    "date": "斜线妙杀——五十三手经典长局",
    "mode": "经典",
    "result": "黑胜",
    "total_moves": 35
  },
  "moves": [
    {"step": 1, "color": "black", "pos": [7, 7]},
    {"step": 2, "color": "white", "pos": [8, 8]}
  ]
}
```

坐标系以 15×15 棋盘左上角为 `[0, 0]`，天元位于 `[7, 7]`。

---

## 技术细节

<details>
<summary><b>AI 评估函数</b></summary>

棋型评分体系：

| 棋型 | 分值 | 说明 |
|------|-----:|------|
| 连五 | 1,000,000 | 五子连珠，直接获胜 |
| 活四 | 100,000 | 两端均开放的四连 |
| 冲四 | 10,000 | 一端被堵的四连 |
| 活三 | 5,000 | 两端均开放的三连 |
| 眠三 | 500 | 一端被堵的三连 |
| 活二 | 200 | 两端均开放的二连 |
| 眠二 | 50 | 一端被堵的二连 |

局面总分 = AI 棋型分 - 对手棋型分

</details>

<details>
<summary><b>候选点生成策略</b></summary>

1. 扫描棋盘，找出所有已有棋子
2. 对每颗棋子，取周围 2 格范围内的空位作为候选
3. 对候选点进行快速评估打分
4. 按分数降序排列，取前 N 个（N 由难度决定）

这一策略避免了遍历全部 225 个空位，将搜索空间压缩至 5~10 个高价值点。

</details>

<details>
<summary><b>渲染器特性</b></summary>

- 15×15 棋盘网格，带 A~O 列标和 1~15 行号
- 5 个星位标记（天元 + 四星）
- 黑白棋子带高光渐变效果
- 最后落子位置红色标记
- 悬停高亮按钮
- 游戏结束半透明遮罩弹窗
- 窗口缩放时等比缩放棋盘、侧栏、字体和鼠标坐标映射

</details>

<details>
<summary><b>资源路径与打包</b></summary>

- 开发环境下，内置棋谱从项目目录 `records/classic/` 读取
- PyInstaller 环境下，内置棋谱从 `_MEIPASS` 临时资源目录读取
- 用户保存棋谱始终写入可写目录：源码运行时为项目目录，打包运行时为 `gomoku.exe` 所在目录
- `gomoku.spec` 会收集 Pygame 数据文件，并打包经典棋谱资源

</details>

---

## 许可

MIT License

---

<div align="center">

**Built with Pygame**

</div>
