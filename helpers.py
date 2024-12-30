import pygame

def scale_button(button, scaling_factor, screen_width):
    btn_width, btn_height = button.get_size()
    btn_new_width = int(screen_width * scaling_factor)
    btn_new_height = int(btn_new_width * btn_height / btn_width)
    return pygame.transform.scale(button, (btn_new_width, btn_new_height))

def render_text(screen, text, font, color, center):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center)
    screen.blit(text_surface, text_rect)
