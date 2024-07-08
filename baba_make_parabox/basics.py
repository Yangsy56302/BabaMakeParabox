import pygame
import os
import sys
import json
import argparse

JsonObject = None | int | float | str | list["JsonObject"] | dict["str", "JsonObject"]

os.makedirs("worlds", exist_ok=True)
options_filename = "options.json"
try:
    file = open(options_filename, "r", encoding="ascii")
    options = json.load(file)
    file.close()
except OSError as e:
    file = open(options_filename, "w", encoding="ascii")
    options = {"fps": 15, "input_cooldown": 3, "level_display_recursion_depth": 2}
    json.dump(options, file, indent=4)
    file.close()
except json.JSONDecodeError as e:
    file.close()
    file = open(options_filename, "w", encoding="ascii")
    options = {"fps": 15, "input_cooldown": 3, "level_display_recursion_depth": 2}
    json.dump(options, file, indent=4)
    file.close()

def remove_same_elements(a_list: list) -> list:
    e_list = list(enumerate(a_list))
    r_list = []
    for i, ie in e_list:
        for j, je in e_list[i + 1:]:
            if ie == je and j not in r_list:
                r_list.append(j)
    o_list = map(lambda e: e[1], filter(lambda e: e[0] not in r_list, e_list))
    return list(o_list)

class GameData(object):
    class_name: str = "GameData"
    sprites: dict[str, pygame.Surface]
    def __init__(self) -> None:
        self.sprites = {}
        path = os.path.abspath(".")
        sprites_path = os.path.join(path, "sprites")
        for filename in os.listdir(sprites_path):
            self.sprites[os.path.splitext(filename)[0]] = pygame.image.load(os.path.join(sprites_path, filename))

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(argument=None, message=message)

parser = ArgumentParser(exit_on_error=False,
                        prog="BabaMakeParabox",
                        description="The information of running a fan-made sokoban-like metagame by Yangsy56302 in terminal",
                        epilog="Thanks argparse")
parser.add_argument("-v", "--versions", dest="versions", action="store_true", help="show the game's version")
play_or_edit_group = parser.add_mutually_exclusive_group()
play_group = parser.add_argument_group()
input_group = play_group.add_mutually_exclusive_group()
input_group.add_argument("-i", "--input", dest="input", action="append", type=str, metavar="filename", help="input worlds from json file at ./worlds")
input_group.add_argument("-t", "--test", dest="test", action="store_true", default=False, help="play the test world")
input_group.add_argument("-c", "--code", dest="code", action="store_true", default=False, help="play the world that you write in code")
play_group.add_argument("-o", "--output", dest="output", type=str, metavar="filename", help="output the last world to json file at ./worlds")
play_or_edit_group.add_argument("-e", "--edit", dest="edit", type=str, metavar="filename", help="open, edit and save the world from json file if exists, otherwise create new, edit and save")
parser.add_argument("bp_1", type=str, default="808", help="bypass pyinstaller, do not use * 1")
parser.add_argument("bp_2", type=str, default="388", help="bypass pyinstaller, do not use * 2")
argv = sys.argv[1:]
argv.extend(["808", "388"])
arg_error = False
try:
    args = parser.parse_args(argv)
except Exception:
    arg_error = True

game_data = GameData()