"""棋盘模块：15x15网格，落子/悔棋/重置，坐标转换。"""

BOARD_SIZE = 15
EMPTY = 0
BLACK = 1
WHITE = 2


class Board:
    def __init__(self):
        self.reset()

    def reset(self):
        """重置棋盘。"""
        self.grid = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.move_history = []  # 落子历史记录

    def place(self, row, col, color):
        """在指定位置落子，返回是否成功。"""
        if not self.is_valid_move(row, col):
            return False
        self.grid[row][col] = color
        self.move_history.append((row, col, color))
        return True

    def undo(self):
        """悔棋，返回被移除的棋子信息。"""
        if not self.move_history:
            return None
        row, col, color = self.move_history.pop()
        self.grid[row][col] = EMPTY
        return (row, col, color)

    def is_valid_move(self, row, col):
        """检查落子是否合法（在棋盘内且为空位）。"""
        if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
            return False
        return self.grid[row][col] == EMPTY

    def is_full(self):
        """检查棋盘是否已满。"""
        for row in self.grid:
            for cell in row:
                if cell == EMPTY:
                    return False
        return True

    def get(self, row, col):
        """获取指定位置的棋子颜色。"""
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.grid[row][col]
        return None

    def last_move(self):
        """获取最后一步落子位置。"""
        if self.move_history:
            return self.move_history[-1][:2]  # (行, 列)
        return None

    def move_count(self):
        """获取总步数。"""
        return len(self.move_history)
