import pygame
from ui import main as run_ui

# Initialize Pygame
pygame.init()

def main():
    """
    Main entry point for the Yin-Yang Puzzle game.
    
    This function initializes the UI and runs the game loop.
    The game is a logic puzzle where players must fill a grid with black and white
    circles following specific rules:
    1. No 2x2 area can be filled with the same color
    2. All cells of the same color must be connected
    3. The board must be completely filled
    
    The game includes multiple levels of different difficulty and
    three different solving algorithms: DFS, BFS, and A*.
    """
    run_ui()

if __name__ == "__main__":
    main()
    pygame.quit()