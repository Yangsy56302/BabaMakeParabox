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

def main(args: dict[str, Any]) -> None:
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
                if os.path.isfile(filename):
                    with open(filename, "r", encoding="ascii") as file:
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
                with open(filename, "w", encoding="ascii") as file:
                    json.dump(levelpack.to_json(), file, indent=None if basics.options["compressed_json_output"] else 4)
            pygame.quit()
            basics.save_options(basics.options)
            print(languages.current_language["game.thank_you"])
            return
        elif args.get("play", False):
            input_filename: str = args["input"]
            with open(input_filename, "r", encoding="ascii") as file:
                levelpack = levelpacks.json_to_levelpack(json.load(file))
                games.play(levelpack)
            pygame.quit()
            basics.save_options(basics.options)
            print(languages.current_language["game.thank_you"])
            return

__all__ = ["basics", "languages", "spaces", "objects", "rules", "worlds", "displays", "levels", "edits", "games", "main"]