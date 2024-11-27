from typing import Any, Optional, TypedDict
import random
import copy
import uuid
import os

from BabaMakeParabox import basics, languages, sounds, spaces, objects, displays, worlds, levels, levelpacks

import pygame

class GameIsDoneError(Exception):
    pass

movement_value: dict[str, tuple[str, spaces.PlayerOperation, spaces.Coord]] = {"W": ("S", spaces.Orient.W, (0, -1)), "S": ("W", spaces.Orient.S, (0, 1)), "A": ("D", spaces.Orient.A, (-1, 0)), "D": ("A", spaces.Orient.D, (1, 0)), " ": ("None", spaces.NullOrient.O, (0, 0))}

def play(levelpack: levelpacks.Levelpack) -> levelpacks.Levelpack:
    for level in levelpack.level_list:
        for world in level.world_list:
            world.set_sprite_states(0)
    levelpack_backup = copy.deepcopy(levelpack)
    window = pygame.display.set_mode((720, 720), pygame.RESIZABLE)
    display_offset = [0.0, 0.0]
    display_offset_speed = [0.0, 0.0]
    pygame.display.set_caption(f"Baba Make Parabox Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("bmp.ico.png"))
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
    current_level: levels.Level = levelpack.get_exist_level(levelpack.main_level)
    current_world: worlds.World = current_level.get_exact_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier})
    levelpack_info: levelpacks.ReTurnValue = levelpacks.default_levelpack_info.copy()
    history: dict[str, list[levels.Level]] = {l.name: [l] for l in levelpack_backup.level_list}
    level_changed = False
    world_changed = False
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
            for key, (negkey, op, (dx, dy)) in movement_value.items():
                if keys[key] and not keys.get(negkey, False):
                    history[current_level.name].append(copy.deepcopy(current_level))
                    levelpack_info = levelpack.turn(current_level, op)
                    if current_level.game_properties.has(objects.TextYou):
                        display_offset[0] += dx * window.get_width() / current_world.width
                        display_offset[1] += dy * window.get_height() / current_world.height
                    if current_level.game_properties.has(objects.TextPush) and levelpack_info["game_push"]:
                        display_offset[0] += dx * window.get_width() / current_world.width
                        display_offset[1] += dy * window.get_height() / current_world.height
                    refresh = True
                    break
            if refresh == True:
                pass
            elif keys["ESCAPE"]:
                level = copy.deepcopy(levelpack_backup.get_level(current_level.name))
                if level is not None:
                    levelpack.set_level(level)
                    history[current_level.name].append(copy.deepcopy(current_level))
                current_level.name = current_level.super_level if current_level.super_level is not None else levelpack.main_level
                current_level = levelpack.get_exist_level(current_level.name)
                current_world = current_level.get_exact_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier})
                level_changed = True
                world_changed = True
                refresh = True
            elif keys["Z"]:
                if len(history[current_level.name]) > 1:
                    current_level = copy.deepcopy(history[current_level.name].pop())
                    current_world = current_level.get_world_or_default({"name": current_world.name, "infinite_tier": current_world.infinite_tier}, default=current_level.main_world)
                    refresh = True
                elif len(history[current_level.name]) == 1:
                    current_level = copy.deepcopy(history[current_level.name][0])
                    current_world = current_level.get_world_or_default({"name": current_world.name, "infinite_tier": current_world.infinite_tier}, default=current_level.main_world)
                    refresh = True
            elif keys["R"]:
                print(languages.current_language["game.level.restart"])
                sounds.play("restart")
                current_level = copy.deepcopy(history[current_level.name][0])
                current_world = current_level.get_world_or_default({"name": current_world.name, "infinite_tier": current_world.infinite_tier}, default=current_level.main_world)
                history[current_level.name] = [copy.deepcopy(current_level)]
                world_changed = True
                refresh = True
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
                current_world_index = current_level.world_list.index(current_world)
                current_world_index -= 1
                current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
                current_world = current_level.world_list[current_world_index]
                world_changed = True
            elif keys["="]:
                current_world_index = current_level.world_list.index(current_world)
                current_world_index += 1
                current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
                current_world = current_level.world_list[current_world_index]
                world_changed = True
            # game properties at every tick
            offset_used = False
            if current_level.game_properties.has(objects.TextStop):
                wiggle = 1
            if current_level.game_properties.has(objects.TextShift):
                display_offset[0] += window.get_width() / basics.options["fps"]
            if current_level.game_properties.has(objects.TextMove):
                display_offset[1] += window.get_height() / (4 * basics.options["fps"])
            if current_level.game_properties.has(objects.TextSink):
                display_offset_speed[1] += window.get_height() / (16 * basics.options["fps"])
                offset_used = True
            if current_level.game_properties.has(objects.TextFloat):
                display_offset_speed[1] -= window.get_height() / (64 * basics.options["fps"])
                offset_used = True
            if not offset_used:
                display_offset_speed[0] = display_offset_speed[0] / 2
                display_offset_speed[1] = display_offset_speed[1] / 2
            del offset_used
        else:
            freeze_time -= 1
        if refresh:
            # game properties at update
            if current_level.game_properties.has(objects.TextWin):
                print(languages.current_language["game.win"])
                sounds.play("win")
                game_running = False
            if current_level.game_properties.has(objects.TextShut):
                sounds.play("defeat")
                game_running = False
            if current_level.game_properties.has(objects.TextEnd):
                print(languages.current_language["game.end"])
                sounds.play("end")
                basics.options["game_is_end"] = True
                game_running = False
            if current_level.game_properties.has(objects.TextDone):
                sounds.play("done")
                basics.options["game_is_done"] = True
                basics.save_options(basics.options)
                game_running = False
                raise GameIsDoneError()
            if current_level.game_properties.has(objects.TextOpen):
                sounds.play("open")
                if basics.current_os == basics.windows:
                    if os.path.exists("bmp.exe"):
                            os.system("start bmp.exe")
                    elif os.path.exists("bmp.py"):
                        os.system("start python bmp.py")
                elif basics.current_os == basics.linux:
                    os.system("python ./bmp.py &")
            if current_level.game_properties.has(objects.TextTele):
                sounds.play("tele")
                display_offset = [float(random.randrange(window.get_width())), float(random.randrange(window.get_height()))]
            if current_level.game_properties.has(objects.TextHot) and current_level.game_properties.has(objects.TextMelt):
                sounds.play("melt")
                game_running = False
            if current_level.game_properties.has(objects.TextYou) and current_level.game_properties.has(objects.TextDefeat):
                sounds.play("defeat")
                game_running = False
            for event in current_level.sound_events:
                sounds.play(event)
            # level state check
            levelpack.set_level(current_level)
            if levelpack_info["win"]:
                print(languages.current_language["game.level.win"])
                if freeze_time == -1:
                    freeze_time = basics.options["fps"]
            elif levelpack_info["end"]:
                print(languages.current_language["game.levelpack.end"])
                if freeze_time == -1:
                    freeze_time = basics.options["fps"]
            elif levelpack_info["transform"]:
                print(languages.current_language["game.level.transform"])
                if freeze_time == -1:
                    freeze_time = basics.options["fps"]
            elif levelpack_info["selected_level"] is not None:
                print(languages.current_language["game.level.enter"])
                if freeze_time == -1:
                    freeze_time = basics.options["fps"]
            for level in levelpack.level_list:
                for world in current_level.world_list:
                    world.set_sprite_states(len(history[current_level.name]))
        if freeze_time == 0:
            level_changed = True
            world_changed = True
            if levelpack_info["win"]:
                level = copy.deepcopy(levelpack_backup.get_level(current_level.name))
                if level is not None:
                    levelpack.set_level(level)
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level = levelpack.get_exist_level(super_level.name if super_level is not None else levelpack.main_level)
                current_world = current_level.get_exact_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier})
            elif levelpack_info["end"]:
                game_running = False
            elif levelpack_info["transform"]:
                super_level_name = current_level.super_level
                super_level = levelpack.get_level(super_level_name if super_level_name is not None else levelpack.main_level)
                current_level = levelpack.get_exist_level(super_level.name if super_level is not None else levelpack.main_level)
                current_world = current_level.get_exact_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier})
            elif levelpack_info["selected_level"] is not None:
                current_level = levelpack.get_exist_level(levelpack_info["selected_level"])
                current_world = current_level.get_exact_world({"name": current_level.main_world_name, "infinite_tier": current_level.main_world_tier})
        if level_changed:
            print(languages.current_language["game.level.current.name"], current_level.name, sep="")
            level_changed = False
        if world_changed:
            print(languages.current_language["game.world.current.name"], current_world.name, sep="")
            print(languages.current_language["game.world.current.infinite_tier"], current_world.infinite_tier, sep="")
            world_changed = False
        pygame.mixer.music.set_volume(1.0 if current_level.have_you() else 0.5)
        # display
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
            del real_fps_string
        # game transform
        game_transform_to = [t for t, n in current_level.game_properties.enabled_dict().items() if issubclass(t, objects.Noun) and not n]
        if len(game_transform_to) != 0:
            transparent_black_background = pygame.Surface(window.get_size(), pygame.SRCALPHA)
            transparent_black_background.fill("#00000080")
            window.blit(transparent_black_background, (0, 0))
        game_transform_to = [o.obj_type for o in game_transform_to if o is not None]
        for obj_type in game_transform_to:
            window.blit(pygame.transform.scale(displays.sprites.get(obj_type.sprite_name, 0, wiggle), window.get_size()), (0, 0))
        del game_transform_to
        # offset
        display_offset_speed[0] = basics.absclampf(display_offset_speed[0], window.get_width() / basics.options["fps"] * 4)
        display_offset_speed[1] = basics.absclampf(display_offset_speed[1], window.get_height() / basics.options["fps"] * 4)
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
    return levelpack