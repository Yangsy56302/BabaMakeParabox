import os
import json

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "TRUE"
import pygame

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.displays as displays
import baba_make_parabox.worlds as worlds
import baba_make_parabox.levels as levels
import baba_make_parabox.levelpacks as levelpacks
import baba_make_parabox.edits as edits
import baba_make_parabox.games as games

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
            default_new_world_settings = basics.options.setdefault("default_new_world", {"width": 9, "height": 9, "color": "#000000"})
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
            filename: str = basics.args.input.lstrip()
            with open(os.path.join("levelpacks", filename + ".json"), "r", encoding="ascii") as file:
                games.play(levelpacks.json_to_levelpack(json.load(file)))
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