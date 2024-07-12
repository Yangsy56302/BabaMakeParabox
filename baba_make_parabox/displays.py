from typing import Optional
import pygame
import os
import random

import baba_make_parabox.objects as objects
import baba_make_parabox.spaces as spaces

DARK_GRAY = pygame.Color("#242424")
LIGHT_GRAY = pygame.Color("#737373")
SILVER = pygame.Color("#C3C3C3")
WHITE = pygame.Color("#FFFFFF")
MAYBE_BLACK = pygame.Color("#080808")

DARKER_GRAY_BLUE = pygame.Color("#15181F")
DARK_GRAY_BLUE = pygame.Color("#293141")
BLUE_GRAY = pygame.Color("#3E7688")
LIGHT_GRAY_BLUE = pygame.Color("#5F9DD1")
LIGHTER_GRAY_BLUE = pygame.Color("#83C8E5")

DARKER_RED = pygame.Color("#421910")
DARK_RED = pygame.Color("#82261C")
LIGHT_RED = pygame.Color("#E5533B")
LIGHT_ORANGE = pygame.Color("#E49950")
LIGHT_YELLOW = pygame.Color("#EDE285")

PURPLE = pygame.Color("#603981")
LIGHT_PURPLE = pygame.Color("#8E5E9C")
DARK_BLUE = pygame.Color("#4759B1")
LIGHT_BLUE = pygame.Color("#557AE0")
GOLD = pygame.Color("#FFBD47")

DARK_MAGENTA = pygame.Color("#682E4C")
MAGENTA = pygame.Color("#D9396A")
PINK = pygame.Color("#EB91CA")
DARKER_BLUE = pygame.Color("#294891")
LIGHTER_BLUE = pygame.Color("#73ABF3")

DARK_GRAY_GREEN = pygame.Color("#303824")
DARK_GREEN = pygame.Color("#4B5C1C")
GRAY_GREEN = pygame.Color("#5C8339")
LIGHT_GRAY_GREEN = pygame.Color("#A5B13F")
LIGHT_GREEN = pygame.Color("#B6D340")

DARK_BROWN = pygame.Color("#503F24")
BROWN = pygame.Color("#90673E")
LIGHT_BROWN = pygame.Color("#C29E46")
DARKER_BROWN = pygame.Color("#362E22")
MAYBE_NOT_BLACK = pygame.Color("#0B0B0E")

def set_color_dark(surface: pygame.Surface, color: pygame.Color) -> pygame.Surface:
    new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    new_surface.fill(pygame.Color(color.r, color.g, color.b, 255))
    new_surface.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
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

def random_world_color() -> pygame.Color:
    color = random_hue()
    color = pygame.Color(color.r // 16, color.g // 16, color.b // 16)
    return color

pixel_size = 6
sprite_size = 24

class Sprites(object):
    def __init__(self, sprite_colors: dict[str, pygame.Color]) -> None:
        self.sprite_colors = sprite_colors
    def update(self) -> None:
        self.sprites = {}
        sprites_path = "sprites"
        for filename in os.listdir(sprites_path):
            sprite = pygame.image.load(os.path.join(sprites_path, filename)).convert_alpha()
            sprite_name = os.path.splitext(filename)[0]
            sprite_basename = sprite_name
            sprite_basename = sprite_basename[:sprite_basename.rfind("_")]
            sprite_basename = sprite_basename[:sprite_basename.rfind("_")]
            self.sprites[sprite_name] = set_color_dark(sprite, self.sprite_colors.get(sprite_basename, WHITE))
    def get(self, sprite_name: str, state: int, frame: int = 0) -> pygame.Surface:
        return self.sprites["_".join([sprite_name, str(state), str(frame)])]

def set_sprite_state(obj: objects.Object, round_num: int = 0, wsad: Optional[dict[spaces.Orient, bool]] = None) -> objects.Object:
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
        obj.set_sprite(wsad if wsad is not None else {spaces.W: False, spaces.S: False, spaces.A: False, spaces.D: False})
    return obj

sprite_colors: dict[str, pygame.Color] = {}

sprite_colors["baba"] = WHITE
sprite_colors["keke"] = LIGHT_RED
sprite_colors["me"] = LIGHT_PURPLE
sprite_colors["skull"] = DARKER_RED
sprite_colors["ghost"] = PINK
sprite_colors["wall"] = DARK_GRAY_BLUE
sprite_colors["tile"] = DARK_GRAY
sprite_colors["grass"] = DARK_GRAY_GREEN
sprite_colors["water"] = LIGHT_GRAY_BLUE
sprite_colors["lava"] = LIGHT_ORANGE
sprite_colors["door"] = LIGHT_RED
sprite_colors["key"] = LIGHT_YELLOW
sprite_colors["box"] = BROWN
sprite_colors["rock"] = LIGHT_BROWN
sprite_colors["sun"] = LIGHT_YELLOW
sprite_colors["flag"] = LIGHT_YELLOW
sprite_colors["cursor"] = PINK
sprite_colors["level"] = MAGENTA
sprite_colors["world"] = PINK
sprite_colors["clone"] = PINK
sprite_colors["text_baba"] = MAGENTA
sprite_colors["text_keke"] = LIGHT_RED
sprite_colors["text_me"] = LIGHT_PURPLE
sprite_colors["text_skull"] = DARKER_RED
sprite_colors["text_ghost"] = PINK
sprite_colors["text_wall"] = LIGHT_GRAY
sprite_colors["text_tile"] = LIGHT_GRAY
sprite_colors["text_grass"] = LIGHT_GRAY_GREEN
sprite_colors["text_water"] = LIGHT_GRAY_BLUE
sprite_colors["text_lava"] = LIGHT_ORANGE
sprite_colors["text_door"] = LIGHT_RED
sprite_colors["text_key"] = LIGHT_YELLOW
sprite_colors["text_box"] = BROWN
sprite_colors["text_rock"] = BROWN
sprite_colors["text_sun"] = LIGHT_YELLOW
sprite_colors["text_flag"] = LIGHT_YELLOW
sprite_colors["text_cursor"] = LIGHT_YELLOW
sprite_colors["text_level"] = MAGENTA
sprite_colors["text_world"] = PINK
sprite_colors["text_clone"] = PINK
sprite_colors["text_text"] = MAGENTA
sprite_colors["text_is"] = WHITE
sprite_colors["text_you"] = MAGENTA
sprite_colors["text_move"] = LIGHT_GREEN
sprite_colors["text_stop"] = DARK_GREEN
sprite_colors["text_push"] = BROWN
sprite_colors["text_sink"] = LIGHT_GRAY_BLUE
sprite_colors["text_float"] = LIGHTER_GRAY_BLUE
sprite_colors["text_open"] = LIGHT_YELLOW
sprite_colors["text_shut"] = LIGHT_RED
sprite_colors["text_hot"] = LIGHT_ORANGE
sprite_colors["text_melt"] = LIGHT_GRAY_BLUE
sprite_colors["text_win"] = LIGHT_YELLOW
sprite_colors["text_defeat"] = DARK_RED
sprite_colors["text_shift"] = LIGHT_GRAY_BLUE
sprite_colors["text_tele"] = LIGHTER_GRAY_BLUE
sprite_colors["text_word"] = WHITE
sprite_colors["text_select"] = LIGHT_YELLOW


order = [objects.Operator,
         objects.Noun,
         objects.Property,
         objects.Character,
         objects.Static,
         objects.AnimatedDirectional,
         objects.Directional,
         objects.Animated,
         objects.Tiled,
         objects.WorldPointer,
         objects.Object]

sprites = Sprites(sprite_colors)