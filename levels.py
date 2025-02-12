import sys
import random
import pygame
import os

from player import Ninja
import game_data

tile_size = 50
screen_width = 1920
screen_height = 1080

def initialize_screen():
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Escape the Maze')
    return screen

BLOB_MOVE_RANGE = 100
TILE_SIZE = 50
MIN_SPAWN_DIST_TILES = 3
MIN_DOOR_DIST_TILES = 2
MIN_VERTICAL_CLEARANCE = 2
MIN_BLOB_HORIZONTAL_GAP = 2

def place_random_blobs_fair(num_blobs, base_world_data):
    data_copy = [row[:] for row in base_world_data]
    rows = len(data_copy)
    cols = len(data_copy[0]) if rows > 0 else 0
    range_in_tiles = BLOB_MOVE_RANGE // TILE_SIZE

    spawn_r = spawn_c = None
    door_r = door_c = None
    for rr in range(rows):
        for cc in range(cols):
            val = data_copy[rr][cc]
            if val == 9:
                spawn_r, spawn_c = rr, cc
            elif val == 7:
                door_r, door_c = rr, cc

    possible_positions = []
    for r in range(2, rows - 1):
        for c in range(cols - range_in_tiles):
            row_open = True
            for step in range(range_in_tiles + 1):
                if data_copy[r][c + step] != 0:
                    row_open = False
                    break
            if not row_open:
                continue

            supported = True
            for step in range(range_in_tiles + 1):
                below_tile = data_copy[r + 1][c + step]
                if below_tile not in [1, 2]:
                    supported = False
                    break
            if not supported:
                continue

            enough_headroom = True
            for step in range(range_in_tiles + 1):
                if data_copy[r - 1][c + step] != 0 or data_copy[r - 2][c + step] != 0:
                    enough_headroom = False
                    break
            if not enough_headroom:
                continue

            if spawn_r is not None:
                dist_spawn = abs(r - spawn_r) + abs(c - spawn_c)
                if dist_spawn < MIN_SPAWN_DIST_TILES:
                    continue

            if door_r is not None:
                dist_door = abs(r - door_r) + abs(c - door_c)
                if dist_door < MIN_DOOR_DIST_TILES:
                    continue

            possible_positions.append((r, c))

    chosen_spots = []
    random.shuffle(possible_positions)
    for (r, c) in possible_positions:
        if len(chosen_spots) >= num_blobs:
            break
        conflict = False
        for (rb, cb) in chosen_spots:
            if rb == r and abs(c - cb) < MIN_BLOB_HORIZONTAL_GAP:
                conflict = True
                break
        if not conflict:
            chosen_spots.append((r, c))

    for (r, c) in chosen_spots:
        data_copy[r][c] = 3

    return data_copy

class Blob:
    def __init__(self, x, y, move_range, solid_tiles):
        self.image = pygame.image.load('assets/images/blob1.png')
        self.image = pygame.transform.scale(self.image, (tile_size - 10, tile_size - 10))
        self.rect = self.image.get_rect(topleft=(x + 5, y + 5))
        self.start_x = x
        self.move_range = move_range
        self.direction = 1
        self.solid_tiles = solid_tiles

    def update(self):
        next_rect = self.rect.copy()
        next_rect.x += self.direction
        collided = False
        for tile_rect in self.solid_tiles:
            if next_rect.colliderect(tile_rect):
                collided = True
                break
        if collided:
            self.direction *= -1
        else:
            self.rect = next_rect
        if self.rect.x > self.start_x + self.move_range or self.rect.x < self.start_x:
            self.direction *= -1

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class World:
    def __init__(self, data, offset_x, offset_y):
        self.tile_list = []
        self.lava_tiles = []
        self.coins = []
        self.blobs = []
        self.spawn_pos = None
        self.exit_pos = None
        self.solid_tiles = []
        dirt_img = pygame.image.load('assets/images/dirt.png')
        grass_img = pygame.image.load('assets/images/grass.png')
        exit_img = pygame.image.load('assets/images/door.png')
        lava_img = pygame.image.load('assets/images/lava.png')
        coin_img = pygame.image.load('assets/images/coin.png')

        for row_count, row in enumerate(data):
            for col_count, tile in enumerate(row):
                x = offset_x + col_count * tile_size
                y = offset_y + row_count * tile_size
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                    self.solid_tiles.append(rect)
                elif tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                    self.solid_tiles.append(rect)
                elif tile == 3:
                    blob = Blob(x, y, BLOB_MOVE_RANGE, self.solid_tiles)
                    self.blobs.append(blob)
                elif tile == 4:
                    img = pygame.transform.scale(lava_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.lava_tiles.append(rect)
                    self.tile_list.append((img, rect))
                elif tile == 5:
                    img = pygame.transform.scale(coin_img, (35, 35))
                    coin_rect = img.get_rect(topleft=(x, y))
                    self.coins.append((img, coin_rect))
                elif tile == 7:
                    img = pygame.transform.scale(exit_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.exit_pos = (x, y)
                    self.tile_list.append((img, rect))
                elif tile == 9:
                    self.spawn_pos = (x, y)
        if self.spawn_pos is None:
            raise ValueError("No spawn position (tile=9) found in level data.")

    def draw(self, screen):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
        for coin in self.coins:
            screen.blit(coin[0], coin[1])
        for blob in self.blobs:
            blob.draw(screen)

def run_level(screen, clock, level_background, world_data, level_status, next_level):
    print("DEBUG: Entered run_level()")
    print(f"[DEBUG] Selected skin: {game_data.selected_skin}")
    offset_x = (screen_width - 1000) // 2
    offset_y = (screen_height - 800) // 2
    world = World(world_data, offset_x, offset_y)
    player = Ninja(*world.spawn_pos, skin=game_data.selected_skin)
    level_coins = 0
    font = pygame.font.SysFont(None, 36)
    run = True
    while run:
        screen.blit(pygame.transform.scale(level_background, (screen_width, screen_height)), (0, 0))
        world.draw(screen)
        for blob in world.blobs:
            blob.update()
        for i in range(len(world.coins) - 1, -1, -1):
            coin_img, coin_rect = world.coins[i]
            if player.rect.colliderect(coin_rect):
                world.coins.pop(i)
                level_coins += 1
                game_data.coins_collected += 1
                print(f"DEBUG: Player picked a coin -> level: {level_coins}, global: {game_data.coins_collected}")
        door_rect = None
        if world.exit_pos:
            door_rect = pygame.Rect(
                world.exit_pos[0] + 10,
                world.exit_pos[1] + 5,
                tile_size - 20,
                tile_size - 10
            )
        game_over = player.update(
            keys=pygame.key.get_pressed(),
            tile_list=[tile[1] for tile in world.tile_list],
            lava_tiles=world.lava_tiles,
            blob_tiles=[b.rect for b in world.blobs],
            door_rect=door_rect
        )
        if game_over:
            print("Game Over! Player died.")
            return False
        if door_rect and player.rect.colliderect(door_rect):
            print("Level Completed!")
            return True
        player.draw(screen)
        text_bg_rect = pygame.Rect(screen_width - 400, screen_height - 150, 350, 100)
        pygame.draw.rect(screen, (1, 50, 32), text_bg_rect)
        level_text = font.render(f"Coins this level: {level_coins}", True, (0, 0, 0))
        screen.blit(level_text, (screen_width - 390, screen_height - 140))
        global_text = font.render(f"Total Coins: {game_data.coins_collected}", True, (0, 0, 0))
        screen.blit(global_text, (screen_width - 390, screen_height - 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False
        pygame.display.update()
        clock.tick(60)
    return False

def level_one_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    world_data = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 1],
        [1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 5, 0, 0, 0, 5, 2, 2, 2, 1],
        [1, 9, 0, 2, 1, 1, 1, 2, 0, 0, 2, 2, 2, 0, 0, 2, 1, 1, 1, 1],
        [1, 2, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1]
    ]
    return run_level(screen, clock, level_background, world_data, level_status, next_level=2)

def level_two_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    world_data = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 5, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 2, 2, 2, 2, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 5, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 5, 1],
        [1, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 1],
        [1, 9, 0, 2, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1],
        [1, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]
    ]
    return run_level(screen, clock, level_background, world_data, level_status, next_level=3)

def level_three_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    world_data = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 5, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 9, 1, 0, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 2, 2, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 5, 1],
        [1, 0, 0, 2, 1, 0, 0, 0, 5, 0, 2, 2, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 5, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 1, 0, 0, 1, 5, 1],
        [1, 2, 2, 2, 2, 2, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 7, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 5, 0, 1, 0, 5, 5, 0, 0, 0, 1, 5, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 0, 1, 0, 2, 2, 2, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
    ]
    return run_level(screen, clock, level_background, world_data, level_status, next_level=4)

def level_four_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    world_data = [
        [1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 5, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 0, 9, 1, 2, 0, 1, 0, 0, 0, 5, 0, 0, 0, 5, 0, 1],
        [1, 0, 2, 2, 2, 2, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 0, 5, 0, 5, 0, 5, 0, 2, 1, 0, 0, 5, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 7, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 1],
        [1, 0, 0, 0, 2, 2, 2, 2, 1, 0, 0, 5, 0, 0, 5, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 5, 1],
        [1, 2, 2, 2, 2, 0, 0, 0, 1, 5, 0, 1, 5, 0, 0, 0, 5, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 1, 2, 2, 0, 0, 2, 1, 5, 1],
        [1, 0, 2, 2, 2, 2, 2, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 2, 2, 2, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
    ]
    return run_level(screen, clock, level_background, world_data, level_status, next_level=4)


def level_five_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    world_data = [
        [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 5, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 5, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
        [1, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 0, 2, 0, 0, 2, 2, 2, 2, 1],
        [1, 0, 0, 5, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 0, 5, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 2, 1, 1],
        [1, 9, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1],
        [1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    return run_level(screen, clock, level_background, world_data, level_status, next_level=6)

def level_six_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    world_data = [
        [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 5, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
        [1, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 4, 4, 2, 4, 4, 2, 4, 4, 2, 2, 2, 2, 1],
        [1, 0, 0, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 1],
        [1, 1, 2, 2, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 1],
        [1, 9, 0, 0, 0, 2, 2, 2, 2, 4, 4, 2, 2, 2, 4, 4, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]


    return run_level(screen, clock, level_background, world_data, level_status, next_level=7)


def level_seven_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 2, 2, 2, 2, 1],
        [1, 0, 0, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 5, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 1],
        [1, 1, 2, 2, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 0, 0, 5, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1],
        [1, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 9, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    world_data = place_random_blobs_fair(3, base_world_data)
    return run_level(screen, clock, level_background, world_data, level_status, next_level=8)

def level_eight_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 0, 0, 0, 0, 0, 1],
        [1, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 1],
        [1, 2, 2, 2, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 5, 1],
        [1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 1],
        [1, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 1, 1],
        [1, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1],
        [1, 5, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 2, 2, 9, 1],
        [1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1]
    ]
    world_data = place_random_blobs_fair(3, base_world_data)
    return run_level(screen, clock, level_background, world_data, level_status, next_level=9)

def level_nine_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 4, 4, 2, 2, 0, 0, 0, 0, 5, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 5, 0, 0, 0, 0, 5, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 4, 4, 2, 2, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 1, 5, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 5, 0, 0, 6, 0, 0, 2, 2, 1, 0, 0, 0, 0, 0, 0, 7, 1],
        [1, 0, 2, 2, 2, 2, 4, 4, 2, 2, 2, 1, 5, 1, 0, 0, 0, 0, 2, 2, 2, 1],
        [1, 0, 0, 0, 0, 1, 1, 1, 1, 5, 0, 0, 0, 1, 2, 2, 2, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    world_data = place_random_blobs_fair(3, base_world_data)
    return run_level(screen, clock, level_background, world_data, level_status, next_level=10)

def level_ten_screen(screen, clock, level_status):
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 9, 0, 5, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 2, 2, 2, 2, 4, 4, 2, 2, 5, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 2, 2, 0, 0, 0, 1, 0, 1],
        [1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 5, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 2, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 0, 0, 0, 0, 1, 5, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 1, 2, 2, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 1, 0, 0, 0, 0, 5, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 2, 1, 0, 0, 0, 2, 2, 1, 0, 1],
        [1, 0, 2, 2, 2, 2, 2, 4, 2, 2, 2, 1, 0, 1, 5, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 2, 2, 0, 0, 0, 1, 0, 1],
        [1, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    world_data = place_random_blobs_fair(4, base_world_data)
    return run_level(screen, clock, level_background, world_data, level_status, next_level=10)
