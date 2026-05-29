"""五子棋Pygame渲染器。纯显示，不含游戏逻辑。"""

import pygame
import os
from board import BOARD_SIZE, EMPTY, BLACK, WHITE

# 布局常量
WINDOW_W = 800
WINDOW_H = 700
BOARD_X = 30
BOARD_Y = 60
BOARD_PX = 560
CELL_SIZE = BOARD_PX // (BOARD_SIZE - 1)
TOP_BAR_H = 50
BOTTOM_BAR_H = 50

# 颜色定义
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
        self._font_cache = {}
        font_path = self._find_font()
        self.font_path = font_path

    @property
    def font_large(self):
        return self._font(32)

    @property
    def font_medium(self):
        return self._font(22)

    @property
    def font_small(self):
        return self._font(16)

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

    def _layout(self):
        win_w, win_h = self.screen.get_size()
        win_w = max(1, win_w)
        win_h = max(1, win_h)
        scale = max(0.01, min(win_w / WINDOW_W, win_h / WINDOW_H))
        scaled_w = max(1, int(round(WINDOW_W * scale)))
        scaled_h = max(1, int(round(WINDOW_H * scale)))
        rect = pygame.Rect((win_w - scaled_w) // 2, (win_h - scaled_h) // 2, scaled_w, scaled_h)
        return rect, scale

    def content_rect(self):
        rect, _ = self._layout()
        return rect

    def scale_x(self, x):
        rect, scale = self._layout()
        return int(round(rect.x + x * scale))

    def scale_y(self, y):
        rect, scale = self._layout()
        return int(round(rect.y + y * scale))

    def scale_rect(self, x, y, w, h):
        rect, scale = self._layout()
        return pygame.Rect(
            int(round(rect.x + x * scale)),
            int(round(rect.y + y * scale)),
            max(1, int(round(w * scale))),
            max(1, int(round(h * scale))),
        )

    def scale_len(self, value):
        _, scale = self._layout()
        return max(1, int(round(value * scale)))

    def _scale_len(self, value):
        return self.scale_len(value)

    def _font(self, base_size):
        size = max(8, int(round(base_size * self._layout()[1])))
        key = (base_size, size)
        if key not in self._font_cache:
            if self.font_path:
                self._font_cache[key] = pygame.font.Font(self.font_path, size)
            else:
                self._font_cache[key] = pygame.font.SysFont("microsoftyahei", size)
        return self._font_cache[key]

    def _grid_to_px(self, row, col):
        x = self.scale_x(BOARD_X + col * CELL_SIZE)
        y = self.scale_y(BOARD_Y + row * CELL_SIZE)
        return x, y

    def _px_to_grid(self, mx, my):
        rect, scale = self._layout()
        if not rect.collidepoint(mx, my):
            return None
        virtual_x = (mx - rect.x) / scale
        virtual_y = (my - rect.y) / scale
        col = round((virtual_x - BOARD_X) / CELL_SIZE)
        row = round((virtual_y - BOARD_Y) / CELL_SIZE)
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            gx, gy = self._grid_to_px(row, col)
            tolerance = self._scale_len(CELL_SIZE) // 2
            if abs(mx - gx) <= tolerance and abs(my - gy) <= tolerance:
                return row, col
        return None

    def draw_board(self):
        self.screen.fill(COLOR_BG)
        for i in range(BOARD_SIZE):
            x1, y1 = self._grid_to_px(i, 0)
            x2, y2 = self._grid_to_px(i, BOARD_SIZE - 1)
            pygame.draw.line(self.screen, COLOR_LINE, (x1, y1), (x2, y2), self._scale_len(1))
            x1, y1 = self._grid_to_px(0, i)
            x2, y2 = self._grid_to_px(BOARD_SIZE - 1, i)
            pygame.draw.line(self.screen, COLOR_LINE, (x1, y1), (x2, y2), self._scale_len(1))
        for r, c in STAR_POINTS:
            x, y = self._grid_to_px(r, c)
            pygame.draw.circle(self.screen, COLOR_STAR, (x, y), self._scale_len(4))
        for i in range(BOARD_SIZE):
            label = chr(ord('A') + i)
            x, _ = self._grid_to_px(0, i)
            text = self.font_small.render(label, True, COLOR_TEXT)
            self.screen.blit(text, (x - text.get_width() // 2, self.scale_y(BOARD_Y - 22)))
            _, y = self._grid_to_px(i, 0)
            text = self.font_small.render(str(i + 1), True, COLOR_TEXT)
            self.screen.blit(text, (self.scale_x(BOARD_X - 25), y - text.get_height() // 2))

    def draw_pieces(self, board, last_move=None):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = board.get(row, col)
                if color == EMPTY:
                    continue
                x, y = self._grid_to_px(row, col)
                radius = max(2, self._scale_len(CELL_SIZE // 2 - 2))
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
            pygame.draw.circle(self.screen, COLOR_LAST_MARKER, (x, y), self._scale_len(5))

    def draw_top_bar(self, current_player, mode_text):
        content = self.content_rect()
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, self.scale_rect(0, 0, WINDOW_W, TOP_BAR_H))
        title = self.font_large.render("五子棋对弈游戏", True, COLOR_TEXT)
        self.screen.blit(title, (self.scale_x(20), self.scale_y(8)))
        player_text = "⚫ 黑棋" if current_player == BLACK else "⚪ 白棋"
        player_surf = self.font_medium.render(f"当前玩家：{player_text}", True, COLOR_TEXT)
        self.screen.blit(player_surf, (content.right - player_surf.get_width() - self._scale_len(20), self.scale_y(14)))

    def draw_bottom_bar(self, status_text, step_count, mode_text):
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, self.scale_rect(0, WINDOW_H - BOTTOM_BAR_H, WINDOW_W, BOTTOM_BAR_H))
        text = self.font_medium.render(status_text, True, COLOR_TEXT)
        self.screen.blit(text, (self.scale_x(20), self.scale_y(WINDOW_H - BOTTOM_BAR_H + 14)))

    def draw_side_panel(self, buttons, step_count, mode_text):
        panel_x = BOARD_X + BOARD_PX + 30
        panel_w = WINDOW_W - panel_x - 10
        mouse_pos = pygame.mouse.get_pos()
        for i, (label, action) in enumerate(buttons):
            btn_y = BOARD_Y + i * 55
            btn_rect = self.scale_rect(panel_x, btn_y, panel_w, 42)
            hover = btn_rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=self._scale_len(8))
            text = self.font_medium.render(label, True, COLOR_BUTTON_TEXT)
            self.screen.blit(text, (btn_rect.centerx - text.get_width() // 2,
                                     btn_rect.centery - text.get_height() // 2))
        info_y = BOARD_Y + len(buttons) * 55 + 20
        pygame.draw.line(self.screen, COLOR_LINE, (self.scale_x(panel_x), self.scale_y(info_y)),
                         (self.scale_x(panel_x + panel_w), self.scale_y(info_y)), self._scale_len(1))
        info_y += 15
        step_text = self.font_small.render(f"步数：第 {step_count} 手", True, COLOR_TEXT)
        self.screen.blit(step_text, (self.scale_x(panel_x), self.scale_y(info_y)))
        info_y += 25
        mode_surf = self.font_small.render(f"模式：{mode_text}", True, COLOR_TEXT)
        self.screen.blit(mode_surf, (self.scale_x(panel_x), self.scale_y(info_y)))

    def get_button_at(self, buttons, pos):
        panel_x = BOARD_X + BOARD_PX + 30
        panel_w = WINDOW_W - panel_x - 10
        for i, (label, action) in enumerate(buttons):
            btn_y = BOARD_Y + i * 55
            btn_rect = self.scale_rect(panel_x, btn_y, panel_w, 42)
            if btn_rect.collidepoint(pos):
                return action
        return None

    def draw_menu(self, title, options, mouse_pos):
        self.screen.fill(COLOR_BG)
        content = self.content_rect()
        title_surf = self.font_large.render(title, True, COLOR_TEXT)
        self.screen.blit(title_surf, (content.centerx - title_surf.get_width() // 2, self.scale_y(150)))
        buttons = []
        for i, (label, value) in enumerate(options):
            btn_rect = self.scale_rect(WINDOW_W // 2 - 120, 250 + i * 60, 240, 45)
            hover = btn_rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=self._scale_len(10))
            text = self.font_medium.render(label, True, COLOR_BUTTON_TEXT)
            self.screen.blit(text, (btn_rect.centerx - text.get_width() // 2,
                                     btn_rect.centery - text.get_height() // 2))
            buttons.append((btn_rect, value))
        return buttons

    def draw_game_over(self, winner_text):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        box_rect = self.scale_rect(WINDOW_W // 2 - 180, WINDOW_H // 2 - 100, 360, 200)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, box_rect, border_radius=self._scale_len(12))
        pygame.draw.rect(self.screen, COLOR_LINE, box_rect, self._scale_len(2), border_radius=self._scale_len(12))
        text = self.font_large.render(winner_text, True, COLOR_TEXT)
        self.screen.blit(text, (box_rect.centerx - text.get_width() // 2,
                                 box_rect.y + self._scale_len(25)))
        btn_w, btn_h = self._scale_len(140), self._scale_len(42)
        gap = self._scale_len(20)
        btn_y = box_rect.y + self._scale_len(110)
        restart_rect = pygame.Rect(box_rect.centerx - btn_w - gap // 2, btn_y, btn_w, btn_h)
        menu_rect = pygame.Rect(box_rect.centerx + gap // 2, btn_y, btn_w, btn_h)
        mouse_pos = pygame.mouse.get_pos()
        for rect, label in [(restart_rect, "重新开始"), (menu_rect, "返回菜单")]:
            hover = rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pygame.draw.rect(self.screen, color, rect, border_radius=self._scale_len(8))
            t = self.font_medium.render(label, True, COLOR_BUTTON_TEXT)
            self.screen.blit(t, (rect.centerx - t.get_width() // 2,
                                  rect.centery - t.get_height() // 2))
        return restart_rect, menu_rect

    def draw_replay_bar(self, current_step, total_steps):
        bar_y = WINDOW_H - 60
        content = self.content_rect()
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, self.scale_rect(0, bar_y, WINDOW_W, 60))
        buttons = []
        labels = [("◀ 上一步", "prev"), ("▶ 下一步", "next"), ("⏯ 自动播放", "auto"), ("接管", "takeover")]
        for i, (label, action) in enumerate(labels):
            btn_rect = self.scale_rect(20 + i * 130, bar_y + 10, 115, 38)
            mouse_pos = pygame.mouse.get_pos()
            hover = btn_rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=self._scale_len(6))
            text = self.font_small.render(label, True, COLOR_BUTTON_TEXT)
            self.screen.blit(text, (btn_rect.centerx - text.get_width() // 2,
                                     btn_rect.centery - text.get_height() // 2))
            buttons.append((btn_rect, action))
        info = self.font_medium.render(f"第 {current_step} / {total_steps} 手", True, COLOR_TEXT)
        self.screen.blit(info, (content.right - info.get_width() - self._scale_len(20), self.scale_y(bar_y + 18)))
        return buttons
