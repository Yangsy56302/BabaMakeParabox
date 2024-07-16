import os
import json

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "TRUE"
import pygame

import BabaMakeParabox.basics as basics
import BabaMakeParabox.spaces as spaces
import BabaMakeParabox.objects as objects
import BabaMakeParabox.rules as rules
import BabaMakeParabox.displays as displays
import BabaMakeParabox.worlds as worlds
import BabaMakeParabox.levels as levels
import BabaMakeParabox.levelpacks as levelpacks
import BabaMakeParabox.edits as edits
import BabaMakeParabox.games as games

def main() -> None:
    print("Baba Make Parabox")
    if os.environ.get("PYINSTALLER") == "TRUE":
        pass # just do nothing
    elif not basics.arg_error:
        if basics.args.versions:
            print(f"Version: {basics.versions}")
        if basics.args.test:
            games.test()
            pygame.quit()
            print("Thank you for testing Baba Make Parabox!")
            basics.save_options(basics.options)
            return
        elif basics.args.edit:
            default_new_world_settings = basics.options["default_new_world"]
            size = (default_new_world_settings["width"], default_new_world_settings["height"])
            color = pygame.Color(default_new_world_settings["color"])
            if basics.args.input is not None:
                filename: str = basics.args.input.lstrip()
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
            if basics.args.output is not None:
                filename: str = basics.args.output.lstrip()
                with open(os.path.join("levelpacks", filename + ".json"), "w", encoding="ascii") as file:
                    json.dump(levelpack.to_json(), file, indent=4)
            pygame.quit()
            basics.save_options(basics.options)
            print("Thank you for editing Baba Make Parabox!")
            return
        elif basics.args.input is not None:
            input_filename: str = basics.args.input.lstrip()
            with open(os.path.join("levelpacks", input_filename + ".json"), "r", encoding="ascii") as file:
                levelpack = levelpacks.json_to_levelpack(json.load(file))
                if basics.args.output is not None:
                    output_filename: str = basics.args.output.lstrip()
                    with open(os.path.join("levelpacks", output_filename + ".json"), "w", encoding="ascii") as file:
                        json.dump(levelpack.to_json(), file, indent=4)
                games.play(levelpack)
            pygame.quit()
            basics.save_options(basics.options)
            print("Thank you for playing Baba Make Parabox!")
            return
    else:
        print("Oops, looks like you enter the wrong argument.")
        print("Now the game will set a test world instead.")
        games.test()
        pygame.quit()
        basics.save_options(basics.options)
        print("Thank you for testing Baba Make Parabox!")
        return

__all__ = ["basics", "spaces", "objects", "rules", "worlds", "displays", "levels", "edits", "main"]