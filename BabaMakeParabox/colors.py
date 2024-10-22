import random

ColorHex = int
ColorRGB = tuple[int, int, int]

DARK_GRAY = 0x242424
LIGHT_GRAY = 0x737373
SILVER = 0xC3C3C3
WHITE = 0xFFFFFF
MAYBE_BLACK = 0x080808

DARKER_GRAY_BLUE = 0x15181F
DARK_GRAY_BLUE = 0x293141
GRAY_BLUE = 0x3E7688
LIGHT_GRAY_BLUE = 0x5F9DD1
LIGHTER_GRAY_BLUE = 0x83C8E5

DARKER_RED = 0x421910
DARK_RED = 0x82261C
LIGHT_RED = 0xE5533B
LIGHT_ORANGE = 0xE49950
LIGHT_YELLOW = 0xEDE285

PURPLE = 0x603981
LIGHT_PURPLE = 0x8E5E9C
DARK_BLUE = 0x4759B1
LIGHT_BLUE = 0x557AE0
GOLD = 0xFFBD47

DARK_MAGENTA = 0x682E4C
MAGENTA = 0xD9396A
PINK = 0xEB91CA
DARKER_BLUE = 0x294891
LIGHTER_BLUE = 0x73ABF3

DARK_GRAY_GREEN = 0x303824
DARK_GREEN = 0x4B5C1C
GRAY_GREEN = 0x5C8339
LIGHT_GRAY_GREEN = 0xA5B13F
LIGHT_GREEN = 0xB6D340

DARK_BROWN = 0x503F24
BROWN = 0x90673E
LIGHT_BROWN = 0xC29E46
DARKER_BROWN = 0x362E22
MAYBE_NOT_BLACK = 0x0B0B0E

def rgb_to_hex(r: int, g: int, b: int) -> ColorHex:
    return r * 0x10000 + g * 0x100 + b

def hex_to_rgb(color: ColorHex) -> ColorRGB:
    r = color // 0x10000 % 0x100
    g = color // 0x100 % 0x100
    b = color // 0x1 % 0x100
    return r, g, b

def str_to_hex(string: str) -> ColorHex:
    try:
        if string.startswith("0x"):
            new_string = string[2:]
        elif string.startswith("#"):
            new_string = string[1:]
        else:
            new_string = string[:]
        r = int(new_string[:2], base=16)
        g = int(new_string[2:4], base=16)
        b = int(new_string[4:], base=16)
        return rgb_to_hex(r, g, b)
    except Exception:
        raise ValueError(string)

def random_hue() -> ColorHex:
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
    return rgb_to_hex(int(r), int(g), int(b))

def random_world_color() -> ColorHex:
    r, g, b = hex_to_rgb(random_hue())
    return rgb_to_hex(r // 16, g // 16, b // 16)

def to_background_color(color: ColorHex) -> ColorHex:
    r, g, b = hex_to_rgb(color)
    return rgb_to_hex(r // 4, g // 4, b // 4)