import os
import random

import PIL.Image

ColorHex = int
ColorRGB = tuple[int, int, int]

PaletteIndex = tuple[int, int]
Palette = dict[PaletteIndex, ColorHex]
def get_palette(path: str) -> Palette:
    palette: Palette = {}
    image = PIL.Image.open(path)
    image.convert("RGB")
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.getpixel((x, y))
            if isinstance(pixel, tuple):
                palette[x, y] = rgb_to_hex(*pixel[:3])
    return palette

current_palette: Palette = {}
def set_palette(path: str) -> None:
    global current_palette
    current_palette.update(get_palette(path))

def rgb_to_hex(r: int, g: int, b: int) -> ColorHex:
    return r * 0x10000 + g * 0x100 + b

def hex_to_rgb(color: ColorHex) -> ColorRGB:
    r = color // 0x10000 % 0x100
    g = color // 0x100 % 0x100
    b = color // 0x1 % 0x100
    return r, g, b

def str_to_hex(string: str) -> ColorHex:
    try:
        if "," in string:
            x, y = string.split(sep=",")
            x = int(x.strip())
            y = int(y.strip())
            color = current_palette[x, y]
        else:
            if string.startswith("0x"):
                new_string = string[2:]
            elif string.startswith("#"):
                new_string = string[1:]
            else:
                new_string = string[:]
            r = int(new_string[:2], base=16)
            g = int(new_string[2:4], base=16)
            b = int(new_string[4:], base=16)
            color = rgb_to_hex(r, g, b)
        return color
    except Exception:
        raise ValueError(string)

def float_to_hue(f: float) -> ColorHex:
    if f <= 1 / 6:
        r = 255
        g = 255 * (f * 6)
        b = 0
    elif f <= 2 / 6:
        r = 255 - 255 * ((f - 1 / 6) * 6)
        g = 255
        b = 0
    elif f <= 3 / 6:
        r = 0
        g = 255
        b = 255 * ((f - 2 / 6) * 6)
    elif f <= 4 / 6:
        r = 0
        g = 255 - 255 * ((f - 3 / 6) * 6)
        b = 255
    elif f <= 5 / 6:
        r = 255 * ((f - 4 / 6) * 6)
        g = 0
        b = 255
    else:
        r = 255
        g = 0
        b = 255 - 255 * ((f - 5 / 6) * 6)
    return rgb_to_hex(int(r), int(g), int(b))

def random_hue() -> ColorHex:
    return float_to_hue(random.random())

def random_space_color() -> ColorHex:
    r, g, b = hex_to_rgb(random_hue())
    return rgb_to_hex(r // 16, g // 16, b // 16)

def to_background_color(color: ColorHex) -> ColorHex:
    r, g, b = hex_to_rgb(color)
    return rgb_to_hex(r // 4, g // 4, b // 4)