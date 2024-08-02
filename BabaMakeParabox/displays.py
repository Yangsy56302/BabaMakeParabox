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
    def __init__(self, sprite_colors: dict[str, colors.ColorHex]) -> None:
        self.sprite_colors = sprite_colors
    def update(self) -> None:
        self.sprites = {}
        for filename in os.listdir(os.path.join("sprites")):
            sprite = pygame.image.load(os.path.join("sprites", filename)).convert_alpha()
            sprite_name = os.path.splitext(filename)[0]
            sprite_basename = sprite_name
            sprite_basename = sprite_basename[:sprite_basename.rfind("_")]
            sprite_basename = sprite_basename[:sprite_basename.rfind("_")]
            sprite_color = self.sprite_colors.get(sprite_basename)
            if sprite_color is None:
                sprite_color = colors.WHITE
            self.sprites[sprite_name] = set_surface_color_dark(sprite, sprite_color)
    def get(self, sprite_name: str, state: int, frame: int = 0) -> pygame.Surface:
        return self.sprites["_".join([sprite_name, str(state), str(frame)])]

def set_sprite_state(obj: objects.BmpObject, round_num: int = 0, wsad: Optional[dict[spaces.Orient, bool]] = None) -> objects.BmpObject:
    if isinstance(obj, objects.Static):
        obj.set_sprite()
    if isinstance(obj, objects.Directional):
        obj.set_sprite()
    if isinstance(obj, objects.Animated):
        obj.set_sprite(round_num)
    if isinstance(obj, objects.AnimatedDirectional):
        obj.set_sprite(round_num)
    if isinstance(obj, objects.Character):
        obj.set_sprite()
    if isinstance(obj, objects.Tiled):
        obj.set_sprite(wsad if wsad is not None else {spaces.Orient.W: False, spaces.Orient.S: False, spaces.Orient.A: False, spaces.Orient.D: False})
    return obj

sprite_colors: dict[str, colors.ColorHex] = {}

sprite_colors["baba"] = colors.WHITE
sprite_colors["keke"] = colors.LIGHT_RED
sprite_colors["me"] = colors.LIGHT_PURPLE
sprite_colors["patrick"] = colors.MAGENTA
sprite_colors["skull"] = colors.DARKER_RED
sprite_colors["ghost"] = colors.PINK
sprite_colors["wall"] = colors.DARK_GRAY_BLUE
sprite_colors["hedge"] = colors.DARK_GREEN
sprite_colors["ice"] = colors.LIGHT_GRAY_BLUE
sprite_colors["tile"] = colors.DARK_GRAY
sprite_colors["grass"] = colors.DARK_GRAY_GREEN
sprite_colors["water"] = colors.LIGHT_GRAY_BLUE
sprite_colors["lava"] = colors.LIGHT_ORANGE
sprite_colors["door"] = colors.LIGHT_RED
sprite_colors["key"] = colors.LIGHT_YELLOW
sprite_colors["box"] = colors.BROWN
sprite_colors["rock"] = colors.LIGHT_BROWN
sprite_colors["fruit"] = colors.LIGHT_RED
sprite_colors["belt"] = colors.DARK_GRAY_BLUE
sprite_colors["sun"] = colors.LIGHT_YELLOW
sprite_colors["moon"] = colors.LIGHT_YELLOW
sprite_colors["star"] = colors.LIGHT_YELLOW
sprite_colors["what"] = colors.WHITE
sprite_colors["love"] = colors.PINK
sprite_colors["flag"] = colors.LIGHT_YELLOW
sprite_colors["cursor"] = colors.PINK
sprite_colors["level"] = colors.WHITE
sprite_colors["world"] = colors.LIGHT_GRAY_BLUE
sprite_colors["clone"] = colors.LIGHTER_GRAY_BLUE
sprite_colors["text_baba"] = colors.MAGENTA
sprite_colors["text_keke"] = colors.LIGHT_RED
sprite_colors["text_me"] = colors.LIGHT_PURPLE
sprite_colors["text_patrick"] = colors.MAGENTA
sprite_colors["text_skull"] = colors.DARKER_RED
sprite_colors["text_ghost"] = colors.PINK
sprite_colors["text_wall"] = colors.LIGHT_GRAY
sprite_colors["text_hedge"] = colors.DARK_GREEN
sprite_colors["text_ice"] = colors.LIGHT_GRAY_BLUE
sprite_colors["text_tile"] = colors.LIGHT_GRAY
sprite_colors["text_grass"] = colors.LIGHT_GRAY_GREEN
sprite_colors["text_water"] = colors.LIGHT_GRAY_BLUE
sprite_colors["text_lava"] = colors.LIGHT_ORANGE
sprite_colors["text_door"] = colors.LIGHT_RED
sprite_colors["text_key"] = colors.LIGHT_YELLOW
sprite_colors["text_box"] = colors.BROWN
sprite_colors["text_rock"] = colors.BROWN
sprite_colors["text_fruit"] = colors.LIGHT_RED
sprite_colors["text_belt"] = colors.LIGHT_GRAY_BLUE
sprite_colors["text_sun"] = colors.LIGHT_YELLOW
sprite_colors["text_moon"] = colors.LIGHT_YELLOW
sprite_colors["text_star"] = colors.LIGHT_YELLOW
sprite_colors["text_what"] = colors.WHITE
sprite_colors["text_love"] = colors.PINK
sprite_colors["text_flag"] = colors.LIGHT_YELLOW
sprite_colors["text_cursor"] = colors.LIGHT_YELLOW
sprite_colors["text_all"] = colors.WHITE
sprite_colors["text_empty"] = colors.WHITE
sprite_colors["text_text"] = colors.MAGENTA
sprite_colors["text_level"] = colors.MAGENTA
sprite_colors["text_world"] = colors.LIGHT_GRAY_BLUE
sprite_colors["text_clone"] = colors.LIGHTER_GRAY_BLUE
sprite_colors["text_game"] = colors.PINK
sprite_colors["text_meta"] = colors.MAGENTA
sprite_colors["text_text_underline"] = colors.MAGENTA
sprite_colors["text_on"] = colors.WHITE
sprite_colors["text_near"] = colors.WHITE
sprite_colors["text_nextto"] = colors.WHITE
sprite_colors["text_feeling"] = colors.WHITE
sprite_colors["text_is"] = colors.WHITE
sprite_colors["text_has"] = colors.WHITE
sprite_colors["text_make"] = colors.WHITE
sprite_colors["text_write"] = colors.WHITE
sprite_colors["text_not"] = colors.LIGHT_RED
sprite_colors["text_and"] = colors.WHITE
sprite_colors["text_you"] = colors.MAGENTA
sprite_colors["text_move"] = colors.LIGHT_GREEN
sprite_colors["text_stop"] = colors.DARK_GREEN
sprite_colors["text_push"] = colors.BROWN
sprite_colors["text_sink"] = colors.LIGHT_GRAY_BLUE
sprite_colors["text_float"] = colors.LIGHTER_GRAY_BLUE
sprite_colors["text_open"] = colors.LIGHT_YELLOW
sprite_colors["text_shut"] = colors.LIGHT_RED
sprite_colors["text_hot"] = colors.LIGHT_ORANGE
sprite_colors["text_melt"] = colors.LIGHT_GRAY_BLUE
sprite_colors["text_win"] = colors.LIGHT_YELLOW
sprite_colors["text_defeat"] = colors.DARK_RED
sprite_colors["text_shift"] = colors.LIGHT_GRAY_BLUE
sprite_colors["text_tele"] = colors.LIGHTER_GRAY_BLUE
sprite_colors["text_word"] = colors.WHITE
sprite_colors["text_select"] = colors.LIGHT_YELLOW
sprite_colors["text_text_plus"] = colors.MAGENTA
sprite_colors["text_text_minus"] = colors.PINK
sprite_colors["text_end"] = colors.WHITE
sprite_colors["text_done"] = colors.WHITE

order = [objects.Cursor,
         objects.Operator,
         objects.Noun,
         objects.Property,
         objects.Character,
         objects.Level,
         objects.Static,
         objects.AnimatedDirectional,
         objects.Directional,
         objects.Animated,
         objects.Tiled,
         objects.WorldPointer,
         objects.BmpObject]

sprites = Sprites(sprite_colors)