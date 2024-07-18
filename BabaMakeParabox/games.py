from typing import Any, Optional
import copy

from BabaMakeParabox import basics
from BabaMakeParabox import languages
from BabaMakeParabox import sounds
from BabaMakeParabox import spaces
from BabaMakeParabox import objects
from BabaMakeParabox import displays
from BabaMakeParabox import levels
from BabaMakeParabox import levelpacks

import pygame

def play(levelpack: levelpacks.levelpack) -> None:
    print(languages.current_language["game.levelpack.rule_list"]) 
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
    window = pygame.display.set_mode((720, 720), pygame.RESIZABLE)
    pygame.display.set_caption(f"Baba Make Parabox Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("BabaMakeParabox.png"))
    displays.sprites.update()
    pygame.key.stop_text_input()
    clock = pygame.time.Clock()
    keybinds = {"W": pygame.K_w,
                "A": pygame.K_a,
                "S": pygame.K_s,
                "D": pygame.K_d,
                "Z": pygame.K_z,
                "R": pygame.K_r,
                "TAB": pygame.K_TAB,
                "ESCAPE": pygame.K_ESCAPE,
                "-": pygame.K_MINUS,
                "=": pygame.K_EQUALS,
                " ": pygame.K_SPACE,
                "F1": pygame.K_F1}
    keys = {v: False for v in keybinds.values()}
    cooldowns = {v: 0 for v in keybinds.values()}
    window.fill("#000000")
    current_level_name = levelpack.main_level
    current_level = levelpack.get_exist_level(current_level_name)
    current_world_index: int = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
    level_info = {"win": False, "end": False, "selected_level": None, "new_levels": [], "transform_to": []}
    level_info_backup = level_info.copy()
    history = [{"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)}]
    level_changed = False
    world_changed = False
    frame = 1
    wiggle = 1
    freeze_time = -1
    milliseconds = 1000 // basics.options["fps"]
    while True:
        frame += 1
        if frame >= basics.options["fpw"]:
            frame = 0
            wiggle = wiggle % 3 + 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key in keybinds.values():
                keys[event.key] = True
            elif event.type == pygame.KEYUP and event.key in keybinds.values():
                keys[event.key] = False
        refresh = False
        if freeze_time == -1:
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
            elif keys[keybinds["ESCAPE"]] and cooldowns[keybinds["ESCAPE"]] == 0:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)})
                current_level_name = current_level.super_level if current_level.super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
                level_changed = True
                world_changed = True
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
                print(languages.current_language["game.levelpack.restart"])
                sounds.play("restart")
                levelpack = copy.deepcopy(levelpack_backup)
                current_level_name = levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
                history = [{"world_index": current_world_index, "level_name": current_level_name, "levelpack": copy.deepcopy(levelpack)}]
                level_info = {"win": False, "end": False, "selected_level": None, "new_levels": [], "transform_to": []}
                refresh = True
                level_changed = True
                world_changed = True
            elif keys[keybinds["TAB"]] and cooldowns[keybinds["TAB"]] == 0:
                print(languages.current_language["game.levelpack.rule_list"])
                for rule in levelpack.rule_list:
                    str_list = []
                    for obj_type in rule:
                        str_list.append(obj_type.class_name)
                    print(" ".join(str_list))
                print(languages.current_language["game.world.rule_list"])
                for rule in current_level.world_list[current_world_index].rule_list:
                    str_list = []
                    for obj_type in rule:
                        str_list.append(obj_type.class_name)
                    print(" ".join(str_list))
            elif keys[keybinds["-"]] and cooldowns[keybinds["-"]] == 0:
                current_world_index -= 1
                world_changed = True
            elif keys[keybinds["="]] and cooldowns[keybinds["="]] == 0:
                current_world_index += 1
                world_changed = True
        else:
            freeze_time -= 1
        for key, value in keys.items():
            if value and cooldowns[key] == 0:
                cooldowns[key] = basics.options["input_cooldown"]
        if refresh:
            for event in current_level.sound_events:
                sounds.play(event)
            for new_level in level_info["new_levels"]:
                levelpack.set_level(new_level)
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
                                for new_world in from_level.world_list:
                                    level.set_world(new_world)
                                new_obj = transform_obj.to_type(transform_obj.pos, from_level.main_world_name, from_level.main_world_tier, transform_obj.facing)
                                world.del_obj(transform_obj.uuid)
                                world.new_obj(new_obj)
                        elif issubclass(transform_obj.from_type, objects.WorldPointer):
                            from_world = level.get_exist_world(transform_obj.from_name, transform_obj.from_inf_tier)
                            if issubclass(transform_obj.to_type, objects.Level):
                                new_level = levels.level(from_world.name, level.world_list, level.name, transform_obj.from_name, transform_obj.from_inf_tier, level.rule_list)
                                levelpack.set_level(new_level)
                                new_obj = objects.Level(transform_obj.pos, from_world.name, icon_color=from_world.color, facing=transform_obj.facing)
                                world.del_obj(transform_obj.uuid)
                                world.new_obj(new_obj)
            levelpack.set_level(current_level)
            if level_info["win"]:
                print(languages.current_language["game.level.win"])
                if freeze_time == -1:
                    level_info_backup = copy.deepcopy(level_info)
                    freeze_time = basics.options["fps"]
            elif level_info["end"]:
                print(languages.current_language["game.levelpack.end"])
                if freeze_time == -1:
                    level_info_backup = copy.deepcopy(level_info)
                    freeze_time = basics.options["fps"]
            elif transform_success and len(level_info["transform_to"]) != 0:
                print(languages.current_language["game.level.transform"])
                if freeze_time == -1:
                    level_info_backup = copy.deepcopy(level_info)
                    freeze_time = basics.options["fps"]
            elif level_info["selected_level"] is not None:
                print(languages.current_language["game.level.enter"])
                if freeze_time == -1:
                    level_info_backup = copy.deepcopy(level_info)
                    freeze_time = basics.options["fps"]
            for level in levelpack.level_list:
                for world in current_level.world_list:
                    world.object_list = list(filter(lambda o: not isinstance(o, objects.Empty), world.object_list))
                    world.set_sprite_states(round_num)
            level_info = {"win": False, "end": False, "selected_level": None, "new_levels": [], "transform_to": []}
        if freeze_time == 0:
            level_changed = True
            world_changed = True
            if level_info_backup["win"]:
                level = levelpack_backup.get_level(current_level.name)
                if level is not None:
                    levelpack.set_level(level)
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level_name = super_level.name if super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
            elif level_info_backup["end"]:
                return
            elif len(level_info_backup["transform_to"]) != 0:
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level_name = super_level.name if super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
            elif level_info_backup["selected_level"] is not None:
                current_level_name = level_info_backup["selected_level"]
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world(current_level.main_world_name, current_level.main_world_tier))
                round_num = 0
        current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
        if level_changed:
            print(languages.current_language["game.level.current.name"], current_level.name, sep="")
            level_changed = False
        if world_changed:
            print(languages.current_language["game.world.current.name"], current_level.world_list[current_world_index].name, sep="")
            print(languages.current_language["game.world.current.inf_tier"], current_level.world_list[current_world_index].inf_tier, sep="")
            world_changed = False
        window.fill("#000000")
        displays.set_pixel_size(window.get_size())
        window.blit(pygame.transform.scale(current_level.show_world(current_level.world_list[current_world_index], wiggle), (window.get_width(), window.get_height())), (0, 0))
        real_fps = str(1000 // milliseconds)
        if keys[keybinds["F1"]]:
            for i in range(len(real_fps)):
                window.blit(displays.sprites.get(f"text_{real_fps[i]}", 0, wiggle), (i * displays.sprite_size, 0))
        pygame.display.flip()
        for key in cooldowns:
            if cooldowns[key] > 0:
                cooldowns[key] -= 1
        milliseconds = clock.tick(basics.options["fps"])