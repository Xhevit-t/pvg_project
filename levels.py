import pygame


from player import Ninja  # Import the Ninja class
from constants import BLACK, WHITE, WIDTH

def level_one_screen(screen, clock,level_status):
    # Load the new background image
    level_background = pygame.image.load('assets/images/level_background.png')

    # Set the screen size
    screen_width = 1920
    screen_height = 1080
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Escape the maze')

    # Game variables
    tile_size = 50
    grid_width = 20  # Number of columns in the grid
    grid_height = 20  # Number of rows in the grid

    # Calculate the offset to center the grid
    grid_pixel_width = grid_width * tile_size
    grid_pixel_height = grid_height * tile_size
    offset_x = (screen_width - grid_pixel_width) // 2
    offset_y = (screen_height - grid_pixel_height) // 2

    # Load images
    def draw_grid():
        for line in range(0, grid_height):
            # Draw horizontal grid lines
            pygame.draw.line(screen, (255, 255, 255),
                             (offset_x, offset_y + line * tile_size),
                             (offset_x + grid_pixel_width, offset_y + line * tile_size))
            # Draw vertical grid lines
            pygame.draw.line(screen, (255, 255, 255),
                             (offset_x + line * tile_size, offset_y),
                             (offset_x + line * tile_size, offset_y + grid_pixel_height))

    class World():
        def __init__(self, data):
            self.tile_list = []
            self.spawn_pos = None  # To store the spawn position
            self.exit_pos = None  # To store the exit position

            # Load images
            dirt_img = pygame.image.load('assets/images/dirt.png')
            grass_img = pygame.image.load('assets/images/grass.png')
            exit_img = pygame.image.load('assets/images/door.png')

            row_count = 0
            for row in data:
                col_count = 0
                for tile in row:
                    if tile == 1:
                        img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = offset_x + col_count * tile_size
                        img_rect.y = offset_y + row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif tile == 2:
                        img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = offset_x + col_count * tile_size
                        img_rect.y = offset_y + row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif tile == 7:  # Exit point
                        img = pygame.transform.scale(exit_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = offset_x + col_count * tile_size
                        img_rect.y = offset_y + row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                        self.exit_pos = (img_rect.x, img_rect.y)  # Store exit position
                    elif tile == 9:  # Spawn point
                        self.spawn_pos = (
                        offset_x + col_count * tile_size, offset_y + row_count * tile_size)  # Store spawn position
                    col_count += 1
                row_count += 1

        def draw(self):
            for tile in self.tile_list:
                screen.blit(tile[0], tile[1])

    world_data = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 1],
        [1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 1],
        [1, 9, 0, 2, 1, 1, 1, 2, 0, 0, 2, 2, 2, 0, 0, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
    ]

    world = World(world_data)

    # Check if spawn position is found before creating the player
    if world.spawn_pos is None:
        raise ValueError("No spawn position found in the level data!")

    player = Ninja(world.spawn_pos[0], world.spawn_pos[1])

    run = True
    while run:
        # Draw the background first
        screen.blit(pygame.transform.scale(level_background, (screen_width, screen_height)), (0, 0))

        # Draw the world (tiles)
        world.draw()

        # Update and draw the player
        keys = pygame.key.get_pressed()
        player.update(keys, [tile[1] for tile in world.tile_list])  # Pass the tiles for collision detection
        player.draw(screen)

        # Check if player reaches the borders of the exit door
        player_rect = player.rect
        exit_rect = pygame.Rect(world.exit_pos[0], world.exit_pos[1], tile_size, tile_size)

        if player_rect.colliderect(exit_rect.inflate(10, 10)):  # Inflate the exit door's rect for proximity detection
            print("Level Complete!")
            level_status[2] = "unlocked"  # Unlock Level 2
            return True  # Return True to indicate level completion

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        pygame.display.update()

    return False  # Return False if the user quits the level