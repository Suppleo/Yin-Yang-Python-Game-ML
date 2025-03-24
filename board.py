import numpy as np
import pygame

# Define puzzle levels with pre-filled cells
# 0 = black, 1 = white, 2 = empty (gray)
# Each level is a numpy array representing the initial state of the board
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
    # Special 10x10 level
    6: np.array([
        [1, 2, 0, 2, 2, 2, 2, 2, 2, 0],
        [2, 0, 2, 2, 2, 2, 2, 2, 1, 2],
        [2, 2, 0, 2, 0, 0, 0, 2, 2, 1],
        [2, 0, 2, 0, 2, 2, 2, 2, 1, 2],
        [2, 2, 2, 2, 2, 0, 0, 2, 2, 2],
        [2, 2, 2, 2, 0, 2, 1, 2, 2, 2],
        [2, 2, 1, 2, 2, 2, 2, 1, 2, 2],
        [2, 2, 2, 2, 0, 1, 2, 2, 1, 2],
        [2, 2, 1, 2, 2, 1, 2, 2, 2, 2],
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    ], dtype=int),
}

class Board:
    def __init__(self, level=1):
        """
        Initialize a new game board with the specified level.
        
        Args:
            level (int): The puzzle level to load (1-6)
        """
        self.level = level
        self.grid = self.load_level(level)
        self.size = self.grid.shape[0]  # Get board size from grid dimensions
    
    def load_level(self, level):
        """
        Load a predefined puzzle based on level number.
        
        Args:
            level (int): The puzzle level to load
            
        Returns:
            numpy.ndarray: The initial grid for the selected level
        """
        return np.array(PUZZLE_LEVELS[level], dtype=int)

    def set_level(self, level):
        """
        Change the current level and reload the board.
        
        Args:
            level (int): The new puzzle level to load
        """
        self.level = level
        self.grid = self.load_level(level)
        self.size = self.grid.shape[0]  # Update size when level changes

    def check_2x2_blocks(self):
        """
        Check for invalid 2x2 blocks of the same color (not allowed in Yin-Yang).
        
        Returns:
            set: Coordinates of cells that are part of invalid 2x2 blocks
        """
        invalid_cells = set()
        for r in range(self.size-1):
            for c in range(self.size-1):
                # Check 2x2 block
                block = self.grid[r:r+2, c:c+2]
                if np.all(block == 0) or np.all(block == 1):
                    invalid_cells.update([(r,c), (r,c+1), (r+1,c), (r+1,c+1)])
        return invalid_cells

    def check_consecutive_blocks(self):
        """
        Check if all cells of the same color form a single connected group.
        Uses flood fill algorithm to count connected regions.
        
        Returns:
            bool: True if both black and white cells form single connected groups
        """
        def flood_fill(r, c, color, visited):
            """
            Recursive flood fill to count connected cells of the same color.
            
            Args:
                r, c (int): Current cell coordinates
                color (int): Color to check (0=black, 1=white)
                visited (set): Set of already visited cells
                
            Returns:
                int: Number of connected cells of the specified color
            """
            if (r < 0 or r >= self.size or c < 0 or c >= self.size or 
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
        
        for r in range(self.size):
            for c in range(self.size):
                if (r,c) not in visited:
                    if self.grid[r,c] == 0:
                        black_regions.append(flood_fill(r, c, 0, visited))
                    elif self.grid[r,c] == 1:
                        white_regions.append(flood_fill(r, c, 1, visited))
        
        # Valid board has exactly one black region and one white region
        return len(black_regions) == 1 and len(white_regions) == 1

    def check_win_condition(self):
        """
        Check if the current board state is a winning solution.
        A valid solution must:
        1. Have no empty cells
        2. Have no 2x2 blocks of the same color
        3. Have all cells of each color connected
        
        Returns:
            str: "WIN" if the board is solved, error message if invalid, None if incomplete
        """
        # Check if board is full
        if not np.any(self.grid == 2):
            if self.check_2x2_blocks():
                return "Invalid: 2x2 blocks detected"
            elif not self.check_consecutive_blocks():
                return "Invalid: Regions must be connected"
            else:
                return "WIN"
        return None
