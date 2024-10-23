import os
import json

import pygame

from BabaMakeParabox import basics, languages, spaces, colors, objects, rules, displays, worlds, levels, levelpacks, edits, games, subgames                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              # monika was there ;)

def play(input_filename: str, output_filename: str) -> None:
    with open(os.path.join("levelpacks", input_filename + ".json"), "r", encoding="utf-8") as file:
        levelpack = levelpacks.json_to_levelpack(json.load(file))
    levelpack = games.play(levelpack)
    if output_filename != "":
        with open(os.path.join("levelpacks", output_filename + ".json"), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, indent=None if basics.options["compressed_json_output"] else 4, separators=(",", ":") if basics.options["compressed_json_output"] else (", ", ": "))

def edit(input_filename: str, output_filename: str) -> None:
    default_new_world_settings = basics.options["default_new_world"]
    size = (default_new_world_settings["width"], default_new_world_settings["height"])
    color = default_new_world_settings["color"]
    if input_filename != "":
        if os.path.isfile(os.path.join("levelpacks", input_filename + ".json")):
            with open(os.path.join("levelpacks", input_filename + ".json"), "r", encoding="utf-8") as file:
                levelpack = levelpacks.json_to_levelpack(json.load(file))
        else:
            world = worlds.World(input_filename, size, color=color)
            level = levels.Level(input_filename, [world])
            levelpack = levelpacks.Levelpack(input_filename, [level])
    else:
        world = worlds.World("main", size, color=color)
        level = levels.Level("main", [world])
        levelpack = levelpacks.Levelpack("main", [level])
    levelpack = edits.levelpack_editor(levelpack)
    if output_filename != "":
        with open(os.path.join("levelpacks", output_filename + ".json"), "w", encoding="utf-8") as file:
            json.dump(levelpack.to_json(), file, indent=None if basics.options["compressed_json_output"] else 4, separators=(",", ":") if basics.options["compressed_json_output"] else (", ", ": "))

def update(input_filename: str, output_filename: str) -> None:
    with open(os.path.join("levelpacks", input_filename + ".json"), "r", encoding="utf-8") as file:
        levelpack = levelpacks.json_to_levelpack(json.load(file))
    with open(os.path.join("levelpacks", output_filename + ".json"), "w", encoding="utf-8") as file:
        json.dump(levelpack.to_json(), file, indent=None if basics.options["compressed_json_output"] else 4, separators=(",", ":") if basics.options["compressed_json_output"] else (", ", ": "))

def main() -> None:
    if os.environ.get("PYINSTALLER") == "TRUE":
        return
    if basics.options.get("game_is_done"):
        raise games.GameIsDoneError()
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
        while True:
            for n in map(lambda x: x + 1, range(4)):
                print(languages.current_language[f"main.game_mode.{n}"])
            game_mode = input(languages.current_language["input.number"])
            try:
                game_mode = int(game_mode)
            except ValueError:
                print(languages.current_language["warn.value.invalid"].format(val=game_mode, cls="int"))
                continue
            if game_mode == 1:
                print(languages.current_language["main.open.levelpack"])
                input_filename = input(languages.current_language["input.file.name"])
                print(languages.current_language["main.save.levelpack"])
                print(languages.current_language["main.save.levelpack.empty.game"])
                output_filename = input(languages.current_language["input.file.name"])
                print(languages.current_language["game.start"])
                play(input_filename, output_filename)
                break
            elif game_mode == 2:
                print(languages.current_language["main.open.levelpack"])
                print(languages.current_language["main.open.levelpack.empty.editor"])
                input_filename = input(languages.current_language["input.file.name"])
                print(languages.current_language["main.save.levelpack"])
                print(languages.current_language["main.save.levelpack.empty.editor"])
                output_filename = input(languages.current_language["input.file.name"])
                edit(input_filename, output_filename)
                break
            elif game_mode == 3:
                while True:
                    print(languages.current_language["main.change_options.fps"])
                    fps_preset = input(languages.current_language["input.number"])
                    try:
                        fps_preset = int(fps_preset)
                    except ValueError:
                        print(languages.current_language["warn.value.invalid"].format(val=fps_preset, cls="int"))
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
                            print(languages.current_language["warn.value.out_of_range"].format(min=1, max=4, val=fps_preset))
                if input(languages.current_language["main.change_options.json"]) in languages.yes:
                    basics.options.update({"compressed_json_output": False})
                else:
                    basics.options.update({"compressed_json_output": True})
                if input(languages.current_language["main.change_options.bgm"]) in languages.yes:
                    basics.options.update({"bgm": {"enabled": True, "name": "rush_baba.mid"}})
                else:
                    basics.options.update({"bgm": {"enabled": False, "name": "rush_baba.mid"}})
                while True:
                    print(languages.current_language["main.change_options.metatext"])
                    metatext_tier = input(languages.current_language["input.number"])
                    try:
                        metatext_tier = int(metatext_tier)
                    except ValueError:
                        print(languages.current_language["warn.value.invalid"].format(val=metatext_tier, cls="int"))
                    else:
                        if metatext_tier < 0:
                            print(languages.current_language["warn.value.underflow"].format(min=0, val=metatext_tier))
                        elif metatext_tier == 0:
                            basics.options.update({"metatext": {"enabled": False, "tier": 0}})
                            break
                        else:
                            basics.options.update({"metatext": {"enabled": True, "tier": metatext_tier}})
                            break
                print(languages.current_language["main.change_options.done"])
                break
            elif game_mode == 4:
                print(languages.current_language["main.open.levelpack"])
                input_filename = input(languages.current_language["input.file.name"])
                print(languages.current_language["main.save.levelpack"])
                output_filename = input(languages.current_language["input.file.name"])
                update(input_filename, output_filename)
                break
            else:
                print(languages.current_language["warn.value.out_of_range"].format(min=1, max=4, val=game_mode))
    except KeyboardInterrupt:
        print()
        print(languages.current_language["main.keyboard_interrupt"])
        print(languages.current_language["main.keyboard_interrupt.insert"])
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

__all__ = ["basics", "languages", "spaces", "colors", "objects", "rules", "displays", "worlds", "levels", "levelpacks", "edits", "games", "subgames", "main"]