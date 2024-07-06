import pygame
import random

def set_color_dark(surface: pygame.Surface, color: pygame.Color) -> pygame.Surface:
    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    new_surface.fill(pygame.Color(color.r, color.g, color.b, 255))
    new_surface.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return new_surface

def set_color_light_(surface: pygame.Surface, color: pygame.Color) -> pygame.Surface:
    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    new_surface.fill(pygame.Color(color.r, color.g, color.b, 255))
    temp_surface = surface.copy()
    temp_surface.fill("#FFFFFF00", special_flags=pygame.BLEND_RGBA_SUB)
    new_surface.blit(temp_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    new_surface.fill("#FFFFFF00", special_flags=pygame.BLEND_RGBA_SUB)
    return new_surface

def set_color_light(surface: pygame.Surface, color: pygame.Color) -> pygame.Surface:
    clr_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    clr_surface.fill(pygame.Color(255 - color.r, 255 - color.g, 255 - color.b, 255))
    neg_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    neg_surface.fill("#FFFFFFFF")
    neg_surface.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    clr_surface.blit(neg_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    new_surface.fill("#FFFFFFFF")
    new_surface.blit(clr_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
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

pixel_size = 6
sprite_size = 24