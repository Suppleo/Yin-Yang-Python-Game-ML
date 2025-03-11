import pygame
import numpy as np
from solver import Solver
from config import SIZE, CELL_SIZE, WHITE, BLACK, GRAY, BLUE
from board import Board

# Khởi tạo pygame
pygame.init()
screen = pygame.display.set_mode((SIZE * CELL_SIZE * 2, SIZE * CELL_SIZE * 2)) 
pygame.display.set_caption("Yin-Yang Puzzle")

# Tạo bảng ban đầu
original_board = np.random.choice([0, 1, 2], (SIZE, SIZE), p=[0.2, 0.2, 0.6])
board = original_board.copy()
solver = Solver(board)

def draw_grid():
    screen.fill(WHITE)
    
    # Calculate offsets to center the board
    board_width = SIZE * CELL_SIZE
    board_height = SIZE * CELL_SIZE
    x_offset = (screen.get_width() - board_width) // 2
    y_offset = (screen.get_height() - (board_height + 50)) // 2
    
    # Draw centered board
    for r in range(SIZE):
        for c in range(SIZE):
            # Draw grey background square for each cell
            pygame.draw.rect(screen, GRAY, 
                           (x_offset + c * CELL_SIZE, 
                            y_offset + r * CELL_SIZE, 
                            CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, 
                           (x_offset + c * CELL_SIZE, 
                            y_offset + r * CELL_SIZE, 
                            CELL_SIZE, CELL_SIZE), 1)
            
            # Draw black or white circle if cell is not empty
            if board[r, c] != 2:
                color = BLACK if board[r, c] == 0 else WHITE
                center = (x_offset + c * CELL_SIZE + CELL_SIZE//2,
                         y_offset + r * CELL_SIZE + CELL_SIZE//2)
                radius = CELL_SIZE//2 - 4  # Slightly smaller than cell
                pygame.draw.circle(screen, color, center, radius)
    
    # Draw centered buttons
    button_y = y_offset + board_height + 10
    
    # Solve button
    pygame.draw.rect(screen, BLUE, (x_offset, button_y, 80, 30))
    # Reset button
    pygame.draw.rect(screen, BLUE, (x_offset + 90, button_y, 80, 30))
    # Back button
    pygame.draw.rect(screen, BLUE, (x_offset + 180, button_y, 80, 30))
    
    font = pygame.font.Font(None, 24)
    solve_text = font.render("Solve", True, WHITE)
    reset_text = font.render("Reset", True, WHITE)
    back_text = font.render("Back", True, WHITE)
    
    screen.blit(solve_text, (x_offset + 20, button_y + 5))
    screen.blit(reset_text, (x_offset + 110, button_y + 5))
    screen.blit(back_text, (x_offset + 200, button_y + 5))
    
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
    
    # Calculate board dimensions and offsets
    board_width = SIZE * CELL_SIZE
    board_height = SIZE * CELL_SIZE
    x_offset = (screen.get_width() - board_width) // 2
    y_offset = (screen.get_height() - (board_height + 50)) // 2

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
                            board = Board(current_level).grid
                            solver = Solver(board)
                            fixed_cells = {(r, c) for r in range(SIZE) for c in range(SIZE) if board[r, c] != 2}
                            level_selected = True
                            break
        
        # Game loop for selected level
        while level_selected and running:
            draw_grid()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    button_y = y_offset + board_height + 10
                    
                    # Solve button
                    if x_offset <= x <= x_offset + 80 and button_y <= y <= button_y + 30:
                        solver.bfs_solve()
                    
                    # Reset button
                    elif x_offset + 90 <= x <= x_offset + 170 and button_y <= y <= button_y + 30:
                        board = Board(current_level).grid
                        solver = Solver(board)
                        fixed_cells = {(r, c) for r in range(SIZE) for c in range(SIZE) if board[r, c] != 2}
                    
                    # Back button
                    elif x_offset + 180 <= x <= x_offset + 260 and button_y <= y <= button_y + 30:
                        level_selected = False
                        break
                    
                    # Board interaction
                    elif (y_offset <= y <= y_offset + board_height and 
                        x_offset <= x <= x_offset + board_width):
                        board_x = (x - x_offset) // CELL_SIZE
                        board_y = (y - y_offset) // CELL_SIZE
                        if (board_y, board_x) not in fixed_cells:
                            if board[board_y, board_x] == 2:
                                board[board_y, board_x] = 0
                            elif board[board_y, board_x] == 0:
                                board[board_y, board_x] = 1
                            else:
                                board[board_y, board_x] = 2

    pygame.quit()

if __name__ == "__main__":
    main()
