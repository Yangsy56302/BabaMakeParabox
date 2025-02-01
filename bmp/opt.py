from typing import Literal, Optional, TypeGuard, TypedDict, Callable, NotRequired
import os
import json
import copy

import bmp.base
import bmp.color

import pygame
pygame.init()

pyinst_env = "PYINST"

class DefaultNewSpaceOptions41(TypedDict):
    width: int
    height: int
    color: int

class DefaultSpaceOptions(TypedDict):
    inf: int
    width: int
    height: int
    color: bmp.color.ColorHex

class BgmOptions(TypedDict):
    enabled: bool
    name: str

class MetatextOptions(TypedDict):
    enabled: bool
    tier: int

class RepeatOptions(TypedDict):
    delay: int
    interval: int

class GameplayOptions(TypedDict):
    repeat: RepeatOptions
    metatext: MetatextOptions
    bgm: BgmOptions
    game_is_end: NotRequired[bool]
    game_is_done: NotRequired[bool]

class RenderOptions(TypedDict):
    fps: int
    space_depth: int
    palette: str
    smooth: Optional[int]

class EditorOptions(TypedDict):
    shortcuts: list[str]
    default_space: DefaultSpaceOptions
    minimal_json: bool

class Options41(TypedDict):
    ver: str
    debug: bool
    lang: str
    fps: int
    space_display_recursion_depth: int
    smooth_animation_multiplier: Optional[int]
    long_press: RepeatOptions
    palette: str
    compressed_json_output: bool
    object_type_shortcuts: list[str]
    default_new_space: DefaultNewSpaceOptions41
    metatext: MetatextOptions
    bgm: BgmOptions
    game_is_end: NotRequired[bool]
    game_is_done: NotRequired[bool]

class Options(TypedDict):
    ver: str
    debug: bool
    lang: str
    gameplay: GameplayOptions
    render: RenderOptions
    editor: EditorOptions

class BaseOptions(TypedDict):
    ver: str
    debug: bool

type AnyOptions = Options | Options41 | BaseOptions

def formatted_before_4101(opt: AnyOptions) -> TypeGuard[Options41]:
    return bmp.base.compare_versions(opt["ver"], "4.101") < 0

def formatted_currently(opt: AnyOptions) -> TypeGuard[Options]:
    return bmp.base.compare_versions(opt["ver"], bmp.base.versions) == 0

def formatted_from_future(opt: AnyOptions) -> TypeGuard[BaseOptions]:
    return bmp.base.compare_versions(opt["ver"], bmp.base.versions) > 0

default_options: Options = {
    "ver": bmp.base.versions,
    "debug": False,
    "lang": "",
    "gameplay": {
        "bgm": {
            "enabled": False,
            "name": "rush_baba.mid",
        },
        "repeat": {
            "delay": 500,
            "interval": 50,
        },
        "metatext": {
            "enabled": True,
            "tier": 5,
        },
    },
    "render": {
        "fps": 30,
        "space_depth": 1,
        "palette": "default.png",
        "smooth": 3,
    },
    "editor": {
        "shortcuts": [
            "space", 
            "clone", 
            "path", 
            "cursor", 
            "level", 
            "text_space", 
            "text_is", 
            "text_you", 
            "text_win", 
            "text_level",
        ],
        "default_space": {
            "inf": 0,
            "width": 15,
            "height": 15,
            "color": 0x000000,
        },
        "minimal_json": True,
    },
}
options_filename: str = "options.json"
options: Options = copy.deepcopy(default_options)

class _JsonDumpKwds(TypedDict):
    indent: Optional[int]
    separators: tuple[str, str]
    
def get_json_dump_kwds() -> _JsonDumpKwds:
    return {
        "indent": None if options["editor"]["minimal_json"] else 4,
        "separators": (",", ":") if options["editor"]["minimal_json"] else (", ", ": ")
    }

def update_json_format(opt: AnyOptions, ver: str = "0.0") -> Options:
    if not isinstance(opt, dict):
        raise TypeError(type(opt))
    elif formatted_currently(opt):
        return opt
    elif formatted_before_4101(opt):
        return {
            "ver": bmp.base.versions,
            "lang": opt["lang"],
            "debug": opt["debug"],
            "gameplay": {
                "bgm": opt["bgm"],
                "repeat": opt["long_press"],
                "metatext": opt["metatext"],
            },
            "render": {
                "fps": opt["fps"],
                "space_depth": opt["space_display_recursion_depth"],
                "palette": opt["palette"],
                "smooth": opt["smooth_animation_multiplier"],
            },
            "editor": {
                "shortcuts": opt["object_type_shortcuts"],
                "default_space": {
                    "inf": 0,
                    "width": opt["default_new_space"]["width"],
                    "height": opt["default_new_space"]["height"],
                    "color": opt["default_new_space"]["color"],
                },
                "minimal_json": opt["compressed_json_output"],
            },
        }
    elif formatted_from_future(opt):
        raise bmp.base.DowngradeError(opt["ver"])
    else:
        raise ValueError(opt)

def load(filename: str = options_filename) -> None:
    global options
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            old_options = update_json_format(json.load(file))
            new_options = default_options.copy()
            new_options.update(old_options)
            options = new_options.copy()
            options["ver"] = bmp.base.versions
    else:
        options = default_options

def save(filename: str = options_filename) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(options, file, **get_json_dump_kwds())

load()