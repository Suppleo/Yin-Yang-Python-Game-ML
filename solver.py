import numpy as np
from collections import deque
import pygame
from config import SIZE

class Solver:
    def __init__(self, board):
        self.board = board
        
    def is_valid_move(self, r, c, color):
        """Check if placing color at (r,c) creates valid board state"""
        if self.board.grid[r,c] != 2:  # Cell already filled
            return False
            
        # Try move
        self.board.grid[r,c] = color
        
        # Check 2x2 blocks
        valid = True
        if r < SIZE-1 and c < SIZE-1:
            block = self.board.grid[r:r+2, c:c+2]
            if np.all(block == color):
                valid = False
                
        # Check connectivity
        if valid:
            valid = self.check_connectivity()
            
        # Revert move
        self.board.grid[r,c] = 2
        return valid
        
    def check_connectivity(self):
        """Check if all same-colored cells are connected"""
        def flood_fill(r, c, color, visited):
            if (r,c) in visited or self.board.grid[r,c] != color:
                return 0
            visited.add((r,c))
            count = 1
            for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE:
                    count += flood_fill(nr, nc, color, visited)
            return count
            
        # Check each color's connectivity
        for color in [0, 1]:
            visited = set()
            regions = []
            for r in range(SIZE):
                for c in range(SIZE):
                    if self.board.grid[r,c] == color and (r,c) not in visited:
                        regions.append(flood_fill(r, c, color, visited))
            if len(regions) > 1:  # Multiple disconnected regions
                return False
                
        return True
        
    def bfs_solve(self):
        """Solve puzzle using BFS"""
        queue = deque([(self.board.grid.copy(), [])])
        visited = set()
        
        while queue:
            current_board, moves = queue.popleft()
            
            # Try each empty cell
            for r in range(SIZE):
                for c in range(SIZE):
                    if current_board[r,c] == 2:
                        for color in [0, 1]:
                            if self.is_valid_move(r, c, color):
                                new_board = current_board.copy()
                                new_board[r,c] = color
                                new_moves = moves + [(r,c,color)]
                                
                                # Check if solved
                                if not np.any(new_board == 2):
                                    # Apply solution
                                    for mr,mc,mcolor in new_moves:
                                        self.board.grid[mr,mc] = mcolor
                                    return True
                                
                                board_hash = str(new_board)
                                if board_hash not in visited:
                                    visited.add(board_hash)
                                    queue.append((new_board, new_moves))
        return False

