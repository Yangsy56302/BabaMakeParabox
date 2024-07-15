import pygame
import os
import sys
import json
import argparse

pygame.init()

versions = "2.51"

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
    options = {}
    json.dump(options, file, indent=4)
    file.close()
except json.JSONDecodeError as e:
    file.close()
    file = open(options_filename, "w", encoding="ascii")
    options = {}
    json.dump(options, file, indent=4)
    file.close()

def save_options(new_options) -> None:
    file = open(options_filename, "w", encoding="ascii")
    json.dump(new_options, file, indent=4)
    file.close()

def remove_same_elements[T](a_list: list[T]) -> list[T]:
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
parser.add_argument("-v", "--versions", dest="versions", action="store_true", default=False, help="show the game's version")
parser.add_argument("-i", "--input", dest="input", type=str, default=None, metavar="filename", help="input or create new levelpack from json file at ./levelpacks")
parser.add_argument("-t", "--test", dest="test", action="store_true", default=False, help="play the test levelpack")
parser.add_argument("-o", "--output", dest="output", type=str, default=None, metavar="filename", help="output levelpack to json file at ./levelpacks")
parser.add_argument("-e", "--edit", dest="edit", action="store_true", default=False, help="open levelpack in editor mode")
parser.add_argument("bp_1", type=str, default="808", help="bypass pyinstaller, do not use * 1")
parser.add_argument("bp_2", type=str, default="388", help="bypass pyinstaller, do not use * 2")
argv = sys.argv[1:]
argv.extend(["808", "388"])
arg_error = False
try:
    args = parser.parse_args(argv)
except Exception:
    arg_error = True