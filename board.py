import numpy as np
import pygame
from config import SIZE, CELL_SIZE, MARGIN, BLACK, WHITE, GRAY

# 0-black, 1-white, 2-gray
PUZZLE_LEVELS = {
    1: [
        [0, 2, 1, 2, 2, 2],
        [2, 2, 1, 1, 2, 2],
        [2, 2, 2, 2, 1, 2],
        [2, 1, 2, 2, 1, 2],
        [2, 2, 2, 0, 2, 2],
        [2, 2, 2, 2, 2, 2],
    ],
    2: [
        [1, 2, 1, 1, 2, 2],
        [2, 0, 2, 2, 0, 2],
        [2, 2, 2, 0, 0, 2],
        [1, 2, 2, 0, 2, 2],
        [2, 2, 0, 2, 2, 2],
        [2, 2, 2, 2, 2, 2],
    ],
    3: [
        [2, 2, 2, 0, 2, 2],
        [2, 0, 0, 2, 2, 2],
        [2, 0, 2, 0, 1, 2],
        [2, 0, 2, 1, 2, 2],
        [2, 2, 1, 2, 2, 2],
        [2, 2, 1, 0, 2, 2],
    ],
    4: [
        [2, 2, 0, 1, 2, 2],
        [2, 2, 2, 1, 2, 2],
        [2, 2, 1, 2, 0, 2],
        [2, 0, 2, 1, 2, 0],
        [2, 2, 1, 2, 2, 2],
        [2, 2, 2, 2, 2, 2],
    ],
    5: [
        [1, 2, 2, 2, 2, 2],
        [2, 1, 2, 0, 2, 1],
        [2, 1, 0, 2, 2, 2],
        [0, 1, 2, 2, 1, 2],
        [2, 2, 0, 1, 1, 2],
        [2, 2, 2, 2, 2, 2],
    ]
}

class Board:
    def __init__(self, level=1):
        self.level = level
        self.grid = self.load_level(level)
    
    def load_level(self, level):
        """Load a predefined puzzle based on level"""
        return np.array(PUZZLE_LEVELS[level], dtype=int)

    
    def draw(self, screen):
        screen.fill(GRAY)
        for r in range(SIZE):
            for c in range(SIZE):
                color = GRAY if self.grid[r, c] == 2 else (BLACK if self.grid[r, c] == 0 else WHITE)
                pygame.draw.rect(screen, color, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE - MARGIN, CELL_SIZE - MARGIN))
        pygame.display.flip()
    
    def set_level(self, level):
        self.level = level
        self.grid = self.load_level(level)
