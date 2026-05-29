# 五子棋

一个基于 Python + Pygame 的五子棋桌面游戏，支持双人对弈、人机对战、悔棋、棋谱保存与回放，并内置经典棋谱示例。

## 功能特性

- 15x15 标准五子棋棋盘
- 双人对弈模式
- 人机对战模式，包含简单、中等、困难三档 AI 难度
- AI 使用 Minimax 搜索与 Alpha-Beta 剪枝，并带候选点剪枝
- 每步落子自动记录，可保存为 JSON 棋谱
- 支持内置经典棋谱回放、上一步、下一步、自动播放和接管对弈
- 支持悔棋、重新开始、返回菜单
- 支持拖拽调整大小的 Pygame 窗口，木质棋盘视觉风格
- 支持 PyInstaller 打包为 Windows 可执行文件

## 运行环境

- Windows
- Python 3.10 或更高版本
- pip

项目依赖见 [requirements.txt](requirements.txt)：

```txt
pygame-ce>=2.5.7
pyinstaller>=6.13
```

## 快速开始

### 1. 创建虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. 安装依赖

```powershell
python -m pip install -r requirements.txt
```

### 3. 启动游戏

可以直接运行 Python 入口：

```powershell
python main.py
```

也可以双击或执行项目内的批处理脚本：

```powershell
.\run.bat
```

`run.bat` 会自动检查 Python 版本和运行依赖。如果缺少依赖，请先执行安装命令。

## 打包

项目已提供 PyInstaller 配置 [gomoku.spec](gomoku.spec) 和构建脚本 [build.bat](build.bat)。

```powershell
.\build.bat
```

构建成功后，可执行文件会生成在：

```txt
dist\gomoku.exe
```

打包时会把 `records/classic` 中的内置经典棋谱一起带入程序资源。

## 游戏说明

### 主菜单

- `双人对弈`：黑白双方轮流由玩家落子
- `人机对战`：玩家执黑先手，AI 执白后手
- `棋谱回放`：选择内置或已保存的棋谱进行回放

### 对弈操作

- 鼠标点击棋盘交叉点落子
- `悔 棋`：撤销上一步；人机模式会撤销玩家和 AI 各一步
- `重新开始`：重置当前模式并开始新局
- `保存棋谱`：保存当前对局记录
- `返回菜单`：回到主菜单

游戏结束后：

- 按 `R` 重新开始
- 按 `M` 返回主菜单

### 棋谱回放

回放界面支持：

- `上一步`
- `下一步`
- `自动播放`
- `接管`：从当前回放局面继续双人对弈

## 项目结构

```txt
.
├── main.py                         # 游戏入口
├── game.py                         # 游戏状态机与主循环
├── board.py                        # 棋盘数据结构、落子、悔棋
├── rules.py                        # 五子连珠和平局判定
├── ai.py                           # AI 对手与局面评估
├── renderer.py                     # Pygame 绘制逻辑
├── history.py                      # 棋谱保存、加载、回放控制
├── paths.py                        # 开发环境与打包环境的路径处理
├── requirements.txt                # Python 依赖
├── run.bat                         # Windows 启动脚本
├── build.bat                       # Windows 打包脚本
├── gomoku.spec                     # PyInstaller 配置
├── records
│   └── classic                     # 内置经典棋谱
└── docs
    └── superpowers                 # 设计规格与实现计划
```

## 棋谱文件

棋谱使用 JSON 格式保存，结构示例：

```json
{
  "meta": {
    "date": "2026-05-29 22:30",
    "mode": "pvp",
    "difficulty": "",
    "result": "黑胜",
    "total_moves": 9
  },
  "moves": [
    {
      "step": 1,
      "color": "black",
      "pos": [7, 7]
    }
  ]
}
```

棋谱目录：

- 内置棋谱：`records/classic`
- 用户保存棋谱：`records/saved`

开发环境下，保存的棋谱会写入项目目录的 `records/saved`。打包为 exe 后，保存的棋谱会写入 exe 所在目录旁边的 `records/saved`。

## 开发说明

核心模块职责清晰分离：

- `Board` 只维护棋盘数据和落子历史
- `rules.py` 只负责胜负和平局判断
- `Renderer` 只负责绘制界面，不处理业务逻辑
- `AI` 只根据当前棋盘返回落子坐标
- `Game` 负责状态流转、事件处理和模块调度
- `GameRecord` 与 `ReplayController` 负责棋谱序列化和回放状态

如果只修改规则或 AI，可优先从 [rules.py](rules.py) 和 [ai.py](ai.py) 入手；如果要调整界面布局或按钮样式，主要修改 [renderer.py](renderer.py)。

## 常见问题

### 提示未检测到 Python

请安装 Python 3.10 或更高版本，并在安装时勾选 `Add python.exe to PATH`。

### 提示缺少运行依赖

执行：

```powershell
python -m pip install -r requirements.txt
```

### 中文字体显示异常

程序会优先查找 Windows 系统字体，例如微软雅黑或黑体。如果在非 Windows 环境运行，可能需要调整 [renderer.py](renderer.py) 中的字体查找逻辑。

### 打包失败

先确认依赖已安装：

```powershell
python -m pip install -r requirements.txt
```

然后重新执行：

```powershell
.\build.bat
```
