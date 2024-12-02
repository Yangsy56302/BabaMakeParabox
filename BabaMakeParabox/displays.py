from typing import Optional
import os

from BabaMakeParabox import colors, objects, spaces

import pygame

pixel_size = 4
sprite_size = 24
pixel_sprite_size = pixel_size * sprite_size

def set_pixel_size(window_size: spaces.Coord) -> None:
    global pixel_size, sprite_size, pixel_sprite_size
    if min(window_size) < 320:
        pixel_size = 1
    elif min(window_size) < 480:
        pixel_size = 2
    elif min(window_size) < 640:
        pixel_size = 3
    elif min(window_size) < 960:
        pixel_size = 4
    elif min(window_size) < 1280:
        pixel_size = 6
    else:
        pixel_size = 8
    pixel_sprite_size = pixel_size * sprite_size

def set_alpha(surface: pygame.Surface, alpha: int) -> pygame.Surface:
    new_surface = surface.copy()
    new_surface.fill(pygame.Color(255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    return new_surface

def set_surface_color_dark(surface: pygame.Surface, color: colors.ColorHex) -> pygame.Surface:
    r, g, b = colors.hex_to_rgb(color)
    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    new_surface.fill(pygame.Color(r, g, b, 255))
    new_surface.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return new_surface

def set_surface_color_light(surface: pygame.Surface, color: colors.ColorHex) -> pygame.Surface:
    r, g, b = colors.hex_to_rgb(color)
    clr_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    clr_surface.fill(pygame.Color(255 - r, 255 - g, 255 - b, 255))
    neg_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    neg_surface.fill("#FFFFFFFF")
    neg_surface.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    clr_surface.blit(neg_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    new_surface.fill("#FFFFFFFF")
    new_surface.blit(clr_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return new_surface

class Sprites(object):
    def __init__(self) -> None:
        pass
    def update(self) -> None:
        self.raw_sprites: dict[str, dict[int, dict[int, pygame.Surface]]] = {}
        self.sprites: dict[str, dict[int, dict[int, pygame.Surface]]] = {}
        for obj_type in objects.object_used:
            sprite_name: str = getattr(obj_type, "sprite_name", "")
            if sprite_name == "":
                continue
            sprite_color: colors.ColorHex = getattr(obj_type, "sprite_color", colors.WHITE)
            sprite_varients: list[int] = getattr(obj_type, "sprite_varients")
            self.raw_sprites.setdefault(sprite_name, {})
            self.sprites.setdefault(sprite_name, {})
            for varient_number in sprite_varients:
                self.raw_sprites[sprite_name].setdefault(varient_number, {})
                self.sprites[sprite_name].setdefault(varient_number, {})
                for frame in range(1, 4):
                    filename = "_".join([sprite_name, str(varient_number), str(frame)]) + ".png"
                    sprite = pygame.image.load(os.path.join("sprites", filename)).convert_alpha()
                    self.raw_sprites[sprite_name][int(varient_number)][int(frame)] = sprite.copy()
                    self.sprites[sprite_name][int(varient_number)][int(frame)] = set_surface_color_dark(sprite, sprite_color)
        special_sprite_name: list[str] = ["empty", "text_infinite", "text_epsilon"]
        special_sprite_name.extend(["text_" + str(i) for i in range(10)])
        for sprite_name in special_sprite_name:
            self.raw_sprites.setdefault(sprite_name, {0: {}})
            self.sprites.setdefault(sprite_name, {0: {}})
            for frame in range(1, 4):
                filename = "_".join([sprite_name, str(varient_number), str(frame)]) + ".png"
                sprite = pygame.image.load(os.path.join("sprites", filename)).convert_alpha()
                self.raw_sprites[sprite_name][0][int(frame)] = sprite.copy()
                self.sprites[sprite_name][0][int(frame)] = set_surface_color_dark(sprite, sprite_color)
    def get(self, name: str, varient: int, frame: int = 0, raw_sprite: bool = False) -> pygame.Surface:
        if raw_sprite:
            return self.raw_sprites[name][varient][frame]
        return self.sprites[name][varient][frame]

order = [objects.Cursor,
         objects.Operator,
         objects.Noun,
         objects.Property,
         objects.Text,
         objects.Character,
         objects.Level,
         objects.Static,
         objects.AnimatedDirectional,
         objects.Directional,
         objects.Animated,
         objects.Tiled,
         objects.WorldPointer,
         objects.BmpObject]

sprites = Sprites()