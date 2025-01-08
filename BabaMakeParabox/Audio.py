import os

import pygame

sounds: dict[str, pygame.mixer.Sound] = {}

for name in [n for n in os.listdir("sounds") if n.endswith(".ogg")]:
    sounds[name[:-4]] = pygame.mixer.Sound(os.path.join("sounds", name))

def play(name: str) -> None:
    sounds[name].play()