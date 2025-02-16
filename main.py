import pygame
import sys
from constants import WIDTH, HEIGHT

# Initialize Pygame and the mixer BEFORE importing screens/levels
pygame.init()
pygame.mixer.init()

# Now that the mixer is ready, we can import screens (which loads sounds in levels.py)
from screens import start_game_screen

def main():
    # Load and play your background music
    pygame.mixer.music.load("assets/sounds/theme_sound.mp3")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)

    # Create the main window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ninja Jungle Game")
    clock = pygame.time.Clock()

    # Go to your start screen
    start_game_screen(screen, clock)

    # Cleanup on exit
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
