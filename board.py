import numpy as np
import pygame
from config import SIZE, CELL_SIZE, MARGIN, BLACK, WHITE, GRAY

# 0-black, 1-white, 2-gray
PUZZLE_LEVELS = {
    1: np.array([
        [0, 2, 1, 2, 2, 2],
        [2, 2, 1, 1, 2, 2],
        [2, 2, 2, 2, 1, 2],
        [2, 1, 2, 2, 1, 2],
        [2, 2, 2, 0, 2, 2],
        [2, 2, 2, 2, 2, 2],
    ], dtype=int),
    2: np.array([
        [1, 2, 1, 1, 2, 2],
        [2, 0, 2, 2, 0, 2],
        [2, 2, 2, 0, 0, 2],
        [1, 2, 2, 0, 2, 2],
        [2, 2, 0, 2, 2, 2],
        [2, 2, 2, 2, 2, 2],
    ], dtype=int),
    3: np.array([
        [2, 2, 2, 0, 2, 2],
        [2, 0, 0, 2, 2, 2],
        [2, 0, 2, 0, 1, 2],
        [2, 0, 2, 1, 2, 2],
        [2, 2, 1, 2, 2, 2],
        [2, 2, 1, 0, 2, 2],
    ], dtype=int),
    4: np.array([
        [2, 2, 0, 1, 2, 2],
        [2, 2, 2, 1, 2, 2],
        [2, 2, 1, 2, 0, 2],
        [2, 0, 2, 1, 2, 0],
        [2, 2, 1, 2, 2, 2],
        [2, 2, 2, 2, 2, 2],
    ], dtype=int),
    5: np.array([
        [1, 2, 2, 2, 2, 2],
        [2, 1, 2, 0, 2, 1],
        [2, 1, 0, 2, 2, 2],
        [0, 1, 2, 2, 1, 2],
        [2, 2, 0, 1, 1, 2],
        [2, 2, 2, 2, 2, 2],
    ], dtype=int),
}

class Board:
    def __init__(self, level=1):
        self.level = level
        self.grid = self.load_level(level)
    
    def load_level(self, level):
        """Load a predefined puzzle based on level"""
        return np.array(PUZZLE_LEVELS[level], dtype=int)

    def set_level(self, level):
        self.level = level
        self.grid = self.load_level(level)
