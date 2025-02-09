import sys

import pygame
import os

class Ninja:
    def __init__(self, x, y):
        self.reset(x, y)

    def reset(self, x, y):
        # Paths
        ninja_path = os.path.join('assets', 'images', 'ninja', 'png')
        self.sprite_width = 40
        self.sprite_height = 50

        # Load animations
        self.animations = {
            "run": self.load_animation(ninja_path, "Run__"),
            "idle": self.load_animation(ninja_path, "Idle__"),
            "jump": self.load_animation(ninja_path, "Jump__"),
            "attack": self.load_animation(ninja_path, "Attack__")
        }

        # Initialize attributes
        self.current_animation = "idle"
        self.index = 0
        self.counter = 0
        self.image = self.animations[self.current_animation][self.index]
        self.rect = self.image.get_rect()
        self.rect.width = 30
        self.rect.height = 45
        self.rect.center = (x, y)
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.in_air = True
        self.direction = 1

    def load_animation(self, path, prefix):
        images = []
        for num in range(10):
            img_path = os.path.join(path, f"{prefix}{str(num).zfill(3)}.png")
            img = pygame.image.load(img_path)
            img = pygame.transform.scale(img, (self.sprite_width, self.sprite_height))
            images.append(img)
        return images

    def update(self, keys, tile_list, lava_tiles, blob_tiles, door_rect):
        dx = 0
        dy = 0
        walk_cooldown = 5

        # Default animation to "idle"
        self.current_animation = "idle"

        # Handle key input for movement
        if keys[pygame.K_LEFT]:
            dx = -5
            self.counter += 1
            self.direction = -1
            self.current_animation = "run"
        if keys[pygame.K_RIGHT]:
            dx = 5
            self.counter += 1
            self.direction = 1
            self.current_animation = "run"
        if keys[pygame.K_SPACE] and not self.jumped and not self.in_air:
            self.vel_y = -15  # Jump velocity
            self.jumped = True
            self.current_animation = "jump"
        if not keys[pygame.K_SPACE]:
            self.jumped = False

        # Gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Animation handling
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.animations[self.current_animation]):
                self.index = 0

        # Set the current animation frame
        self.image = self.animations[self.current_animation][self.index]
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        # Collision detection
        self.in_air = True
        for tile in tile_list:
            # Skip the door tile from collision checks
            if tile.colliderect(door_rect):  # Skip the door rect
                continue

            # Collision in the x-direction
            if tile.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            # Collision in the y-direction
            if tile.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y < 0:  # If jumping
                    dy = tile.bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:  # If falling
                    dy = tile.top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        # ✅ Check collision with lava tiles (player's feet)
        for lava_rect in lava_tiles:
            if (
                    self.rect.bottom >= lava_rect.top - 5  # Allow small overlap
                    and self.rect.bottom <= lava_rect.bottom
                    and self.rect.centerx > lava_rect.left
                    and self.rect.centerx < lava_rect.right
            ):
                print("Game Over! Player touched lava.")
                pygame.quit()
                sys.exit()

        # ✅ Check collision with blob tiles (player's body)
        for blob_rect in blob_tiles:
            # Adjust the blob hitbox to make it smaller for better visuals
            smaller_blob_rect = blob_rect.inflate(-10, -10)  # Reduce width and height by 10 pixels
            if self.rect.colliderect(smaller_blob_rect):
                print("Game Over! Player touched a blob.")
                pygame.quit()
                sys.exit()

        # Update position
        self.rect.x += dx
        self.rect.y += dy

        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
