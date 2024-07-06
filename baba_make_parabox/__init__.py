import os
import sys
import copy

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.levels as levels
import baba_make_parabox.displays as displays
import baba_make_parabox.worlds as worlds

import pygame

def main(world: worlds.world) -> None:
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
    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
        keys = pygame.key.get_pressed()
        refresh = False
        if keys[keybinds["W"]] and cooldowns[keybinds["W"]] == 0:
            history.append(copy.deepcopy(world))
            world.round("W")
            cooldowns[keybinds["W"]] = default_cooldown
            refresh = True
        elif keys[keybinds["S"]] and cooldowns[keybinds["S"]] == 0:
            history.append(copy.deepcopy(world))
            world.round("S")
            cooldowns[keybinds["S"]] = default_cooldown
            refresh = True
        elif keys[keybinds["A"]] and cooldowns[keybinds["A"]] == 0:
            history.append(copy.deepcopy(world))
            world.round("A")
            cooldowns[keybinds["A"]] = default_cooldown
            refresh = True
        elif keys[keybinds["D"]] and cooldowns[keybinds["D"]] == 0:
            history.append(copy.deepcopy(world))
            world.round("D")
            cooldowns[keybinds["D"]] = default_cooldown
            refresh = True
        elif keys[keybinds["_"]] and cooldowns[keybinds["_"]] == 0:
            history.append(copy.deepcopy(world))
            world.round("_")
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
        clock.tick(15)
    pygame.quit()

def test() -> None:
    level_0 = levels.level("0", 0, (7, 7))
    level_0.new_obj(objects.Baba((1, 1), "W"))
    level_0.new_obj(objects.Wall((1, 3), "W"))
    level_0.new_obj(objects.Wall((3, 1), "W"))
    level_0.new_obj(objects.Level((3, 3), "W", name="0", inf_tier=0))
    level_0.new_obj(objects.Clone((3, 5), "W", name="0", inf_tier=0))
    level_0.new_obj(objects.WALL((5, 2), "W"))
    level_0.new_obj(objects.IS((5, 3), "W"))
    level_0.new_obj(objects.STOP((5, 4), "W"))
    level_0_pos_1 = levels.level("0", 1, (3, 3))
    level_0_neg_1 = levels.level("0", -1, (3, 3))
    level_1 = levels.level("test", -1, (7, 7))
    level_1.new_obj(objects.Level((1, 3), "W", name="0", inf_tier=-1))
    level_1.new_obj(objects.Level((3, 3), "W", name="0", inf_tier=0))
    level_1.new_obj(objects.Level((5, 3), "W", name="0", inf_tier=1))
    world = worlds.world(level_0, level_0_pos_1, level_0_neg_1, level_1,
                         rule_list=[(objects.BABA, objects.IS, objects.YOU),
                                    (objects.TEXT, objects.IS, objects.PUSH),
                                    (objects.LEVEL, objects.IS, objects.PUSH),
                                    (objects.CLONE, objects.IS, objects.PUSH)])
    main(world)

if __name__ == "__main__" or "--debug" in sys.argv or "-d" in sys.argv:
    test()
    print("Thank you for playing Baba Make Parabox!")

__all__ = ["basics", "spaces", "objects", "rules", "levels", "displays", "worlds"]