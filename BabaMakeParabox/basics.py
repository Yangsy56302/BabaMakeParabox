from typing import Literal, Optional, TypedDict, Callable, NotRequired
import os
import json
import copy
import platform

def clampi(__min: int, __num: int, __max: int, /) -> int:
    return min(__max, max(__num, __min))

def absclampi(__num: int, __lim: int, /) -> int:
    return min(abs(__lim), max(__num, -abs(__lim)))

def clampf(__min: float, __num: float, __max: float, /) -> float:
    return min(__max, max(__num, __min))

def absclampf(__num: float, __lim: float, /) -> float:
    return min(abs(__lim), max(__num, -abs(__lim)))

import pygame
pygame.init()

versions = "3.925"
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

pyinst_env = "PYINST"

class DefaultNewSpaceOptions(TypedDict):
    width: int
    height: int
    color: int

class BgmOptions(TypedDict):
    enabled: bool
    name: str

class MetatextOptions(TypedDict):
    enabled: bool
    tier: int

class Options(TypedDict):
    ver: str
    debug: bool
    lang: str
    fps: int
    space_display_recursion_depth: int
    smooth_animation_multiplier: Optional[int]
    palette: str
    compressed_json_output: bool
    object_type_shortcuts: list[str]
    default_new_space: DefaultNewSpaceOptions
    metatext: MetatextOptions
    bgm: BgmOptions
    game_is_end: NotRequired[bool]
    game_is_done: NotRequired[bool]

default_options: Options = {
    "ver": versions,
    "debug": False,
    "lang": "",
    "fps": 30,
    "space_display_recursion_depth": 1,
    "smooth_animation_multiplier": 3,
    "palette": "default.png",
    "compressed_json_output": False,
    "default_new_space": {
        "width": 15,
        "height": 15,
        "color": 0x000000
    },
    "object_type_shortcuts": [
        "baba", 
        "wall", 
        "rock", 
        "flag", 
        "text_space", 
        "text_is", 
        "text_you", 
        "text_push", 
        "text_win", 
        "text_level"
    ],
    "metatext": {
        "enabled": True,
        "tier": 5
    },
    "bgm": {
        "enabled": False,
        "name": "rush_baba.mid"
    }
}
options_filename = "options.json"
options: Options = Options(copy.deepcopy(default_options))

class _JsonDumpKwds(TypedDict):
    indent: Optional[int]
    separators: tuple[str, str]
    
def get_json_dump_kwds() -> _JsonDumpKwds:
    return {"indent": None if options["compressed_json_output"] else 4,
            "separators": (",", ":") if options["compressed_json_output"] else (", ", ": ")}

def save_options(new_options: Options) -> None:
    with open(options_filename, "w", encoding="utf-8") as file:
        json.dump(new_options, file, **get_json_dump_kwds())

def update_options(old_options: Options) -> Options:
    new_options = old_options.copy()
    temp_options = default_options.copy()
    temp_options.update(new_options)
    new_options = temp_options.copy()
    new_options["ver"] = versions
    return new_options

current_os = platform.system()
windows = "Windows"
linux = "Linux"

if os.path.exists(options_filename):
    with open(options_filename, "r", encoding="utf-8") as file:
        options = json.load(file)
        options = update_options(options)
else:
    with open(options_filename, "w", encoding="utf-8") as file:
        options = default_options
        json.dump(default_options, file)

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