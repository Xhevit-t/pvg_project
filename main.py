import pygame
from screens import start_game_screen
from constants import WIDTH, HEIGHT

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("assets/sounds/theme_sound.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ninja Jungle Game")
clock = pygame.time.Clock()

if __name__ == "__main__":
    start_game_screen(screen, clock)
    pygame.mixer.music.stop()
    pygame.quit()
