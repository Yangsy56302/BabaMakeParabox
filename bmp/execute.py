from typing import Final, Optional, Callable
import os
import json
import traceback

import pygame

import bmp.audio
import bmp.base
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

def gameplay() -> bool:
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.opt.options["debug"] else s.endswith(".json"))
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.open.file")))
    bmp.lang.fprint("launch.open.levelpack")
    input_filename = bmp.lang.input_str(bmp.lang.fformat("input.file.name"))
    input_filename += "" if bmp.opt.options["debug"] or input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        bmp.lang.fwarn("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
        levelpack_json = json.load(file)
        bmp.lang.fprint("launch.open.levelpack.done", file=input_filename)
        levelpack = bmp.levelpack.json_to_levelpack(levelpack_json)
    bmp.lang.fprint("play.start")
    levelpack = bmp.game.play(levelpack)
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.save.file")))
    bmp.lang.fprint("launch.save.levelpack")
    bmp.lang.fprint("launch.save.levelpack.empty.game")
    output_filename = bmp.lang.input_str(bmp.lang.fformat("input.file.name"))
    if output_filename != "":
        output_filename += "" if bmp.opt.options["debug"] or output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **bmp.opt.get_json_dump_kwds())
            bmp.lang.fprint("launch.save.levelpack.done", file=output_filename)
    return True

def editor() -> bool:
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.opt.options["debug"] else s.endswith(".json"))
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.open.file")))
    bmp.lang.fprint("launch.open.levelpack")
    bmp.lang.fprint("launch.open.levelpack.empty.editor")
    input_filename = bmp.lang.input_str(bmp.lang.fformat("input.file.name"))
    if input_filename != "":
        input_filename += "" if bmp.opt.options["debug"] or input_filename.endswith(".json") else ".json"
        if not os.path.isfile(os.path.join("levelpacks", input_filename)):
            bmp.lang.fwarn("warn.file.not_found", file=input_filename)
            return False
        with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
            levelpack_json = json.load(file)
            bmp.lang.fprint("launch.open.levelpack.done", file=input_filename)
            levelpack = bmp.levelpack.json_to_levelpack(levelpack_json)
    else:
        size = (
            bmp.opt.options["editor"]["default_space"]["width"],
            bmp.opt.options["editor"]["default_space"]["height"],
        )
        color = bmp.opt.options["editor"]["default_space"]["color"]
        space = bmp.space.Space(bmp.ref.SpaceID("0space"), size, color=color)
        level = bmp.level.Level(bmp.ref.LevelID("0level"), [space.space_id], space.space_id)
        levelpack = bmp.levelpack.Levelpack({level.level_id: level}, {space.space_id: space}, level.level_id)
    levelpack = bmp.editor.levelpack_editor(levelpack)
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.save.file")))
    bmp.lang.fprint("launch.save.levelpack")
    bmp.lang.fprint("launch.save.levelpack.empty.editor")
    output_filename = bmp.lang.input_str(bmp.lang.fformat("input.file.name"))
    if output_filename != "":
        output_filename += "" if bmp.opt.options["debug"] or output_filename.endswith(".json") else ".json"
        with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, **bmp.opt.get_json_dump_kwds())
            bmp.lang.fprint("launch.save.levelpack.done", file=output_filename)
    return True

def update_levelpack() -> bool:
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.opt.options["debug"] else s.endswith(".json"))
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.open.file")))
    bmp.lang.fprint("launch.open.levelpack")
    input_filename = bmp.lang.input_str(bmp.lang.fformat("input.file.name"))
    input_filename += "" if bmp.opt.options["debug"] or input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        bmp.lang.fwarn("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
        levelpack_json: bmp.levelpack.AnyLevelpackJson = json.load(file)
        bmp.lang.fprint("launch.open.levelpack.done", file=input_filename)
        levelpack_json = bmp.levelpack.update_json_format(levelpack_json, levelpack_json["ver"])
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.save.file")))
    bmp.lang.fprint("launch.save.levelpack")
    bmp.lang.fprint("launch.save.levelpack.empty.update")
    output_filename = bmp.lang.input_str(bmp.lang.fformat("input.file.name"))
    output_filename += "" if bmp.opt.options["debug"] or output_filename.endswith(".json") else ".json"
    if output_filename == "":
        output_filename = input_filename
    with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
        json.dump(levelpack_json, file, **bmp.opt.get_json_dump_kwds())
        bmp.lang.fprint("launch.save.levelpack.done", file=output_filename)
    return True

def set_levelpack_to_initial() -> bool:
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.directory", dir="levelpacks")))
    show_dir("levelpacks", lambda s: True if bmp.opt.options["debug"] else s.endswith(".json"))
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.open.file")))
    bmp.lang.fprint("launch.open.levelpack")
    input_filename = bmp.lang.input_str(bmp.lang.fformat("input.file.name"))
    input_filename += "" if bmp.opt.options["debug"] or input_filename.endswith(".json") else ".json"
    if not os.path.isfile(os.path.join("levelpacks", input_filename)):
        bmp.lang.fwarn("warn.file.not_found", file=input_filename)
        return False
    with open(os.path.join("levelpacks", input_filename), "r", encoding="utf-8") as file:
        levelpack_json: bmp.levelpack.LevelpackJson = json.load(file)
        bmp.lang.fprint("launch.open.levelpack.done", file=input_filename)
        levelpack_json.pop("level_init_states")
        levelpack_json.pop("space_init_states")
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.save.file")))
    bmp.lang.fprint("launch.save.levelpack")
    bmp.lang.fprint("launch.save.levelpack.empty.update")
    output_filename = bmp.lang.input_str(bmp.lang.fformat("input.file.name"))
    output_filename += "" if bmp.opt.options["debug"] or output_filename.endswith(".json") else ".json"
    if output_filename == "":
        output_filename = input_filename
    with open(os.path.join("levelpacks", output_filename), "w", encoding="utf-8") as file:
        json.dump(levelpack_json, file, **bmp.opt.get_json_dump_kwds())
        bmp.lang.fprint("launch.save.levelpack.done", file=output_filename)
    return True

def change_options() -> bool:
    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.change_options")))
    while True:
        bmp.opt.options["debug"] = bmp.lang.input_yes(bmp.lang.fformat("launch.change_options.debug"))
        bmp.lang.fprint(f"launch.change_options.performance")
        performance_preset_index = bmp.lang.input_int(bmp.lang.fformat("input.number"))
        match int(performance_preset_index):
            case 1:
                bmp.opt.options["render"].update({"fps": 5, "smooth": None}); break
            case 2:
                bmp.opt.options["render"].update({"fps": 10, "smooth": None}); break
            case 3:
                bmp.opt.options["render"].update({"fps": 15, "smooth": 3}); break
            case 4:
                bmp.opt.options["render"].update({"fps": 30, "smooth": 3}); break
            case 5:
                bmp.opt.options["render"].update({"fps": 60, "smooth": 3}); break
            case _:
                bmp.lang.fwarn("warn.value.out_of_range", min=1, max=5, value=performance_preset_index); continue
    while True:
        bmp.lang.fprint("launch.change_options.display_layer")
        display_layer = bmp.lang.input_int(bmp.lang.fformat("input.number"))
        if display_layer < 0:
            bmp.lang.fwarn("warn.value.underflow", min=0, value=display_layer)
            continue
        bmp.opt.options["render"].update({"space_depth": display_layer})
        break
    while True:
        bmp.lang.fprint("launch.change_options.long_press")
        bmp.lang.fprint("launch.change_options.long_press.delay")
        bmp.lang.fprint("launch.change_options.long_press.delay.disable")
        delay = bmp.lang.input_int(bmp.lang.fformat("input.number"))
        if delay < 0:
            bmp.lang.fwarn("warn.value.underflow", min=0, value=display_layer)
            continue
        elif delay == 0:
            interval = 0
        else:
            bmp.lang.fprint("launch.change_options.long_press.interval")
            interval = bmp.lang.input_int(bmp.lang.fformat("input.number"))
            if interval < 0:
                bmp.lang.fwarn("warn.value.underflow", min=0, value=display_layer)
                continue
        bmp.opt.options["gameplay"]["repeat"].update({"delay": delay, "interval": interval})
        break
    while True:
        bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.directory", dir="palettes")))
        show_dir("palettes", lambda s: True if bmp.opt.options["debug"] else s.endswith(".png"))
        bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.open.file")))
        palette_filename = bmp.lang.input_str(bmp.lang.fformat("input.file.name"))
        if palette_filename == "":
            break
        palette_filename += "" if bmp.opt.options["debug"] or palette_filename.endswith(".png") else ".png"
        pelette_path = os.path.join(".", "palettes", palette_filename)
        if not os.path.isfile(pelette_path):
            bmp.lang.fwarn("warn.file.not_found", file=palette_filename)
            continue
        try:
            bmp.color.set_palette(pelette_path)
            bmp.opt.options["render"]["palette"] = palette_filename
        except Exception:
            bmp.lang.fwarn("warn.unknown", value=traceback.format_exc())
        else:
            break
    bmp.opt.options["editor"].update({"minimal_json": bmp.lang.input_yes(bmp.lang.fformat("launch.change_options.json"))})
    while True:
        bmp.lang.fprint("launch.change_options.metatext")
        metatext_tier = bmp.lang.input_int(bmp.lang.fformat("input.number"))
        if metatext_tier < 0:
            bmp.lang.fwarn("warn.value.underflow", min=0, value=metatext_tier)
            continue
        elif metatext_tier == 0:
            bmp.opt.options["gameplay"].update({"metatext": {"enabled": False, "tier": 0}})
            break
        else:
            bmp.opt.options["gameplay"].update({"metatext": {"enabled": True, "tier": metatext_tier}})
            break
    bmp.lang.fprint("launch.change_options.done")
    return True

def pre_main_check() -> bool:
    if os.environ.get(bmp.base.pyinst_env) == "TRUE":
        return False
    if bmp.opt.options.get("game_is_done"):
        raise bmp.game.GameIsDoneError()
    return True

def pre_main() -> None:
    os.makedirs("levelpacks", exist_ok=True)
    if bmp.opt.options["lang"] not in bmp.lang.language_dict.keys():
        for lang in bmp.lang.language_dict.keys():
            print(bmp.lang.language_dict[lang]["language.select"])
        lang = bmp.lang.input(">>> ")
        bmp.lang.set_current_language(lang)
        bmp.opt.options["lang"] = lang
    else:
        bmp.lang.set_current_language(bmp.opt.options["lang"])

def main() -> int:
    gpl_output: str = "\n".join([
        "    Baba Make Parabox  Copyright (C) 2025  Yangsy56302",
        "    This program comes with ABSOLUTELY NO WARRANTY; for details type `w'.",
        "    This is free software, and you are welcome to redistribute it",
        "    under certain conditions; type `c' for details.",
    ])
    print(gpl_output)
    gpl_choice: dict[str, str] = {
        "w": "\n".join([
            "    This program is distributed in the hope that it will be useful,",
            "    but WITHOUT ANY WARRANTY; without even the implied warranty of",
            "    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the",
            "    GNU General Public License for more details.",
        ]),
        "c": "\n".join([
            "    This program is free software: you can redistribute it and/or modify",
            "    it under the terms of the GNU General Public License as published by",
            "    the Free Software Foundation, either version 3 of the License, or",
            "    (at your option) any later version.",
        ]),
    }
    choice: dict[str, Callable[[], bool]] = {
        "1": gameplay,
        "2": editor,
        "3": change_options,
        "4": update_levelpack,
        "5": set_levelpack_to_initial,
    }
    if not pre_main_check():
        return 0
    pre_main()
    try:
        bmp.lang.fprint("launch.welcome")
        if bmp.opt.options["debug"]:
            bmp.lang.fprint("launch.debug")
        while True:
            bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.game.name")))
            for k in choice.keys():
                bmp.lang.fprint(f"launch.game_mode.{k}")
            bmp.lang.fprint(f"launch.game_mode._")
            game_mode = bmp.lang.input_str(bmp.lang.fformat("input.string"))
            match game_mode:
                case k if k in choice.keys():
                    if choice[k]():
                        continue
                case k if k in gpl_choice.keys():
                    print(gpl_choice[k])
                    continue
                case _:
                    break
    except KeyboardInterrupt:
        print()
        bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.warning")))
        bmp.lang.fprint("launch.keyboard_interrupt")
        bmp.lang.fprint("launch.keyboard_interrupt.insert")
        bmp.opt.save()
        bmp.lang.fprint("launch.exit")
        pygame.quit()
        bmp.lang.fprint("launch.thank_you")
        return 2
    except Exception:
        pygame.quit()
        print()
        bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.exception")))
        bmp.lang.fprint("launch.exception")
        bmp.lang.fprint("launch.exception.report")
        bmp.lang.fprint("launch.exception.record")
        traceback.print_exc()
        return 1
    else:
        print()
        bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.game.name")))
        bmp.opt.save()
        bmp.lang.fprint("launch.exit")
        pygame.quit()
        bmp.lang.fprint("launch.thank_you")
        return 0