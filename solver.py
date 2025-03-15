import numpy as np
from collections import deque
import heapq
import random
from config import SIZE

class Solver:
    def __init__(self, board, fixed_cells):
        self.board = board
        self.fixed_cells = fixed_cells  # Cells that cannot be changed
        self.draw_callback = None  # Will be set by UI

    def is_valid_move(self, r, c, color):
        """Check if placing `color` at (r, c) is valid."""
        if self.board.grid[r, c] != 2:  # Ensure the cell is empty
            return False
        
        # Temporarily place the move
        self.board.grid[r, c] = color
        
        # Use Board's check_2x2_blocks() to ensure no 2x2 monochrome blocks
        invalid_cells = self.board.check_2x2_blocks()
        if (r, c) in invalid_cells:
            self.board.grid[r, c] = 2  # Revert move
            return False
        
        # Check connectivity **only when the board is full**
        if not np.any(self.board.grid == 2):
            if not self.board.check_consecutive_blocks():
                self.board.grid[r, c] = 2  # Revert move
                return False
        
        self.board.grid[r, c] = 2  # Revert move
        return True

    def check_2x2_cross(self, grid=None):
        """Check for forbidden 2x2 crosses of black and white."""
        if grid is None:
            grid = self.board.grid
            
        for r in range(grid.shape[0] - 1):
            for c in range(grid.shape[1] - 1):
                block = grid[r:r+2, c:c+2].flatten()
                if sorted(block) == [0, 0, 1, 1]:  # A cross shape
                    # Check if it's a checkerboard pattern (diagonal cells match)
                    if (grid[r, c] == grid[r+1, c+1] and 
                        grid[r, c+1] == grid[r+1, c] and
                        grid[r, c] != grid[r, c+1]):
                        return False
        return True

    def count_filled_neighbors(self, r, c, grid=None):
        """Count how many adjacent cells are already filled."""
        if grid is None:
            grid = self.board.grid
            
        count = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1] and grid[nr, nc] != 2:
                count += 1
        return count

    def is_single_connected_group(self, grid, color):
        """Check if all cells of `color` are part of a single connected group using BFS."""
        visited = set()
        start = None

        # Find a starting point for BFS
        for r in range(grid.shape[0]):
            for c in range(grid.shape[1]):
                if grid[r, c] == color:
                    start = (r, c)
                    break
            if start:
                break

        if not start:
            return True  # No cells of this color exist yet

        queue = [start]
        visited.add(start)

        while queue:
            r, c = queue.pop(0)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                    if (nr, nc) not in visited and grid[nr, nc] == color:
                        visited.add((nr, nc))
                        queue.append((nr, nc))

        # Check if all cells of the given color were visited
        total_cells = np.count_nonzero(grid == color)
        return len(visited) == total_cells

    def calculate_heuristic(self, grid):
        """Calculate heuristic value for A* search."""
        # Count empty cells - fewer is better
        empty_count = np.count_nonzero(grid == 2)
        
        # Check for 2x2 blocks of same color - penalize heavily
        invalid_cells = set()
        for r in range(SIZE-1):
            for c in range(SIZE-1):
                block = grid[r:r+2, c:c+2]
                if np.all(block == 0) or np.all(block == 1):
                    invalid_cells.update([(r,c), (r,c+1), (r+1,c), (r+1,c+1)])
        invalid_blocks_penalty = len(invalid_cells) * 10
        
        # Check for connectivity - penalize disconnected regions
        connectivity_penalty = 0
        if np.count_nonzero(grid == 0) > 0 and not self.is_single_connected_group(grid, 0):
            connectivity_penalty += 20
        if np.count_nonzero(grid == 1) > 0 and not self.is_single_connected_group(grid, 1):
            connectivity_penalty += 20
        
        # Check for bounded regions - penalize heavily
        bounded_regions_penalty = 0
        if self.has_bounded_regions(grid):
            bounded_regions_penalty = 50
        
        # Check for balance between black and white - slight penalty for imbalance
        black_count = np.count_nonzero(grid == 0)
        white_count = np.count_nonzero(grid == 1)
        balance_penalty = abs(black_count - white_count)
        
        # Check for 2x2 cross patterns
        cross_penalty = 0 if self.check_2x2_cross(grid) else 15
        
        # Combine all factors
        return empty_count + invalid_blocks_penalty + connectivity_penalty + bounded_regions_penalty + balance_penalty + cross_penalty

    def has_bounded_regions(self, grid):
        """
        Check if there are bounded regions that can never be connected.
        A bounded region is a set of empty cells surrounded by cells of the opposite color,
        making it impossible for a color to maintain connectivity.
        """
        # For each color, find all regions and check if any are bounded
        for color in [0, 1]:
            opposite_color = 1 - color
            
            # Find all empty cells
            empty_cells = set(map(tuple, np.argwhere(grid == 2)))
            if not empty_cells:
                continue
                
            # Find all regions of this color
            color_regions = self.find_regions(grid, color)
            
            # If there's more than one region, check if they can be connected
            if len(color_regions) > 1:
                # For each pair of regions, check if they can be connected
                for i in range(len(color_regions)):
                    for j in range(i+1, len(color_regions)):
                        # If these regions can't be connected, the board is invalid
                        if not self.can_regions_connect(grid, color_regions[i], color_regions[j], empty_cells, opposite_color):
                            return True
        
        return False

    def find_regions(self, grid, color):
        """Find all connected regions of a specific color."""
        regions = []
        visited = set()
        
        for r in range(grid.shape[0]):
            for c in range(grid.shape[1]):
                if grid[r, c] == color and (r, c) not in visited:
                    # Start a new region
                    region = set()
                    queue = [(r, c)]
                    visited.add((r, c))
                    
                    while queue:
                        curr_r, curr_c = queue.pop(0)
                        region.add((curr_r, curr_c))
                        
                        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                            nr, nc = curr_r + dr, curr_c + dc
                            if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                                if grid[nr, nc] == color and (nr, nc) not in visited:
                                    visited.add((nr, nc))
                                    queue.append((nr, nc))
                    
                    regions.append(region)
        
        return regions

    def can_regions_connect(self, grid, region1, region2, empty_cells, blocking_color):
        """
        Check if two regions of the same color can be connected through empty cells
        without being blocked by cells of the opposite color.
        """
        # Create a set of cells that can't be used for the path (cells of the opposite color)
        blocked_cells = set(map(tuple, np.argwhere(grid == blocking_color)))
        
        # Use BFS to find a path from region1 to region2 through empty cells
        visited = set()
        queue = list(region1)
        visited.update(region1)
        
        while queue:
            r, c = queue.pop(0)
            
            # Check if we've reached region2
            for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                    if (nr, nc) in region2:
                        return True  # Found a direct connection
            
            # Add empty neighbors to the queue
            for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                    if (nr, nc) in empty_cells and (nr, nc) not in visited and (nr, nc) not in blocked_cells:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        
        # If we've exhausted all possible paths and haven't reached region2, they can't be connected
        return False

    def get_preferred_colors(self, r, c, grid):
        """Determine which color to try first based on surrounding cells."""
        # Count adjacent cells of each color
        black_count = 0
        white_count = 0
        
        for dr, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                if grid[nr, nc] == 0:
                    black_count += 1
                elif grid[nr, nc] == 1:
                    white_count += 1
        
        # If more black neighbors, try white first to avoid 2x2 blocks
        if black_count > white_count:
            return [1, 0]
        # If more white neighbors, try black first
        elif white_count > black_count:
            return [0, 1]
        # If equal, try both
        else:
            return [0, 1]

    def a_star_solve(self):
        """Solve the board using A* search with improved heuristics and bounded region detection."""
        # Initialize visited states set to avoid revisiting
        visited = set()
        
        # Priority queue for A* search
        pq = []
        
        # Initial state
        initial_state = self.board.grid.copy()
        initial_state_tuple = tuple(map(tuple, initial_state))
        
        # Use a counter to break ties and ensure unique comparison
        counter = 0
        heapq.heappush(pq, (self.calculate_heuristic(initial_state), counter, initial_state_tuple, []))
        visited.add(initial_state_tuple)
        
        # Keep track of the number of states explored
        states_explored = 0
        
        while pq and states_explored < 100000:  # Increased limit for more thorough search
            # Get the state with lowest f-score (priority)
            f_score, _, state_tuple, path = heapq.heappop(pq)
            states_explored += 1
            
            # Convert tuple back to numpy array
            current_state = np.array([list(row) for row in state_tuple])
            
            # Update the board for visualization
            self.board.grid = current_state.copy()
            if self.draw_callback:
                self.draw_callback()
            
            # Check if we've reached a solution
            if not np.any(current_state == 2):  # No empty cells
                win_status = self.board.check_win_condition()
                if win_status == "WIN":
                    return True
                continue
            
            # Skip states with bounded regions that can't be connected
            if self.has_bounded_regions(current_state):
                continue
            
            # Find all empty cells
            empty_cells = list(zip(*np.where(current_state == 2)))
            
            # Prioritize cells with more filled neighbors (more constrained)
            empty_cells.sort(key=lambda pos: -self.count_filled_neighbors(pos[0], pos[1], current_state))
            
            # Try each empty cell
            for r, c in empty_cells[:1]:  # Only try the most constrained cell
                # Skip if this cell is fixed
                if (r, c) in self.fixed_cells:
                    continue
                
                # Try colors in order determined by surrounding cells
                colors_to_try = self.get_preferred_colors(r, c, current_state)
                
                for color in colors_to_try:
                    # Check if this is a valid move
                    original_board = self.board.grid.copy()
                    self.board.grid = current_state.copy()
                    
                    if self.is_valid_move(r, c, color):
                        # Create a new state by filling this cell
                        new_state = current_state.copy()
                        new_state[r, c] = color
                        
                        # Skip if this creates bounded regions
                        if self.has_bounded_regions(new_state):
                            self.board.grid = original_board
                            continue
                        
                        new_state_tuple = tuple(map(tuple, new_state))
                        
                        # Skip if we've seen this state before
                        if new_state_tuple not in visited:
                            # Add to visited set
                            visited.add(new_state_tuple)
                            
                            # Calculate new g_score (path cost)
                            new_g_score = len(path) + 1
                            
                            # Calculate new f_score (g_score + heuristic)
                            new_f_score = new_g_score + self.calculate_heuristic(new_state)
                            
                            # Add to priority queue with unique counter to break ties
                            counter += 1
                            new_path = path + [(r, c, color)]
                            heapq.heappush(pq, (new_f_score, counter, new_state_tuple, new_path))
                    
                    # Restore the original board
                    self.board.grid = original_board
        
        return False  # No solution found


    def dfs_solve(self):
        """Solve the board using DFS (backtracking with a stack)."""
        stack = []
        empty_cells = set(map(tuple, np.argwhere(self.board.grid == 2)))  # All empty cells

        if not empty_cells:
            return self.board.check_win_condition() == "WIN"

        # Initialize stack with both colors for the first empty cell
        start_r, start_c = next(iter(empty_cells))
        for color in [0, 1]:  
            if self.is_valid_move(start_r, start_c, color):
                new_grid = self.board.grid.copy()
                new_grid[start_r, start_c] = color
                stack.append((start_r, start_c, color, new_grid))

        while stack:
            r, c, color, current_grid = stack.pop()  # DFS pops last added state (LIFO)
            self.board.grid = current_grid  # Update board state

            if self.draw_callback:
                self.draw_callback()  # Update the display

            if not np.any(current_grid == 2):  # Board is full
                if self.board.check_win_condition() == "WIN":
                    return True
                continue

            # Expand to all valid empty neighbors with both colors
            empty_cells = list(zip(*np.where(current_grid == 2)))
            # Prioritize cells with more filled neighbors
            empty_cells.sort(key=lambda pos: -self.count_filled_neighbors(pos[0], pos[1], current_grid))
            
            for nr, nc in empty_cells[:1]:  # Only try the most constrained cell
                if (nr, nc) not in self.fixed_cells:
                    for new_color in [0, 1]:  # Try both black and white
                        if self.is_valid_move(nr, nc, new_color):
                            new_grid = current_grid.copy()
                            new_grid[nr, nc] = new_color
                            stack.append((nr, nc, new_color, new_grid))  # Push to stack (LIFO)

        return False  # No solution found
    
    def bfs_solve(self):
        """Solve the board using BFS (Breadth-First Search)."""
        queue = deque()
        visited = set()
        empty_cells = set(map(tuple, np.argwhere(self.board.grid == 2)))  # All empty cells

        if not empty_cells:
            return self.board.check_win_condition() == "WIN"

        # Initialize queue with both colors for the first empty cell
        start_r, start_c = next(iter(empty_cells))
        for color in [0, 1]:  
            if self.is_valid_move(start_r, start_c, color):
                new_grid = self.board.grid.copy()
                new_grid[start_r, start_c] = color
                state_tuple = tuple(map(tuple, new_grid))
                if state_tuple not in visited:
                    queue.append((start_r, start_c, color, new_grid))
                    visited.add(state_tuple)

        while queue:
            r, c, color, current_grid = queue.popleft()
            self.board.grid = current_grid  # Update board state

            # Visualize in Pygame
            if self.draw_callback:
                self.draw_callback()

            if not np.any(current_grid == 2):  # Board is full
                if self.board.check_win_condition() == "WIN":
                    return True
                continue

            # Find all empty cells
            empty_cells = list(zip(*np.where(current_grid == 2)))
            # Prioritize cells with more filled neighbors
            empty_cells.sort(key=lambda pos: -self.count_filled_neighbors(pos[0], pos[1], current_grid))
            
            for nr, nc in empty_cells[:1]:  # Only try the most constrained cell
                if (nr, nc) not in self.fixed_cells:
                    for new_color in [0, 1]:  # Try both black and white
                        if self.is_valid_move(nr, nc, new_color):
                            new_grid = current_grid.copy()
                            new_grid[nr, nc] = new_color
                            state_tuple = tuple(map(tuple, new_grid))
                            if state_tuple not in visited:
                                queue.append((nr, nc, new_color, new_grid))
                                visited.add(state_tuple)

        return False  # No solution found
