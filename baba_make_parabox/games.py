import os
import copy
import json

import baba_make_parabox.basics as basics
import baba_make_parabox.objects as objects
import baba_make_parabox.levels as levels
import baba_make_parabox.worlds as worlds

import pygame

def play(world: worlds.world) -> None:
    if not basics.arg_error:
        if basics.args.output is not None:
            filename: str = basics.args.output
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
                "=": pygame.K_EQUALS,
                " ": pygame.K_SPACE}
    cooldowns = {v: 0 for v in keybinds.values()}
    default_cooldown = 3
    window.fill("#000000")
    current_level_index = 0
    window.blit(pygame.transform.scale(world.show_level(world.level_list[current_level_index], basics.options["level_display_recursion_depth"]), (720, 720)), (0, 0))
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
        elif keys[keybinds[" "]] and cooldowns[keybinds[" "]] == 0:
            history.append(copy.deepcopy(world))
            winned = world.round(" ")
            cooldowns[keybinds[" "]] = default_cooldown
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
            current_level_index -= 1
            cooldowns[keybinds["-"]] = default_cooldown
            refresh = True
        elif keys[keybinds["="]] and cooldowns[keybinds["="]] == 0:
            current_level_index += 1
            cooldowns[keybinds["="]] = default_cooldown
            refresh = True
        current_level_index = current_level_index % len(world.level_list) if current_level_index >= 0 else len(world.level_list) - 1
        if refresh:
            window.fill("#000000")
            window.blit(pygame.transform.scale(world.show_level(world.level_list[current_level_index], basics.options["level_display_recursion_depth"]), (720, 720)), (0, 0))
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