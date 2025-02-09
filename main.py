import pygame
from screens import start_game_screen
from constants import WIDTH, HEIGHT

# Initialize Pygame
pygame.init()

# Create the screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape The Maze")
clock = pygame.time.Clock()

if __name__ == "__main__":
    start_game_screen(screen, clock)
    pygame.quit()
                             