from typing import Any
import os
import json

import pygame

from BabaMakeParabox import basics, languages, spaces, colors, objects, rules, displays, worlds, levels, levelpacks, edits, games, subgames

def logic(args: dict[str, Any]) -> None:
    print(languages.current_language["game.name"])
    if args.get("edit", False):
        default_new_world_settings = basics.options["default_new_world"]
        size = (default_new_world_settings["width"], default_new_world_settings["height"])
        color = default_new_world_settings["color"]
        if args.get("input") != "":
            filename: str = args["input"]
            if os.path.isfile(os.path.join("levelpacks", filename + ".json")):
                with open(os.path.join("levelpacks", filename + ".json"), "r", encoding="utf-8") as file:
                    levelpack = levelpacks.json_to_levelpack(json.load(file))
            else:
                world = worlds.World(filename, size, color=color)
                level = levels.Level(filename, [world])
                levelpack = levelpacks.Levelpack(filename, [level])
        else:
            world = worlds.World("main", size, color=color)
            level = levels.Level("main", [world])
            levelpack = levelpacks.Levelpack("main", [level])
        levelpack = edits.levelpack_editor(levelpack)
        if args.get("output") != "":
            filename: str = args["output"]
            with open(os.path.join("levelpacks", filename + ".json"), "w", encoding="utf-8") as file:
                json.dump(levelpack.to_json(), file, indent=None if basics.options["compressed_json_output"] else 4, separators=(",", ":") if basics.options["compressed_json_output"] else (", ", ": "))
        return
    elif args.get("play", False):
        filename: str = args["input"]
        with open(os.path.join("levelpacks", filename + ".json"), "r", encoding="utf-8") as file:
            levelpack = levelpacks.json_to_levelpack(json.load(file))
            games.play(levelpack)
        return

def main() -> None:
    if os.environ.get("PYINSTALLER") == "TRUE":
        return
    if basics.options.get("game_is_done"):
        raise games.GameIsDoneError()
    settings = {}
    if basics.options["lang"] not in languages.language_dict.keys():
        for lang in languages.language_dict.keys():
            print(languages.language_dict[lang]["language.select"])
        lang = input(">>> ")
        languages.set_current_language(lang)
        basics.options["lang"] = lang
    else:
        languages.set_current_language(basics.options["lang"])
    try:
        print(languages.current_language["main.welcome"])
        if input(languages.current_language["main.change_options"]) in languages.yes:
            print(languages.current_language["main.change_options.fps"])
            match int(input(languages.current_language["input.number"])):
                case 1:
                    basics.options.update({"fps": 5, "fpw": 1, "world_display_recursion_depth": 1})
                case 2:
                    basics.options.update({"fps": 15, "fpw": 3, "world_display_recursion_depth": 2})
                case 3:
                    basics.options.update({"fps": 30, "fpw": 5, "world_display_recursion_depth": 3})
                case 4:
                    basics.options.update({"fps": 60, "fpw": 10, "world_display_recursion_depth": 4})
            if input(languages.current_language["main.change_options.json"]) in languages.yes:
                basics.options.update({"compressed_json_output": False})
            else:
                basics.options.update({"compressed_json_output": True})
            if input(languages.current_language["main.change_options.bgm"]) in languages.yes:
                basics.options.update({"bgm": {"enabled": True, "name": "rush_baba.mid"}})
            else:
                basics.options.update({"bgm": {"enabled": False, "name": "rush_baba.mid"}})
            print(languages.current_language["main.change_options.metatext"])
            metatext_tier = int(input(languages.current_language["input.number"]))
            if metatext_tier == 0:
                basics.options.update({"metatext": {"enabled": False, "tier": 1}})
            else:
                basics.options.update({"metatext": {"enabled": True, "tier": metatext_tier}})
            print(languages.current_language["main.change_options.done"])
        else:
            print(languages.current_language["main.play_or_edit"])
            play_or_edit = int(input(languages.current_language["input.number"]))
            if play_or_edit == 1:
                settings["play"] = True
                print(languages.current_language["main.open.levelpack"])
                settings["input"] = input(languages.current_language["input.file.name"])
            else:
                settings["edit"] = True
                print(languages.current_language["main.open.levelpack"])
                print(languages.current_language["main.open.levelpack.empty.editor"])
                settings["input"] = input(languages.current_language["input.file.name"])
                print(languages.current_language["main.save.levelpack"])
                print(languages.current_language["main.save.levelpack.empty.editor"])
                settings["output"] = input(languages.current_language["input.file.name"])
            print(languages.current_language["game.start"])
            logic(settings)
    except KeyboardInterrupt:
        print()
        print(languages.current_language["main.keyboard_interrupt"])
        print(languages.current_language["main.exit"])
        basics.save_options(basics.options)
        pygame.quit()
        print(languages.current_language["main.thank_you"])
    except Exception as e:
        print()
        print(languages.current_language["main.exception"])
        print(languages.current_language["main.exception.report"])
        print(languages.current_language["main.exception.record"])
        raise e
    else:
        print()
        print(languages.current_language["main.exit"])
        basics.save_options(basics.options)
        pygame.quit()
        print(languages.current_language["main.thank_you"])

__all__ = ["basics", "languages", "spaces", "colors", "objects", "rules", "worlds", "displays", "levels", "edits", "games", "subgames", "main"]