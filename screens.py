import sys
import pygame
import os
import textwrap
from assets import load_image, load_font
from helpers import render_text
from constants import WIDTH, HEIGHT, WHITE, BLACK
from levels import *
import game_data

def start_game_screen(screen, clock):
    background = load_image("background.jpg", (WIDTH, HEIGHT))
    button_bg = load_image("button.png", (300, 100))

    title_font = load_font('freesansbold.ttf', size=100)
    button_font = load_font('freesans.ttf', size=50)

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
                        frame.fill((128, 128, 128))
                    level_status = {i: "locked" for i in range(1, 11)}
                    level_status[1] = "unlocked"
                    level_selection_screen(screen, clock, frames, level_status)
                if about_us_btn.collidepoint(mouse_pos):
                    about_us_screen(screen, clock)
                if exit_btn.collidepoint(mouse_pos):
                    running = False

        screen.blit(background, (0, 0))
        render_text(screen, "Ninja Jungle Game", title_font, WHITE, (WIDTH // 2, HEIGHT // 3))
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
    background_path = os.path.join('assets', 'images', 'background.jpg')
    background = pygame.image.load(background_path)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    box_image_path = os.path.join('assets', 'images', 'box.png')
    box_image = pygame.image.load(box_image_path)
    box_width, box_height = 900, 500
    box_image = pygame.transform.scale(box_image, (box_width, box_height))
    box_x = (WIDTH - box_width) // 2
    box_y = (HEIGHT - box_height) // 2

    button_image_path = os.path.join('assets', 'images', 'buttonbackground.png')
    button_image = pygame.image.load(button_image_path)
    button_width, button_height = 120, 120
    button_image = pygame.transform.scale(button_image, (button_width, button_height))

    lock_image_path = os.path.join('assets', 'images', 'lock.png')
    lock_image = pygame.image.load(lock_image_path)
    lock_image = pygame.transform.scale(lock_image, (button_width, button_height))

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

    btn_width, btn_height = 80, 80
    button_spacing = 20
    total_button_width = 5 * btn_width + 4 * button_spacing
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

    store_button_path = os.path.join('assets', 'images', 'shop.png')
    store_button_image = pygame.image.load(store_button_path)
    store_button_image = pygame.transform.scale(store_button_image, (btn_width, btn_height))
    store_button_rect = pygame.Rect(exit_button_rect.right + button_spacing, button_y, btn_width, btn_height)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(mouse_pos):
                    print("Back button clicked! Returning to start screen...")
                    return
                if play_button_rect.collidepoint(mouse_pos):
                    print("Play button clicked!")
                    return
                if info_button_rect.collidepoint(mouse_pos):
                    print("Info button clicked! Opening How To Play screen...")
                    how_to_play_screen(screen, clock)

                if exit_button_rect.collidepoint(mouse_pos):
                    print("Exit button clicked! Exiting the game...")
                    pygame.quit()
                    sys.exit()
                if store_button_rect.collidepoint(mouse_pos):
                    print("Store button clicked! Opening store screen...")
                    store_screen(screen, clock)


                for level, rect in level_buttons:
                    if rect.collidepoint(mouse_pos) and level_status[level] == "unlocked":
                        print(f"Level {level} clicked!")
                        if level == 1:
                            completed = level_one_screen(screen, clock, level_status)
                            if completed:
                                level_status[2] = "unlocked"
                        elif level == 2:
                            completed = level_two_screen(screen, clock, level_status)
                            if completed:
                                level_status[3] = "unlocked"
                        elif level == 3:
                            completed = level_three_screen(screen, clock, level_status)
                            if completed:
                                level_status[4] = "unlocked"
                        elif level == 4:
                            completed = level_four_screen(screen, clock, level_status)
                            if completed:
                                level_status[5] = "unlocked"
                        elif level == 5:
                            completed = level_five_screen(screen, clock, level_status)
                            if completed:
                                level_status[6] = "unlocked"
                        elif level == 6:
                            completed = level_six_screen(screen, clock, level_status)
                            if completed:
                                level_status[7] = "unlocked"
                        elif level == 7:
                            completed = level_seven_screen(screen, clock, level_status)
                            if completed:
                                level_status[8] = "unlocked"
                        elif level == 8:
                            completed = level_eight_screen(screen, clock, level_status)
                            if completed:
                                level_status[9] = "unlocked"
                        elif level == 9:
                            completed = level_nine_screen(screen, clock, level_status)
                            if completed:
                                level_status[10] = "unlocked"
                        elif level == 10:
                            completed = level_ten_screen(screen, clock, level_status)
                            if completed:
                                game_finish_screen(screen, clock)

                        break

        screen.blit(background, (0, 0))
        screen.blit(box_image, (box_x, box_y))
        for level, rect in level_buttons:
            if level_status[level] == "unlocked":
                screen.blit(button_image, rect.topleft)
                text = pygame.font.Font(None, 64).render(str(level), True, WHITE)
                screen.blit(text, text.get_rect(center=rect.center))
            else:
                screen.blit(lock_image, rect.topleft)
        screen.blit(back_button_image, back_button_rect.topleft)
        screen.blit(play_button_image, play_button_rect.topleft)
        screen.blit(info_button_image, info_button_rect.topleft)
        screen.blit(exit_button_image, exit_button_rect.topleft)
        screen.blit(store_button_image, store_button_rect.topleft)
        pygame.display.flip()
        clock.tick(60)

def about_us_screen(screen, clock):
    pygame.init()
    base_path = os.path.join(os.path.dirname(__file__), 'assets')
    background_image_path = os.path.join(base_path, 'images', 'background.jpg')
    info_box_image_path = os.path.join(base_path, 'images', 'info_box_.png')
    button_image_path = os.path.join(base_path, 'images', 'Button.png')
    background_image = pygame.image.load(background_image_path)
    background_image = pygame.transform.scale(background_image, screen.get_size())
    info_box_image = pygame.image.load(info_box_image_path)
    info_box_image = pygame.transform.scale(info_box_image, (800, 500))
    button_image = pygame.image.load(button_image_path)
    button_image = pygame.transform.scale(button_image, (200, 60))
    black = (0, 0, 0)
    white = (255, 255, 255)
    text_font = pygame.font.Font(None, 40)
    button_font = pygame.font.Font(None, 60)
    about_text = (
        "This game is made as a project for Programming Video Games course at FCSE. "
        "By students Xhevit Tairi and Enes Sejfovski."
    )
    text_lines = textwrap.wrap(about_text, width=30)
    line_height = text_font.get_height()
    total_text_height = len(text_lines) * line_height
    start_y = (screen.get_height() - total_text_height) // 2
    button_rect = button_image.get_rect(center=(screen.get_width() // 2, screen.get_height() - 200))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    return
        screen.blit(background_image, (0, 0))
        info_box_rect = info_box_image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(info_box_image, info_box_rect.topleft)
        y_offset = start_y
        for line in text_lines:
            text_surface = text_font.render(line, True, black)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += line_height + 5
        screen.blit(button_image, button_rect.topleft)
        button_text = button_font.render("Back", True, white)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)
        pygame.display.flip()
        clock.tick(60)

def how_to_play_screen(screen, clock):
    print("How to? screen showing")
    pygame.init()
    base_path = os.path.join(os.path.dirname(__file__), 'assets')
    background_image_path = os.path.join(base_path, 'images', 'background.jpg')
    background_image = pygame.image.load(background_image_path)
    background_image = pygame.transform.scale(background_image, screen.get_size())
    info_box_path = os.path.join(base_path, 'images', 'info_box_.png')
    info_box_image = pygame.image.load(info_box_path)
    info_box_image = pygame.transform.scale(info_box_image, (800, 500))
    info_box_rect = info_box_image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    button_image_path = os.path.join(base_path, 'images', 'Button.png')
    button_image = pygame.image.load(button_image_path)
    button_image = pygame.transform.scale(button_image, (200, 60))
    white = (255, 255, 255)
    black = (0, 0, 0)
    text_font = pygame.font.Font("freesansbold.ttf", 30)
    button_font = pygame.font.Font("freesansbold.ttf", 40)
    about_text = (
        "Welcome to the NinjaJungle Game. "
        "Your goal is to navigate through the maze and reach the exit door. "
        "Use the arrow keys to move left and right. Press the space key to jump. "
        "Collect as many coins as you can to unlock new characters."
    )
    max_width = info_box_rect.width - 40
    text_lines = []
    for paragraph in about_text.split(". "):
        wrapped_lines = textwrap.wrap(paragraph, width=40)
        text_lines.extend(wrapped_lines)
    line_height = text_font.get_height()
    total_text_height = len(text_lines) * line_height
    text_start_y = info_box_rect.top + (info_box_rect.height - total_text_height) // 2
    button_rect = button_image.get_rect(center=(screen.get_width() // 2, screen.get_height() - 200))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    return
        screen.blit(background_image, (0, 0))
        screen.blit(info_box_image, info_box_rect.topleft)
        y_offset = text_start_y
        for line in text_lines:
            text_surface = text_font.render(line, True, black)
            text_rect = text_surface.get_rect(center=(info_box_rect.centerx, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += line_height + 5
        screen.blit(button_image, button_rect.topleft)
        button_text = button_font.render("Back", True, white)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)
        pygame.display.flip()
        clock.tick(60)

def game_finish_screen(screen, clock):
    print("Game Finished Screen showing")
    pygame.init()
    base_path = os.path.join(os.path.dirname(__file__), 'assets')
    background_image_path = os.path.join(base_path, 'images', 'background.jpg')
    background_image = pygame.image.load(background_image_path)
    background_image = pygame.transform.scale(background_image, screen.get_size())
    button_image_path = os.path.join(base_path, 'images', 'Button.png')
    button_image = pygame.image.load(button_image_path)
    button_image = pygame.transform.scale(button_image, (200, 60))
    white = (255, 255, 255)
    text_font = pygame.font.Font("freesansbold.ttf", 50)
    button_font = pygame.font.Font("freesansbold.ttf", 40)
    message = "Congratulations! You finished all the levels."
    text_surface = text_font.render(message, True, white)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    button_rect = button_image.get_rect(center=(screen.get_width() // 2, screen.get_height() - 200))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    return
        screen.blit(background_image, (0, 0))
        screen.blit(text_surface, text_rect)
        screen.blit(button_image, button_rect.topleft)
        button_text = button_font.render("Back", True, white)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)
        pygame.display.flip()
        clock.tick(60)


def store_screen(screen, clock):
    print("Store screen called")
    pygame.init()
    base_path = os.path.join(os.path.dirname(__file__), 'assets')


    background_image_path = os.path.join(base_path, 'images', 'background.jpg')
    info_box_image_path = os.path.join(base_path, 'images', 'shop_box.png')
    button_image_path = os.path.join(base_path, 'images', 'Button.png')

    default_image_path = os.path.join(base_path, 'images', 'ninja', 'png', 'Idle__000.png')

    alternative_image_path = os.path.join(base_path, 'images', 'ninjagirlnew', 'png', 'Idle__000.png')

    background_image = pygame.image.load(background_image_path)
    background_image = pygame.transform.scale(background_image, screen.get_size())

    info_box_image = pygame.image.load(info_box_image_path)
    info_box_image = pygame.transform.scale(info_box_image, (1150, 700))

    button_image = pygame.image.load(button_image_path)
    button_image = pygame.transform.scale(button_image, (200, 80))

    smaller_button_image = pygame.image.load(button_image_path)
    smaller_button_image = pygame.transform.scale(smaller_button_image, (150, 40))

    default_image = pygame.image.load(default_image_path)
    default_image = pygame.transform.scale(default_image, (60, 80))
    alternative_image = pygame.image.load(alternative_image_path)
    alternative_image = pygame.transform.scale(alternative_image, (60, 80))


    black = (0, 0, 0)
    white = (255, 255, 255)
    text_font = pygame.font.Font(None, 25)
    button_font = pygame.font.Font(None, 40)


    back_button_rect = button_image.get_rect(center=(screen.get_width() // 2, screen.get_height() - 200))


    info_box_rect = info_box_image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))


    store_box = info_box_image.copy()


    default_card_rect = pygame.Rect(410, 250, 150, 250)

    alternative_card_rect = pygame.Rect(570, 250, 150, 250)
    pygame.draw.rect(store_box, white, default_card_rect)
    pygame.draw.rect(store_box, white, alternative_card_rect)


    store_box.blit(text_font.render("Ninja 1", True, black), (465, 370))
    store_box.blit(text_font.render("Ninja 2", True, black), (615, 370))


    store_box.blit(default_image,
                   default_image.get_rect(center=(default_card_rect.centerx, default_card_rect.top + 50)))
    store_box.blit(alternative_image,
                   alternative_image.get_rect(center=(alternative_card_rect.centerx, alternative_card_rect.top + 50)))


    default_button_rect = smaller_button_image.get_rect(center=(875, 640))
    alternative_button_rect = smaller_button_image.get_rect(center=(1037, 640))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button_rect.collidepoint(event.pos):
                    return

                if default_button_rect.collidepoint(event.pos):
                    import game_data
                    game_data.selected_skin = "ninja"
                    print("Default skin selected.")

                if alternative_button_rect.collidepoint(event.pos):
                    import game_data
                    if not game_data.alternative_skin_bought:
                        if game_data.coins_collected >= 25:
                            game_data.alternative_skin_bought = True
                            game_data.selected_skin = "ninjagirlnew"
                            print("Alternative skin bought and selected.")
                        else:
                            print("Not enough coins to buy the alternative skin.")
                    else:
                        game_data.selected_skin = "ninjagirlnew"
                        print("Alternative skin selected.")


        screen.blit(background_image, (0, 0))
        screen.blit(store_box, info_box_rect.topleft)
        screen.blit(button_image, back_button_rect.topleft)
        back_text = button_font.render("Back", True, white)
        screen.blit(back_text, back_text.get_rect(center=back_button_rect.center))


        screen.blit(smaller_button_image, default_button_rect.topleft)
        default_btn_text = button_font.render("Select", True, white)
        screen.blit(default_btn_text, default_btn_text.get_rect(center=default_button_rect.center))


        import game_data
        if game_data.alternative_skin_bought:
            screen.blit(smaller_button_image, alternative_button_rect.topleft)
            alt_btn_text = button_font.render("Select", True, white)
            screen.blit(alt_btn_text, alt_btn_text.get_rect(center=alternative_button_rect.center))
        else:
            if game_data.coins_collected >= 3:
                screen.blit(smaller_button_image, alternative_button_rect.topleft)
                alt_btn_text = button_font.render("Buy", True, white)
                screen.blit(alt_btn_text, alt_btn_text.get_rect(center=alternative_button_rect.center))
            else:
                locked_text = button_font.render("Locked", True, white)
                screen.blit(locked_text, locked_text.get_rect(center=alternative_button_rect.center))


        coin_info = text_font.render(f"Coins: {game_data.coins_collected}", True, white)
        screen.blit(coin_info, (50, 50))

        pygame.display.flip()
        clock.tick(60)


def buy_skin(screen, clock):
    import game_data
    if game_data.coins_collected >= 3 and not game_data.alternative_skin_bought:
        game_data.alternative_skin_bought = True
        game_data.selected_skin = "ninjagirlnew"
        print("Buy button clicked: Alternative skin bought and selected.")
    else:
        print("Buy button clicked: Not enough coins or already bought.")


def select_skin(screen, clock):
    import game_data
    if game_data.alternative_skin_bought:

        if game_data.selected_skin == "ninjagirlnew":
            game_data.selected_skin = "ninja"
            print("Select skin button clicked: Skin changed to 'ninja'.")
        else:
            game_data.selected_skin = "ninjagirlnew"
            print("Select skin button clicked: Skin changed to 'ninjagirlnew'.")
    else:
        print("Select skin button clicked: Alternative skin not purchased yet.")
