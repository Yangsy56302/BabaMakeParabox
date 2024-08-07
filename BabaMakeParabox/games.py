from typing import Any, Optional, TypedDict
import random
import copy
import uuid
import os

from BabaMakeParabox import basics, languages, sounds, spaces, objects, displays, worlds, levels, levelpacks

import pygame

class History(TypedDict):
    world_index: int
    level_name: str
    level_info: levels.ReTurnValue
    levelpack: levelpacks.Levelpack

def play(levelpack: levelpacks.Levelpack) -> None:
    for level in levelpack.level_list:
        old_prop_dict: dict[uuid.UUID, list[tuple[type[objects.Text], int]]] = {}
        for world in level.world_list:
            world.set_sprite_states(0)
            for obj in world.object_list:
                old_prop_dict[obj.uuid] = [t for t in obj.properties]
        level.update_rules(old_prop_dict)
    levelpack_backup = copy.deepcopy(levelpack)
    window = pygame.display.set_mode((720, 720), pygame.RESIZABLE)
    display_offset = [0.0, 0.0]
    display_offset_speed = [0.0, 0.0]
    pygame.display.set_caption(f"Baba Make Parabox Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("BabaMakeParabox.png"))
    displays.sprites.update()
    pygame.key.set_repeat()
    pygame.key.stop_text_input()
    clock = pygame.time.Clock()
    keybinds = {pygame.K_w: "W",
                pygame.K_a: "A",
                pygame.K_s: "S",
                pygame.K_d: "D",
                pygame.K_z: "Z",
                pygame.K_r: "R",
                pygame.K_TAB: "TAB",
                pygame.K_ESCAPE: "ESCAPE",
                pygame.K_MINUS: "-",
                pygame.K_EQUALS: "=",
                pygame.K_SPACE: " ",
                pygame.K_F1: "F1"}
    keys = {v: False for v in keybinds.values()}
    window.fill("#000000")
    current_level_name = levelpack.main_level
    current_level: levels.Level = levelpack.get_exist_level(current_level_name)
    current_world_index: int = current_level.world_list.index(current_level.get_exist_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier}))
    current_world: worlds.World = current_level.world_list[current_world_index]
    default_level_info: levels.ReTurnValue = {"win": False, "end": False, "game_push": False, "selected_level": None, "transform_to": None}
    level_info: levels.ReTurnValue = default_level_info.copy()
    level_info_backup: levels.ReTurnValue = default_level_info.copy()
    history: list[History] = [{"world_index": current_world_index, "level_name": current_level_name, "level_info": default_level_info, "levelpack": copy.deepcopy(levelpack)}]
    level_changed = False
    world_changed = False
    round_num = 0
    frame = 1
    wiggle = 1
    freeze_time = -1
    milliseconds = 1000 // basics.options["fps"]
    real_fps = basics.options["fps"]
    show_fps = False
    if basics.options["bgm"]["enabled"] and basics.current_os == basics.windows:
        pygame.mixer.music.load(os.path.join("midi", basics.options["bgm"]["name"]))
        pygame.mixer.music.play(-1)
    game_running = True
    while game_running:
        frame += 1
        if frame >= basics.options["fpw"]:
            frame = 0
            wiggle = wiggle % 3 + 1
        for key in keybinds.values():
            keys[key] = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            if event.type == pygame.KEYDOWN:
                if event.key in keybinds.keys():
                    keys[keybinds[event.key]] = True
        refresh = False
        if freeze_time == -1:
            if keys["W"]:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.turn(spaces.Orient.W)
                if objects.TextYou in current_level.game_properties:
                    display_offset[1] -= window.get_height() / current_world.width
                if objects.TextPush in current_level.game_properties and level_info["game_push"]:
                    display_offset[1] -= window.get_height() / current_world.width
                refresh = True
            elif keys["S"]:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.turn(spaces.Orient.S)
                if objects.TextYou in current_level.game_properties:
                    display_offset[1] += window.get_height() / current_world.width
                if objects.TextPush in current_level.game_properties and level_info["game_push"]:
                    display_offset[1] += window.get_height() / current_world.width
                refresh = True
            elif keys["A"]:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.turn(spaces.Orient.A)
                if objects.TextYou in current_level.game_properties:
                    display_offset[0] -= window.get_width() / current_world.height
                if objects.TextPush in current_level.game_properties and level_info["game_push"]:
                    display_offset[0] -= window.get_width() / current_world.height
                refresh = True
            elif keys["D"]:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.turn(spaces.Orient.D)
                if objects.TextYou in current_level.game_properties:
                    display_offset[0] += window.get_width() / current_world.height
                if objects.TextPush in current_level.game_properties and level_info["game_push"]:
                    display_offset[0] += window.get_width() / current_world.height
                refresh = True
            elif keys[" "]:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                round_num += 1
                level_info = current_level.turn(spaces.NullOrient.O)
                refresh = True
            elif keys["ESCAPE"]:
                history.append({"world_index": current_world_index, "level_name": current_level_name, "level_info": level_info, "levelpack": copy.deepcopy(levelpack)})
                current_level_name = current_level.super_level if current_level.super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier}))
                current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
                current_world = current_level.world_list[current_world_index]
                level_changed = True
                world_changed = True
                refresh = True
            elif keys["Z"]:
                if len(history) > 1:
                    data = copy.deepcopy(history.pop())
                    current_world_index = data["world_index"]
                    current_level_name = data["level_name"]
                    level_info = data["level_info"]
                    levelpack = data["levelpack"]
                    current_level = levelpack.get_exist_level(current_level_name)
                    current_world = current_level.world_list[current_world_index]
                    round_num -= 1
                    refresh = True
                elif len(history) == 1:
                    data = copy.deepcopy(history[0])
                    current_world_index = data["world_index"]
                    current_level_name = data["level_name"]
                    level_info = data["level_info"]
                    levelpack = data["levelpack"]
                    current_level = levelpack.get_exist_level(current_level_name)
                    current_world = current_level.world_list[current_world_index]
                    round_num = 0
                    refresh = True
            elif keys["R"]:
                print(languages.current_language["game.levelpack.restart"])
                sounds.play("restart")
                levelpack = copy.deepcopy(levelpack_backup)
                current_level_name = levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier}))
                current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
                current_world = current_level.world_list[current_world_index]
                history = [{"world_index": current_world_index, "level_name": current_level_name, "level_info": default_level_info, "levelpack": copy.deepcopy(levelpack)}]
                level_info = default_level_info.copy()
                display_offset = [0.0, 0.0]
                display_offset_speed = [0.0, 0.0]
                refresh = True
                level_changed = True
                world_changed = True
            elif keys["TAB"]:
                print(languages.current_language["game.levelpack.rule_list"])
                for rule in levelpack.rule_list:
                    str_list = []
                    for obj_type in rule:
                        str_list.append(obj_type.display_name)
                    print(" ".join(str_list))
                print(languages.current_language["game.world.rule_list"])
                for rule in current_world.rule_list:
                    str_list = []
                    for obj_type in rule:
                        str_list.append(obj_type.display_name)
                    print(" ".join(str_list))
            elif keys["-"]:
                current_world_index -= 1
                current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
                current_world = current_level.world_list[current_world_index]
                world_changed = True
            elif keys["="]:
                current_world_index += 1
                current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
                current_world = current_level.world_list[current_world_index]
                world_changed = True
            offset_used = False
            for prop, prop_negated_count in current_level.game_properties:
                if prop_negated_count % 2 == 1:
                    continue
                if prop == objects.TextStop:
                    wiggle = 1
                elif prop == objects.TextShift:
                    display_offset[0] += window.get_width() / basics.options["fps"]
                elif prop == objects.TextMove:
                    display_offset[1] += window.get_height() / (4 * basics.options["fps"])
                elif prop == objects.TextSink:
                    display_offset_speed[1] += window.get_height() / (16 * basics.options["fps"])
                    offset_used = True
                elif prop == objects.TextFloat:
                    display_offset_speed[1] -= window.get_height() / (64 * basics.options["fps"])
                    offset_used = True
            if not offset_used:
                display_offset_speed[0] = display_offset_speed[0] / 2
                display_offset_speed[1] = display_offset_speed[1] / 2
        else:
            freeze_time -= 1
        if refresh:
            game_is_hot = False
            game_is_melt = False
            game_is_you = False
            game_is_defeat = False
            for prop, prop_negated_count in current_level.game_properties:
                if prop_negated_count % 2 == 1:
                    continue
                if prop == objects.TextWin:
                    sounds.play("win")
                    game_running = False
                elif prop == objects.TextShut:
                    sounds.play("defeat")
                    game_running = False
                elif prop == objects.TextEnd:
                    sounds.play("end")
                    game_running = False
                elif prop == objects.TextDone:
                    sounds.play("done")
                    game_running = False
                elif prop == objects.TextOpen:
                    if basics.current_os == basics.windows:
                        if os.path.exists("BabaMakeParabox.exe"):
                                os.system("start BabaMakeParabox.exe")
                        elif os.path.exists("BabaMakeParabox.py"):
                            os.system("start python BabaMakeParabox.py")
                    elif basics.current_os == basics.linux:
                        os.system("python ./BabaMakeParabox.py &")
                elif prop == objects.TextHot:
                    game_is_hot = True
                elif prop == objects.TextMelt:
                    game_is_melt = True
                elif prop == objects.TextYou:
                    game_is_you = True
                elif prop == objects.TextDefeat:
                    game_is_defeat = True
                elif prop == objects.TextTele:
                    sounds.play("tele")
                    display_offset = [float(random.randrange(window.get_width())), float(random.randrange(window.get_height()))]
            if game_is_hot and game_is_melt:
                sounds.play("melt")
                game_running = False
            if game_is_you and game_is_defeat:
                sounds.play("defeat")
                game_running = False
            for event in current_level.sound_events:
                sounds.play(event)
            for new_level in current_level.created_levels:
                levelpack.set_level(new_level)
            for obj_type in current_level.new_games:
                obj_type: type[objects.BmpObject]
                if basics.current_os == basics.windows:
                    if os.path.exists("SubabaMakeParabox.exe"):
                        os.system(f"start SubabaMakeParabox.exe {obj_type.json_name}")
                    elif os.path.exists("SubabaMakeParabox.py"):
                        os.system(f"start /b python SubabaMakeParabox.py {obj_type.json_name}")
                elif basics.current_os == basics.linux:
                    os.system(f"python ./SubabaMakeParabox.py {obj_type.json_name} &")
            transform_success = False
            if level_info["transform_to"] is not None:
                for level in levelpack.level_list:
                    for world in level.world_list:
                        for level_obj in world.get_levels():
                            if current_level.name == level_obj.level_info["name"]:
                                transform_success = True
                                for obj in level_info["transform_to"]:
                                    obj: objects.BmpObject
                                    obj.pos = level_obj.pos
                                    obj.orient = level_obj.orient
                                    world.new_obj(obj)
                                world.del_obj(level_obj)
            for level in levelpack.level_list:
                for world in level.world_list:
                    transform_objs = world.get_objs_from_type(objects.Transform)
                    for transform_obj in transform_objs:
                        if issubclass(transform_obj.from_type, objects.LevelPointer):
                            from_level = levelpack.get_exist_level(transform_obj.from_name)
                            if issubclass(transform_obj.to_type, objects.WorldPointer):
                                for new_world in from_level.world_list:
                                    level.set_world(new_world)
                                world_obj_info: objects.WorldPointerExtraJson = {"name": from_level.main_world_name, "infinite_tier": from_level.main_world_tier}
                                new_obj = transform_obj.to_type(transform_obj.pos, transform_obj.orient, world_info=world_obj_info)
                                world.del_obj(transform_obj)
                                world.new_obj(new_obj)
                        elif issubclass(transform_obj.from_type, objects.WorldPointer):
                            from_world = level.get_exist_world({"name": transform_obj.from_name, "infinite_tier": transform_obj.from_infinite_tier})
                            if issubclass(transform_obj.to_type, objects.LevelPointer):
                                new_level = levels.Level(from_world.name, level.world_list, level.name, transform_obj.from_name, transform_obj.from_infinite_tier, level.rule_list)
                                levelpack.set_level(new_level)
                                level_obj_info: objects.LevelPointerExtraJson = {"name": from_world.name, "icon": {"name": "empty", "color": from_world.color}}
                                new_obj = objects.Level(transform_obj.pos, orient=transform_obj.orient, level_info=level_obj_info)
                                world.del_obj(transform_obj)
                                world.new_obj(new_obj)
            for level in levelpack.level_list:
                level.repeated_world_to_clone()
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
            elif transform_success and level_info["transform_to"] is not None:
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
            level_info = default_level_info.copy()
        if freeze_time == 0:
            level_changed = True
            world_changed = True
            if level_info_backup["win"]:
                level = copy.deepcopy(levelpack_backup.get_level(current_level.name))
                if level is not None:
                    levelpack.set_level(level)
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level_name = super_level.name if super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier}))
                current_world = current_level.world_list[current_world_index]
            elif level_info_backup["end"]:
                game_running = False
            elif level_info_backup["transform_to"] is not None:
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level_name = super_level.name if super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier}))
                current_world = current_level.world_list[current_world_index]
            elif level_info_backup["selected_level"] is not None:
                current_level_name = level_info_backup["selected_level"]
                current_level = levelpack.get_exist_level(current_level_name)
                current_world_index = current_level.world_list.index(current_level.get_exist_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier}))
                current_world = current_level.world_list[current_world_index]
                round_num = 0
        if level_changed:
            print(languages.current_language["game.level.current.name"], current_level.name, sep="")
            level_changed = False
        if world_changed:
            print(languages.current_language["game.world.current.name"], current_world.name, sep="")
            print(languages.current_language["game.world.current.infinite_tier"], current_world.infinite_tier, sep="")
            world_changed = False
        pygame.mixer.music.set_volume(1.0 if current_level.have_you() else 0.5)
        # world
        window.fill("#000000")
        displays.set_pixel_size(window.get_size())
        world_display_size = (int(min(window.get_size()) * min(1, current_world.width / current_world.height)), int(min(window.get_size()) * min(1, current_world.height / current_world.width)))
        world_display_pos = ((window.get_width() - world_display_size[0]) // 2, (window.get_height() - world_display_size[1]) // 2)
        window.blit(pygame.transform.scale(current_level.show_world(current_world, wiggle), world_display_size), world_display_pos)
        # fps
        real_fps = min(1000 / milliseconds, (real_fps * (basics.options["fps"] - 1) + 1000 / milliseconds) / basics.options["fps"])
        if keys["F1"]:
            show_fps = not show_fps
        if show_fps:
            real_fps_string = str(int(real_fps))
            for i in range(len(real_fps_string)):
                window.blit(displays.sprites.get(f"text_{real_fps_string[i]}", 0, wiggle), (i * displays.sprite_size, 0))
        # game is baba
        game_transform_to = [t[0] for t in current_level.game_properties if issubclass(t[0], objects.Noun) and t[1] % 2 == 0]
        if len(game_transform_to) != 0:
            transparent_black_background = pygame.Surface(window.get_size(), pygame.SRCALPHA)
            transparent_black_background.fill("#00000088")
            window.blit(transparent_black_background, (0, 0))
        game_transform_to = [o.obj_type for o in game_transform_to if o is not None]
        for obj_type in game_transform_to:
            window.blit(pygame.transform.scale(displays.sprites.get(obj_type.sprite_name, 0, wiggle), window.get_size()), (0, 0))
        # offset
        if abs(display_offset_speed[0]) > window.get_width() / basics.options["fps"] * 4:
            symbol = 1 if display_offset_speed[0] > 0 else -1
            display_offset_speed[0] = window.get_width() / basics.options["fps"] * symbol * 4
        if abs(display_offset_speed[1]) > window.get_height() / basics.options["fps"] * 4:
            symbol = 1 if display_offset_speed[1] > 0 else -1
            display_offset_speed[1] = window.get_height() / basics.options["fps"] * symbol * 4
        display_offset[0] += display_offset_speed[0]
        display_offset[1] += display_offset_speed[1]
        display_offset[0] %= float(window.get_width())
        display_offset[1] %= float(window.get_height())
        if display_offset[0] != 0.0 or display_offset[1] != 0.0:
            window_surface = pygame.display.get_surface().copy()
            window.blit(window_surface, [int(display_offset[0]), int(display_offset[1])])
            window.blit(window_surface, [int(display_offset[0] - window.get_width()), int(display_offset[1])])
            window.blit(window_surface, [int(display_offset[0]), int(display_offset[1] - window.get_height())])
            window.blit(window_surface, [int(display_offset[0] - window.get_width()), int(display_offset[1] - window.get_height())])
        pygame.display.flip()
        milliseconds = clock.tick(basics.options["fps"])