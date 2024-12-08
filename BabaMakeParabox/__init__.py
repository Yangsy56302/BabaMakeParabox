from typing import AnyStr, Optional, Callable
import os
import json
import traceback

import pygame

from BabaMakeParabox import basics, languages, positions, refs, colors, objects, collects, rules, displays, spaces, levels, levelpacks, plays, edits, subs
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
    languages.lang_print("seperator.title", text=languages.lang_format("title.directory", dir="levelpacks"))
    show_dir("levelpacks", lambda s: True if basics.options["debug"] else s.endswith(".json"))
    languages.lang_print("seperator.title", text=languages.lang_format("title.open.file"))
    languages.lang_print("launch.open.levelpack")
    input_filename = languages.lang_input("input.file.name")
    input_filename += "" if basics.options["debug"] and not input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        languages.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
        levelpack_json = json.load(file)
        languages.lang_print("launch.open.levelpack.done", file=input_filename)
        levelpack = levelpacks.json_to_levelpack(levelpack_json)
    languages.lang_print("play.start")
    levelpack = plays.play(levelpack)
    languages.lang_print("seperator.title", text=languages.lang_format("title.save.file"))
    languages.lang_print("launch.save.levelpack")
    languages.lang_print("launch.save.levelpack.empty.game")
    output_filename = languages.lang_input("input.file.name")
    if output_filename != "":
        output_filename += "" if basics.options["debug"] and not output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **basics.get_json_dump_kwds())
            languages.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def pre_edit() -> bool:
    languages.lang_print("seperator.title", text=languages.lang_format("title.directory", dir="levelpacks"))
    show_dir("levelpacks", lambda s: True if basics.options["debug"] else s.endswith(".json"))
    languages.lang_print("seperator.title", text=languages.lang_format("title.open.file"))
    languages.lang_print("launch.open.levelpack")
    languages.lang_print("launch.open.levelpack.empty.editor")
    input_filename = languages.lang_input("input.file.name")
    size = positions.Coordinate(basics.options["default_new_space"]["width"], basics.options["default_new_space"]["height"])
    color = basics.options["default_new_space"]["color"]
    if input_filename != "":
        input_filename += "" if basics.options["debug"] and not input_filename.endswith(".json") else ".json"
        if not os.path.isfile(os.path.join("levelpacks", input_filename)):
            languages.lang_print("warn.file.not_found", file=input_filename)
            return False
        with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            languages.lang_print("launch.open.levelpack.done", file=input_filename)
            levelpack = levelpacks.json_to_levelpack(levelpack_json)
    else:
        space = spaces.Space(refs.SpaceID("main_space"), size, color=color)
        level = levels.Level(refs.LevelID("main_level"), [space])
        levelpack = levelpacks.Levelpack([level])
    levelpack = edits.levelpack_editor(levelpack)
    languages.lang_print("seperator.title", text=languages.lang_format("title.save.file"))
    languages.lang_print("launch.save.levelpack")
    languages.lang_print("launch.save.levelpack.empty.editor")
    output_filename = languages.lang_input("input.file.name")
    if output_filename != "":
        output_filename += "" if basics.options["debug"] and not output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **basics.get_json_dump_kwds())
            languages.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def update_levelpack() -> bool:
    languages.lang_print("seperator.title", text=languages.lang_format("title.directory", dir="levelpacks"))
    show_dir("levelpacks", lambda s: True if basics.options["debug"] else s.endswith(".json"))
    languages.lang_print("seperator.title", text=languages.lang_format("title.open.file"))
    languages.lang_print("launch.open.levelpack")
    input_filename = languages.lang_input("input.file.name")
    input_filename += "" if basics.options["debug"] and not input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        languages.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            languages.lang_print("launch.open.levelpack.done", file=input_filename)
            levelpack = levelpacks.json_to_levelpack(levelpack_json)
    languages.lang_print("seperator.title", text=languages.lang_format("title.save.file"))
    languages.lang_print("launch.save.levelpack")
    languages.lang_print("launch.save.levelpack.empty.update")
    output_filename = languages.lang_input("input.file.name")
    output_filename += "" if basics.options["debug"] and not output_filename.endswith(".json") else ".json"
    if output_filename == "":
        output_filename = input_filename
    with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
        json.dump(levelpack.to_json(), file, **basics.get_json_dump_kwds())
        languages.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def change_options() -> bool:
    languages.lang_print("seperator.title", text=languages.lang_format("title.change_options"))
    while True:
        basics.options["debug"] = languages.lang_input("launch.change_options.debug") in languages.yes
        languages.lang_print(f"launch.change_options.performance")
        performance_preset = languages.lang_input("input.number")
        try:
            performance_preset = int(performance_preset)
        except ValueError:
            languages.lang_print("warn.value.invalid", value=performance_preset, cls="int")
        match int(performance_preset):
            case 1:
                basics.options.update({"fps": 5, "fpw": 1, "smooth_animation_multiplier": None})
                break
            case 2:
                basics.options.update({"fps": 10, "fpw": 2, "smooth_animation_multiplier": None})
                break
            case 3:
                basics.options.update({"fps": 20, "fpw": 3, "smooth_animation_multiplier": 3})
                break
            case 4:
                basics.options.update({"fps": 30, "fpw": 5, "smooth_animation_multiplier": 3})
                break
            case 5:
                basics.options.update({"fps": 60, "fpw": 10, "smooth_animation_multiplier": 3})
                break
            case _:
                languages.lang_print("warn.value.out_of_range", min=1, max=5, value=performance_preset)
    while True:
        languages.lang_print("launch.change_options.display_layer")
        display_layer = languages.lang_input("input.number")
        try:
            display_layer = int(display_layer)
        except ValueError:
            languages.lang_print("warn.value.invalid", value=display_layer, cls="int")
            continue
        if display_layer < 0:
            languages.lang_print("warn.value.underflow", min=1, value=display_layer)
        else:
            basics.options.update({"space_display_recursion_depth": display_layer})
            break
    while True:
        languages.lang_print("seperator.title", text=languages.lang_format("title.directory", dir="palettes"))
        show_dir("palettes", lambda s: True if basics.options["debug"] else s.endswith(".png"))
        languages.lang_print("seperator.title", text=languages.lang_format("title.open.file"))
        palette_filename = languages.lang_input("input.file.name")
        if palette_filename == "":
            break
        palette_filename += "" if basics.options["debug"] and not palette_filename.endswith(".png") else ".png"
        pelette_path = os.path.join(".", "palettes", palette_filename)
        if not os.path.isfile(pelette_path):
            languages.lang_print("warn.file.not_found", file=palette_filename)
            continue
        try:
            colors.set_palette(pelette_path)
            basics.options["palette"] = palette_filename
        except Exception:
            languages.lang_print("warn.unknown", value=traceback.format_exc())
        else:
            break
    if languages.lang_input("launch.change_options.json") in languages.yes:
        basics.options.update({"compressed_json_output": False})
    else:
        basics.options.update({"compressed_json_output": True})
    if languages.lang_input("launch.change_options.bgm") in languages.yes:
        basics.options.update({"bgm": {"enabled": True, "name": "rush_baba.mid"}})
    else:
        basics.options.update({"bgm": {"enabled": False, "name": "rush_baba.mid"}})
    while True:
        languages.lang_print("launch.change_options.metatext")
        metatext_tier = languages.lang_input("input.number")
        try:
            metatext_tier = int(metatext_tier)
        except ValueError:
            languages.lang_print("warn.value.invalid", value=metatext_tier, cls="int")
            continue
        if metatext_tier < 0:
            languages.lang_print("warn.value.underflow", min=0, value=metatext_tier)
        elif metatext_tier == 0:
            basics.options.update({"metatext": {"enabled": False, "tier": 0}})
            break
        else:
            basics.options.update({"metatext": {"enabled": True, "tier": metatext_tier}})
            break
    languages.lang_print("launch.change_options.done")
    return True

def pre_main_check() -> bool:
    if os.environ.get(basics.pyinst_env) == "TRUE":
        return False
    if basics.options.get("game_is_done"):
        raise plays.GameIsDoneError()
    return True

def pre_main() -> None:
    os.makedirs("levelpacks", exist_ok=True)
    if basics.options["lang"] not in languages.language_dict.keys():
        for lang in languages.language_dict.keys():
            print(languages.language_dict[lang]["language.select"])
        lang = input(">>> ")
        languages.set_current_language(lang)
        basics.options["lang"] = lang
    else:
        languages.set_current_language(basics.options["lang"])

def main() -> int:
    if not pre_main_check():
        return 0
    pre_main()
    try:
        languages.lang_print("launch.welcome")
        if basics.options["debug"]:
            languages.lang_print("launch.debug")
        while True:
            languages.lang_print("seperator.title", text=languages.lang_format("title.game.name"))
            for n in map(lambda x: x + 1, range(4)):
                languages.lang_print(f"launch.game_mode.{n}")
            languages.lang_print(f"launch.game_mode.0")
            game_mode = languages.lang_input("input.number")
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
        languages.lang_print("seperator.title", text=languages.lang_format("title.warning"))
        languages.lang_print("launch.keyboard_interrupt")
        languages.lang_print("launch.keyboard_interrupt.insert")
        basics.save_options(basics.options)
        languages.lang_print("launch.exit")
        pygame.quit()
        languages.lang_print("launch.thank_you")
        return 0
    except Exception:
        pygame.quit()
        print()
        languages.lang_print("seperator.title", text=languages.lang_format("title.exception"))
        languages.lang_print("launch.exception")
        languages.lang_print("launch.exception.report")
        languages.lang_print("launch.exception.record")
        traceback.print_exc()
        return 1
    else:
        print()
        languages.lang_print("seperator.title", text=languages.lang_format("title.game.name"))
        basics.save_options(basics.options)
        languages.lang_print("launch.exit")
        pygame.quit()
        languages.lang_print("launch.thank_you")
        return 0

__all__ = ["basics", "refs", "languages", "positions", "colors", "objects", "collects", "rules", "displays", "spaces", "levels", "levelpacks", "edits", "plays", "subs", "main"]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          # monika was there ;)