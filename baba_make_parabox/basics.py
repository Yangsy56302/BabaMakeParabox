import pygame
import os

JsonObject = None | int | float | str | list["JsonObject"] | dict["str", "JsonObject"]

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

game_data = GameData()