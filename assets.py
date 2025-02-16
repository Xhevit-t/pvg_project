import pygame
from constants import IMAGES_DIR, SOUNDS_DIR

def load_image(filename, size=None):
    path = f"{IMAGES_DIR}/{filename}"
    image = pygame.image.load(path)
    if size:
        image = pygame.transform.scale(image, size)
    return image

def load_sound(filename):
    path = f"{SOUNDS_DIR}/{filename}"
    sound = pygame.mixer.Sound(path)
    return sound

def load_font(filename='freesans', size=30):

    return pygame.font.SysFont(filename, size) if filename else pygame.font.SysFont(None, size)

