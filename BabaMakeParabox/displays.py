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
    if color == 0xFFFFFF:
        return surface.copy()
    r, g, b = colors.hex_to_rgb(color)
    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    new_surface.fill(pygame.Color(r, g, b, 255))
    new_surface.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return new_surface

def set_surface_color_light(surface: pygame.Surface, color: colors.ColorHex) -> pygame.Surface:
    if color == 0x000000:
        return surface.copy()
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
        for object_type in objects.object_used:
            sprite_name: str = getattr(object_type, "sprite_name", "")
            if sprite_name == "":
                continue
            sprite_color: colors.ColorHex = getattr(object_type, "sprite_color", colors.WHITE)
            sprite_varients: list[int] = getattr(object_type, "sprite_varients")
            self.raw_sprites.setdefault(object_type.json_name, {})
            self.sprites.setdefault(object_type.json_name, {})
            for varient_number in sprite_varients:
                self.raw_sprites[object_type.json_name].setdefault(varient_number, {})
                self.sprites[object_type.json_name].setdefault(varient_number, {})
                for wiggle in range(1, 4):
                    filename = "_".join([sprite_name, str(varient_number), str(wiggle)]) + ".png"
                    sprite = pygame.image.load(os.path.join("sprites", filename)).convert_alpha()
                    self.raw_sprites[object_type.json_name][int(varient_number)][int(wiggle)] = sprite.copy()
                    self.sprites[object_type.json_name][int(varient_number)][int(wiggle)] = set_surface_color_dark(sprite, sprite_color)
        special_sprite_name: list[str] = ["empty", "text_infinity", "text_epsilon"]
        special_sprite_name.extend(["text_" + str(i) for i in range(10)])
        for sprite_name in special_sprite_name:
            self.raw_sprites.setdefault(sprite_name, {0: {}})
            self.sprites.setdefault(sprite_name, {0: {}})
            for wiggle in range(1, 4):
                filename = "_".join([sprite_name, str(varient_number), str(wiggle)]) + ".png"
                sprite = pygame.image.load(os.path.join("sprites", filename)).convert_alpha()
                self.raw_sprites[sprite_name][0][int(wiggle)] = sprite.copy()
                self.sprites[sprite_name][0][int(wiggle)] = set_surface_color_dark(sprite, sprite_color)
    def get(self, name: str, varient: int, wiggle: int = 1, raw: bool = False) -> pygame.Surface:
        if raw:
            return self.raw_sprites[name][varient][wiggle]
        return self.sprites[name][varient][wiggle]
sprites = Sprites()

def simple_type_to_surface(object_type: type[objects.Object], varient: int = 0, wiggle: int = 1, default_surface: Optional[pygame.Surface] = None, debug: bool = False) -> pygame.Surface:
    if issubclass(object_type, objects.WorldObject):
        if default_surface is not None:
            obj_surface = default_surface.copy()
        else:
            obj_surface = pygame.Surface((pixel_sprite_size, pixel_sprite_size), pygame.SRCALPHA)
            obj_surface.fill(object_type.sprite_color)
        obj_surface = set_surface_color_light(obj_surface, object_type.light_overlay)
        obj_surface = set_surface_color_dark(obj_surface, object_type.dark_overlay)
    else:
        obj_surface = sprites.get(object_type.json_name, varient, wiggle).copy()
        if issubclass(object_type, objects.Metatext):
            obj_surface = pygame.transform.scale(obj_surface, (sprite_size * len(str(object_type.meta_tier)), sprite_size * len(str(object_type.meta_tier))))
            tier_surface = pygame.Surface((sprite_size * len(str(object_type.meta_tier)), sprite_size), pygame.SRCALPHA)
            tier_surface.fill("#00000000")
            for digit, char in enumerate(str(object_type.meta_tier)):
                tier_surface.blit(sprites.get("text_" + char, varient, wiggle), (sprite_size * digit, 0))
            tier_surface = set_alpha(tier_surface, 0x80)
            tier_surface_pos = ((obj_surface.get_width() - tier_surface.get_width()) // 2,
                                (obj_surface.get_height() - tier_surface.get_height()) // 2)
            obj_surface.blit(tier_surface, tier_surface_pos)
    return obj_surface

def simple_object_to_surface(obj: objects.Object, wiggle: int = 1, default_surface: Optional[pygame.Surface] = None, debug: bool = False) -> pygame.Surface:
    if isinstance(obj, objects.LevelObject):
        obj_surface = set_surface_color_dark(sprites.get(obj.json_name, obj.sprite_state, wiggle, raw=True).copy(), obj.level_object_extra["icon"]["color"])
        icon_surface = sprites.get(obj.level_object_extra["icon"]["name"], 0, wiggle, raw=True).copy()
        icon_surface = set_surface_color_light(set_surface_color_dark(icon_surface, obj.level_object_extra["icon"]["color"]), 0xC0C0C0)
        icon_surface_pos = ((obj_surface.get_width() - icon_surface.get_width()) // 2,
                            (obj_surface.get_height() - icon_surface.get_height()) // 2)
        obj_surface.blit(icon_surface, icon_surface_pos)
    else:
        obj_surface = simple_type_to_surface(type(obj), obj.sprite_state, wiggle, default_surface, debug)
        if isinstance(obj, objects.Path):
            if not obj.unlocked:
                if debug:
                    obj_surface = set_alpha(obj_surface, 0x80)
                else:
                    obj_surface.fill("#00000000")
    return obj_surface

order: tuple[type[objects.Object], ...] = (
    objects.Cursor,
    objects.Operator,
    objects.Noun,
    objects.Property,
    objects.Text,
    objects.Character,
    objects.LevelObject,
    objects.Static,
    objects.AnimatedDirectional,
    objects.Directional,
    objects.Animated,
    objects.Tiled,
    objects.WorldObject,
    objects.Object
)