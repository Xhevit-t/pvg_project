import sys
import random
import pygame
from player import Ninja

#
# --------------- SCREEN & GLOBAL SETTINGS ---------------
#

tile_size = 50
screen_width = 1920
screen_height = 1080


def initialize_screen():
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Escape the Maze')
    return screen


#
# --------------- ADVANCED FAIR BLOB PLACEMENT ---------------
#

BLOB_MOVE_RANGE = 100  # Each Blob moves 100 pixels horizontally
TILE_SIZE = 50  # each tile is 50px
MIN_SPAWN_DIST_TILES = 3
MIN_DOOR_DIST_TILES = 2

# Additional fairness constraints
MIN_VERTICAL_CLEARANCE = 2  # Need 2 rows of empty air overhead
MIN_BLOB_HORIZONTAL_GAP = 2  # If more than 1 blob, keep them spaced on the same row.


def place_random_blobs_fair(num_blobs, base_world_data):
    """
    Returns a copy of 'base_world_data' with up to 'num_blobs' replaced by '3' (Blob).

    Key points:
      - Only spawn the blob if row=r is '0' (empty), so it never spawns inside grass/dirt.
      - Row (r+1) must be ground (1 or 2) across the entire horizontal range => no floating.
      - At least 2 rows of overhead air => row (r-1) & (r-2) must be 0 as well.
      - Keep distance from spawn(9) & door(7).
      - If more than 1 blob, ensure horizontal spacing on same row.
    """
    data_copy = [row[:] for row in base_world_data]
    rows = len(data_copy)
    cols = len(data_copy[0]) if rows > 0 else 0

    range_in_tiles = BLOB_MOVE_RANGE // TILE_SIZE  # e.g. 2 for 100 px / 50 px

    # Find spawn(9) and door(7)
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

    # Start from row=2 so we have 2 rows above => r-1, r-2
    # Also ensure r+1 < rows => r < rows-1
    for r in range(2, rows - 1):
        for c in range(cols - range_in_tiles):
            # 1) row=r must be all '0' across c..c+range_in_tiles
            row_open = True
            for step in range(range_in_tiles + 1):
                if data_copy[r][c + step] != 0:  # strictly 0 only
                    row_open = False
                    break
            if not row_open:
                continue

            # 2) row below must be ground => 1 or 2
            supported = True
            for step in range(range_in_tiles + 1):
                below_tile = data_copy[r + 1][c + step]
                if below_tile not in [1, 2]:
                    supported = False
                    break
            if not supported:
                continue

            # 3) overhead clearance => row (r-1) and (r-2) must be 0
            #    across c..c+range_in_tiles
            enough_headroom = True
            for step in range(range_in_tiles + 1):
                if data_copy[r - 1][c + step] != 0 or data_copy[r - 2][c + step] != 0:
                    enough_headroom = False
                    break
            if not enough_headroom:
                continue

            # 4) distance from spawn
            if spawn_r is not None:
                dist_spawn = abs(r - spawn_r) + abs(c - spawn_c)
                if dist_spawn < MIN_SPAWN_DIST_TILES:
                    continue

            # 5) distance from door
            if door_r is not None:
                dist_door = abs(r - door_r) + abs(c - door_c)
                if dist_door < MIN_DOOR_DIST_TILES:
                    continue

            possible_positions.append((r, c))

    # If multiple blobs, enforce horizontal gap
    chosen_spots = []
    random.shuffle(possible_positions)
    for (r, c) in possible_positions:
        if len(chosen_spots) >= num_blobs:
            break
        conflict = False
        for (rb, cb) in chosen_spots:
            if rb == r:
                if abs(c - cb) < MIN_BLOB_HORIZONTAL_GAP:
                    conflict = True
                    break
        if not conflict:
            chosen_spots.append((r, c))

    # Mark them as '3'
    for (r, c) in chosen_spots:
        data_copy[r][c] = 3

    return data_copy


#
# --------------- BLOB WITH COLLISION ---------------
#

class Blob:
    """A horizontally-moving slime that checks for collisions with solid walls."""

    def __init__(self, x, y, move_range, solid_tiles):
        self.image = pygame.image.load('assets/images/blob1.png')
        self.image = pygame.transform.scale(self.image, (tile_size - 10, tile_size - 10))
        self.rect = self.image.get_rect(topleft=(x + 5, y + 5))
        self.start_x = x
        self.move_range = move_range
        self.direction = 1  # +1 => moves right, -1 => left

        # Keep references to all solid tiles (dirt=1, grass=2)
        # We'll collide with these.
        self.solid_tiles = solid_tiles

    def update(self):
        """Move left/right one pixel at a time, reversing if hitting walls or range edges."""
        # Predict next position
        next_rect = self.rect.copy()
        next_rect.x += self.direction

        # Check collision with any solid tile
        collided = False
        for tile_rect in self.solid_tiles:
            if next_rect.colliderect(tile_rect):
                collided = True
                break

        # If collision, reverse direction; else move
        if collided:
            self.direction *= -1
        else:
            self.rect = next_rect

        # Also handle range boundaries
        if self.rect.x > self.start_x + self.move_range or self.rect.x < self.start_x:
            self.direction *= -1

    def draw(self, screen):
        screen.blit(self.image, self.rect)


#
# --------------- WORLD CLASS ---------------
#

class World:
    """Holds tile data, lava, and blob instances for a given level."""

    def __init__(self, data, offset_x, offset_y):
        self.tile_list = []
        self.lava_tiles = []
        self.blobs = []
        self.spawn_pos = None
        self.exit_pos = None

        # We'll store all solid tile rects here, to pass to Blobs
        self.solid_tiles = []

        dirt_img = pygame.image.load('assets/images/dirt.png')
        grass_img = pygame.image.load('assets/images/grass.png')
        exit_img = pygame.image.load('assets/images/door.png')
        lava_img = pygame.image.load('assets/images/lava.png')

        for row_count, row in enumerate(data):
            for col_count, tile in enumerate(row):
                x = offset_x + col_count * tile_size
                y = offset_y + row_count * tile_size

                if tile == 1:
                    # Dirt => solid
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                    self.solid_tiles.append(rect)

                elif tile == 2:
                    # Grass => solid
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                    self.solid_tiles.append(rect)

                elif tile == 3:
                    # Blob => pass self.solid_tiles for collision
                    blob = Blob(x, y, BLOB_MOVE_RANGE, self.solid_tiles)
                    self.blobs.append(blob)

                elif tile == 4:
                    # Lava
                    img = pygame.transform.scale(lava_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.lava_tiles.append(rect)
                    self.tile_list.append((img, rect))

                elif tile == 7:
                    # Exit
                    img = pygame.transform.scale(exit_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.exit_pos = (x, y)
                    self.tile_list.append((img, rect))

                elif tile == 9:
                    # Player spawn
                    self.spawn_pos = (x, y)

        if self.spawn_pos is None:
            raise ValueError("No spawn position (tile=9) found in level data.")

    def draw(self, screen):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
        for blob in self.blobs:
            blob.draw(screen)


#
# --------------- RUN LEVEL ---------------
#

def run_level(screen, clock, level_background, world_data, level_status, next_level):
    """Main loop for a level. Returns True if completed, False if game over."""
    offset_x = (screen_width - 1000) // 2
    offset_y = (screen_height - 800) // 2

    world = World(world_data, offset_x, offset_y)
    player = Ninja(*world.spawn_pos)

    run = True
    while run:
        screen.blit(pygame.transform.scale(level_background, (screen_width, screen_height)), (0, 0))
        world.draw(screen)

        # Update all blobs
        for blob in world.blobs:
            blob.update()

        # Check door collision
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
            blob_tiles=[blob.rect for blob in world.blobs],
            door_rect=door_rect
        )
        if game_over:
            print("Game Over! Player died.")
            return False

        if door_rect and player.rect.colliderect(door_rect):
            print("Level Completed!")
            return True

        player.draw(screen)

        # Debug bounding boxes (optional)
        pygame.draw.rect(screen, (255, 0, 0), player.rect, 2)
        if door_rect:
            pygame.draw.rect(screen, (0, 255, 0), door_rect, 2)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False

        pygame.display.update()
        clock.tick(60)


#
#
# --------------- LEVEL SCREENS 1-10 ---------------
#
def level_one_screen(screen, clock, level_status):
    # 0 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
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
    random_data = place_random_blobs_fair(0, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=2)

def level_two_screen(screen, clock, level_status):
    # 2 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 1],
        [1, 9, 0, 2, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
    ]
    random_data = place_random_blobs_fair(1, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=3)

def level_three_screen(screen, clock, level_status):
    # 2 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 9, 1, 0, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 2, 2, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 2, 1, 0, 0, 0, 0, 0, 2, 2, 1, 0, 1, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
        [1, 2, 2, 2, 2, 2, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 7, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 0, 1, 0, 2, 2, 2, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    random_data = place_random_blobs_fair(4, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=4)

def level_four_screen(screen, clock, level_status):
    # 3 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 0, 9, 1, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 2, 2, 2, 2, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 7, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 0, 1, 0, 1],
        [1, 2, 2, 2, 2, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 1, 2, 2, 0, 0, 2, 1, 0, 1],
        [1, 0, 2, 2, 2, 2, 2, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 2, 2, 2, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
    ]
    random_data = place_random_blobs_fair(4, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=5)

def level_five_screen(screen, clock, level_status):
    # 3 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 0, 2, 0, 0, 2, 2, 2, 2, 1],
        [1, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1],
        [1, 9, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    random_data = place_random_blobs_fair(2, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=6)

def level_six_screen(screen, clock, level_status):
    # 4 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 4, 4, 2, 4, 4, 2, 4, 4, 2, 2, 2, 2, 1],
        [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 9, 0, 0, 0, 2, 2, 2, 2, 4, 4, 2, 2, 2, 4, 4, 2, 2, 2, 1],
        [1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    random_data = place_random_blobs_fair(3, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=7)

def level_seven_screen(screen, clock, level_status):
    # 4 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 1],
        [1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 0, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 9, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    random_data = place_random_blobs_fair(3, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=8)

def level_eight_screen(screen, clock, level_status):
    # 5 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1],
        [1, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 2, 2, 9, 1],
        [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    random_data = place_random_blobs_fair(4, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=9)

def level_nine_screen(screen, clock, level_status):
    # 5 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4, 4, 2, 2, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 4, 4, 2, 2, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 1, 0, 0, 2, 2, 2, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 0, 0, 0, 0, 0, 0, 7, 1],
        [1, 0, 2, 2, 2, 2, 4, 2, 2, 2, 2, 1, 0, 1, 0, 0, 0, 0, 2, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 2, 2, 2, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    random_data = place_random_blobs_fair(4, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=10)

def level_ten_screen(screen, clock, level_status):
    # 6 Blobs
    level_background = pygame.image.load('assets/images/level_background.png')
    base_world_data = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 2, 2, 2, 2, 4, 4, 2, 2, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 2, 2, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 2, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 1, 2, 2, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 0, 0, 0, 2, 2, 1, 0, 1],
        [1, 0, 2, 2, 2, 2, 4, 2, 2, 2, 2, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 2, 2, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    random_data = place_random_blobs_fair(5, base_world_data)
    return run_level(screen, clock, level_background, random_data, level_status, next_level=10)
