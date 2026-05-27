"""五子棋胜负判定模块。"""

from board import BOARD_SIZE, EMPTY

# 四个方向：水平、垂直、左上-右下对角线、右上-左下对角线
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


def check_win(grid, row, col):
    """检查指定位置是否形成五子连珠，返回获胜方颜色。"""
    color = grid[row][col]
    if color == EMPTY:
        return None

    for dr, dc in DIRECTIONS:
        count = 1
        # 正向计数
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and grid[r][c] == color:
            count += 1
            r += dr
            c += dc
        # 反向计数
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and grid[r][c] == color:
            count += 1
            r -= dr
            c -= dc
        if count >= 5:
            return color

    return None


def check_draw(grid):
    """检查是否平局（棋盘已满）。"""
    for row in grid:
        for cell in row:
            if cell == EMPTY:
                return False
    return True
