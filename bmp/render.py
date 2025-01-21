from typing import Any, Callable, Optional
import os
import string

import bmp.base
import bmp.color
import bmp.lang
import bmp.obj

import pygame

def calc_smooth(frame: int) -> Optional[float]:
    multiplier = bmp.base.options["smooth_animation_multiplier"]
    if multiplier is not None:
        smooth_value = frame / bmp.base.options["fps"] * multiplier
        if smooth_value >= 0 and smooth_value <= 1:
            return (1 - smooth_value) ** 4

sprite_size = 24
gui_scale = 3

def set_alpha(surface: pygame.Surface, alpha: int) -> pygame.Surface:
    new_surface = surface.copy()
    new_surface.fill(pygame.Color(255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    return new_surface

def set_surface_color_dark(surface: pygame.Surface, color: bmp.color.ColorHex) -> pygame.Surface:
    if color == 0xFFFFFF:
        return surface.copy()
    r, g, b = bmp.color.hex_to_rgb(color)
    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    new_surface.fill(pygame.Color(r, g, b, 255))
    new_surface.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return new_surface

def set_surface_color_light(surface: pygame.Surface, color: bmp.color.ColorHex) -> pygame.Surface:
    if color == 0x000000:
        return surface.copy()
    r, g, b = bmp.color.hex_to_rgb(color)
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
        self.raw_sprites: dict[str, dict[int, dict[int, pygame.Surface]]] = {}
        self.sprites: dict[str, dict[int, dict[int, pygame.Surface]]] = {}
    def update(self) -> None:
        self.raw_sprites.clear()
        self.sprites.clear()
        empty_sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        empty_sprite.fill("#00000000")
        self.raw_sprites.setdefault("empty", {0: {}})
        self.sprites.setdefault("empty", {0: {}})
        for wiggle in range(1, 4):
            self.raw_sprites["empty"][0][int(wiggle)] = empty_sprite.copy()
            self.sprites["empty"][0][int(wiggle)] = empty_sprite.copy()
        for object_type in bmp.obj.object_class_list:
            sprite_name: str = getattr(object_type, "sprite_name", "")
            if sprite_name == "":
                continue
            sprite_palette: bmp.color.ColorHex = object_type.get_color()
            sprite_varients: list[int] = bmp.obj.Object.sprite_varients[object_type.sprite_category]
            self.raw_sprites.setdefault(object_type.json_name, {})
            self.sprites.setdefault(object_type.json_name, {})
            for varient_number in sprite_varients:
                self.raw_sprites[object_type.json_name].setdefault(varient_number, {})
                self.sprites[object_type.json_name].setdefault(varient_number, {})
                for wiggle in range(1, 4):
                    filename = "_".join([sprite_name, str(varient_number), str(wiggle)]) + ".png"
                    if os.path.isfile(os.path.join("sprites", filename)):
                        sprite = pygame.image.load(os.path.join("sprites", filename)).convert_alpha()
                    else:
                        bmp.lang.lang_warn("warn.file.not_found", file=os.path.join("sprites", filename))
                        sprite = empty_sprite.copy()
                    self.raw_sprites[object_type.json_name][int(varient_number)][int(wiggle)] = sprite.copy()
                    self.sprites[object_type.json_name][int(varient_number)][int(wiggle)] = set_surface_color_dark(sprite, sprite_palette)
        special_sprite_name: list[str] = ["text_" + c for c in string.digits]
        special_sprite_name.extend(["text_" + c for c in string.ascii_lowercase])
        for sprite_name in special_sprite_name:
            self.raw_sprites.setdefault(sprite_name, {0: {}})
            self.sprites.setdefault(sprite_name, {0: {}})
            for wiggle in range(1, 4):
                filename = "_".join([sprite_name, str(varient_number), str(wiggle)]) + ".png"
                if os.path.isfile(os.path.join("sprites", filename)):
                    sprite = pygame.image.load(os.path.join("sprites", filename)).convert_alpha()
                else:
                    bmp.lang.lang_warn("warn.file.not_found", file=os.path.join("sprites", filename))
                    sprite = empty_sprite.copy()
                self.raw_sprites[sprite_name][0][int(wiggle)] = sprite.copy()
                self.sprites[sprite_name][0][int(wiggle)] = set_surface_color_dark(sprite, sprite_palette)
    def get(self, name: str, varient: int, wiggle: int = 1, raw: bool = False) -> pygame.Surface:
        if raw: return self.raw_sprites[name][varient][wiggle]
        return self.sprites[name][varient][wiggle]
current_sprites = Sprites()

def simple_type_to_surface(object_type: type[bmp.obj.Object], varient: int = 0, wiggle: int = 1, default_surface: Optional[pygame.Surface] = None, debug: bool = False) -> pygame.Surface:
    obj_surface = current_sprites.get("empty", 0, wiggle, raw=True).copy()
    if issubclass(object_type, bmp.obj.SpaceObject):
        if default_surface is not None:
            obj_surface = default_surface.copy()
        else:
            obj_surface = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            obj_surface.fill(object_type.get_color())
        obj_surface = set_surface_color_light(obj_surface, object_type.light_overlay)
        obj_surface = set_surface_color_dark(obj_surface, object_type.dark_overlay)
        overlay_surface = current_sprites.get(bmp.obj.SpaceObject.sprite_name, 0, wiggle, raw=True).copy()
        overlay_surface = pygame.transform.scale(set_alpha(overlay_surface, 0x40), obj_surface.get_size())
        obj_surface.blit(overlay_surface, (0, 0))
    elif object_type.json_name in current_sprites.sprites.keys():
        obj_surface = current_sprites.get(object_type.json_name, varient, wiggle).copy()
    elif issubclass(object_type, bmp.obj.Metatext):
        obj_surface = current_sprites.get(object_type.basic_ref_type.json_name, varient, wiggle).copy()
        obj_surface = pygame.transform.scale(obj_surface, (sprite_size * len(str(object_type.meta_tier)), sprite_size * len(str(object_type.meta_tier))))
        tier_surface = pygame.Surface((sprite_size * len(str(object_type.meta_tier)), sprite_size), pygame.SRCALPHA)
        tier_surface.fill("#00000000")
        for digit, char in enumerate(str(object_type.meta_tier)):
            tier_surface.blit(current_sprites.get("text_" + char, varient, wiggle), (sprite_size * digit, 0))
        tier_surface = set_alpha(tier_surface, 0x80)
        tier_surface_pos = ((obj_surface.get_width() - tier_surface.get_width()) // 2,
                            (obj_surface.get_height() - tier_surface.get_height()) // 2)
        obj_surface.blit(tier_surface, tier_surface_pos)
    return obj_surface

def simple_object_to_surface(obj: bmp.obj.Object, wiggle: int = 1, default_surface: Optional[pygame.Surface] = None, debug: bool = False) -> pygame.Surface:
    if isinstance(obj, bmp.obj.LevelObject):
        obj_surface = set_surface_color_dark(current_sprites.get(obj.json_name, obj.sprite_state, wiggle, raw=True).copy(), obj.level_extra["icon"]["color"])
        icon_surface = current_sprites.get(obj.level_extra["icon"]["name"], 0, wiggle, raw=True).copy()
        icon_surface_pos = ((obj_surface.get_width() - icon_surface.get_width()) // 2,
                            (obj_surface.get_height() - icon_surface.get_height()) // 2)
        obj_surface.blit(icon_surface, icon_surface_pos)
    else:
        obj_surface = simple_type_to_surface(type(obj), obj.sprite_state, wiggle, default_surface, debug)
        if isinstance(obj, bmp.obj.Path):
            if not obj.unlocked:
                if debug:
                    obj_surface = set_alpha(obj_surface, 0x80)
                else:
                    obj_surface.fill("#00000000")
        if isinstance(obj, bmp.obj.SpaceObject) and obj.space_id.infinite_tier != 0:
            infinite_text_surface = current_sprites.get("text_infinity" if obj.space_id.infinite_tier > 0 else "text_epsilon", 0, wiggle, raw=True)
            infinite_tier_surface = pygame.Surface((sprite_size, sprite_size * abs(obj.space_id.infinite_tier)), pygame.SRCALPHA)
            infinite_tier_surface.fill("#00000000")
            for i in range(abs(obj.space_id.infinite_tier)):
                infinite_tier_surface.blit(infinite_text_surface, (0, i * sprite_size))
            infinite_tier_surface = set_alpha(infinite_tier_surface, 0x80)
            infinite_tier_surface = pygame.transform.scale(infinite_tier_surface, obj_surface.get_size())
            obj_surface.blit(infinite_tier_surface, (0, 0))
    return obj_surface

def valid(__obj: bmp.obj.Object, /) -> bool:
    return __obj.sprite_category != "none" or isinstance(__obj, (bmp.obj.SpaceObject, bmp.obj.LevelObject, bmp.obj.Metatext))

order: list[Callable[..., bool]] = [
    lambda o: isinstance(o, bmp.obj.Cursor),
    lambda o: isinstance(o, bmp.obj.Operator),
    lambda o: isinstance(o, bmp.obj.Noun),
    lambda o: isinstance(o, bmp.obj.Property),
    lambda o: isinstance(o, bmp.obj.Text),
    lambda o: isinstance(o, bmp.obj.LevelObject),
    lambda o: isinstance(o, bmp.obj.SpaceObject),
    lambda o: isinstance(o, bmp.obj.Object) and o.sprite_category == "character",
    lambda o: isinstance(o, bmp.obj.Object) and o.sprite_category == "animated_directional",
    lambda o: isinstance(o, bmp.obj.Object) and o.sprite_category == "directional",
    lambda o: isinstance(o, bmp.obj.Object) and o.sprite_category == "animated",
    lambda o: isinstance(o, bmp.obj.Object) and o.sprite_category == "static",
    lambda o: isinstance(o, bmp.obj.Object) and o.sprite_category == "tiled",
    lambda o: isinstance(o, bmp.obj.Object),
    lambda c: True
]