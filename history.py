"""棋谱系统：保存、加载、回放。"""

import json
import os
from datetime import datetime
from paths import resource_path, user_data_path

RECORDS_DIR = "records"
CLASSIC_DIR = resource_path(RECORDS_DIR, "classic")
SAVED_DIR = user_data_path(RECORDS_DIR, "saved")


class GameRecord:
    """棋谱记录类。"""

    def __init__(self):
        self.meta = {
            "date": "",
            "mode": "",
            "difficulty": "",
            "result": "",
            "total_moves": 0,
        }
        self.moves = []  # 落子记录列表

    def add_move(self, step, color, row, col):
        """添加一步落子记录。"""
        color_str = "black" if color == 1 else "white"  # BLACK=1, WHITE=2
        self.moves.append({"step": step, "color": color_str, "pos": [row, col]})

    def undo_moves(self, count):
        """撤销指定步数的记录。"""
        for _ in range(count):
            if self.moves:
                self.moves.pop()

    def set_meta(self, mode, difficulty="", result=""):
        """设置棋谱元信息。"""
        self.meta["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.meta["mode"] = mode
        self.meta["difficulty"] = difficulty
        self.meta["result"] = result
        self.meta["total_moves"] = len(self.moves)

    def to_dict(self):
        """转换为字典格式。"""
        self.meta["total_moves"] = len(self.moves)
        return {"meta": self.meta, "moves": self.moves}

    @classmethod
    def from_dict(cls, data):
        """从字典创建棋谱对象。"""
        record = cls()
        record.meta = data.get("meta", {})
        record.moves = data.get("moves", [])
        return record

    def save(self, filename=None):
        """保存棋谱到JSON文件。"""
        os.makedirs(SAVED_DIR, exist_ok=True)
        if not filename:
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
            mode = self.meta.get("mode", "game")
            filename = f"{ts}_{mode}.json"
        filepath = SAVED_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return str(filepath)

    @classmethod
    def load(cls, filepath):
        """从JSON文件加载棋谱。"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def list_saved(cls):
        """列出所有用户保存的棋谱。"""
        os.makedirs(SAVED_DIR, exist_ok=True)
        files = []
        for f in os.listdir(SAVED_DIR):
            if f.endswith(".json"):
                files.append(str(SAVED_DIR / f))
        files.sort(key=os.path.getmtime, reverse=True)
        return files

    @classmethod
    def list_classic(cls):
        """列出所有内置经典棋谱。"""
        if not CLASSIC_DIR.exists():
            return []
        files = []
        for f in os.listdir(CLASSIC_DIR):
            if f.endswith(".json"):
                files.append(str(CLASSIC_DIR / f))
        return files


class ReplayController:
    """棋谱回放控制器。"""

    def __init__(self, record):
        self.record = record
        self.current_step = 0
        self.total_steps = len(record.moves)
        self.auto_play = False
        self.auto_timer = 0

    def next_step(self):
        """前进到下一步。"""
        if self.current_step < self.total_steps:
            self.current_step += 1
            return self.record.moves[self.current_step - 1]
        return None

    def prev_step(self):
        """后退到上一步。"""
        if self.current_step > 0:
            self.current_step -= 1
            return True
        return False

    def get_moves_up_to_current(self):
        """获取到当前步为止的所有落子。"""
        return self.record.moves[:self.current_step]

    def toggle_auto_play(self):
        """切换自动播放状态。"""
        self.auto_play = not self.auto_play
        self.auto_timer = 0
