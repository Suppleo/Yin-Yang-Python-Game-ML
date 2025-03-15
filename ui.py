import pygame
import numpy as np
import time
import psutil
import os
from solver import Solver
from config import SIZE, CELL_SIZE, WHITE, BLACK, GRAY, BLUE
from board import Board

# Khởi tạo pygame
pygame.init()
screen = pygame.display.set_mode((SIZE * CELL_SIZE * 2, SIZE * CELL_SIZE * 2)) 
pygame.display.set_caption("Yin-Yang Puzzle")

# Get the current process for memory tracking
process = psutil.Process(os.getpid())

def draw_grid():
    screen.fill(WHITE)
    
    # Calculate offsets to center the board
    board_width = SIZE * CELL_SIZE
    board_height = SIZE * CELL_SIZE
    x_offset = (screen.get_width() - board_width) // 2
    y_offset = (screen.get_height() - (board_height + 100)) // 2  # Increased space for buttons
    
    invalid_cells = board.check_2x2_blocks()

    # Draw board with red backgrounds for invalid cells
    for r in range(SIZE):
        for c in range(SIZE):
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

    # Check win condition and display message
    win_status = board.check_win_condition()
    if win_status:
        font = pygame.font.Font(None, 48)
        if win_status == "WIN":
            text = font.render("You Won!", True, (0,255,0))
        else:
            text = font.render(win_status, True, (255,0,0))
        text_rect = text.get_rect(center=(screen.get_width()//2, 40))
        screen.blit(text, text_rect)
    
    # Display elapsed time and memory info
    font = pygame.font.Font(None, 24)
    if solving and solve_start_time:
        elapsed = time.time() - solve_start_time
        time_text = font.render(f"Time: {elapsed:.2f}s", True, BLACK)
        screen.blit(time_text, (x_offset, y_offset - 40))
        
        # Only show memory during solving
        try:
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            memory_text = font.render(f"Memory: {memory_usage:.2f} MB", True, BLACK)
            screen.blit(memory_text, (x_offset, y_offset - 20))
        except Exception:
            pass
    
    elif solve_end_time:
        # After solving, show time and peak memory
        elapsed = solve_end_time - solve_start_time
        time_text = font.render(f"Time: {elapsed:.2f}s", True, BLACK)
        screen.blit(time_text, (x_offset, y_offset - 40))
        
        # Only show peak memory after solving is complete
        if peak_memory > 0:
            peak_text = font.render(f"Peak Memory: {peak_memory:.2f} MB", True, BLACK)
            screen.blit(peak_text, (x_offset, y_offset - 20))
    
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
    
    # Calculate board dimensions and offsets
    board_width = SIZE * CELL_SIZE
    board_height = SIZE * CELL_SIZE
    x_offset = (screen.get_width() - board_width) // 2
    y_offset = (screen.get_height() - (board_height + 100)) // 2  # Increased space for buttons

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
                    
                    for i in range(5):
                        if (screen.get_width()//2 - button_width//2 <= x <= screen.get_width()//2 + button_width//2 and 
                            180 + i*button_spacing <= y <= 180 + i*button_spacing + button_height):
                            current_level = i + 1
                            board = Board(current_level)    
                            fixed_cells = {(r, c) for r in range(SIZE) for c in range(SIZE) if board.grid[r, c] != 2}
                            solver = Solver(board, fixed_cells)
                            solver.draw_callback = draw_grid
                            level_selected = True
                            solving = False
                            solve_start_time = None
                            solve_end_time = None
                            peak_memory = 0
                            break
        
        # Game loop for selected level
        while level_selected and running:
            draw_grid()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and not solving:
                    x, y = event.pos
                    button_y = y_offset + board_height + 10
                    algo_button_y = button_y + 40
                    
                    # Solve button
                    if x_offset <= x <= x_offset + 80 and button_y <= y <= button_y + 30:
                        if not solving:
                            solving = True
                            solve_start_time = time.time()
                            solve_end_time = None
                            peak_memory = 0
                            
                            # Run the selected algorithm
                            result = False
                            
                            # Track memory usage during solving
                            def memory_tracking_callback():
                                global peak_memory
                                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                                peak_memory = max(peak_memory, current_memory)
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
                            
                            print(f"Puzzle solved: {result}, Time: {solve_end_time - solve_start_time:.2f}s, Peak Memory: {peak_memory:.2f} MB")
                    
                    # Reset button
                    elif x_offset + 90 <= x <= x_offset + 170 and button_y <= y <= button_y + 30:
                        board = Board(current_level)
                        fixed_cells = {(r, c) for r in range(SIZE) for c in range(SIZE) if board.grid[r, c] != 2}
                        solver = Solver(board, fixed_cells)
                        solver.draw_callback = draw_grid
                        solving = False
                        solve_start_time = None
                        solve_end_time = None
                        peak_memory = 0
                    
                    # Back button
                    elif x_offset + 180 <= x <= x_offset + 260 and button_y <= y <= button_y + 30:
                        level_selected = False
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
                        if (board_y, board_x) not in fixed_cells:
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

if __name__ == "__main__":
    main()
