import pygame
import os
import sys
import json
import argparse

pygame.init()

versions = "2.12"

BasicJsonElement = None | int | float | str
JsonElement = list[BasicJsonElement] | list["JsonElement"] | dict[str, BasicJsonElement] | dict[str, "JsonElement"]
JsonObject = dict[str, JsonElement]

os.makedirs("levelpacks", exist_ok=True)
options_filename = "options.json"
try:
    file = open(options_filename, "r", encoding="ascii")
    options = json.load(file)
    file.close()
except OSError as e:
    file = open(options_filename, "w", encoding="ascii")
    options = {"fps": 15, "input_cooldown": 3, "world_display_recursion_depth": 2}
    json.dump(options, file, indent=4)
    file.close()
except json.JSONDecodeError as e:
    file.close()
    file = open(options_filename, "w", encoding="ascii")
    options = {"fps": 15, "input_cooldown": 3, "world_display_recursion_depth": 2}
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

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(argument=None, message=message)

parser = ArgumentParser(exit_on_error=False,
                        prog="BabaMakeParabox",
                        description="The information of running a fan-made sokoban-like metagame by Yangsy56302 in terminal",
                        epilog="Thank you argparse")
parser.add_argument("-v", "--versions", dest="versions", action="store_true", help="show the game's version")
play_or_edit_group = parser.add_mutually_exclusive_group()
play_group = parser.add_argument_group()
input_group = play_group.add_mutually_exclusive_group()
input_group.add_argument("-i", "--input", dest="input", type=str, metavar="filename", help="input levelpack from json file at ./levelpacks")
input_group.add_argument("-t", "--test", dest="test", action="store_true", default=False, help="play the test levelpack")
play_group.add_argument("-o", "--output", dest="output", type=str, metavar="filename", help="output levelpack to json file at ./levelpacks")
play_or_edit_group.add_argument("-e", "--edit", dest="edit", action="store_true", default=False, help="open in editor mode")
parser.add_argument("bp_1", type=str, default="808", help="bypass pyinstaller, do not use * 1")
parser.add_argument("bp_2", type=str, default="388", help="bypass pyinstaller, do not use * 2")
argv = sys.argv[1:]
argv.extend(["808", "388"])
arg_error = False
try:
    args = parser.parse_args(argv)
except Exception:
    arg_error = True