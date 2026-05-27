"""游戏状态机与调度模块。"""

import os
import pygame
from board import Board, BLACK, WHITE, EMPTY
from rules import check_win, check_draw
from ai import AI
from history import GameRecord, ReplayController
from renderer import Renderer

# 游戏状态
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_DIFFICULTY = "difficulty"
STATE_REPLAY_SELECT = "replay_select"
STATE_REPLAY = "replay"
STATE_LOAD_SELECT = "load_select"


class Game:
    """游戏主类，管理状态机和各模块协调。"""

    def __init__(self, screen):
        self.screen = screen
        self.renderer = Renderer(screen)
        self.board = Board()
        self.state = STATE_MENU
        self.current_player = BLACK
        self.mode = None  # 'pvp' 或 'pve'
        self.difficulty = None
        self.ai = None
        self.winner = None
        self.status_text = ""
        self.record = GameRecord()
        self.replay_ctrl = None

    def run(self):
        """游戏主循环。"""
        clock = pygame.time.Clock()
        running = True
        auto_play_delay = 0

        while running:
            dt = clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if self.state == STATE_GAME_OVER:
                        if event.key == pygame.K_r:
                            self._restart()
                        elif event.key == pygame.K_m:
                            self._back_to_menu()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

            # 回放模式自动播放
            if self.state == STATE_REPLAY and self.replay_ctrl and self.replay_ctrl.auto_play:
                auto_play_delay += dt
                if auto_play_delay >= 800:  # 每步800毫秒
                    auto_play_delay = 0
                    move = self.replay_ctrl.next_step()
                    if move is None:
                        self.replay_ctrl.auto_play = False

            # 人机模式AI落子
            if self.state == STATE_PLAYING and self.mode == "pve" and self.current_player == self.ai.color:
                self._make_ai_move()

            # 绘制
            self._draw(mouse_pos)
            pygame.display.flip()

        pygame.quit()

    def _handle_click(self, pos):
        """处理鼠标点击事件。"""
        if self.state == STATE_MENU:
            self._handle_menu_click(pos)
        elif self.state == STATE_DIFFICULTY:
            self._handle_difficulty_click(pos)
        elif self.state == STATE_PLAYING:
            self._handle_play_click(pos)
        elif self.state == STATE_REPLAY_SELECT:
            self._handle_replay_select_click(pos)
        elif self.state == STATE_REPLAY:
            self._handle_replay_click(pos)
        elif self.state == STATE_LOAD_SELECT:
            self._handle_load_select_click(pos)

    def _handle_menu_click(self, pos):
        """处理主菜单点击。"""
        buttons = self.renderer.draw_menu("五子棋", [
            ("双人对弈", "pvp"),
            ("人机对战", "pve"),
            ("棋谱回放", "replay"),
        ], pos)
        for rect, value in buttons:
            if rect.collidepoint(pos):
                if value == "pvp":
                    self._start_pvp()
                elif value == "pve":
                    self.state = STATE_DIFFICULTY
                elif value == "replay":
                    self._show_replay_list()

    def _handle_difficulty_click(self, pos):
        """处理难度选择点击。"""
        buttons = self.renderer.draw_menu("选择难度", [
            ("简 单", "easy"),
            ("中 等", "medium"),
            ("困 难", "hard"),
        ], pos)
        for rect, value in buttons:
            if rect.collidepoint(pos):
                self._start_pve(value)

    def _handle_play_click(self, pos):
        """处理对弈中的点击。"""
        # 先检查侧边按钮
        buttons = self._get_play_buttons()
        action = self.renderer.get_button_at(buttons, pos)
        if action == "undo":
            self._undo()
            return
        elif action == "restart":
            self._restart()
            return
        elif action == "save":
            self._save_record()
            return
        elif action == "menu":
            self._back_to_menu()
            return

        # 检查棋盘点击
        grid_pos = self.renderer._px_to_grid(pos[0], pos[1])
        if grid_pos:
            row, col = grid_pos
            self._place_piece(row, col)

    def _handle_replay_select_click(self, pos):
        """处理棋谱选择点击。"""
        back_rect = pygame.Rect(20, 20, 80, 35)
        if back_rect.collidepoint(pos):
            self.state = STATE_MENU
            return

        records = GameRecord.list_classic() + GameRecord.list_saved()
        for i, filepath in enumerate(records):
            btn_rect = pygame.Rect(100, 100 + i * 50, 600, 40)
            if btn_rect.collidepoint(pos):
                self._start_replay(filepath)
                return

    def _handle_replay_click(self, pos):
        """处理回放模式点击。"""
        buttons = self.renderer.draw_replay_bar(
            self.replay_ctrl.current_step if self.replay_ctrl else 0,
            self.replay_ctrl.total_steps if self.replay_ctrl else 0
        )
        for rect, action in buttons:
            if rect.collidepoint(pos):
                if action == "prev":
                    self.replay_ctrl.prev_step()
                elif action == "next":
                    self.replay_ctrl.next_step()
                elif action == "auto":
                    self.replay_ctrl.toggle_auto_play()
                elif action == "takeover":
                    self._takeover_replay()
                return

    def _handle_load_select_click(self, pos):
        """处理加载棋谱选择点击。"""
        back_rect = pygame.Rect(20, 20, 80, 35)
        if back_rect.collidepoint(pos):
            self.state = STATE_MENU
            return

        records = GameRecord.list_saved()
        for i, filepath in enumerate(records):
            btn_rect = pygame.Rect(100, 100 + i * 50, 600, 40)
            if btn_rect.collidepoint(pos):
                self._load_and_resume(filepath)
                return

    def _start_pvp(self):
        """开始双人对弈。"""
        self.mode = "pvp"
        self.difficulty = None
        self.board.reset()
        self.current_player = BLACK
        self.winner = None
        self.record = GameRecord()
        self.state = STATE_PLAYING
        self.status_text = "黑棋落子..."

    def _start_pve(self, difficulty):
        """开始人机对战。"""
        self.mode = "pve"
        self.difficulty = difficulty
        self.board.reset()
        self.current_player = BLACK
        self.winner = None
        self.ai = AI(WHITE, difficulty)
        self.record = GameRecord()
        self.state = STATE_PLAYING
        self.status_text = "黑棋落子..."

    def _place_piece(self, row, col):
        """落子并检查胜负。"""
        if not self.board.place(row, col, self.current_player):
            return

        step = self.board.move_count()
        self.record.add_move(step, self.current_player, row, col)

        # 检查胜负
        winner = check_win(self.board.grid, row, col)
        if winner:
            self.winner = winner
            self._end_game()
            return

        # 检查平局
        if check_draw(self.board.grid):
            self.winner = "draw"
            self._end_game()
            return

        # 切换玩家
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        if self.current_player == BLACK:
            self.status_text = "黑棋落子..."
        else:
            self.status_text = "白棋落子..."

    def _make_ai_move(self):
        """AI落子。"""
        move = self.ai.get_move(self.board)
        if move:
            self._place_piece(move[0], move[1])

    def _undo(self):
        """悔棋。"""
        if self.board.move_count() == 0:
            return

        if self.mode == "pve":
            # 人机模式悔两步（AI + 玩家各一步）
            if self.board.move_count() >= 2:
                self.board.undo()
                self.board.undo()
                self.record.undo_moves(2)
                self.current_player = BLACK
                self.status_text = "黑棋落子..."
        else:
            self.board.undo()
            self.record.undo_moves(1)
            self.current_player = WHITE if self.current_player == BLACK else BLACK
            self.status_text = "黑棋落子..." if self.current_player == BLACK else "白棋落子..."

    def _restart(self):
        """重新开始。"""
        if self.mode == "pvp":
            self._start_pvp()
        elif self.mode == "pve":
            self._start_pve(self.difficulty)

    def _back_to_menu(self):
        """返回主菜单。"""
        self.state = STATE_MENU
        self.board.reset()
        self.winner = None

    def _end_game(self):
        """游戏结束处理。"""
        self.state = STATE_GAME_OVER
        if self.winner == "draw":
            self.status_text = "平局！"
            self.record.set_meta(self.mode, self.difficulty or "", "平局")
        elif self.winner == BLACK:
            self.status_text = "黑棋获胜！"
            self.record.set_meta(self.mode, self.difficulty or "", "黑胜")
        else:
            self.status_text = "白棋获胜！"
            self.record.set_meta(self.mode, self.difficulty or "", "白胜")

    def _save_record(self):
        """保存棋谱。"""
        filepath = self.record.save()
        self.status_text = f"已保存: {filepath}"

    def _show_replay_list(self):
        """显示棋谱列表。"""
        self.state = STATE_REPLAY_SELECT

    def _start_replay(self, filepath):
        """开始棋谱回放。"""
        record = GameRecord.load(filepath)
        self.replay_ctrl = ReplayController(record)
        self.board.reset()
        self.state = STATE_REPLAY

    def _takeover_replay(self):
        """从回放中途接管对弈。"""
        if not self.replay_ctrl:
            return
        self.board.reset()
        moves = self.replay_ctrl.get_moves_up_to_current()
        for move in moves:
            color = BLACK if move["color"] == "black" else WHITE
            r, c = move["pos"]
            self.board.place(r, c, color)

        self.mode = "pvp"
        self.current_player = BLACK if len(moves) % 2 == 0 else WHITE
        self.winner = None
        self.record = GameRecord()
        for move in moves:
            color = BLACK if move["color"] == "black" else WHITE
            self.record.add_move(move["step"], color, move["pos"][0], move["pos"][1])
        self.state = STATE_PLAYING
        self.status_text = "黑棋落子..." if self.current_player == BLACK else "白棋落子..."

    def _load_and_resume(self, filepath):
        """加载棋谱并继续对弈。"""
        record = GameRecord.load(filepath)
        self.board.reset()
        for move in record.moves:
            color = BLACK if move["color"] == "black" else WHITE
            r, c = move["pos"]
            self.board.place(r, c, color)
        self.record = record
        self.mode = "pvp"
        self.current_player = BLACK if len(record.moves) % 2 == 0 else WHITE
        self.winner = None
        self.state = STATE_PLAYING
        self.status_text = "黑棋落子..." if self.current_player == BLACK else "白棋落子..."

    def _get_play_buttons(self):
        """获取对弈界面的按钮列表。"""
        return [
            ("悔 棋", "undo"),
            ("重新开始", "restart"),
            ("保存棋谱", "save"),
            ("返回菜单", "menu"),
        ]

    def _draw(self, mouse_pos):
        """根据当前状态绘制界面。"""
        if self.state == STATE_MENU:
            self.renderer.draw_menu("五子棋", [
                ("双人对弈", "pvp"),
                ("人机对战", "pve"),
                ("棋谱回放", "replay"),
            ], mouse_pos)

        elif self.state == STATE_DIFFICULTY:
            self.renderer.draw_menu("选择难度", [
                ("简 单", "easy"),
                ("中 等", "medium"),
                ("困 难", "hard"),
            ], mouse_pos)

        elif self.state == STATE_PLAYING:
            self.renderer.draw_board()
            self.renderer.draw_pieces(self.board, self.board.last_move())
            mode_text = "双人对弈" if self.mode == "pvp" else f"人机-{self.difficulty}"
            self.renderer.draw_top_bar(self.current_player, mode_text)
            self.renderer.draw_bottom_bar(self.status_text, self.board.move_count(), mode_text)
            self.renderer.draw_side_panel(self._get_play_buttons(), self.board.move_count(), mode_text)

        elif self.state == STATE_GAME_OVER:
            self.renderer.draw_board()
            self.renderer.draw_pieces(self.board, self.board.last_move())
            mode_text = "双人对弈" if self.mode == "pvp" else f"人机-{self.difficulty}"
            self.renderer.draw_top_bar(self.current_player, mode_text)
            self.renderer.draw_bottom_bar(self.status_text, self.board.move_count(), mode_text)
            self.renderer.draw_side_panel(self._get_play_buttons(), self.board.move_count(), mode_text)
            self.renderer.draw_game_over(self.status_text)

        elif self.state == STATE_REPLAY_SELECT:
            self._draw_replay_list(mouse_pos)

        elif self.state == STATE_REPLAY:
            self._draw_replay(mouse_pos)

    def _draw_replay_list(self, mouse_pos):
        """绘制棋谱选择列表。"""
        self.screen.fill((222, 184, 104))
        title = self.renderer.font_large.render("选择棋谱", True, (60, 45, 15))
        self.screen.blit(title, (400 - title.get_width() // 2, 40))

        # 返回按钮
        back_rect = pygame.Rect(20, 20, 80, 35)
        pygame.draw.rect(self.screen, (160, 130, 60), back_rect, border_radius=6)
        text = self.renderer.font_small.render("返回", True, (255, 255, 255))
        self.screen.blit(text, (back_rect.centerx - text.get_width() // 2,
                                 back_rect.centery - text.get_height() // 2))

        records = GameRecord.list_classic() + GameRecord.list_saved()
        if not records:
            empty = self.renderer.font_medium.render("暂无棋谱", True, (60, 45, 15))
            self.screen.blit(empty, (400 - empty.get_width() // 2, 200))
            return

        for i, filepath in enumerate(records):
            btn_rect = pygame.Rect(100, 100 + i * 50, 600, 40)
            hover = btn_rect.collidepoint(mouse_pos)
            color = (180, 150, 80) if hover else (160, 130, 60)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=6)
            name = os.path.basename(filepath)
            text = self.renderer.font_small.render(name, True, (255, 255, 255))
            self.screen.blit(text, (btn_rect.x + 15, btn_rect.centery - text.get_height() // 2))

    def _draw_replay(self, mouse_pos):
        """绘制回放界面。"""
        # 从回放记录重建棋盘
        self.board.reset()
        if self.replay_ctrl:
            moves = self.replay_ctrl.get_moves_up_to_current()
            for move in moves:
                color = BLACK if move["color"] == "black" else WHITE
                r, c = move["pos"]
                self.board.place(r, c, color)

        last = self.board.last_move()
        self.renderer.draw_board()
        self.renderer.draw_pieces(self.board, last)

        # 标题栏
        pygame.draw.rect(self.screen, (200, 168, 90), (0, 0, 800, 50))
        title = self.renderer.font_large.render("棋谱回放", True, (60, 45, 15))
        self.screen.blit(title, (20, 8))

        # 回放控制栏
        if self.replay_ctrl:
            self.renderer.draw_replay_bar(self.replay_ctrl.current_step, self.replay_ctrl.total_steps)
