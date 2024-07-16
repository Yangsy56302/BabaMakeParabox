from typing import Any
import os
import json

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "TRUE"
import pygame

import BabaMakeParabox.basics as basics
import BabaMakeParabox.languages as languages
import BabaMakeParabox.spaces as spaces
import BabaMakeParabox.objects as objects
import BabaMakeParabox.rules as rules
import BabaMakeParabox.displays as displays
import BabaMakeParabox.worlds as worlds
import BabaMakeParabox.levels as levels
import BabaMakeParabox.levelpacks as levelpacks
import BabaMakeParabox.edits as edits
import BabaMakeParabox.games as games

def logic(args: dict[str, Any]) -> None:
    print(languages.current_language["game.name"])
    if os.environ.get("PYINSTALLER") == "TRUE":
        pass # just do nothing
    else:
        if args.get("edit", False):
            default_new_world_settings = basics.options["default_new_world"]
            size = (default_new_world_settings["width"], default_new_world_settings["height"])
            color = pygame.Color(default_new_world_settings["color"])
            if args.get("input") != "":
                filename: str = args["input"]
                if os.path.isfile(os.path.join("levelpacks", filename + ".json")):
                    with open(os.path.join("levelpacks", filename + ".json"), "r", encoding="ascii") as file:
                        levelpack = levelpacks.json_to_levelpack(json.load(file))
                else:
                    world = worlds.world(filename, size, color=color)
                    level = levels.level(filename, [world])
                    levelpack = levelpacks.levelpack(filename, [level])
            else:
                world = worlds.world("main", size, color=color)
                level = levels.level("main", [world])
                levelpack = levelpacks.levelpack("main", [level])
            levelpack = edits.levelpack_editor(levelpack)
            if args.get("output") != "":
                filename: str = args["output"]
                with open(os.path.join("levelpacks", filename + ".json"), "w", encoding="ascii") as file:
                    json.dump(levelpack.to_json(), file, indent=None if basics.options["compressed_json_output"] else 4)
            return
        elif args.get("play", False):
            filename: str = args["input"]
            with open(os.path.join("levelpacks", filename + ".json"), "r", encoding="ascii") as file:
                levelpack = levelpacks.json_to_levelpack(json.load(file))
                games.play(levelpack)
            return

def main() -> None:
    settings = {}
    if basics.options["lang"] not in languages.language_dict.keys():
        for lang in languages.language_dict.keys():
            print(languages.language_dict[lang]["language.select"])
        lang = input(">>> ")
        languages.set_current_language(lang)
        basics.options["lang"] = lang
    else:
        languages.set_current_language(basics.options["lang"])
    print(languages.current_language["main.welcome"])
    print(languages.current_language["main.change_options"])
    change_options = input(languages.current_language["input.string"]) != ""
    if change_options:
        print(languages.current_language["main.change_options.fps"])
        computer_level = int(input(languages.current_language["input.number"]))
        match computer_level:
            case 1:
                basics.options.update({"fps": 5, "fpw": 1, "input_cooldown": 1, "world_display_recursion_depth": 1, "compressed_json_output": True})
            case 2:
                basics.options.update({"fps": 15, "fpw": 3, "input_cooldown": 2, "world_display_recursion_depth": 2, "compressed_json_output": True})
            case 3:
                basics.options.update({"fps": 30, "fpw": 5, "input_cooldown": 4, "world_display_recursion_depth": 3, "compressed_json_output": True})
            case 4:
                basics.options.update({"fps": 60, "fpw": 10, "input_cooldown": 8, "world_display_recursion_depth": 4, "compressed_json_output": False})
        print(languages.current_language["main.change_options.done"])
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
    print(languages.current_language["game.exit"])
    basics.save_options(basics.options)
    pygame.quit()
    print(languages.current_language["game.thank_you"])

__all__ = ["basics", "languages", "spaces", "objects", "rules", "worlds", "displays", "levels", "edits", "games", "main"]