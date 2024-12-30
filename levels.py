# levels.py
import pygame
from player import Ninja  # Import the Ninja class
from constants import BLACK, WHITE, WIDTH

def level_one_screen(screen, clock):
    font = pygame.font.Font(None, 74)

    # Create a Ninja instance
    ninja = Ninja(100, 300)  # Starting position (x=100, y=300)

    # Example tile_list for collision (replace with actual tiles)
    tile_list = [pygame.Rect(0, 500, 1920, 50)]  # Ground tile

    running = True
    while running:
        screen.fill(BLACK)  # Clear the screen

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Exit Level 1
                    running = False

        # Update and draw the ninja
        ninja.update(keys, tile_list)
        ninja.draw(screen)

        # Draw tiles (example ground platform)
        for tile in tile_list:
            pygame.draw.rect(screen, (0, 255, 0), tile)  # Green tile as ground

        # Render Level 1 text
        text = font.render("Level 1 - Ninja Adventure", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, 50))
        screen.blit(text, text_rect)

        # Refresh the screen
        pygame.display.flip()
        clock.tick(60)
