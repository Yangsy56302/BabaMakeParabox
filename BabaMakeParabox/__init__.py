from typing import AnyStr, Optional, Callable
import os
import json

import pygame

from BabaMakeParabox import basics, languages, spaces, colors, objects, rules, displays, worlds, levels, levelpacks, plays, edits, subs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   # monika was there ;)

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
    languages.lang_print("line")
    languages.lang_print("output.directory")
    show_dir("levelpacks", lambda s: s.endswith(".json"))
    languages.lang_print("output.end")
    languages.lang_print("line")
    languages.lang_print("main.open.levelpack")
    input_filename = languages.lang_input("input.file.name")
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        languages.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
        levelpack_json = json.load(file)
        languages.lang_print("main.open.levelpack.done", file=input_filename)
        levelpack = levelpacks.json_to_levelpack(levelpack_json)
    languages.lang_print("game.start")
    levelpack = plays.play(levelpack)
    languages.lang_print("line")
    languages.lang_print("main.save.levelpack")
    languages.lang_print("main.save.levelpack.empty.game")
    output_filename = languages.lang_input("input.file.name")
    if output_filename != "":
        if not os.path.isfile(os.path.join("levelpacks", output_filename)):
            languages.lang_print("warn.file.not_found", file=input_filename)
            return False
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, indent=None if basics.options["compressed_json_output"] else 4, separators=(",", ":") if basics.options["compressed_json_output"] else (", ", ": "))
    return True

def pre_edit() -> bool:
    languages.lang_print("line")
    languages.lang_print("output.directory")
    show_dir("levelpacks", lambda s: s.endswith(".json"))
    languages.lang_print("output.end")
    languages.lang_print("line")
    languages.lang_print("main.open.levelpack")
    languages.lang_print("main.open.levelpack.empty.editor")
    input_filename = languages.lang_input("input.file.name")
    default_new_world_settings = basics.options["default_new_world"]
    size = (default_new_world_settings["width"], default_new_world_settings["height"])
    color = default_new_world_settings["color"]
    if input_filename != "":
        if not os.path.isfile(os.path.join("levelpacks", input_filename)):
            languages.lang_print("warn.file.not_found", file=input_filename)
            return False
        with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            languages.lang_print("main.open.levelpack.done", file=input_filename)
            levelpack = levelpacks.json_to_levelpack(levelpack_json)
    else:
        world = worlds.World("main", size, color=color)
        level = levels.Level("main", [world])
        levelpack = levelpacks.Levelpack("main", [level])
    levelpack = edits.levelpack_editor(levelpack)
    languages.lang_print("line")
    languages.lang_print("main.save.levelpack")
    languages.lang_print("main.save.levelpack.empty.editor")
    output_filename = languages.lang_input("input.file.name")
    if output_filename != "":
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, indent=None if basics.options["compressed_json_output"] else 4, separators=(",", ":") if basics.options["compressed_json_output"] else (", ", ": "))
            languages.lang_print("main.save.levelpack.done", file=output_filename)
    return True

def update_levelpack() -> bool:
    languages.lang_print("line")
    languages.lang_print("output.directory")
    show_dir("levelpacks", lambda s: s.endswith(".json"))
    languages.lang_print("output.end")
    languages.lang_print("line")
    languages.lang_print("main.open.levelpack")
    input_filename = languages.lang_input("input.file.name")
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        languages.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            languages.lang_print("main.open.levelpack.done", file=input_filename)
            levelpack = levelpacks.json_to_levelpack(levelpack_json)
    languages.lang_print("line")
    languages.lang_print("main.save.levelpack")
    languages.lang_print("main.save.levelpack.empty.update")
    output_filename = languages.lang_input("input.file.name")
    if output_filename == "":
        output_filename = input_filename
    with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
        json.dump(levelpack.to_json(), file, indent=None if basics.options["compressed_json_output"] else 4, separators=(",", ":") if basics.options["compressed_json_output"] else (", ", ": "))
        languages.lang_print("main.save.levelpack.done", file=output_filename)
    return True

def pre_main_check() -> bool:
    if os.environ.get(basics.pyinst_env) == "TRUE":
        return False
    if basics.options.get("game_is_done"):
        raise plays.GameIsDoneError()
    return True

def change_options() -> bool:
    languages.lang_print("line")
    while True:
        languages.lang_print("main.change_options.fps")
        fps_preset = languages.lang_input("input.number")
        try:
            fps_preset = int(fps_preset)
        except ValueError:
            languages.lang_print("warn.value.invalid", val=fps_preset, cls="int")
        match int(fps_preset):
            case 1:
                basics.options.update({"fps": 5, "fpw": 1, "world_display_recursion_depth": 1})
                break
            case 2:
                basics.options.update({"fps": 15, "fpw": 3, "world_display_recursion_depth": 2})
                break
            case 3:
                basics.options.update({"fps": 30, "fpw": 5, "world_display_recursion_depth": 3})
                break
            case 4:
                basics.options.update({"fps": 60, "fpw": 10, "world_display_recursion_depth": 4})
                break
            case _:
                languages.lang_print("warn.value.out_of_range", min=1, max=4, val=fps_preset)
    if languages.lang_input("main.change_options.json") in languages.yes:
        basics.options.update({"compressed_json_output": False})
    else:
        basics.options.update({"compressed_json_output": True})
    if languages.lang_input("main.change_options.bgm") in languages.yes:
        basics.options.update({"bgm": {"enabled": True, "name": "rush_baba.mid"}})
    else:
        basics.options.update({"bgm": {"enabled": False, "name": "rush_baba.mid"}})
    while True:
        languages.lang_print("main.change_options.metatext")
        metatext_tier = languages.lang_input("input.number")
        try:
            metatext_tier = int(metatext_tier)
        except ValueError:
            languages.lang_print("warn.value.invalid", val=metatext_tier, cls="int")
        else:
            if metatext_tier < 0:
                languages.lang_print("warn.value.underflow", min=0, val=metatext_tier)
            elif metatext_tier == 0:
                basics.options.update({"metatext": {"enabled": False, "tier": 0}})
                break
            else:
                basics.options.update({"metatext": {"enabled": True, "tier": metatext_tier}})
                break
    languages.lang_print("main.change_options.done")
    return True

def main() -> None:
    if basics.options["lang"] not in languages.language_dict.keys():
        for lang in languages.language_dict.keys():
            print(languages.language_dict[lang]["language.select"])
        lang = input(">>> ")
        languages.set_current_language(lang)
        basics.options["lang"] = lang
    else:
        languages.set_current_language(basics.options["lang"])
    try:
        languages.lang_print("main.welcome")
        while True:
            languages.lang_print("line")
            for n in map(lambda x: x + 1, range(4)):
                print(languages.current_language[f"main.game_mode.{n}"])
            game_mode = languages.lang_input("input.number")
            try:
                game_mode = int(game_mode)
            except ValueError:
                languages.lang_print("warn.value.invalid", val=game_mode, cls="int")
                continue
            if game_mode == 1:
                if pre_play():
                    break
            elif game_mode == 2:
                if pre_edit():
                    break
            elif game_mode == 3:
                if change_options():
                    break
            elif game_mode == 4:
                if update_levelpack():
                    break
            else:
                languages.lang_print("warn.value.out_of_range", min=1, max=4, val=game_mode)
    except KeyboardInterrupt:
        print()
        languages.lang_print("main.keyboard_interrupt")
        languages.lang_print("main.keyboard_interrupt.insert")
        languages.lang_print("main.exit")
        basics.save_options(basics.options)
        pygame.quit()
        languages.lang_print("main.thank_you")
    except Exception as e:
        print()
        languages.lang_print("main.exception")
        languages.lang_print("main.exception.report")
        languages.lang_print("main.exception.record")
        raise e
    else:
        print()
        languages.lang_print("main.exit")
        basics.save_options(basics.options)
        pygame.quit()
        languages.lang_print("main.thank_you")

__all__ = ["basics", "languages", "spaces", "colors", "objects", "rules", "displays", "worlds", "levels", "levelpacks", "edits", "plays", "subs", "main"]