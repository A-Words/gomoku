"""Board module: 15x15 grid, place/undo/reset, coordinate conversion."""

BOARD_SIZE = 15
EMPTY = 0
BLACK = 1
WHITE = 2


class Board:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.move_history = []

    def place(self, row, col, color):
        if not self.is_valid_move(row, col):
            return False
        self.grid[row][col] = color
        self.move_history.append((row, col, color))
        return True

    def undo(self):
        if not self.move_history:
            return None
        row, col, color = self.move_history.pop()
        self.grid[row][col] = EMPTY
        return (row, col, color)

    def is_valid_move(self, row, col):
        if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
            return False
        return self.grid[row][col] == EMPTY

    def is_full(self):
        for row in self.grid:
            for cell in row:
                if cell == EMPTY:
                    return False
        return True

    def get(self, row, col):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.grid[row][col]
        return None

    def last_move(self):
        if self.move_history:
            return self.move_history[-1][:2]
        return None

    def move_count(self):
        return len(self.move_history)
