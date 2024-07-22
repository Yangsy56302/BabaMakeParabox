import os
import json
import copy

import pygame

pygame.init()

versions = "3.12"

default_options = {
    "lang": "id_FK",
    "fps": 30,
    "fpw": 5,
    "input_cooldown": 4,
    "world_display_recursion_depth": 3,
    "compressed_json_output": True,
    "default_new_world": {
        "width": 9,
        "height": 9,
        "color": 0x000000
    },
    "object_type_shortcuts": ["Baba", "Wall", "Rock", "Flag", "Skull", "WORLD", "LEVEL", "IS", "YOU", "WIN"],
    "bgm": {
        "enabled": False,
        "name": "rush_baba.mid"
    }
}

os.makedirs("levelpacks", exist_ok=True)
options_filename = "options.json"
options = copy.deepcopy(default_options)
if os.path.exists(options_filename):
    with open(options_filename, "r", encoding="utf-8") as file:
        options = json.load(file)
        updated_options = copy.deepcopy(default_options)
        updated_options.update(options)
        options = copy.deepcopy(updated_options)
else:
    with open(options_filename, "w", encoding="utf-8") as file:
        options = default_options
        json.dump(default_options, file)

def save_options(new_options) -> None:
    file = open(options_filename, "w", encoding="utf-8")
    json.dump(new_options, file, indent=None if options["compressed_json_output"] else 4)
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