import os
import sys
import copy
import argparse
import json

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "TRUE"

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.levels as levels
import baba_make_parabox.displays as displays
import baba_make_parabox.worlds as worlds

import pygame

__all__ = ["basics", "spaces", "objects", "rules", "levels", "displays", "worlds", "play", "test", "stop"]

print("Baba Make Parabox")
versions = "1.31"

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(argument=None, message="Oops")

parser = ArgumentParser(exit_on_error=False,
                        prog="BabaMakeParabox",
                        description="The information of running a fan-made sokoban-like metagame by Yangsy56302 in terminal",
                        epilog="Thanks argparse")
parser.add_argument("-v", "--versions", dest="versions", action="store_true", help="show the game's version")
input_group = parser.add_mutually_exclusive_group()
input_group.add_argument("-i", "--input", dest="input", action="append", type=str, metavar="filename", help="input worlds from json file at ./worlds")
input_group.add_argument("-t", "--test", dest="test", action="store_true", default=False, help="play the test world")
input_group.add_argument("-c", "--code", dest="code", action="store_true", default=False, help="play the world that you write in code")
parser.add_argument("-o", "--output", dest="output", type=str, metavar="filename", help="output the last world to json file at ./worlds")
parser.add_argument("bp_1", type=str, default="808", help="bypass pyinstaller, do not use * 1")
parser.add_argument("bp_2", type=str, default="388", help="bypass pyinstaller, do not use * 2")
argv = sys.argv[1:]
argv.extend(["808", "388"])
arg_error = False
try:
    args = parser.parse_args(argv)
except Exception:
    arg_error = True

def stop() -> None:
    pygame.quit()
    print("Thank you for playing Baba Make Parabox!")

def play(world: worlds.world) -> None:
    if not arg_error:
        if args.output is not None:
            filename: str = args.output
            filename = filename.lstrip()
            with open(os.path.join("worlds", filename + ".json"), "w", encoding="ascii") as file:
                json.dump(world.to_json(), file, indent=4)
    print("Global Rule List:")
    for rule in world.rule_list:
        str_list = []
        for obj_type in rule:
            str_list.append(obj_type.class_name)
        print(" ".join(str_list))
    for level in world.level_list:
        level.update_rules()
    history = [copy.deepcopy(world)]
    window = pygame.display.set_mode((720, 720))
    clock = pygame.time.Clock()
    keybinds = {"W": pygame.K_w,
                "A": pygame.K_a,
                "S": pygame.K_s,
                "D": pygame.K_d,
                "Z": pygame.K_z,
                "R": pygame.K_r,
                "-": pygame.K_MINUS,
                "+": pygame.K_EQUALS,
                "_": pygame.K_SPACE}
    cooldowns = {value: 0 for value in keybinds.values()}
    default_cooldown = 3
    window.fill("#112244")
    current_level = 0
    window.blit(pygame.transform.scale(world.show_level(world.level_list[current_level], 2), (720, 720)), (0, 0))
    pygame.display.flip()
    winned = False
    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
        keys = pygame.key.get_pressed()
        refresh = False
        if keys[keybinds["W"]] and cooldowns[keybinds["W"]] == 0:
            history.append(copy.deepcopy(world))
            winned = world.round("W")
            cooldowns[keybinds["W"]] = default_cooldown
            refresh = True
        elif keys[keybinds["S"]] and cooldowns[keybinds["S"]] == 0:
            history.append(copy.deepcopy(world))
            winned = world.round("S")
            cooldowns[keybinds["S"]] = default_cooldown
            refresh = True
        elif keys[keybinds["A"]] and cooldowns[keybinds["A"]] == 0:
            history.append(copy.deepcopy(world))
            winned = world.round("A")
            cooldowns[keybinds["A"]] = default_cooldown
            refresh = True
        elif keys[keybinds["D"]] and cooldowns[keybinds["D"]] == 0:
            history.append(copy.deepcopy(world))
            winned = world.round("D")
            cooldowns[keybinds["D"]] = default_cooldown
            refresh = True
        elif keys[keybinds["_"]] and cooldowns[keybinds["_"]] == 0:
            history.append(copy.deepcopy(world))
            winned = world.round("_")
            cooldowns[keybinds["_"]] = default_cooldown
            refresh = True
        elif keys[keybinds["Z"]] and cooldowns[keybinds["Z"]] == 0:
            if len(history) > 1:
                world = copy.deepcopy(history.pop())
            else:
                world = copy.deepcopy(history[0])
            cooldowns[keybinds["Z"]] = default_cooldown
            refresh = True
        elif keys[keybinds["R"]] and cooldowns[keybinds["R"]] == 0:
            world = copy.deepcopy(history[0])
            cooldowns[keybinds["R"]] = default_cooldown
            refresh = True
        elif keys[keybinds["-"]] and cooldowns[keybinds["-"]] == 0:
            current_level -= 1
            cooldowns[keybinds["-"]] = default_cooldown
            refresh = True
        elif keys[keybinds["+"]] and cooldowns[keybinds["+"]] == 0:
            current_level += 1
            cooldowns[keybinds["+"]] = default_cooldown
            refresh = True
        current_level = current_level % len(world.level_list) if current_level >= 0 else len(world.level_list) - 1
        if refresh:
            window.fill("#112244")
            window.blit(pygame.transform.scale(world.show_level(world.level_list[current_level], 2), (720, 720)), (0, 0))
            pygame.display.flip()
        for key in cooldowns:
            if cooldowns[key] > 0:
                cooldowns[key] -= 1
        if len(history) > 100:
            history = history[1:]
        if winned:
            print("Congratulations!")
            print("You Win!")
            game_running = False
        clock.tick(15)

def test() -> None:
    # Superlevel
    level_0 = levels.level("main", (9, 9), color=pygame.Color("#888888"))
    # Rules
    level_0.new_obj(objects.BABA((0, 1)))
    level_0.new_obj(objects.IS((1, 1)))
    level_0.new_obj(objects.YOU((2, 1)))
    level_0.new_obj(objects.WALL((8, 1)))
    level_0.new_obj(objects.IS((8, 2)))
    level_0.new_obj(objects.STOP((8, 3)))
    level_0.new_obj(objects.TEXT((8, 5)))
    level_0.new_obj(objects.IS((8, 6)))
    level_0.new_obj(objects.PUSH((8, 7)))
    level_0.new_obj(objects.FLAG((4, 1)))
    level_0.new_obj(objects.IS((5, 1)))
    # Things
    level_0.new_obj(objects.Level((3, 3), name="sub"))
    level_0.new_obj(objects.WIN((2, 4)))
    level_0.new_obj(objects.Flag((4, 6)))
    level_0.new_obj(objects.Baba((1, 7)))
    # Empty spaces
    level_0.new_obj(objects.Keke((6, 1)))
    level_0.new_obj(objects.Keke((6, 2)))
    level_0.new_obj(objects.Keke((1, 3)))
    level_0.new_obj(objects.Keke((2, 3)))
    level_0.new_obj(objects.Keke((4, 3)))
    level_0.new_obj(objects.Keke((5, 3)))
    level_0.new_obj(objects.Keke((6, 3)))
    level_0.new_obj(objects.Keke((1, 4)))
    level_0.new_obj(objects.Keke((6, 4)))
    level_0.new_obj(objects.Keke((2, 5)))
    level_0.new_obj(objects.Keke((6, 5)))
    level_0.new_obj(objects.Keke((1, 6)))
    level_0.new_obj(objects.Keke((2, 6)))
    level_0.new_obj(objects.Keke((5, 6)))
    level_0.new_obj(objects.Keke((6, 6)))
    level_0.new_obj(objects.Keke((2, 7)))
    # Walls
    for x in range(9):
        for y in range(9):
            if len(level_0.get_objs_from_pos((x, y))) == 0:
                level_0.new_obj(objects.Wall((x, y)))
    level_0.del_objs_from_type(objects.Keke)
    # Sublevel
    level_1 = levels.level("sub", (7, 7), color=pygame.Color("#004488"))
    # Rules
    level_1.new_obj(objects.BABA((6, 0)))
    level_1.new_obj(objects.IS((6, 1)))
    level_1.new_obj(objects.YOU((6, 2)))
    level_1.new_obj(objects.WALL((6, 4)))
    level_1.new_obj(objects.IS((6, 5)))
    level_1.new_obj(objects.STOP((6, 6)))
    level_1.new_obj(objects.TEXT((2, 6)))
    level_1.new_obj(objects.IS((3, 6)))
    level_1.new_obj(objects.PUSH((4, 6)))
    # Empty spaces
    level_1.new_obj(objects.Keke((3, 0)))
    level_1.new_obj(objects.Keke((3, 1)))
    level_1.new_obj(objects.Keke((3, 2)))
    level_1.new_obj(objects.Keke((0, 3)))
    level_1.new_obj(objects.Keke((1, 3)))
    level_1.new_obj(objects.Keke((2, 3)))
    level_1.new_obj(objects.Keke((3, 3)))
    level_1.new_obj(objects.Keke((2, 4)))
    level_1.new_obj(objects.Keke((3, 4)))
    # Walls
    for x in range(9):
        for y in range(9):
            if len(level_1.get_objs_from_pos((x, y))) == 0:
                level_1.new_obj(objects.Wall((x, y)))
    level_1.del_objs_from_type(objects.Keke)
    # World
    world = worlds.world("Intro 4", [level_0, level_1])
    play(world)

os.makedirs("worlds", exist_ok=True)

if not arg_error:
    if args.versions:
        print(f"Version: {versions}")
    if args.test:
        test()
        stop()
    elif args.code:
        pass
    elif args.input != "None":
        for filename in args.input:
            filename: str
            filename = filename.lstrip()
            with open(os.path.join("worlds", filename + ".json"), "r", encoding="ascii") as file:
                play(worlds.json_to_world(json.load(file)))
        stop()
else:
    print("Oops, looks like you enter the wrong argument.")
    print("Now the game will set a test world instead.")
    test()
    stop()