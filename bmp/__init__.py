from typing import AnyStr, Optional, Callable
import os
import json
import traceback

import pygame

import bmp.Base
import bmp.Collect
import bmp.Color
import bmp.Editor
import bmp.Game
import bmp.Lang
import bmp.Level
import bmp.Levelpack
import bmp.Locate
import bmp.Object
import bmp.Ref
import bmp.Render
import bmp.Rule
import bmp.Space
import bmp.Subgame

def show_dir(path: str, filter_func: Optional[Callable[[str], bool]] = None, tab: int = 0) -> None:
    def default_filter_func(filename: str) -> bool:
        return True
    filter_func = filter_func if filter_func is not None else default_filter_func
    print(f"{' ' * (tab * 2)}+ {os.path.basename(path)}")
    path = os.path.abspath(path)
    for filelike in os.scandir(path):
        if filelike.is_file() and filter_func(os.path.basename(filelike.name)):
            print(f"{' ' * (tab * 2)}  - {os.path.basename(filelike.name)}")
        elif filelike.is_dir():
            show_dir(os.path.abspath(filelike.path), filter_func, tab + 1)

def pre_play() -> bool:
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.Base.options["debug"] else s.endswith(".json"))
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.open.file")))
    bmp.Lang.lang_print("launch.open.levelpack")
    input_filename = bmp.Lang.lang_input("input.file.name")
    input_filename += "" if bmp.Base.options["debug"] or input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        bmp.Lang.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
        levelpack_json = json.load(file)
        bmp.Lang.lang_print("launch.open.levelpack.done", file=input_filename)
        levelpack = bmp.Levelpack.json_to_levelpack(levelpack_json)
    bmp.Lang.lang_print("play.start")
    levelpack = bmp.Game.play(levelpack)
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.save.file")))
    bmp.Lang.lang_print("launch.save.levelpack")
    bmp.Lang.lang_print("launch.save.levelpack.empty.game")
    output_filename = bmp.Lang.lang_input("input.file.name")
    if output_filename != "":
        output_filename += "" if bmp.Base.options["debug"] or output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **bmp.Base.get_json_dump_kwds())
            bmp.Lang.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def pre_edit() -> bool:
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.Base.options["debug"] else s.endswith(".json"))
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.open.file")))
    bmp.Lang.lang_print("launch.open.levelpack")
    bmp.Lang.lang_print("launch.open.levelpack.empty.editor")
    input_filename = bmp.Lang.lang_input("input.file.name")
    size = bmp.Locate.Coordinate(bmp.Base.options["default_new_space"]["width"], bmp.Base.options["default_new_space"]["height"])
    color = bmp.Base.options["default_new_space"]["color"]
    if input_filename != "":
        input_filename += "" if bmp.Base.options["debug"] or input_filename.endswith(".json") else ".json"
        if not os.path.isfile(os.path.join("levelpacks", input_filename)):
            bmp.Lang.lang_print("warn.file.not_found", file=input_filename)
            return False
        with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            bmp.Lang.lang_print("launch.open.levelpack.done", file=input_filename)
            levelpack = bmp.Levelpack.json_to_levelpack(levelpack_json)
    else:
        space = bmp.Space.Space(bmp.Ref.SpaceID("main_space"), size, color=color)
        level = bmp.Level.Level(bmp.Ref.LevelID("main_level"), [space])
        levelpack = bmp.Levelpack.Levelpack([level])
    levelpack = bmp.Editor.levelpack_editor(levelpack)
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.save.file")))
    bmp.Lang.lang_print("launch.save.levelpack")
    bmp.Lang.lang_print("launch.save.levelpack.empty.editor")
    output_filename = bmp.Lang.lang_input("input.file.name")
    if output_filename != "":
        output_filename += "" if bmp.Base.options["debug"] or output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **bmp.Base.get_json_dump_kwds())
            bmp.Lang.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def update_levelpack() -> bool:
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.Base.options["debug"] else s.endswith(".json"))
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.open.file")))
    bmp.Lang.lang_print("launch.open.levelpack")
    input_filename = bmp.Lang.lang_input("input.file.name")
    input_filename += "" if bmp.Base.options["debug"] or input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        bmp.Lang.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            bmp.Lang.lang_print("launch.open.levelpack.done", file=input_filename)
            levelpack = bmp.Levelpack.json_to_levelpack(levelpack_json)
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.save.file")))
    bmp.Lang.lang_print("launch.save.levelpack")
    bmp.Lang.lang_print("launch.save.levelpack.empty.update")
    output_filename = bmp.Lang.lang_input("input.file.name")
    output_filename += "" if bmp.Base.options["debug"] or output_filename.endswith(".json") else ".json"
    if output_filename == "":
        output_filename = input_filename
    with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
        json.dump(levelpack.to_json(), file, **bmp.Base.get_json_dump_kwds())
        bmp.Lang.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def change_options() -> bool:
    bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.change_options")))
    while True:
        bmp.Base.options["debug"] = bmp.Lang.lang_input("launch.change_options.debug") in bmp.Lang.yes
        bmp.Lang.lang_print(f"launch.change_options.performance")
        performance_preset_index = bmp.Lang.lang_input("input.number")
        try:
            performance_preset_index = int(performance_preset_index)
        except ValueError:
            bmp.Lang.lang_print("warn.value.invalid", value=performance_preset_index, cls="int")
            continue
        match int(performance_preset_index):
            case 1:
                bmp.Base.options.update({"fps": 5, "smooth_animation_multiplier": None}); break
            case 2:
                bmp.Base.options.update({"fps": 10, "smooth_animation_multiplier": None}); break
            case 3:
                bmp.Base.options.update({"fps": 15, "smooth_animation_multiplier": 3}); break
            case 4:
                bmp.Base.options.update({"fps": 30, "smooth_animation_multiplier": 3}); break
            case 5:
                bmp.Base.options.update({"fps": 60, "smooth_animation_multiplier": 3}); break
            case _:
                bmp.Lang.lang_print("warn.value.out_of_range", min=1, max=5, value=performance_preset_index)
    while True:
        bmp.Lang.lang_print("launch.change_options.display_layer")
        display_layer = bmp.Lang.lang_input("input.number")
        try:
            display_layer = int(display_layer)
        except ValueError:
            bmp.Lang.lang_print("warn.value.invalid", value=display_layer, cls="int")
            continue
        if display_layer < 0:
            bmp.Lang.lang_print("warn.value.underflow", min=1, value=display_layer)
        else:
            bmp.Base.options.update({"space_display_recursion_depth": display_layer})
            break
    while True:
        bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.directory", dir="palettes")))
        show_dir("palettes", lambda s: True if bmp.Base.options["debug"] else s.endswith(".png"))
        bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.open.file")))
        palette_filename = bmp.Lang.lang_input("input.file.name")
        if palette_filename == "":
            break
        palette_filename += "" if bmp.Base.options["debug"] or palette_filename.endswith(".png") else ".png"
        pelette_path = os.path.join(".", "palettes", palette_filename)
        if not os.path.isfile(pelette_path):
            bmp.Lang.lang_print("warn.file.not_found", file=palette_filename)
            continue
        try:
            bmp.Color.set_palette(pelette_path)
            bmp.Base.options["palette"] = palette_filename
        except Exception:
            bmp.Lang.lang_print("warn.unknown", value=traceback.format_exc())
        else:
            break
    if bmp.Lang.lang_input("launch.change_options.json") in bmp.Lang.yes:
        bmp.Base.options.update({"compressed_json_output": False})
    else:
        bmp.Base.options.update({"compressed_json_output": True})
    if bmp.Lang.lang_input("launch.change_options.bgm") in bmp.Lang.yes:
        bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.directory", dir="midi")))
        show_dir("midi", lambda s: True if bmp.Base.options["debug"] else s.endswith(".mid"))
        bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.open.file")))
        mid_filename = bmp.Lang.lang_input("input.file.name")
        mid_filename += "" if bmp.Base.options["debug"] or mid_filename.endswith(".mid") else ".mid"
        if os.path.isfile(os.path.join(".", "midi", mid_filename)):
            bmp.Base.options.update({"bgm": {"enabled": True, "name": mid_filename}})
        else:
            bmp.Lang.lang_print("warn.file.not_found", file=mid_filename)
            bmp.Base.options.update({"bgm": {"enabled": False, "name": mid_filename}})
    else:
        bmp.Base.options.update({"bgm": {"enabled": False, "name": "rush_baba.mid"}})
    while True:
        bmp.Lang.lang_print("launch.change_options.metatext")
        metatext_tier = bmp.Lang.lang_input("input.number")
        try:
            metatext_tier = int(metatext_tier)
        except ValueError:
            bmp.Lang.lang_print("warn.value.invalid", value=metatext_tier, cls="int")
            continue
        if metatext_tier < 0:
            bmp.Lang.lang_print("warn.value.underflow", min=0, value=metatext_tier)
        elif metatext_tier == 0:
            bmp.Base.options.update({"metatext": {"enabled": False, "tier": 0}})
            break
        else:
            bmp.Base.options.update({"metatext": {"enabled": True, "tier": metatext_tier}})
            break
    bmp.Lang.lang_print("launch.change_options.done")
    return True

def pre_main_check() -> bool:
    if os.environ.get(bmp.Base.pyinst_env) == "TRUE":
        return False
    if bmp.Base.options.get("game_is_done"):
        raise bmp.Game.GameIsDoneError()
    return True

def pre_main() -> None:
    os.makedirs("levelpacks", exist_ok=True)
    if bmp.Base.options["lang"] not in bmp.Lang.language_dict.keys():
        for lang in bmp.Lang.language_dict.keys():
            print(bmp.Lang.language_dict[lang]["language.select"])
        lang = input(">>> ")
        bmp.Lang.set_current_language(lang)
        bmp.Base.options["lang"] = lang
    else:
        bmp.Lang.set_current_language(bmp.Base.options["lang"])

def main() -> int:
    if not pre_main_check():
        return 0
    pre_main()
    try:
        bmp.Lang.lang_print("launch.welcome")
        if bmp.Base.options["debug"]:
            bmp.Lang.lang_print("launch.debug")
        while True:
            bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.game.name")))
            for n in map(lambda x: x + 1, range(4)):
                bmp.Lang.lang_print(f"launch.game_mode.{n}")
            bmp.Lang.lang_print(f"launch.game_mode.0")
            game_mode = bmp.Lang.lang_input("input.number")
            try:
                game_mode = int(game_mode)
            except ValueError:
                break
            if game_mode == 1:
                if pre_play():
                    continue
            elif game_mode == 2:
                if pre_edit():
                    continue
            elif game_mode == 3:
                if change_options():
                    continue
            elif game_mode == 4:
                if update_levelpack():
                    continue
            else:
                break
    except KeyboardInterrupt:
        print()
        bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.warning")))
        bmp.Lang.lang_print("launch.keyboard_interrupt")
        bmp.Lang.lang_print("launch.keyboard_interrupt.insert")
        bmp.Base.save_options(bmp.Base.options)
        bmp.Lang.lang_print("launch.exit")
        pygame.quit()
        bmp.Lang.lang_print("launch.thank_you")
        return 0
    except Exception:
        pygame.quit()
        print()
        bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.exception")))
        bmp.Lang.lang_print("launch.exception")
        bmp.Lang.lang_print("launch.exception.report")
        bmp.Lang.lang_print("launch.exception.record")
        traceback.print_exc()
        return 1
    else:
        print()
        bmp.Lang.lang_print(bmp.Lang.seperator_line(bmp.Lang.lang_format("title.game.name")))
        bmp.Base.save_options(bmp.Base.options)
        bmp.Lang.lang_print("launch.exit")
        pygame.quit()
        bmp.Lang.lang_print("launch.thank_you")
        return 0
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          # monika was there ;)
__all__ = ["main"]