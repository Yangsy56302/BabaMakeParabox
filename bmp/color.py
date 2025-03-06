import os
import random

import PIL.Image

ColorHex = int
ColorHexA = int
ColorRGB = tuple[int, int, int]
ColorRGBA = tuple[int, int, int, int]

PaletteIndex = tuple[int, int]
Palette = dict[PaletteIndex, ColorHex]

def get_palette(_path: str, /) -> Palette:
    palette: Palette = {}
    image = PIL.Image.open(_path)
    image.convert("RGB")
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.getpixel((x, y))
            if isinstance(pixel, tuple):
                palette[x, y] = rgb_to_hex((pixel[0], pixel[1], pixel[2]))
    return palette

current_palette: Palette = {}
def set_palette(_path: str, /) -> None:
    global current_palette
    current_palette.update(get_palette(_path))

def rgb_to_hex(i: ColorRGB, /) -> ColorHex:
    r, g, b = i
    return r * 0x10000 + g * 0x100 + b * 0x1

def rgba_to_hexa(i: ColorRGBA, /) -> ColorHexA:
    r, g, b, a = i
    return r * 0x1000000 + g * 0x10000 + b * 0x100 + a * 0x1

def hex_to_rgb(color: ColorHex, /) -> ColorRGB:
    r = color // 0x10000 % 0x100
    g = color // 0x100 % 0x100
    b = color // 0x1 % 0x100
    return r, g, b

def hexa_to_rgba(color: ColorHexA, /) -> ColorRGBA:
    r = color // 0x1000000 % 0x100
    g = color // 0x10000 % 0x100
    b = color // 0x100 % 0x100
    a = color // 0x1 % 0x100
    return r, g, b, a

def str_to_hex(_str: str, /) -> ColorHex:
    try:
        if "," in _str:
            x, y = _str.split(sep=",")
            x = int(x.strip())
            y = int(y.strip())
            color = current_palette[x, y]
        else:
            if _str.startswith("0x"):
                new_string = _str[2:]
            elif _str.startswith("#"):
                new_string = _str[1:]
            else:
                new_string = _str[:]
            r = int(new_string[:2], base=16)
            g = int(new_string[2:4], base=16)
            b = int(new_string[4:], base=16)
            color = rgb_to_hex((r, g, b))
        return color
    except ValueError:
        raise ValueError(_str)

def pallete_to_hex(_str: str, /) -> ColorHex:
    try:
        palette_str = _str.lstrip("([").rstrip("])").split(",")
        return current_palette[int(palette_str[0].strip()), int(palette_str[1].strip())]
    except ValueError:
        raise ValueError(_str)
    except IndexError:
        raise ValueError(_str)

def str_or_palette_to_hex(_str: str, /) -> ColorHex:
    try:
        return str_to_hex(_str)
    except ValueError:
        try:
            return pallete_to_hex(_str)
        except ValueError:
            raise ValueError(_str)

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
    return rgb_to_hex((int(r), int(g), int(b)))

def random_hue() -> ColorHex:
    return float_to_hue(random.random())

def random_space_color() -> ColorHex:
    r, g, b = hex_to_rgb(random_hue())
    return rgb_to_hex((r // 16, g // 16, b // 16))

def to_background_color(color: ColorHex) -> ColorHex:
    r, g, b = hex_to_rgb(color)
    return rgb_to_hex((r // 4, g // 4, b // 4))