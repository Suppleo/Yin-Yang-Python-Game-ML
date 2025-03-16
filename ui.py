import pygame
import numpy as np
import time
import psutil
import os
from solver import Solver
from config import CELL_SIZE, WHITE, BLACK, GRAY, BLUE
from board import Board

# Initialize pygame
pygame.init()
# Start with a normal window size for the menu
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Yin-Yang Puzzle")

# Get the current process for memory tracking
process = psutil.Process(os.getpid())

def draw_grid():
    screen.fill(WHITE)
    
    # Get the current board size
    board_size = board.size
    
    # Calculate offsets to center the board
    board_width = board_size * CELL_SIZE
    board_height = board_size * CELL_SIZE
    x_offset = (screen.get_width() - board_width) // 2
    y_offset = (screen.get_height() - (board_height + 100)) // 2  # Increased space for buttons
    
    invalid_cells = board.check_2x2_blocks()

    # Draw board with red backgrounds for invalid cells
    for r in range(board_size):
        for c in range(board_size):
            bg_color = (255,0,0) if (r,c) in invalid_cells else GRAY
            pygame.draw.rect(screen, bg_color, 
                           (x_offset + c * CELL_SIZE, 
                            y_offset + r * CELL_SIZE, 
                            CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, 
                           (x_offset + c * CELL_SIZE, 
                            y_offset + r * CELL_SIZE, 
                            CELL_SIZE, CELL_SIZE), 1)
            
            if board.grid[r, c] != 2:
                color = BLACK if board.grid[r, c] == 0 else WHITE
                center = (x_offset + c * CELL_SIZE + CELL_SIZE//2,
                         y_offset + r * CELL_SIZE + CELL_SIZE//2)
                radius = CELL_SIZE//2 - 4
                pygame.draw.circle(screen, color, center, radius)

                # Add brown dot for fixed cells
                if (r, c) in fixed_cells:
                    pygame.draw.circle(screen, (139,69,19), center, 4)
    
    # Draw centered buttons
    button_y = y_offset + board_height + 10
    
    # Solve button
    solve_color = (0, 100, 255) if not solving else (100, 100, 100)
    pygame.draw.rect(screen, solve_color, (x_offset, button_y, 80, 30))
    
    # Reset button
    pygame.draw.rect(screen, BLUE, (x_offset + 90, button_y, 80, 30))
    
    # Back button
    pygame.draw.rect(screen, BLUE, (x_offset + 180, button_y, 80, 30))
    
    # Algorithm selection buttons
    algo_button_y = button_y + 40
    
    # DFS button
    dfs_color = (0, 150, 0) if selected_algo == "DFS" else (100, 100, 100)
    pygame.draw.rect(screen, dfs_color, (x_offset, algo_button_y, 80, 30))
    
    # BFS button
    bfs_color = (0, 150, 0) if selected_algo == "BFS" else (100, 100, 100)
    pygame.draw.rect(screen, bfs_color, (x_offset + 90, algo_button_y, 80, 30))
    
    # A* button
    astar_color = (0, 150, 0) if selected_algo == "A*" else (100, 100, 100)
    pygame.draw.rect(screen, astar_color, (x_offset + 180, algo_button_y, 80, 30))
    
    font = pygame.font.Font(None, 24)
    solve_text = font.render("Solve", True, WHITE)
    reset_text = font.render("Reset", True, WHITE)
    back_text = font.render("Back", True, WHITE)
    dfs_text = font.render("DFS", True, WHITE)
    bfs_text = font.render("BFS", True, WHITE)
    astar_text = font.render("A*", True, WHITE)
    
    screen.blit(solve_text, (x_offset + 20, button_y + 5))
    screen.blit(reset_text, (x_offset + 110, button_y + 5))
    screen.blit(back_text, (x_offset + 200, button_y + 5))
    screen.blit(dfs_text, (x_offset + 25, algo_button_y + 5))
    screen.blit(bfs_text, (x_offset + 115, algo_button_y + 5))
    screen.blit(astar_text, (x_offset + 205, algo_button_y + 5))

    # Add "?" button for Level 5 to access 10x10 board
    if current_level == 5:
        question_button_size = 30
        pygame.draw.rect(screen, (100, 100, 100),
                        (screen.get_width() - question_button_size - 10,
                         screen.get_height() - question_button_size - 10,
                         question_button_size,
                         question_button_size))
        question_text = font.render("?", True, WHITE)
        question_rect = question_text.get_rect(center=(
                                              screen.get_width() - question_button_size//2 - 10,
                                              screen.get_height() - question_button_size//2 - 10))
        screen.blit(question_text, question_rect)

    # Check win condition and display message
    win_status = board.check_win_condition()
    if win_status:
        font_large = pygame.font.Font(None, 48)
        if win_status == "WIN":
            text = font_large.render("You Won!", True, (0,255,0))
        else:
            text = font_large.render(win_status, True, (255,0,0))
        text_rect = text.get_rect(center=(screen.get_width()//2, 40))
        screen.blit(text, text_rect)
    
    # Use consistent font size for time and memory displays
    font = pygame.font.Font(None, 24)
    
    # Display elapsed time if solving or after solving
    if solving and solve_start_time:
        elapsed = time.time() - solve_start_time
        time_text = font.render(f"Time: {elapsed:.2f}s", True, BLACK)
        screen.blit(time_text, (x_offset, y_offset - 40))
    elif solve_end_time:
        elapsed = solve_end_time - solve_start_time
        time_text = font.render(f"Time: {elapsed:.2f}s", True, BLACK)
        screen.blit(time_text, (x_offset, y_offset - 40))
    
    # Display memory usage (only show algorithm memory usage, not total app memory)
    if peak_memory > 0:
        memory_text = font.render(f"Memory: {peak_memory:.2f} KB", True, BLACK)
        screen.blit(memory_text, (x_offset, y_offset - 20))
    
    pygame.display.flip()

def draw_level_menu():
    screen.fill(WHITE)
    font_large = pygame.font.Font(None, 48)
    font_normal = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 28)
    
    # Main title
    title = font_large.render("Yin-Yang Puzzle Game", True, BLACK)
    title_rect = title.get_rect(center=(screen.get_width()//2, 60))
    screen.blit(title, title_rect)
    
    # Subtitle
    subtitle = font_small.render("By: Duc Long and Ngoc Thach", True, BLACK)
    subtitle_rect = subtitle.get_rect(center=(screen.get_width()//2, 100))
    screen.blit(subtitle, subtitle_rect)
    
    # Level buttons with more padding
    button_width = 200
    button_height = 60
    button_spacing = 80
    
    for i in range(5):
        pygame.draw.rect(screen, BLUE, 
                        (screen.get_width()//2 - button_width//2, 
                         180 + i*button_spacing, 
                         button_width, 
                         button_height))
        level_text = font_normal.render(f"Level {i+1}", True, WHITE)
        text_rect = level_text.get_rect(center=(screen.get_width()//2, 
                                               180 + i*button_spacing + button_height//2))
        screen.blit(level_text, text_rect)
    
    pygame.display.flip()


def main():
    global board, solver, fixed_cells, x_offset, y_offset, board_width, board_height, current_level
    global selected_algo, solving, solve_start_time, solve_end_time, peak_memory
    
    # Initialize algorithm selection
    selected_algo = "A*"  # Default algorithm
    solving = False
    solve_start_time = None
    solve_end_time = None
    peak_memory = 0
    
    # Set up initial window size for menu
    resize_window(600, 600)

    running = True
    while running:
        # Show level selection menu
        draw_level_menu()
        level_selected = False
        
        # Level selection loop
        while not level_selected and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    button_width = 200
                    button_height = 60
                    button_spacing = 80
                    
                    # Check if regular level buttons were clicked
                    for i in range(5):
                        if (screen.get_width()//2 - button_width//2 <= x <= screen.get_width()//2 + button_width//2 and 
                            180 + i*button_spacing <= y <= 180 + i*button_spacing + button_height):
                            current_level = i + 1
                            board = Board(current_level)    
                            fixed_cells = {(r, c) for r in range(board.size) for c in range(board.size) if board.grid[r, c] != 2}
                            solver = Solver(board, fixed_cells)
                            solver.draw_callback = draw_grid
                            level_selected = True
                            solving = False
                            solve_start_time = None
                            solve_end_time = None
                            peak_memory = 0
                            
                            # Resize window based on board size
                            resize_window_for_board(board.size)
                            break
        
        # Game loop for selected level
        while level_selected and running:
            draw_grid()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and not solving:
                    x, y = event.pos
                    
                    # Calculate board dimensions and offsets for the current board size
                    board_width = board.size * CELL_SIZE
                    board_height = board.size * CELL_SIZE
                    x_offset = (screen.get_width() - board_width) // 2
                    y_offset = (screen.get_height() - (board_height + 100)) // 2
                    
                    button_y = y_offset + board_height + 10
                    algo_button_y = button_y + 40
                    
                    # Check if "?" button was clicked (only on Level 5)
                    if current_level == 5:
                        question_button_size = 30
                        question_button_x = screen.get_width() - question_button_size - 10
                        question_button_y = screen.get_height() - question_button_size - 10
                        
                        if (question_button_x <= x <= question_button_x + question_button_size and
                            question_button_y <= y <= question_button_y + question_button_size):
                            # Load the special 10x10 level
                            current_level = 6  # Level 6 is our 10x10 level
                            board = Board(current_level)
                            fixed_cells = {(r, c) for r in range(board.size) for c in range(board.size) if board.grid[r, c] != 2}
                            solver = Solver(board, fixed_cells)
                            solver.draw_callback = draw_grid
                            solving = False
                            solve_start_time = None
                            solve_end_time = None
                            peak_memory = 0
                            
                            # Resize window for 10x10 board
                            resize_window_for_board(board.size)
                            continue
                    
                    # Solve button
                    if x_offset <= x <= x_offset + 80 and button_y <= y <= button_y + 30:
                        if not solving:
                            solving = True
                            solve_start_time = time.time()
                            solve_end_time = None
                            peak_memory = 0
                            
                            # Get baseline memory before solving
                            baseline_memory = process.memory_info().rss / 1024  # KB
                            
                            # Run the selected algorithm
                            result = False
                            
                            # Track memory usage during solving
                            def memory_tracking_callback():
                                global peak_memory
                                current_memory = process.memory_info().rss / 1024  # KB
                                # Calculate memory used by algorithm (relative to baseline)
                                algorithm_memory = current_memory - baseline_memory
                                peak_memory = max(peak_memory, algorithm_memory)
                                draw_grid()  # Update display with current memory usage
                            
                            # Set the callback for memory tracking
                            solver.draw_callback = memory_tracking_callback
                            
                            if selected_algo == "DFS":
                                result = solver.dfs_solve()
                            elif selected_algo == "BFS":
                                result = solver.bfs_solve()
                            else:  # A*
                                result = solver.a_star_solve()
                            
                            solve_end_time = time.time()
                            solving = False
                            
                            # Reset the callback
                            solver.draw_callback = draw_grid
                            
                            print(f"Puzzle solved: {result}, Time: {solve_end_time - solve_start_time:.2f}s, Memory: {peak_memory:.2f} KB")
                    
                    # Reset button
                    elif x_offset + 90 <= x <= x_offset + 170 and button_y <= y <= button_y + 30:
                        board = Board(current_level)
                        fixed_cells = {(r, c) for r in range(board.size) for c in range(board.size) if board.grid[r, c] != 2}
                        solver = Solver(board, fixed_cells)
                        solver.draw_callback = draw_grid
                        solving = False
                        solve_start_time = None
                        solve_end_time = None
                        peak_memory = 0
                    
                    # Back button
                    elif x_offset + 180 <= x <= x_offset + 260 and button_y <= y <= button_y + 30:
                        level_selected = False
                        # Reset window size for menu
                        resize_window(600, 600)
                        break
                    
                    # DFS button
                    elif x_offset <= x <= x_offset + 80 and algo_button_y <= y <= algo_button_y + 30:
                        selected_algo = "DFS"
                    
                    # BFS button
                    elif x_offset + 90 <= x <= x_offset + 170 and algo_button_y <= y <= algo_button_y + 30:
                        selected_algo = "BFS"
                    
                    # A* button
                    elif x_offset + 180 <= x <= x_offset + 260 and algo_button_y <= y <= algo_button_y + 30:
                        selected_algo = "A*"
                    
                    # Board interaction
                    elif (y_offset <= y <= y_offset + board_height and 
                        x_offset <= x <= x_offset + board_width):
                        board_x = (x - x_offset) // CELL_SIZE
                        board_y = (y - y_offset) // CELL_SIZE
                        if (board_y, board_x) not in fixed_cells and board_y < board.size and board_x < board.size:
                            if event.button == 1:  # Left click
                                if board.grid[board_y, board_x] == 0:  # If black
                                    board.grid[board_y, board_x] = 2  # Change to grey
                                else:
                                    board.grid[board_y, board_x] = 0  # Change to black
                            elif event.button == 3:  # Right click
                                if board.grid[board_y, board_x] == 1:  # If white
                                    board.grid[board_y, board_x] = 2  # Change to grey
                                else:
                                    board.grid[board_y, board_x] = 1  # Change to white
                            else:
                                board.grid[board_y, board_x] = 2

    pygame.quit()

def resize_window(width, height):
    """Resize the pygame window to the specified dimensions."""
    global screen
    screen = pygame.display.set_mode((width, height))

def resize_window_for_board(board_size):
    """Resize the window based on the board size."""
    # For 10x10 board, make the window larger
    if board_size == 10:
        resize_window(800, 800)
    else:
        # For smaller boards, use a standard size
        resize_window(600, 600)

if __name__ == "__main__":
    main()
