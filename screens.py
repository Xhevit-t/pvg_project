import pygame
import os
from assets import load_image, load_font
from helpers import render_text
from constants import WIDTH, HEIGHT, WHITE, BLACK
from levels import level_one_screen

def start_game_screen(screen, clock):
    background = load_image("background.jpg", (WIDTH, HEIGHT))
    button_bg = load_image("button.png", (300, 100))

    title_font = load_font(size=100)
    button_font = load_font(size=50)

    start_btn = pygame.Rect(WIDTH // 3 - 150, HEIGHT // 2, 300, 100)
    about_us_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 100)
    exit_btn = pygame.Rect(2 * WIDTH // 3 - 150, HEIGHT // 2, 300, 100)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(mouse_pos):
                    frames = [pygame.Surface((150, 150)) for _ in range(10)]
                    for frame in frames:
                        frame.fill((128, 128, 128))  # Placeholder gray frames
                        # Initialize level_status: Only Level 1 unlocked
                        level_status = {i: "locked" for i in range(1, 11)}
                        level_status[1] = "unlocked"
                        level_selection_screen(screen, clock, frames, level_status)
                if about_us_btn.collidepoint(mouse_pos):
                    about_us_screen(screen, clock)
                if exit_btn.collidepoint(mouse_pos):
                    running = False

        screen.blit(background, (0, 0))
        render_text(screen, "Escape The Maze", title_font, WHITE, (WIDTH // 2, HEIGHT // 3))

        screen.blit(button_bg, start_btn.topleft)
        render_text(screen, "START", button_font, WHITE, start_btn.center)

        screen.blit(button_bg, about_us_btn.topleft)
        render_text(screen, "ABOUT US", button_font, WHITE, about_us_btn.center)

        screen.blit(button_bg, exit_btn.topleft)
        render_text(screen, "EXIT", button_font, WHITE, exit_btn.center)

        pygame.display.flip()
        clock.tick(60)

def level_selection_screen(screen, clock, frames, level_status):
    print("Displaying level selection screen...")

    # Load the background
    background_path = os.path.join('assets', 'images', 'background.jpg')
    background = pygame.image.load(background_path)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Load the large box image
    box_image_path = os.path.join('assets', 'images', 'box.png')
    box_image = pygame.image.load(box_image_path)
    box_width, box_height = 900, 500
    box_image = pygame.transform.scale(box_image, (box_width, box_height))

    # Center the box on the screen
    box_x = (WIDTH - box_width) // 2
    box_y = (HEIGHT - box_height) // 2

    # Load the button background
    button_image_path = os.path.join('assets', 'images', 'buttonbackground.png')
    button_image = pygame.image.load(button_image_path)
    button_width, button_height = 120, 120
    button_image = pygame.transform.scale(button_image, (button_width, button_height))

    # Load the lock image
    lock_image_path = os.path.join('assets', 'images', 'lock.png')
    lock_image = pygame.image.load(lock_image_path)
    lock_image = pygame.transform.scale(lock_image, (button_width, button_height))

    # Configure grid for level buttons
    rows, cols = 2, 5
    padding_x, padding_y = 20, 20
    start_x = box_x + (box_width - (cols * button_width + (cols - 1) * padding_x)) // 2
    start_y = box_y + (box_height - (rows * button_height + (rows - 1) * padding_y)) // 2

    level_buttons = []
    for row in range(rows):
        for col in range(cols):
            level = row * cols + col + 1
            x = start_x + col * (button_width + padding_x)
            y = start_y + row * (button_height + padding_y)
            rect = pygame.Rect(x, y, button_width, button_height)
            level_buttons.append((level, rect))

    # Back, Play, Info, and Exit Buttons
    btn_width, btn_height = 80, 80
    button_spacing = 20

    total_button_width = 4 * btn_width + 3 * button_spacing
    first_button_x = box_x + (box_width - total_button_width) // 2
    button_y = box_y + box_height - 40

    back_button_path = os.path.join('assets', 'images', 'back.png')
    back_button_image = pygame.image.load(back_button_path)
    back_button_image = pygame.transform.scale(back_button_image, (btn_width, btn_height))
    back_button_rect = pygame.Rect(first_button_x, button_y, btn_width, btn_height)

    play_button_path = os.path.join('assets', 'images', 'play.png')
    play_button_image = pygame.image.load(play_button_path)
    play_button_image = pygame.transform.scale(play_button_image, (btn_width, btn_height))
    play_button_rect = pygame.Rect(first_button_x + (btn_width + button_spacing), button_y, btn_width, btn_height)

    info_button_path = os.path.join('assets', 'images', 'info.png')
    info_button_image = pygame.image.load(info_button_path)
    info_button_image = pygame.transform.scale(info_button_image, (btn_width, btn_height))
    info_button_rect = pygame.Rect(play_button_rect.right + button_spacing, button_y, btn_width, btn_height)

    exit_button_path = os.path.join('assets', 'images', 'exit.png')
    exit_button_image = pygame.image.load(exit_button_path)
    exit_button_image = pygame.transform.scale(exit_button_image, (btn_width, btn_height))
    exit_button_rect = pygame.Rect(info_button_rect.right + button_spacing, button_y, btn_width, btn_height)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle level buttons
                for level, rect in level_buttons:
                    if rect.collidepoint(mouse_pos) and level_status[level] == "unlocked":
                        print(f"Level {level} clicked!")
                        if level == 1:
                            completed = level_one_screen(screen, clock)
                            if completed:
                                level_status[2] = "unlocked"
                        elif level == 2:
                            completed = level_two_screen(screen, clock)
                            if completed:
                                level_status[3] = "unlocked"

                # Handle Back Button
                if back_button_rect.collidepoint(mouse_pos):
                    print("Back button clicked! Returning to start screen...")
                    return start_game_screen(screen, clock)

                # Handle Play Button
                if play_button_rect.collidepoint(mouse_pos):
                    print("Play button clicked! Starting the first unlocked level...")
                    for level, status in level_status.items():
                        if status == "unlocked":
                            print(f"Starting Level {level}...")
                            return

                # Handle Info Button
                if info_button_rect.collidepoint(mouse_pos):
                    print("Info button clicked! Opening About Us screen...")
                    about_us_screen(screen, clock)
                    return

                # Handle Exit Button
                if exit_button_rect.collidepoint(mouse_pos):
                    print("Exit button clicked! Exiting the game...")
                    pygame.quit()
                    sys.exit()

        # Render the background
        screen.blit(background, (0, 0))
        screen.blit(box_image, (box_x, box_y))

        # Render level buttons
        for level, rect in level_buttons:
            if level_status[level] == "unlocked":
                screen.blit(button_image, rect.topleft)
                text = pygame.font.Font(None, 64).render(str(level), True, WHITE)
                screen.blit(text, text.get_rect(center=rect.center))
            else:
                screen.blit(lock_image, rect.topleft)

        # Render Back, Play, Info, and Exit buttons
        screen.blit(back_button_image, back_button_rect.topleft)
        screen.blit(play_button_image, play_button_rect.topleft)
        screen.blit(info_button_image, info_button_rect.topleft)
        screen.blit(exit_button_image, exit_button_rect.topleft)

        pygame.display.flip()
        clock.tick(60)
