import os
import copy
import json

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.worlds as worlds
import baba_make_parabox.displays as displays
import baba_make_parabox.levels as levels
import baba_make_parabox.levelpacks as levelpacks

import pygame

def play(levelpack: levelpacks.levelpack) -> None:
    if not basics.arg_error:
        if basics.args.output is not None:
            filename: str = basics.args.output
            filename = filename.lstrip()
            with open(os.path.join("levelpacks", filename + ".json"), "w", encoding="ascii") as file:
                json.dump(levelpack.to_json(), file, indent=4)
    print("Levelpack's Global Rule List:")
    for rule in levelpack.rule_list:
        str_list = []
        for obj_type in rule:
            str_list.append(obj_type.class_name)
        print(" ".join(str_list))
    for level in levelpack.level_list:
        level.update_rules()
        for world in level.world_list:
            world.set_sprite_states(0)
    levelpack_backup = copy.deepcopy(levelpack)
    round_num = 0
    window = pygame.display.set_mode((720, 720))
    pygame.display.set_caption(f"Baba Make Parabox Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("BabaMakeParabox.png"))
    displays.sprites.update()
    milliseconds = 0
    clock = pygame.time.Clock()
    keybinds = {"W": pygame.K_w,
                "A": pygame.K_a,
                "S": pygame.K_s,
                "D": pygame.K_d,
                "Z": pygame.K_z,
                "R": pygame.K_r,
                "\x1B": pygame.K_ESCAPE,
                "-": pygame.K_MINUS,
                "=": pygame.K_EQUALS,
                " ": pygame.K_SPACE}
    keys = {v: False for v in keybinds.values()}
    cooldowns = {v: 0 for v in keybinds.values()}
    window.fill("#000000")
    current_level_name = levelpack.main_level
    current_level = levelpack.get_exist_level(current_level_name)
    current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
    level_info = {"win": False, "selected_level": None, "new_levels": [], "transform_to": []}
    history = [{"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)}]
    window.blit(pygame.transform.scale(current_level.show_world(current_level.world_list[current_world_index], 1), (720, 720)), (0, 0))
    pygame.display.flip()
    while True:
        if milliseconds >= 360000000:
            milliseconds = 0
        frame = (milliseconds // 333) % 3 + 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key in keybinds.values():
                keys[event.key] = True
            elif event.type == pygame.KEYUP and event.key in keybinds.values():
                keys[event.key] = False
        refresh = False
        if keys[keybinds["W"]] and cooldowns[keybinds["W"]] == 0:
            history.append({"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)})
            round_num += 1
            level_info = current_level.round(spaces.W)
            refresh = True
        elif keys[keybinds["S"]] and cooldowns[keybinds["S"]] == 0:
            history.append({"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)})
            round_num += 1
            level_info = current_level.round(spaces.S)
            refresh = True
        elif keys[keybinds["A"]] and cooldowns[keybinds["A"]] == 0:
            history.append({"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)})
            round_num += 1
            level_info = current_level.round(spaces.A)
            refresh = True
        elif keys[keybinds["D"]] and cooldowns[keybinds["D"]] == 0:
            history.append({"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)})
            round_num += 1
            level_info = current_level.round(spaces.D)
            refresh = True
        elif keys[keybinds[" "]] and cooldowns[keybinds[" "]] == 0:
            history.append({"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)})
            round_num += 1
            level_info = current_level.round(spaces.O)
            refresh = True
        elif keys[keybinds["\x1B"]] and cooldowns[keybinds["\x1B"]] == 0:
            history.append({"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)})
            current_level_name = current_level.super_level if current_level.super_level is not None else levelpack.main_level
            current_level = levelpack.get_exist_level(current_level_name)
            current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
            refresh = True
        elif keys[keybinds["Z"]] and cooldowns[keybinds["Z"]] == 0:
            if len(history) > 1:
                data = copy.deepcopy(history.pop())
                current_world_index = data["world_index"]
                current_level_name = data["level_name"]
                levelpack = data["levelpack"]
                current_level = levelpack.get_exist_level(current_level_name)
                round_num -= 1
            else:
                data = copy.deepcopy(history[0])
                current_world_index = data["world_index"]
                current_level_name = data["level_name"]
                levelpack = data["levelpack"]
                current_level = levelpack.get_exist_level(current_level_name)
                round_num = 0
            refresh = True
        elif keys[keybinds["R"]] and cooldowns[keybinds["R"]] == 0:
            levelpack = copy.deepcopy(levelpack_backup)
            current_level_name = levelpack.main_level
            current_level = levelpack.get_exist_level(current_level_name)
            current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
            history = [{"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)}]
            level_info = {"win": False, "selected_level": None, "new_levels": [], "transform_to": []}
            refresh = True
        elif keys[keybinds["-"]] and cooldowns[keybinds["-"]] == 0:
            current_world_index -= 1
        elif keys[keybinds["="]] and cooldowns[keybinds["="]] == 0:
            current_world_index += 1
        for key, value in keys.items():
            if value and cooldowns[key] == 0:
                cooldowns[key] = basics.options.get("input_cooldown", 3)
        if refresh:
            levelpack.level_list.extend(level_info["new_levels"])
            transform_success = False
            if len(level_info["transform_to"]) != 0:
                for level in levelpack.level_list:
                    for world in level.world_list:
                        for level_obj in world.get_levels():
                            if current_level.name == level_obj.name:
                                transform_success = True
                                for obj in level_info["transform_to"]:
                                    obj: objects.Object
                                    obj.pos = level_obj.pos
                                    obj.facing = level_obj.facing
                                    world.new_obj(obj)
                                world.del_obj(level_obj.uuid)
            for level in levelpack.level_list:
                for world in level.world_list:
                    transform_objs = filter(lambda o: isinstance(o, objects.Transform), world.object_list)
                    for transform_obj in transform_objs: # type: ignore
                        transform_obj: objects.Transform
                        if issubclass(transform_obj.from_type, objects.Level):
                            from_level = levelpack.get_exist_level(transform_obj.from_name)
                            if issubclass(transform_obj.to_type, objects.WorldPointer):
                                level.world_list.extend(from_level.world_list)
                                new_obj = transform_obj.to_type(transform_obj.pos, from_level.main_world_name, from_level.main_world_tier, transform_obj.facing)
                                world.del_obj(transform_obj.uuid)
                                world.new_obj(new_obj)
                        elif issubclass(transform_obj.from_type, objects.WorldPointer):
                            from_world = level.get_exist_world(transform_obj.from_name, transform_obj.from_inf_tier)
                            if issubclass(transform_obj.to_type, objects.Level):
                                new_level = levels.level(from_world.name, level.world_list, level.name, transform_obj.from_name, transform_obj.from_inf_tier, level.rule_list)
                                levelpack.set_level(new_level)
                                new_obj = objects.Level(transform_obj.pos, from_world.name, transform_obj.facing)
                                world.del_obj(transform_obj.uuid)
                                world.new_obj(new_obj)
            levelpack.set_level(current_level)
            if level_info["win"]:
                if current_level.name == levelpack.main_level:
                    print("You Won This Levelpack!")
                    return
                else:
                    print("Congratulations!")
                level = levelpack_backup.get_level(current_level.name)
                if level is not None:
                    levelpack.set_level(level)
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level_name = super_level.name if super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
            elif transform_success:
                print("This level has been transformed into something...")
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level_name = super_level.name if super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
            elif level_info["selected_level"] is not None:
                current_level_name = level_info["selected_level"]
                current_level = levelpack.get_exist_level(current_level_name)
                print(f"You have entered a level named \"{current_level.name}\".")
                current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
                round_num = 0
            for level in levelpack.level_list:
                for world in current_level.world_list:
                    world.set_sprite_states(round_num)
            level_info = {"win": False, "selected_level": None, "new_levels": [], "transform_to": []}
        current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
        window.fill("#000000")
        window.blit(pygame.transform.scale(current_level.show_world(current_level.world_list[current_world_index], frame), (720, 720)), (0, 0))
        pygame.display.flip()
        for key in cooldowns:
            if cooldowns[key] > 0:
                cooldowns[key] -= 1
        milliseconds += clock.tick(basics.options.get("fps", 15))

def test() -> None:
    # Superworld
    world_0 = worlds.world("main", (9, 9), color=pygame.Color("#111111"))
    # Rules
    world_0.new_obj(objects.BABA((0, 1)))
    world_0.new_obj(objects.IS((1, 1)))
    world_0.new_obj(objects.YOU((2, 1)))
    world_0.new_obj(objects.WALL((8, 1)))
    world_0.new_obj(objects.IS((8, 2)))
    world_0.new_obj(objects.STOP((8, 3)))
    world_0.new_obj(objects.TEXT((8, 5)))
    world_0.new_obj(objects.IS((8, 6)))
    world_0.new_obj(objects.PUSH((8, 7)))
    world_0.new_obj(objects.FLAG((4, 1)))
    world_0.new_obj(objects.IS((5, 1)))
    # Things
    world_0.new_obj(objects.World((3, 3), name="sub"))
    world_0.new_obj(objects.WIN((2, 4)))
    world_0.new_obj(objects.Flag((4, 6)))
    world_0.new_obj(objects.Baba((1, 7)))
    # Empty spaces
    world_0.new_obj(objects.Keke((6, 1)))
    world_0.new_obj(objects.Keke((6, 2)))
    world_0.new_obj(objects.Keke((1, 3)))
    world_0.new_obj(objects.Keke((2, 3)))
    world_0.new_obj(objects.Keke((4, 3)))
    world_0.new_obj(objects.Keke((5, 3)))
    world_0.new_obj(objects.Keke((6, 3)))
    world_0.new_obj(objects.Keke((1, 4)))
    world_0.new_obj(objects.Keke((6, 4)))
    world_0.new_obj(objects.Keke((2, 5)))
    world_0.new_obj(objects.Keke((6, 5)))
    world_0.new_obj(objects.Keke((1, 6)))
    world_0.new_obj(objects.Keke((2, 6)))
    world_0.new_obj(objects.Keke((5, 6)))
    world_0.new_obj(objects.Keke((6, 6)))
    world_0.new_obj(objects.Keke((2, 7)))
    # Walls
    for x in range(9):
        for y in range(9):
            if len(world_0.get_objs_from_pos((x, y))) == 0:
                world_0.new_obj(objects.Wall((x, y)))
    world_0.del_objs_from_type(objects.Keke)
    # Subworld
    world_1 = worlds.world("sub", (7, 7), color=pygame.Color("#000022"))
    # Rules
    world_1.new_obj(objects.BABA((6, 0)))
    world_1.new_obj(objects.IS((6, 1)))
    world_1.new_obj(objects.YOU((6, 2)))
    world_1.new_obj(objects.WALL((6, 4)))
    world_1.new_obj(objects.IS((6, 5)))
    world_1.new_obj(objects.STOP((6, 6)))
    world_1.new_obj(objects.TEXT((2, 6)))
    world_1.new_obj(objects.IS((3, 6)))
    world_1.new_obj(objects.PUSH((4, 6)))
    # Empty spaces
    world_1.new_obj(objects.Keke((3, 0)))
    world_1.new_obj(objects.Keke((3, 1)))
    world_1.new_obj(objects.Keke((3, 2)))
    world_1.new_obj(objects.Keke((0, 3)))
    world_1.new_obj(objects.Keke((1, 3)))
    world_1.new_obj(objects.Keke((2, 3)))
    world_1.new_obj(objects.Keke((3, 3)))
    world_1.new_obj(objects.Keke((2, 4)))
    world_1.new_obj(objects.Keke((3, 4)))
    # Walls
    for x in range(9):
        for y in range(9):
            if len(world_1.get_objs_from_pos((x, y))) == 0:
                world_1.new_obj(objects.Wall((x, y)))
    world_1.del_objs_from_type(objects.Keke)
    # World
    level = levels.level("Intro 4", [world_0, world_1])
    play(levelpacks.levelpack("Intro 4", [level]))