from typing import AnyStr, Optional, Callable
import os
import json
import traceback

import pygame

from bmp import Base, Collect, Color, Editor, Game, Lang, Level, Levelpack, Locate, Object, Ref, Render, Rule, Space, Subgame

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
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if Base.options["debug"] else s.endswith(".json"))
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.open.file")))
    Lang.lang_print("launch.open.levelpack")
    input_filename = Lang.lang_input("input.file.name")
    input_filename += "" if Base.options["debug"] or input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        Lang.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
        levelpack_json = json.load(file)
        Lang.lang_print("launch.open.levelpack.done", file=input_filename)
        levelpack = Levelpack.json_to_levelpack(levelpack_json)
    Lang.lang_print("play.start")
    levelpack = Game.play(levelpack)
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.save.file")))
    Lang.lang_print("launch.save.levelpack")
    Lang.lang_print("launch.save.levelpack.empty.game")
    output_filename = Lang.lang_input("input.file.name")
    if output_filename != "":
        output_filename += "" if Base.options["debug"] or output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **Base.get_json_dump_kwds())
            Lang.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def pre_edit() -> bool:
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if Base.options["debug"] else s.endswith(".json"))
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.open.file")))
    Lang.lang_print("launch.open.levelpack")
    Lang.lang_print("launch.open.levelpack.empty.editor")
    input_filename = Lang.lang_input("input.file.name")
    size = Locate.Coordinate(Base.options["default_new_space"]["width"], Base.options["default_new_space"]["height"])
    color = Base.options["default_new_space"]["color"]
    if input_filename != "":
        input_filename += "" if Base.options["debug"] or input_filename.endswith(".json") else ".json"
        if not os.path.isfile(os.path.join("levelpacks", input_filename)):
            Lang.lang_print("warn.file.not_found", file=input_filename)
            return False
        with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            Lang.lang_print("launch.open.levelpack.done", file=input_filename)
            levelpack = Levelpack.json_to_levelpack(levelpack_json)
    else:
        space = Space.Space(Ref.SpaceID("main_space"), size, color=color)
        level = Level.Level(Ref.LevelID("main_level"), [space])
        levelpack = Levelpack.Levelpack([level])
    levelpack = Editor.levelpack_editor(levelpack)
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.save.file")))
    Lang.lang_print("launch.save.levelpack")
    Lang.lang_print("launch.save.levelpack.empty.editor")
    output_filename = Lang.lang_input("input.file.name")
    if output_filename != "":
        output_filename += "" if Base.options["debug"] or output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **Base.get_json_dump_kwds())
            Lang.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def update_levelpack() -> bool:
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if Base.options["debug"] else s.endswith(".json"))
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.open.file")))
    Lang.lang_print("launch.open.levelpack")
    input_filename = Lang.lang_input("input.file.name")
    input_filename += "" if Base.options["debug"] or input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        Lang.lang_print("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            Lang.lang_print("launch.open.levelpack.done", file=input_filename)
            levelpack = Levelpack.json_to_levelpack(levelpack_json)
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.save.file")))
    Lang.lang_print("launch.save.levelpack")
    Lang.lang_print("launch.save.levelpack.empty.update")
    output_filename = Lang.lang_input("input.file.name")
    output_filename += "" if Base.options["debug"] or output_filename.endswith(".json") else ".json"
    if output_filename == "":
        output_filename = input_filename
    with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
        json.dump(levelpack.to_json(), file, **Base.get_json_dump_kwds())
        Lang.lang_print("launch.save.levelpack.done", file=output_filename)
    return True

def change_options() -> bool:
    Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.change_options")))
    while True:
        Base.options["debug"] = Lang.lang_input("launch.change_options.debug") in Lang.yes
        Lang.lang_print(f"launch.change_options.performance")
        performance_preset_index = Lang.lang_input("input.number")
        try:
            performance_preset_index = int(performance_preset_index)
        except ValueError:
            Lang.lang_print("warn.value.invalid", value=performance_preset_index, cls="int")
            continue
        match int(performance_preset_index):
            case 1:
                Base.options.update({"fps": 5, "smooth_animation_multiplier": None}); break
            case 2:
                Base.options.update({"fps": 10, "smooth_animation_multiplier": None}); break
            case 3:
                Base.options.update({"fps": 15, "smooth_animation_multiplier": 3}); break
            case 4:
                Base.options.update({"fps": 30, "smooth_animation_multiplier": 3}); break
            case 5:
                Base.options.update({"fps": 60, "smooth_animation_multiplier": 3}); break
            case _:
                Lang.lang_print("warn.value.out_of_range", min=1, max=5, value=performance_preset_index)
    while True:
        Lang.lang_print("launch.change_options.display_layer")
        display_layer = Lang.lang_input("input.number")
        try:
            display_layer = int(display_layer)
        except ValueError:
            Lang.lang_print("warn.value.invalid", value=display_layer, cls="int")
            continue
        if display_layer < 0:
            Lang.lang_print("warn.value.underflow", min=1, value=display_layer)
        else:
            Base.options.update({"space_display_recursion_depth": display_layer})
            break
    while True:
        Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.directory", dir="palettes")))
        show_dir("palettes", lambda s: True if Base.options["debug"] else s.endswith(".png"))
        Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.open.file")))
        palette_filename = Lang.lang_input("input.file.name")
        if palette_filename == "":
            break
        palette_filename += "" if Base.options["debug"] or palette_filename.endswith(".png") else ".png"
        pelette_path = os.path.join(".", "palettes", palette_filename)
        if not os.path.isfile(pelette_path):
            Lang.lang_print("warn.file.not_found", file=palette_filename)
            continue
        try:
            Color.set_palette(pelette_path)
            Base.options["palette"] = palette_filename
        except Exception:
            Lang.lang_print("warn.unknown", value=traceback.format_exc())
        else:
            break
    if Lang.lang_input("launch.change_options.json") in Lang.yes:
        Base.options.update({"compressed_json_output": False})
    else:
        Base.options.update({"compressed_json_output": True})
    if Lang.lang_input("launch.change_options.bgm") in Lang.yes:
        Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.directory", dir="midi")))
        show_dir("midi", lambda s: True if Base.options["debug"] else s.endswith(".mid"))
        Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.open.file")))
        mid_filename = Lang.lang_input("input.file.name")
        mid_filename += "" if Base.options["debug"] or mid_filename.endswith(".mid") else ".mid"
        if os.path.isfile(os.path.join(".", "midi", mid_filename)):
            Base.options.update({"bgm": {"enabled": True, "name": mid_filename}})
        else:
            Lang.lang_print("warn.file.not_found", file=mid_filename)
            Base.options.update({"bgm": {"enabled": False, "name": mid_filename}})
    else:
        Base.options.update({"bgm": {"enabled": False, "name": "rush_baba.mid"}})
    while True:
        Lang.lang_print("launch.change_options.metatext")
        metatext_tier = Lang.lang_input("input.number")
        try:
            metatext_tier = int(metatext_tier)
        except ValueError:
            Lang.lang_print("warn.value.invalid", value=metatext_tier, cls="int")
            continue
        if metatext_tier < 0:
            Lang.lang_print("warn.value.underflow", min=0, value=metatext_tier)
        elif metatext_tier == 0:
            Base.options.update({"metatext": {"enabled": False, "tier": 0}})
            break
        else:
            Base.options.update({"metatext": {"enabled": True, "tier": metatext_tier}})
            break
    Lang.lang_print("launch.change_options.done")
    return True

def pre_main_check() -> bool:
    if os.environ.get(Base.pyinst_env) == "TRUE":
        return False
    if Base.options.get("game_is_done"):
        raise Game.GameIsDoneError()
    return True

def pre_main() -> None:
    os.makedirs("levelpacks", exist_ok=True)
    if Base.options["lang"] not in Lang.language_dict.keys():
        for lang in Lang.language_dict.keys():
            print(Lang.language_dict[lang]["language.select"])
        lang = input(">>> ")
        Lang.set_current_language(lang)
        Base.options["lang"] = lang
    else:
        Lang.set_current_language(Base.options["lang"])

def main() -> int:
    if not pre_main_check():
        return 0
    pre_main()
    try:
        Lang.lang_print("launch.welcome")
        if Base.options["debug"]:
            Lang.lang_print("launch.debug")
        while True:
            Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.game.name")))
            for n in map(lambda x: x + 1, range(4)):
                Lang.lang_print(f"launch.game_mode.{n}")
            Lang.lang_print(f"launch.game_mode.0")
            game_mode = Lang.lang_input("input.number")
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
        Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.warning")))
        Lang.lang_print("launch.keyboard_interrupt")
        Lang.lang_print("launch.keyboard_interrupt.insert")
        Base.save_options(Base.options)
        Lang.lang_print("launch.exit")
        pygame.quit()
        Lang.lang_print("launch.thank_you")
        return 0
    except Exception:
        pygame.quit()
        print()
        Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.exception")))
        Lang.lang_print("launch.exception")
        Lang.lang_print("launch.exception.report")
        Lang.lang_print("launch.exception.record")
        traceback.print_exc()
        return 1
    else:
        print()
        Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.game.name")))
        Base.save_options(Base.options)
        Lang.lang_print("launch.exit")
        pygame.quit()
        Lang.lang_print("launch.thank_you")
        return 0
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          # monika was there ;)
__all__ = ["Base", "Ref", "Lang", "Locate", "Color", "Object", "Collect", "Rule", "Render", "Space", "Level", "Levelpack", "Editor", "Game", "Subgame", "main"]