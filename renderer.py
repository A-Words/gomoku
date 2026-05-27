"""Pygame renderer for Gomoku. Pure display, no game logic."""

import pygame
import os
from board import BOARD_SIZE, EMPTY, BLACK, WHITE

# Layout constants
WINDOW_W = 800
WINDOW_H = 700
BOARD_X = 30
BOARD_Y = 60
BOARD_PX = 560
CELL_SIZE = BOARD_PX // (BOARD_SIZE - 1)
TOP_BAR_H = 50
BOTTOM_BAR_H = 50

# Colors
COLOR_BG = (222, 184, 104)
COLOR_LINE = (92, 74, 30)
COLOR_STAR = (92, 74, 30)
COLOR_BLACK_PIECE = (30, 30, 30)
COLOR_BLACK_HIGHLIGHT = (80, 80, 80)
COLOR_WHITE_PIECE = (240, 240, 235)
COLOR_WHITE_BORDER = (180, 180, 180)
COLOR_WHITE_HIGHLIGHT = (255, 255, 255)
COLOR_LAST_MARKER = (220, 50, 50)
COLOR_PANEL_BG = (200, 168, 90)
COLOR_BUTTON = (160, 130, 60)
COLOR_BUTTON_HOVER = (180, 150, 80)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_TEXT = (60, 45, 15)
COLOR_TEXT_LIGHT = (255, 255, 255)

STAR_POINTS = [(7, 7), (3, 3), (3, 11), (11, 3), (11, 11)]


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        font_path = self._find_font()
        if font_path:
            self.font_large = pygame.font.Font(font_path, 32)
            self.font_medium = pygame.font.Font(font_path, 22)
            self.font_small = pygame.font.Font(font_path, 16)
        else:
            self.font_large = pygame.font.SysFont("microsoftyahei", 32)
            self.font_medium = pygame.font.SysFont("microsoftyahei", 22)
            self.font_small = pygame.font.SysFont("microsoftyahei", 16)

    def _find_font(self):
        candidates = [
            "assets/fonts/msyh.ttc",
            "assets/fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def _grid_to_px(self, row, col):
        x = BOARD_X + col * CELL_SIZE
        y = BOARD_Y + row * CELL_SIZE
        return x, y

    def _px_to_grid(self, mx, my):
        col = round((mx - BOARD_X) / CELL_SIZE)
        row = round((my - BOARD_Y) / CELL_SIZE)
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            gx, gy = self._grid_to_px(row, col)
            if abs(mx - gx) <= CELL_SIZE // 2 and abs(my - gy) <= CELL_SIZE // 2:
                return row, col
        return None

    def draw_board(self):
        self.screen.fill(COLOR_BG)
        for i in range(BOARD_SIZE):
            x1, y1 = self._grid_to_px(i, 0)
            x2, y2 = self._grid_to_px(i, BOARD_SIZE - 1)
            pygame.draw.line(self.screen, COLOR_LINE, (x1, y1), (x2, y2), 1)
            x1, y1 = self._grid_to_px(0, i)
            x2, y2 = self._grid_to_px(BOARD_SIZE - 1, i)
            pygame.draw.line(self.screen, COLOR_LINE, (x1, y1), (x2, y2), 1)
        for r, c in STAR_POINTS:
            x, y = self._grid_to_px(r, c)
            pygame.draw.circle(self.screen, COLOR_STAR, (x, y), 4)
        for i in range(BOARD_SIZE):
            label = chr(ord('A') + i)
            x, _ = self._grid_to_px(0, i)
            text = self.font_small.render(label, True, COLOR_TEXT)
            self.screen.blit(text, (x - text.get_width() // 2, BOARD_Y - 22))
            _, y = self._grid_to_px(i, 0)
            text = self.font_small.render(str(i + 1), True, COLOR_TEXT)
            self.screen.blit(text, (BOARD_X - 25, y - text.get_height() // 2))

    def draw_pieces(self, board, last_move=None):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = board.get(row, col)
                if color == EMPTY:
                    continue
                x, y = self._grid_to_px(row, col)
                radius = CELL_SIZE // 2 - 2
                if color == BLACK:
                    pygame.draw.circle(self.screen, COLOR_BLACK_PIECE, (x, y), radius)
                    hx, hy = x - radius // 3, y - radius // 3
                    pygame.draw.circle(self.screen, COLOR_BLACK_HIGHLIGHT, (hx, hy), radius // 3)
                else:
                    pygame.draw.circle(self.screen, COLOR_WHITE_PIECE, (x, y), radius)
                    pygame.draw.circle(self.screen, COLOR_WHITE_BORDER, (x, y), radius, 1)
                    hx, hy = x - radius // 3, y - radius // 3
                    pygame.draw.circle(self.screen, COLOR_WHITE_HIGHLIGHT, (hx, hy), radius // 3)
        if last_move:
            r, c = last_move
            x, y = self._grid_to_px(r, c)
            pygame.draw.circle(self.screen, COLOR_LAST_MARKER, (x, y), 5)

    def draw_top_bar(self, current_player, mode_text):
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, (0, 0, WINDOW_W, TOP_BAR_H))
        title = self.font_large.render("五子棋对弈游戏", True, COLOR_TEXT)
        self.screen.blit(title, (20, 8))
        player_text = "⚫ 黑棋" if current_player == BLACK else "⚪ 白棋"
        player_surf = self.font_medium.render(f"当前玩家：{player_text}", True, COLOR_TEXT)
        self.screen.blit(player_surf, (WINDOW_W - player_surf.get_width() - 20, 14))

    def draw_bottom_bar(self, status_text, step_count, mode_text):
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, (0, WINDOW_H - BOTTOM_BAR_H, WINDOW_W, BOTTOM_BAR_H))
        text = self.font_medium.render(status_text, True, COLOR_TEXT)
        self.screen.blit(text, (20, WINDOW_H - BOTTOM_BAR_H + 14))

    def draw_side_panel(self, buttons, step_count, mode_text):
        panel_x = BOARD_X + BOARD_PX + 30
        panel_w = WINDOW_W - panel_x - 10
        mouse_pos = pygame.mouse.get_pos()
        for i, (label, action) in enumerate(buttons):
            btn_y = BOARD_Y + i * 55
            btn_rect = pygame.Rect(panel_x, btn_y, panel_w, 42)
            hover = btn_rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=8)
            text = self.font_medium.render(label, True, COLOR_BUTTON_TEXT)
            self.screen.blit(text, (btn_rect.centerx - text.get_width() // 2,
                                     btn_rect.centery - text.get_height() // 2))
        info_y = BOARD_Y + len(buttons) * 55 + 20
        pygame.draw.line(self.screen, COLOR_LINE, (panel_x, info_y),
                         (panel_x + panel_w, info_y), 1)
        info_y += 15
        step_text = self.font_small.render(f"步数：第 {step_count} 手", True, COLOR_TEXT)
        self.screen.blit(step_text, (panel_x, info_y))
        info_y += 25
        mode_surf = self.font_small.render(f"模式：{mode_text}", True, COLOR_TEXT)
        self.screen.blit(mode_surf, (panel_x, info_y))

    def get_button_at(self, buttons, pos):
        panel_x = BOARD_X + BOARD_PX + 30
        panel_w = WINDOW_W - panel_x - 10
        for i, (label, action) in enumerate(buttons):
            btn_y = BOARD_Y + i * 55
            btn_rect = pygame.Rect(panel_x, btn_y, panel_w, 42)
            if btn_rect.collidepoint(pos):
                return action
        return None

    def draw_menu(self, title, options, mouse_pos):
        self.screen.fill(COLOR_BG)
        title_surf = self.font_large.render(title, True, COLOR_TEXT)
        self.screen.blit(title_surf, (WINDOW_W // 2 - title_surf.get_width() // 2, 150))
        buttons = []
        for i, (label, value) in enumerate(options):
            btn_rect = pygame.Rect(WINDOW_W // 2 - 120, 250 + i * 60, 240, 45)
            hover = btn_rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=10)
            text = self.font_medium.render(label, True, COLOR_BUTTON_TEXT)
            self.screen.blit(text, (btn_rect.centerx - text.get_width() // 2,
                                     btn_rect.centery - text.get_height() // 2))
            buttons.append((btn_rect, value))
        return buttons

    def draw_game_over(self, winner_text):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        box_rect = pygame.Rect(WINDOW_W // 2 - 160, WINDOW_H // 2 - 80, 320, 160)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, box_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_LINE, box_rect, 2, border_radius=12)
        text = self.font_large.render(winner_text, True, COLOR_TEXT)
        self.screen.blit(text, (box_rect.centerx - text.get_width() // 2,
                                 box_rect.y + 30))
        hint = self.font_small.render("按 R 重新开始 | 按 M 返回菜单", True, COLOR_TEXT)
        self.screen.blit(hint, (box_rect.centerx - hint.get_width() // 2,
                                 box_rect.y + 110))

    def draw_replay_bar(self, current_step, total_steps):
        bar_y = WINDOW_H - 60
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, (0, bar_y, WINDOW_W, 60))
        buttons = []
        labels = [("◀ 上一步", "prev"), ("▶ 下一步", "next"), ("⏯ 自动播放", "auto"), ("接管", "takeover")]
        for i, (label, action) in enumerate(labels):
            btn_rect = pygame.Rect(20 + i * 130, bar_y + 10, 115, 38)
            mouse_pos = pygame.mouse.get_pos()
            hover = btn_rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=6)
            text = self.font_small.render(label, True, COLOR_BUTTON_TEXT)
            self.screen.blit(text, (btn_rect.centerx - text.get_width() // 2,
                                     btn_rect.centery - text.get_height() // 2))
            buttons.append((btn_rect, action))
        info = self.font_medium.render(f"第 {current_step} / {total_steps} 手", True, COLOR_TEXT)
        self.screen.blit(info, (WINDOW_W - info.get_width() - 20, bar_y + 18))
        return buttons
