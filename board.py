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

    def check_2x2_blocks(self):
        invalid_cells = set()
        for r in range(SIZE-1):
            for c in range(SIZE-1):
                # Check 2x2 block
                block = self.grid[r:r+2, c:c+2]
                if np.all(block == 0) or np.all(block == 1):
                    invalid_cells.update([(r,c), (r,c+1), (r+1,c), (r+1,c+1)])
        return invalid_cells

    def check_consecutive_blocks(self):
        def flood_fill(r, c, color, visited):
            if (r < 0 or r >= SIZE or c < 0 or c >= SIZE or 
                (r,c) in visited or self.grid[r,c] != color):
                return 0
            visited.add((r,c))
            count = 1
            for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                count += flood_fill(r+dr, c+dc, color, visited)
            return count

        # Count black and white regions
        black_regions = []
        white_regions = []
        visited = set()
        
        for r in range(SIZE):
            for c in range(SIZE):
                if (r,c) not in visited:
                    if self.grid[r,c] == 0:
                        black_regions.append(flood_fill(r, c, 0, visited))
                    elif self.grid[r,c] == 1:
                        white_regions.append(flood_fill(r, c, 1, visited))
        
        return len(black_regions) == 1 and len(white_regions) == 1

    def check_win_condition(self):
        # Check if board is full
        if not np.any(self.grid == 2):
            if self.check_2x2_blocks():
                return "Invalid: 2x2 blocks detected"
            elif not self.check_consecutive_blocks():
                return "Invalid: Regions must be connected"
            else:
                return "WIN"
        return None