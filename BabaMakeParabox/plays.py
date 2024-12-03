import random
import copy
import os

from BabaMakeParabox import basics, languages, refs, sounds, spaces, objects, collects, displays, worlds, levels, levelpacks

import pygame

class GameIsDoneError(Exception):
    pass

movements: dict[str, tuple[str, spaces.PlayerOperation, spaces.Coord]] = {"W": ("S", spaces.Orient.W, (0, -1)), "S": ("W", spaces.Orient.S, (0, 1)), "A": ("D", spaces.Orient.A, (-1, 0)), "D": ("A", spaces.Orient.D, (1, 0)), " ": ("None", spaces.NullOrient.O, (0, 0))}

def play(levelpack: levelpacks.Levelpack) -> levelpacks.Levelpack:
    for level in levelpack.level_list:
        for world in level.world_list:
            world.set_sprite_states(0)
    levelpack.prepare(levelpack.get_exact_level(levelpack.main_level_id))
    levelpack_backup = copy.deepcopy(levelpack)
    current_level: levels.Level = levelpack.get_exact_level(levelpack.main_level_id)
    current_world: worlds.World = current_level.get_exact_world(current_level.main_world_id)
    levelpack_info: levelpacks.ReturnInfo = levelpacks.default_levelpack_info.copy()
    history: list[tuple[levelpacks.Levelpack, levelpacks.ReturnInfo, refs.LevelID, refs.WorldID]] = [(
        copy.deepcopy(levelpack),
        levelpack_info.copy(),
        current_level.level_id,
        current_world.world_id
    )]
    savepoint_dict: dict[str, tuple[levelpacks.Levelpack, levelpacks.ReturnInfo, refs.LevelID, refs.WorldID]] = {}
    default_savepoint_name = "_"
    window = pygame.display.set_mode((720, 720), pygame.RESIZABLE)
    display_offset = [0.0, 0.0]
    display_offset_speed = [0.0, 0.0]
    pygame.display.set_caption(f"Baba Make Parabox Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("bmp.png"))
    window.fill("#000000")
    pygame.key.stop_text_input()
    clock = pygame.time.Clock()
    keybinds = {
        pygame.K_w: "W",
        pygame.K_a: "A",
        pygame.K_s: "S",
        pygame.K_d: "D",
        pygame.K_z: "Z",
        pygame.K_r: "R",
        pygame.K_o: "O",
        pygame.K_p: "P",
        pygame.K_TAB: "TAB",
        pygame.K_ESCAPE: "ESCAPE",
        pygame.K_MINUS: "-",
        pygame.K_EQUALS: "=",
        pygame.K_SPACE: " ",
        pygame.K_F1: "F1",
    }
    keymods = {
        pygame.KMOD_LSHIFT: "LSHIFT",
        pygame.KMOD_RSHIFT: "RSHIFT",
        pygame.KMOD_LCTRL: "LCTRL",
        pygame.KMOD_RCTRL: "RCTRL",
        pygame.KMOD_LALT: "LALT",
        pygame.KMOD_RALT: "RALT",
    }
    keys = {v: False for v in keybinds.values()}
    keys.update({v: False for v in keymods.values()})
    displays.sprites.update()
    level_changed = False
    world_changed = False
    frame = 1
    wiggle = 1
    milliseconds = 1000 // basics.options["fps"]
    real_fps = basics.options["fps"]
    show_fps = False
    if basics.options["bgm"]["enabled"] and basics.current_os == basics.windows:
        pygame.mixer.music.load(os.path.join("midi", basics.options["bgm"]["name"]))
        pygame.mixer.music.play(-1)
    game_running = True
    display_refresh = False
    levelpack_refresh = False
    press_key_to_continue = False
    while game_running:
        frame += 1
        if frame >= basics.options["fpw"]:
            frame = 0
            wiggle = wiggle % 3 + 1
        for key in keybinds.values():
            keys[key] = False
        for key in keymods.values():
            keys[key] = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in keybinds.keys():
                    keys[keybinds[event.key]] = True
                for n, key in keymods.items():
                    if event.mod & n:
                        keys[key] = True
        if not press_key_to_continue:
            for key, (negative_key, op, (dx, dy)) in movements.items():
                if keys[key] and not keys.get(negative_key, False):
                    new_history: tuple[levelpacks.Levelpack, levelpacks.ReturnInfo, refs.LevelID, refs.WorldID] = (
                        copy.deepcopy(levelpack),
                        levelpack.turn(current_level, op),
                        current_level.level_id,
                        current_world.world_id
                    )
                    history.append(new_history)
                    levelpack_info, current_level_id, current_world_id = new_history[1:]
                    current_level = levelpack.get_exact_level(current_level_id)
                    current_world = current_level.get_exact_world(current_world_id)
                    if current_level.game_properties.has(objects.TextYou):
                        display_offset[0] += dx * window.get_width() / current_world.width
                        display_offset[1] += dy * window.get_height() / current_world.height
                    if current_level.game_properties.has(objects.TextPush) and levelpack_info["game_push"]:
                        display_offset[0] += dx * window.get_width() / current_world.width
                        display_offset[1] += dy * window.get_height() / current_world.height
                    for level in levelpack.level_list:
                        for world in current_level.world_list:
                            world.set_sprite_states(len(history))
                    display_refresh = True
                    levelpack_refresh = True
                    break
        else:
            for key in movements.keys():
                if keys[key]:
                    display_refresh = True
                    levelpack_refresh = True
                    break
        if levelpack_refresh:
            pass
        elif keys["ESCAPE"]:
            for index, (old_levelpack, old_levelpack_info, old_level_id, old_world_id) in reversed(list(enumerate(history))):
                if old_levelpack_info["selected_level"] is not None:
                    levelpack = copy.deepcopy(old_levelpack)
                    levelpack_info = levelpacks.default_levelpack_info.copy()
                    current_level = levelpack.get_exact_level(old_level_id)
                    current_world = current_level.get_exact_world(old_world_id)
                    history = history[:index]
                    level_changed = True
                    world_changed = True
                    display_refresh = True
        elif keys["Z"]:
            if len(history) >= 1:
                levelpack = copy.deepcopy(history[-1][0])
                levelpack_info = levelpacks.default_levelpack_info.copy()
                current_level = levelpack.get_exact_level(history[-1][2])
                current_world = current_level.get_exact_world(history[-1][3])
                if len(history) != 1:
                    history.pop()
                level_changed = True
                world_changed = True
                display_refresh = True
        elif keys["R"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                languages.lang_print("play.level.restart")
                sounds.play("restart")
                levelpack = copy.deepcopy(levelpack_backup)
                levelpack_info = levelpacks.default_levelpack_info.copy()
                current_level = copy.deepcopy(levelpack.get_exact_level(levelpack.main_level_id))
                current_world = current_level.get_exact_world(current_level.main_world_id)
                history = [(
                    copy.deepcopy(levelpack),
                    levelpack_info.copy(),
                    current_level.level_id,
                    current_world.world_id
                )]
                level_changed = True
                world_changed = True
                display_refresh = True
        elif keys["O"]:
            languages.lang_print("seperator.title", text=languages.lang_format("title.savepoint"))
            savepoint_name = ""
            if keys["LCTRL"] or keys["RCTRL"]:
                savepoint_name = languages.lang_input("input.savepoint.name")
            savepoint_name = savepoint_name if savepoint_name != "" else default_savepoint_name
            savepoint = savepoint_dict.get(savepoint_name)
            if savepoint is not None:
                levelpack = savepoint[0]
                levelpack_info = levelpacks.default_levelpack_info.copy()
                current_level = copy.deepcopy(levelpack.get_exact_level(savepoint[2]))
                current_world = current_level.get_exact_world(savepoint[3])
                languages.lang_print("play.savepoint.loaded", value=savepoint_name)
                level_changed = True
                world_changed = True
                display_refresh = True
            else:
                languages.lang_print("warn.savepoint.not_found", value=savepoint_name)
        elif keys["P"]:
            languages.lang_print("seperator.title", text=languages.lang_format("title.savepoint"))
            savepoint_name = ""
            if keys["LCTRL"] or keys["RCTRL"]:
                savepoint_name = languages.lang_input("input.savepoint.name")
            savepoint_name = savepoint_name if savepoint_name != "" else default_savepoint_name
            savepoint_dict[savepoint_name] = (copy.deepcopy(levelpack), levelpack_info.copy(), current_level.level_id, current_world.world_id)
            languages.lang_print("play.savepoint.saved", value=savepoint_name)
        elif keys["TAB"]:
            languages.lang_print("seperator.title", text=languages.lang_format("title.info"))
            languages.lang_print("play.level.current.name", value=current_level.level_id.name)
            languages.lang_print("play.world.current.name", value=current_world.world_id.name)
            languages.lang_print("play.world.current.infinite_tier", value=current_world.world_id.infinite_tier)
            languages.lang_print("seperator.title", text=languages.lang_format("title.world.rule_list"))
            for rule in current_world.rule_list:
                str_list = []
                for obj_type in rule:
                    str_list.append(obj_type.display_name)
                print(" ".join(str_list))
            languages.lang_print("seperator.title", text=languages.lang_format("title.levelpack.rule_list"))
            for rule in levelpack.rule_list:
                str_list = []
                for obj_type in rule:
                    str_list.append(obj_type.display_name)
                print(" ".join(str_list))
            languages.lang_print("seperator.title", text=languages.lang_format("title.collectibles"))
            if len(levelpack.collectibles) == 0:
                languages.lang_print("play.levelpack.collectibles.empty")
            else:
                for collects_type in collects.collectible_dict.keys():
                    collects_number = len({c for c in levelpack.collectibles if isinstance(c, collects_type)})
                    if collects_number != 0:
                        languages.lang_print("play.levelpack.collectibles", key=collects_type.json_name, value=collects_number)
        elif keys["-"] and not keys["="]:
            current_world_index = current_level.world_list.index(current_world)
            current_world_index -= 1
            current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
            current_world = current_level.world_list[current_world_index]
            world_changed = True
            display_refresh = True
        elif keys["="] and not keys["-"]:
            current_world_index = current_level.world_list.index(current_world)
            current_world_index += 1
            current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
            current_world = current_level.world_list[current_world_index]
            world_changed = True
            display_refresh = True
        if current_level.game_properties:
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
        if display_refresh:
            if current_level.game_properties.has(objects.TextWin):
                languages.lang_print("play.win")
                sounds.play("win")
                game_running = False
            if current_level.game_properties.has(objects.TextShut):
                sounds.play("defeat")
                game_running = False
            if current_level.game_properties.has(objects.TextEnd):
                languages.lang_print("play.end")
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
            display_refresh = False
        if levelpack_refresh:
            if not press_key_to_continue:
                for event in current_level.sound_events:
                    sounds.play(event)
                if levelpack_info["win"]:
                    languages.lang_print("play.level.win")
                    languages.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["end"]:
                    languages.lang_print("play.levelpack.end")
                    languages.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["transform"]:
                    languages.lang_print("play.level.transform")
                    languages.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["selected_level"] is not None:
                    languages.lang_print("play.level.enter")
                    languages.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
            else:
                press_key_to_continue = False
                level_changed = True
                world_changed = True
                if levelpack_info["win"]:
                    level = copy.deepcopy(levelpack_backup.get_level(current_level.level_id))
                    if level is not None:
                        levelpack.set_level(level)
                    super_level = levelpack.get_level(current_level.super_level_id) if current_level.super_level_id is not None else levelpack.get_exact_level(levelpack.main_level_id)
                    current_level = super_level if super_level is not None else levelpack.get_exact_level(levelpack.main_level_id)
                    current_world = current_level.main_world
                elif levelpack_info["end"]:
                    game_running = False
                elif levelpack_info["transform"]:
                    super_level = levelpack.get_level(current_level.super_level_id) if current_level.super_level_id is not None else levelpack.get_exact_level(levelpack.main_level_id)
                    current_level = super_level if super_level is not None else levelpack.get_exact_level(levelpack.main_level_id)
                    current_world = current_level.main_world
                elif levelpack_info["selected_level"] is not None:
                    current_level = levelpack.get_exact_level(levelpack_info["selected_level"])
                    current_world = current_level.main_world
                levelpack.prepare(current_level)
            levelpack_refresh = False
        if level_changed:
            languages.lang_print("seperator.title", text=languages.lang_format("title.level"))
            languages.lang_print("play.level.current.name", value=current_level.level_id.name)
            level_changed = False
        if world_changed:
            languages.lang_print("seperator.title", text=languages.lang_format("title.world"))
            languages.lang_print("play.world.current.name", value=current_world.world_id.name)
            languages.lang_print("play.world.current.infinite_tier", value=current_world.world_id.infinite_tier)
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
    pygame.display.quit()
    return levelpack