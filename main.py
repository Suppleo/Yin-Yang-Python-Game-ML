import pygame
from ui import main as run_ui

# Initialize Pygame
pygame.init()

def main():
    """
    Main entry point for the Yin-Yang Puzzle game.
    It initializes the UI and runs the game loop.
    """
    run_ui()

if __name__ == "__main__":
    main()
    pygame.quit()