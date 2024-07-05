import pygame
import random

def set_color_dark(surface: pygame.Surface, color: pygame.Color) -> pygame.Surface:
    color = pygame.Color(color)
    new_surface = surface.copy()
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            pixel_color = pygame.Color(surface.get_at((x, y)))
            pixel_color.r = int(pixel_color.r * color.r / 255)
            pixel_color.g = int(pixel_color.g * color.g / 255)
            pixel_color.b = int(pixel_color.b * color.b / 255)
            new_surface.set_at((x, y), pixel_color)
    return new_surface

def set_color_light(surface: pygame.Surface, color: pygame.Color) -> pygame.Surface:
    color = pygame.Color(color)
    new_surface = surface.copy()
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            pixel_color = pygame.Color(surface.get_at((x, y)))
            pixel_color.r = 255 - int((255 - pixel_color.r) * color.r / 255)
            pixel_color.g = 255 - int((255 - pixel_color.g) * color.b / 255)
            pixel_color.b = 255 - int((255 - pixel_color.g) * color.b / 255)
            new_surface.set_at((x, y), pixel_color)
    return new_surface

def random_hue() -> pygame.Color:
    n = random.random()
    if n <= 1 / 6:
        r = 255
        g = 255 * (n * 6)
        b = 0
    elif n <= 2 / 6:
        r = 255 - 255 * ((n - 1 / 6) * 6)
        g = 255
        b = 0
    elif n <= 3 / 6:
        r = 0
        g = 255
        b = 255 * ((n - 2 / 6) * 6)
    elif n <= 4 / 6:
        r = 0
        g = 255 - 255 * ((n - 3 / 6) * 6)
        b = 255
    elif n <= 5 / 6:
        r = 255 * ((n - 4 / 6) * 6)
        g = 0
        b = 255
    else:
        r = 255
        g = 0
        b = 255 * ((n - 5 / 6) * 6)
    return pygame.Color(int(r), int(g), int(b))

default_surface_size = 24
sprite_size = 24