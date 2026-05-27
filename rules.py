"""Win/draw detection for Gomoku."""

from board import BOARD_SIZE, EMPTY

DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


def check_win(grid, row, col):
    color = grid[row][col]
    if color == EMPTY:
        return None

    for dr, dc in DIRECTIONS:
        count = 1
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and grid[r][c] == color:
            count += 1
            r += dr
            c += dc
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and grid[r][c] == color:
            count += 1
            r -= dr
            c -= dc
        if count >= 5:
            return color

    return None


def check_draw(grid):
    for row in grid:
        for cell in row:
            if cell == EMPTY:
                return False
    return True
