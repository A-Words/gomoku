"""AI对手模块：Minimax + Alpha-Beta剪枝，三档难度。"""

import random
from board import BOARD_SIZE, EMPTY, BLACK, WHITE

# 棋型评分
SCORES = {
    'five': 1000000,       # 连五
    'live_four': 100000,   # 活四
    'rush_four': 10000,    # 冲四
    'live_three': 5000,    # 活三
    'sleep_three': 500,    # 眠三
    'live_two': 200,       # 活二
    'sleep_two': 50,       # 眠二
}

# 难度配置
DIFFICULTY = {
    'easy': {'depth': 2, 'candidates': 5, 'randomize': True},
    'medium': {'depth': 4, 'candidates': 8, 'randomize': False},
    'hard': {'depth': 6, 'candidates': 15, 'randomize': False},
}

# 四个方向：水平、垂直、两条对角线
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


class AI:
    def __init__(self, color, difficulty='medium'):
        """初始化AI，color为AI执子颜色，difficulty为难度等级。"""
        self.color = color
        self.opponent = WHITE if color == BLACK else BLACK
        self.config = DIFFICULTY.get(difficulty, DIFFICULTY['medium'])

    def get_move(self, board):
        """获取AI的落子位置，返回(行, 列)元组。"""
        candidates = self._get_candidates(board)
        if not candidates:
            return (7, 7)  # 默认下天元

        if board.move_count() == 0:
            return (7, 7)  # 先手下天元

        best_score = float('-inf')
        best_moves = []

        for row, col in candidates:
            board.place(row, col, self.color)
            score = self._minimax(board, self.config['depth'] - 1, float('-inf'), float('inf'), False)
            board.undo()

            if score > best_score:
                best_score = score
                best_moves = [(row, col)]
            elif score == best_score:
                best_moves.append((row, col))

        # 简单模式加入随机性
        if self.config['randomize'] and len(best_moves) > 1:
            pool = best_moves[:min(len(best_moves), self.config['candidates'])]
            return random.choice(pool)

        return best_moves[0]

    def _minimax(self, board, depth, alpha, beta, is_maximizing):
        """Minimax搜索 + Alpha-Beta剪枝。"""
        # 检查终止状态
        last = board.last_move()
        if last:
            winner = self._check_win_fast(board.grid, last[0], last[1])
            if winner == self.color:
                return SCORES['five'] + depth
            elif winner == self.opponent:
                return -SCORES['five'] - depth

        if depth == 0 or board.is_full():
            return self._evaluate(board)

        candidates = self._get_candidates(board)

        if is_maximizing:
            max_eval = float('-inf')
            for row, col in candidates:
                board.place(row, col, self.color)
                eval_score = self._minimax(board, depth - 1, alpha, beta, False)
                board.undo()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta剪枝
            return max_eval
        else:
            min_eval = float('inf')
            for row, col in candidates:
                board.place(row, col, self.opponent)
                eval_score = self._minimax(board, depth - 1, alpha, beta, True)
                board.undo()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha剪枝
            return min_eval

    def _get_candidates(self, board):
        """获取候选落子位置（已有棋子周围2格范围内的空位）。"""
        candidates = set()
        range_limit = 2

        has_pieces = False
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board.grid[row][col] != EMPTY:
                    has_pieces = True
                    for dr in range(-range_limit, range_limit + 1):
                        for dc in range(-range_limit, range_limit + 1):
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                                if board.grid[nr][nc] == EMPTY:
                                    candidates.add((nr, nc))

        if not has_pieces:
            return [(7, 7)]

        # 按位置评分排序，取最优的N个候选
        scored = []
        for row, col in candidates:
            score = self._evaluate_position(board.grid, row, col)
            scored.append((score, row, col))

        scored.sort(reverse=True)
        limit = self.config['candidates']
        return [(r, c) for _, r, c in scored[:limit]]

    def _evaluate_position(self, grid, row, col):
        """快速评估某个位置的价值，用于候选点排序。"""
        score = 0
        for color in [self.color, self.opponent]:
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
                    score += SCORES['five']
                elif count == 4:
                    score += SCORES['live_three']
                elif count == 3:
                    score += SCORES['live_two']
        return score

    def _evaluate(self, board):
        """评估整个棋盘局面，返回AI优势分值。"""
        ai_score = 0
        opp_score = 0

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = board.grid[row][col]
                if color == EMPTY:
                    continue
                for dr, dc in DIRECTIONS:
                    # 只在一个方向上计数，避免重复
                    r, c = row - dr, col - dc
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board.grid[r][c] == color:
                        continue  # 跳过，这是连续棋型的延续

                    count = 0
                    open_ends = 0
                    r, c = row, col
                    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board.grid[r][c] == color:
                        count += 1
                        r += dr
                        c += dc

                    # 检查两端是否开放
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board.grid[r][c] == EMPTY:
                        open_ends += 1
                    r2, c2 = row - dr, col - dc
                    if 0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE and board.grid[r2][c2] == EMPTY:
                        open_ends += 1

                    pattern_score = self._pattern_score(count, open_ends)
                    if color == self.color:
                        ai_score += pattern_score
                    else:
                        opp_score += pattern_score

        return ai_score - opp_score

    def _pattern_score(self, count, open_ends):
        """根据棋子数量和开放端数计算棋型得分。"""
        if count >= 5:
            return SCORES['five']
        if open_ends == 0:
            return 0
        if count == 4:
            return SCORES['live_four'] if open_ends == 2 else SCORES['rush_four']
        if count == 3:
            return SCORES['live_three'] if open_ends == 2 else SCORES['sleep_three']
        if count == 2:
            return SCORES['live_two'] if open_ends == 2 else SCORES['sleep_two']
        return 10 if open_ends == 2 else 1

    def _check_win_fast(self, grid, row, col):
        """快速检查指定位置是否形成五子连珠。"""
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
