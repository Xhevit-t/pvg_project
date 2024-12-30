import pygame
import os


class Ninja:
    def __init__(self, x, y):
        self.reset(x, y)

    def reset(self, x, y):
        # Paths
        ninja_path = os.path.join('assets', 'images', 'ninja', 'png')
        self.sprite_width = 40  # Standardized width for all sprites
        self.sprite_height = 50  # Standardized height for all sprites

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
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.in_air = True
        self.direction = 1  # 1 = right, -1 = left

    def load_animation(self, path, prefix):
        """Load a sequence of images for an animation."""
        images = []
        for num in range(10):  # Assuming 10 frames per animation
            img_path = os.path.join(path, f"{prefix}{str(num).zfill(3)}.png")
            img = pygame.image.load(img_path)
            # Resize all sprites to consistent dimensions
            img = pygame.transform.scale(img, (self.sprite_width, self.sprite_height))
            images.append(img)
        return images

    def update(self, keys, tile_list):
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

        # Update position
        self.rect.x += dx
        self.rect.y += dy

    def draw(self, screen):
        """Draw the ninja on the screen."""
        screen.blit(self.image, self.rect)
