from typing import Literal, Optional, TypedDict, Callable, NotRequired
import platform

import pygame
pygame.init()

def remove_same_elements[T](a_list: list[T], a_func: Optional[Callable[[T, T], bool]] = None) -> list[T]:
    if a_func is None:
        a_func = lambda x, y: x == y
    e_list = list(enumerate(a_list))
    r_list = []
    for i, ie in e_list:
        for j, je in e_list[i + 1:]:
            if a_func(ie, je) and j not in r_list:
                r_list.append(j)
    o_list = map(lambda e: e[1], filter(lambda e: e[0] not in r_list, e_list))
    return list(o_list)

def clampi(__min: int, __num: int, __max: int, /) -> int:
    return min(__max, max(__num, __min))

def absclampi(__num: int, __lim: int, /) -> int:
    return min(abs(__lim), max(__num, -abs(__lim)))

def clampf(__min: float, __num: float, __max: float, /) -> float:
    return min(__max, max(__num, __min))

def absclampf(__num: float, __lim: float, /) -> float:
    return min(abs(__lim), max(__num, -abs(__lim)))

def snake_to_camel(__str: str, /, *, is_big: bool) -> str:
    word_list = __str.split("_")
    camel_head = word_list[0].capitalize() if is_big else word_list[0].lower()
    return camel_head + "".join(word.capitalize() for word in word_list[1:])

version: str = "4.103"
def compare_versions(ver_1: str, ver_2: str) -> Literal[-1, 0, 1]:
    for char_1, char_2 in zip(ver_1, ver_2):
        if ord(char_1) > ord(char_2):
            return 1
        elif ord(char_1) < ord(char_2):
            return -1
    if len(ver_1) == len(ver_2):
        return 0
    elif len(ver_1) > len(ver_2):
        return 1
    else:
        return -1

class UpgradeError(Exception):
    pass

class DowngradeError(Exception):
    pass

pyinst_env = "PYINST"

current_os = platform.system()
windows: Literal["Windows"] = "Windows"
linux: Literal["Linux"] = "Linux"