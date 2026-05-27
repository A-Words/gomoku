"""五子棋游戏主入口。"""

import pygame
import sys
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("五子棋")
    game = Game(screen)
    game.run()


if __name__ == "__main__":
    main()
