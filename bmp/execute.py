from typing import Optional, Callable
import os
import json
import traceback

import pygame

import bmp.audio
import bmp.base
import bmp.collect
import bmp.color
import bmp.editor
import bmp.game
import bmp.lang
import bmp.level
import bmp.levelpack
import bmp.loc
import bmp.obj
import bmp.ref
import bmp.render
import bmp.rule
import bmp.space
import bmp.sub

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
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.base.options["debug"] else s.endswith(".json"))
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.open.file")))
    bmp.lang.lang_print("launch.open.levelpack")
    input_filename = bmp.lang.lang_input("input.file.name")
    input_filename += "" if bmp.base.options["debug"] or input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        bmp.lang.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
        levelpack_json = json.load(file)
        bmp.lang.lang_print("launch.open.levelpack.done", file=input_filename)
        levelpack = bmp.levelpack.json_to_levelpack(levelpack_json)
    bmp.lang.lang_print("play.start")
    levelpack = bmp.game.play(levelpack)
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.save.file")))
    bmp.lang.lang_print("launch.save.levelpack")
    bmp.lang.lang_print("launch.save.levelpack.empty.game")
    output_filename = bmp.lang.lang_input("input.file.name")
    if output_filename != "":
        output_filename += "" if bmp.base.options["debug"] or output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **bmp.base.get_json_dump_kwds())
            bmp.lang.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def pre_edit() -> bool:
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.base.options["debug"] else s.endswith(".json"))
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.open.file")))
    bmp.lang.lang_print("launch.open.levelpack")
    bmp.lang.lang_print("launch.open.levelpack.empty.editor")
    input_filename = bmp.lang.lang_input("input.file.name")
    size = bmp.loc.Coordinate(bmp.base.options["default_new_space"]["width"], bmp.base.options["default_new_space"]["height"])
    color = bmp.base.options["default_new_space"]["color"]
    if input_filename != "":
        input_filename += "" if bmp.base.options["debug"] or input_filename.endswith(".json") else ".json"
        if not os.path.isfile(os.path.join("levelpacks", input_filename)):
            bmp.lang.lang_print("warn.file.not_found", file=input_filename)
            return False
        with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            bmp.lang.lang_print("launch.open.levelpack.done", file=input_filename)
            levelpack = bmp.levelpack.json_to_levelpack(levelpack_json)
    else:
        space = bmp.space.Space(bmp.ref.SpaceID("main_space"), size, color=color)
        level = bmp.level.Level(bmp.ref.LevelID("main_level"), [space])
        levelpack = bmp.levelpack.Levelpack([level])
    levelpack = bmp.editor.levelpack_editor(levelpack)
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.save.file")))
    bmp.lang.lang_print("launch.save.levelpack")
    bmp.lang.lang_print("launch.save.levelpack.empty.editor")
    output_filename = bmp.lang.lang_input("input.file.name")
    if output_filename != "":
        output_filename += "" if bmp.base.options["debug"] or output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **bmp.base.get_json_dump_kwds())
            bmp.lang.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def update_levelpack() -> bool:
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.base.options["debug"] else s.endswith(".json"))
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.open.file")))
    bmp.lang.lang_print("launch.open.levelpack")
    input_filename = bmp.lang.lang_input("input.file.name")
    input_filename += "" if bmp.base.options["debug"] or input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        bmp.lang.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            bmp.lang.lang_print("launch.open.levelpack.done", file=input_filename)
            levelpack = bmp.levelpack.json_to_levelpack(levelpack_json)
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.save.file")))
    bmp.lang.lang_print("launch.save.levelpack")
    bmp.lang.lang_print("launch.save.levelpack.empty.update")
    output_filename = bmp.lang.lang_input("input.file.name")
    output_filename += "" if bmp.base.options["debug"] or output_filename.endswith(".json") else ".json"
    if output_filename == "":
        output_filename = input_filename
    with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
        json.dump(levelpack.to_json(), file, **bmp.base.get_json_dump_kwds())
        bmp.lang.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def change_options() -> bool:
    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.change_options")))
    while True:
        bmp.base.options["debug"] = bmp.lang.lang_input("launch.change_options.debug") in bmp.lang.yes
        bmp.lang.lang_print(f"launch.change_options.performance")
        performance_preset_index = bmp.lang.lang_input("input.number")
        try:
            performance_preset_index = int(performance_preset_index)
        except ValueError:
            bmp.lang.lang_print("warn.value.invalid", value=performance_preset_index, cls="int")
            continue
        match int(performance_preset_index):
            case 1:
                bmp.base.options.update({"fps": 5, "smooth_animation_multiplier": None}); break
            case 2:
                bmp.base.options.update({"fps": 10, "smooth_animation_multiplier": None}); break
            case 3:
                bmp.base.options.update({"fps": 15, "smooth_animation_multiplier": 3}); break
            case 4:
                bmp.base.options.update({"fps": 30, "smooth_animation_multiplier": 3}); break
            case 5:
                bmp.base.options.update({"fps": 60, "smooth_animation_multiplier": 3}); break
            case _:
                bmp.lang.lang_print("warn.value.out_of_range", min=1, max=5, value=performance_preset_index)
    while True:
        bmp.lang.lang_print("launch.change_options.display_layer")
        display_layer = bmp.lang.lang_input("input.number")
        try:
            display_layer = int(display_layer)
        except ValueError:
            bmp.lang.lang_print("warn.value.invalid", value=display_layer, cls="int")
            continue
        if display_layer < 0:
            bmp.lang.lang_print("warn.value.underflow", min=1, value=display_layer)
        else:
            bmp.base.options.update({"space_display_recursion_depth": display_layer})
            break
    while True:
        bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.directory", dir="palettes")))
        show_dir("palettes", lambda s: True if bmp.base.options["debug"] else s.endswith(".png"))
        bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.open.file")))
        palette_filename = bmp.lang.lang_input("input.file.name")
        if palette_filename == "":
            break
        palette_filename += "" if bmp.base.options["debug"] or palette_filename.endswith(".png") else ".png"
        pelette_path = os.path.join(".", "palettes", palette_filename)
        if not os.path.isfile(pelette_path):
            bmp.lang.lang_print("warn.file.not_found", file=palette_filename)
            continue
        try:
            bmp.color.set_palette(pelette_path)
            bmp.base.options["palette"] = palette_filename
        except Exception:
            bmp.lang.lang_print("warn.unknown", value=traceback.format_exc())
        else:
            break
    if bmp.lang.lang_input("launch.change_options.json") in bmp.lang.yes:
        bmp.base.options.update({"compressed_json_output": False})
    else:
        bmp.base.options.update({"compressed_json_output": True})
    if bmp.lang.lang_input("launch.change_options.bgm") in bmp.lang.yes:
        bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.directory", dir="midi")))
        show_dir("midi", lambda s: True if bmp.base.options["debug"] else s.endswith(".mid"))
        bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.open.file")))
        mid_filename = bmp.lang.lang_input("input.file.name")
        mid_filename += "" if bmp.base.options["debug"] or mid_filename.endswith(".mid") else ".mid"
        if os.path.isfile(os.path.join(".", "midi", mid_filename)):
            bmp.base.options.update({"bgm": {"enabled": True, "name": mid_filename}})
        else:
            bmp.lang.lang_print("warn.file.not_found", file=mid_filename)
            bmp.base.options.update({"bgm": {"enabled": False, "name": mid_filename}})
    else:
        bmp.base.options.update({"bgm": {"enabled": False, "name": "rush_baba.mid"}})
    while True:
        bmp.lang.lang_print("launch.change_options.metatext")
        metatext_tier = bmp.lang.lang_input("input.number")
        try:
            metatext_tier = int(metatext_tier)
        except ValueError:
            bmp.lang.lang_print("warn.value.invalid", value=metatext_tier, cls="int")
            continue
        if metatext_tier < 0:
            bmp.lang.lang_print("warn.value.underflow", min=0, value=metatext_tier)
        elif metatext_tier == 0:
            bmp.base.options.update({"metatext": {"enabled": False, "tier": 0}})
            break
        else:
            bmp.base.options.update({"metatext": {"enabled": True, "tier": metatext_tier}})
            break
    bmp.lang.lang_print("launch.change_options.done")
    return True

def pre_main_check() -> bool:
    if os.environ.get(bmp.base.pyinst_env) == "TRUE":
        return False
    if bmp.base.options.get("game_is_done"):
        raise bmp.game.GameIsDoneError()
    return True

def pre_main() -> None:
    os.makedirs("levelpacks", exist_ok=True)
    if bmp.base.options["lang"] not in bmp.lang.language_dict.keys():
        for lang in bmp.lang.language_dict.keys():
            print(bmp.lang.language_dict[lang]["language.select"])
        lang = input(">>> ")
        bmp.lang.set_current_language(lang)
        bmp.base.options["lang"] = lang
    else:
        bmp.lang.set_current_language(bmp.base.options["lang"])

def main() -> int:
    if not pre_main_check():
        return 0
    pre_main()
    try:
        bmp.lang.lang_print("launch.welcome")
        if bmp.base.options["debug"]:
            bmp.lang.lang_print("launch.debug")
        while True:
            bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.game.name")))
            for n in map(lambda x: x + 1, range(4)):
                bmp.lang.lang_print(f"launch.game_mode.{n}")
            bmp.lang.lang_print(f"launch.game_mode.0")
            game_mode = bmp.lang.lang_input("input.number")
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
        bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.warning")))
        bmp.lang.lang_print("launch.keyboard_interrupt")
        bmp.lang.lang_print("launch.keyboard_interrupt.insert")
        bmp.base.save_options(bmp.base.options)
        bmp.lang.lang_print("launch.exit")
        pygame.quit()
        bmp.lang.lang_print("launch.thank_you")
        return 2
    except Exception:
        pygame.quit()
        print()
        bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.exception")))
        bmp.lang.lang_print("launch.exception")
        bmp.lang.lang_print("launch.exception.report")
        bmp.lang.lang_print("launch.exception.record")
        traceback.print_exc()
        return 1
    else:
        print()
        bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.game.name")))
        bmp.base.save_options(bmp.base.options)
        bmp.lang.lang_print("launch.exit")
        pygame.quit()
        bmp.lang.lang_print("launch.thank_you")
        return 0