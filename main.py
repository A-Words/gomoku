"""五子棋游戏主入口。"""

import pygame
import sys
from game import Game
from renderer import WINDOW_H, WINDOW_W


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
    pygame.display.set_caption("五子棋")
    game = Game(screen)
    game.run()


if __name__ == "__main__":
    main()
