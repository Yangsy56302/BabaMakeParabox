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

class Options4101(TypedDict):
    ver: str
    debug: bool
    lang: str
    gameplay: GameplayOptions
    render: RenderOptions
    editor: EditorOptions

type Options = Options4101

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

type AnyOptions = Options | Options41 | Options4101

def formatted_before_4101(json_object: AnyOptions, ver: str) -> TypeGuard[Options41]:
    return bmp.base.compare_versions(ver, "4.101") < 0

def formatted_after_4101(json_object: AnyOptions, ver: str) -> TypeGuard[Options4101]:
    return bmp.base.compare_versions(ver, "4.101") >= 0

def formatted_currently(json_object: AnyOptions, ver: str) -> TypeGuard[Options]:
    return bmp.base.compare_versions(ver, bmp.base.versions) == 0

def formatted_from_future(json_object: AnyOptions, ver: str) -> TypeGuard[AnyOptions]:
    return bmp.base.compare_versions(ver, bmp.base.versions) > 0

def update_json_format(json_object: AnyOptions) -> Options:
    if not isinstance(json_object, dict):
        raise TypeError(type(json_object))
    ver = json_object["ver"]
    if formatted_from_future(json_object, ver):
        raise bmp.base.DowngradeError(ver)
    elif formatted_currently(json_object, ver):
        return json_object
    elif formatted_after_4101(json_object, ver):
        return json_object
    elif formatted_before_4101(json_object, ver):
        return {
            "ver": bmp.base.versions,
            "lang": json_object["lang"],
            "debug": json_object["debug"],
            "gameplay": {
                "bgm": json_object["bgm"],
                "repeat": json_object["long_press"],
                "metatext": json_object["metatext"],
            },
            "render": {
                "fps": json_object["fps"],
                "space_depth": json_object["space_display_recursion_depth"],
                "palette": json_object["palette"],
                "smooth": json_object["smooth_animation_multiplier"],
            },
            "editor": {
                "shortcuts": json_object["object_type_shortcuts"],
                "default_space": {
                    "inf": 0,
                    "width": json_object["default_new_space"]["width"],
                    "height": json_object["default_new_space"]["height"],
                    "color": json_object["default_new_space"]["color"],
                },
                "minimal_json": json_object["compressed_json_output"],
            },
        }
    else:
        raise bmp.base.UpgradeError(json_object)

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