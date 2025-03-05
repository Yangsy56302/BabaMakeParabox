from typing import Optional
import os
import copy
import json
import random

import bmp.audio
import bmp.base
import bmp.color
import bmp.lang
import bmp.level
import bmp.levelpack
import bmp.loc
import bmp.obj
import bmp.ref
import bmp.render
import bmp.space

import pygame

class GameIsDefeatError(Exception):
    pass

class GameIsDoneError(Exception):
    pass

keybinds: dict[int, str] = {
    pygame.K_w: "W",
    pygame.K_a: "A",
    pygame.K_s: "S",
    pygame.K_d: "D",
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
    pygame.K_z: "Z",
    pygame.K_r: "R",
    pygame.K_o: "O",
    pygame.K_p: "P",
    pygame.K_RETURN: "RETURN",
    pygame.K_TAB: "TAB",
    pygame.K_ESCAPE: "ESCAPE",
    pygame.K_MINUS: "-",
    pygame.K_EQUALS: "=",
    pygame.K_SPACE: " ",
    pygame.K_F1: "F1",
    pygame.K_F12: "F12",
}
keymods: dict[int, str] = {
    pygame.KMOD_LSHIFT: "LSHIFT",
    pygame.KMOD_RSHIFT: "RSHIFT",
    pygame.KMOD_LCTRL: "LCTRL",
    pygame.KMOD_RCTRL: "RCTRL",
    pygame.KMOD_LALT: "LALT",
    pygame.KMOD_RALT: "RALT",
}
movements: dict[str, tuple[str, Optional[bmp.loc.Orient], bmp.loc.Coord]] = {
    "W": ("S", bmp.loc.Orient.W, (0, -1)),
    "UP": ("DOWN", bmp.loc.Orient.W, (0, -1)),
    "S": ("W", bmp.loc.Orient.S, (0, 1)),
    "DOWN": ("UP", bmp.loc.Orient.S, (0, 1)),
    "A": ("D", bmp.loc.Orient.A, (-1, 0)),
    "LEFT": ("RIGHT", bmp.loc.Orient.A, (-1, 0)),
    "D": ("A", bmp.loc.Orient.D, (1, 0)),
    "RIGHT": ("LEFT", bmp.loc.Orient.D, (1, 0)),
    " ": ("None", None, (0, 0)),
    "RETURN": ("None", None, (0, 0)),
}

def play(levelpack: bmp.levelpack.Levelpack) -> bmp.levelpack.Levelpack:
    levelpack.prepare()
    for level in levelpack.level_list:
        for space in level.space_list:
            space.set_sprite_states(0)
        levelpack.set_level_init_state(level.level_id, copy.deepcopy(level))
    levelpack_unchanged = copy.deepcopy(levelpack)
    levelpack_info: bmp.levelpack.ReturnInfo = bmp.levelpack.default_levelpack_info.copy()
    history: list[tuple[
        bmp.levelpack.Levelpack,
        bmp.levelpack.ReturnInfo
    ]] = [(
        copy.deepcopy(levelpack),
        levelpack_info.copy()
    )]
    savepoint_dict: dict[str, tuple[bmp.levelpack.Levelpack, bmp.levelpack.ReturnInfo]] = {}
    default_savepoint_name = "_"
    window = pygame.display.set_mode((720, 720), pygame.RESIZABLE)
    game_offset = [0.0, 0.0]
    game_offset_speed = [0.0, 0.0]
    pygame.display.set_caption(bmp.lang.fformat(
        "title.window.play",
        ver=bmp.base.version,
        debug=bmp.lang.fformat("debug.name") if bmp.opt.options["debug"] else "",
    ))
    pygame.display.set_icon(pygame.image.load(os.path.join(".", "logo", "a8icon.png")))
    window.fill("#000000")
    pygame.key.stop_text_input()
    pygame.key.set_repeat(bmp.opt.options["gameplay"]["repeat"]["delay"], bmp.opt.options["gameplay"]["repeat"]["interval"])
    clock = pygame.time.Clock()
    monochrome: Optional[bmp.color.ColorHex] = None
    keys = {v: False for v in keybinds.values()}
    keys.update({v: False for v in keymods.values()})
    mouses: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    mouse_pos: bmp.loc.Coord[int]
    mouse_pos_in_space: bmp.loc.Coord[int]
    space_surface_size: bmp.loc.Coord[int] = window.get_size()
    space_surface_pos: bmp.loc.Coord[int] = (0, 0)
    bmp.color.set_palette(os.path.join(".", "palettes", bmp.opt.options["render"]["palette"]))
    bmp.render.current_sprites.update()
    level_changed = False
    space_changed = False
    frame = 0
    frame_since_last_move = 0
    wiggle = 1
    milliseconds = 1000 // bmp.opt.options["render"]["fps"]
    real_fps = bmp.opt.options["render"]["fps"]
    show_fps = False
    if bmp.opt.options["gameplay"]["bgm"]["enabled"] and bmp.base.current_os == bmp.base.windows:
        pygame.mixer.music.load(os.path.join("midi", bmp.opt.options["gameplay"]["bgm"]["name"]))
        pygame.mixer.music.play(-1)
    game_running = True
    display_refresh = False
    levelpack_refresh = False
    press_key_to_continue = False
    while game_running:
        frame += 1
        frame_since_last_move += 1
        if frame % (bmp.opt.options["render"]["fps"] // 6) == 0:
            wiggle = wiggle % 3 + 1
        for key in keybinds.values():
            keys[key] = False
        for key in keymods.values():
            keys[key] = False
        mouse_scroll: tuple[bool, bool] = (False, False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in keybinds.keys():
                    keys[keybinds[event.key]] = True
                for n, key in keymods.items():
                    if event.mod & n:
                        keys[key] = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    mouse_scroll = (True, mouse_scroll[1])
                if event.button == 5:
                    mouse_scroll = (mouse_scroll[0], True)
        keymod_info = pygame.key.get_mods()
        for n, key in keymods.items():
            if keymod_info & n:
                keys[key] = True
        new_mouses = pygame.mouse.get_pressed(num_buttons=3)
        mouses = (
            (mouses[0] + 1) * int(new_mouses[0]),
            (mouses[1] + 1) * int(new_mouses[1]),
            (mouses[2] + 1) * int(new_mouses[2]),
            int(mouse_scroll[0]), int(mouse_scroll[1])
        )
        del new_mouses
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_in_space = (
            (mouse_pos[0] - space_surface_pos[0]) * levelpack.current_level.current_space.width // space_surface_size[0],
            (mouse_pos[1] - space_surface_pos[1]) * levelpack.current_level.current_space.height // space_surface_size[1]
        )
        if not press_key_to_continue:
            for key, (negative_key, op, (dx, dy)) in movements.items():
                if keys[key] and not keys.get(negative_key, False):
                    new_history: tuple[bmp.levelpack.Levelpack, bmp.levelpack.ReturnInfo] = (
                        copy.deepcopy(levelpack),
                        levelpack.tick(op)
                    )
                    history.append(new_history)
                    levelpack_info = new_history[1]
                    if levelpack.current_level.game_properties.enabled(bmp.obj.TextYou):
                        game_offset[0] += dx * window.get_width() / levelpack.current_level.current_space.width
                        game_offset[1] += dy * window.get_height() / levelpack.current_level.current_space.height
                    if levelpack.current_level.game_properties.enabled(bmp.obj.TextPush) and levelpack_info["game_push"]:
                        game_offset[0] += dx * window.get_width() / levelpack.current_level.current_space.width
                        game_offset[1] += dy * window.get_height() / levelpack.current_level.current_space.height
                    display_refresh = True
                    levelpack_refresh = True
                    break
        else:
            for key in movements.keys():
                if keys[key]:
                    display_refresh = True
                    levelpack_refresh = True
                    break
        if not levelpack_refresh:
            if any(mouses) and not levelpack.current_level.current_space.out_of_range(mouse_pos_in_space):
                visible_space_list: list[bmp.space.Space] = [
                    s for s in levelpack.current_level.space_list
                    if not s.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextHide)
                ]
                if mouses[0] == 1:
                    sub_space_objs: list[bmp.obj.SpaceObject] = [
                        o for o in levelpack.current_level.current_space.get_spaces_from_pos(mouse_pos_in_space)
                        if not o.properties.enabled(bmp.obj.TextHide)
                    ]
                    sub_spaces = [levelpack.current_level.get_space(o.space_id) for o in sub_space_objs]
                    sub_spaces = [
                        s for s in sub_spaces
                        if s is not None
                        and not s.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextHide)
                    ]
                    if len(sub_spaces) != 0:
                        levelpack.current_level.current_space = random.choice(sub_spaces)
                        space_changed = True
                        display_refresh = True
                elif mouses[2] == 1:
                    super_spaces: list[bmp.space.Space] = [
                        s for s, o in levelpack.current_level.find_super_spaces(levelpack.current_level.current_space_id)
                        if not o.properties.enabled(bmp.obj.TextHide)
                        and not s.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextHide)
                    ]
                    if len(super_spaces) != 0:
                        levelpack.current_level.current_space = random.choice(super_spaces)
                        space_changed = True
                        display_refresh = True
                elif mouses[1] == 1:
                    object_list = levelpack.current_level.current_space.get_objs_from_pos(mouse_pos_in_space)
                    if len(object_list) != 0:
                        bmp.lang.print(bmp.lang.seperator_line(bmp.lang.fformat("title.object")))
                        for obj in object_list:
                            bmp.lang.print(obj.get_info() if bmp.opt.options["debug"] else repr(obj))
                elif bool(mouses[3]) ^ bool(mouses[4]):
                    current_space_index = visible_space_list.index(levelpack.current_level.current_space) if levelpack.current_level.current_space in visible_space_list else 0
                    current_space_index += 1 if mouses[3] else -1
                    current_space_index = current_space_index % len(visible_space_list) if current_space_index >= 0 else len(visible_space_list) - 1
                    levelpack.current_level.current_space = visible_space_list[current_space_index]
                    space_changed = True
                    display_refresh = True
                    del current_space_index
            elif keys["Z"]:
                if len(history) >= 1:
                    levelpack = copy.deepcopy(history[-1][0])
                    levelpack_info = copy.deepcopy(history[-1][1])
                    if len(history) != 1:
                        history.pop()
                    level_changed = True
                    display_refresh = True
                    press_key_to_continue = False
            elif keys["ESCAPE"]:
                if levelpack.current_level.super_level_id is not None and levelpack.current_level.super_level_id in levelpack.level_dict.keys():
                    levelpack.current_level_id = levelpack.current_level.super_level_id
                    new_history: tuple[bmp.levelpack.Levelpack, bmp.levelpack.ReturnInfo] = (
                        copy.deepcopy(levelpack),
                        bmp.levelpack.default_levelpack_info.copy()
                    )
                    history.append(new_history)
                    level_changed = True
                    display_refresh = True
            elif keys["R"]:
                restart_failed = True
                if not (keys["LCTRL"] or keys["RCTRL"]):
                    for index, (old_levelpack, old_levelpack_info) in reversed(list(enumerate(history))):
                        if index == 0 or history[index - 1][1]["select"] is not None:
                            bmp.lang.fprint("play.level.restart")
                            bmp.audio.play("restart")
                            levelpack = copy.deepcopy(old_levelpack)
                            levelpack_info = old_levelpack_info.copy()
                            history = history[:index + 1]
                            level_changed = True
                            display_refresh = True
                            press_key_to_continue = False
                            restart_failed = False
                            break
                else:
                    bmp.lang.fprint("play.level.restart" if restart_failed else "play.levelpack.restart")
                    bmp.audio.play("restart")
                    levelpack = copy.deepcopy(levelpack_unchanged)
                    levelpack_info = bmp.levelpack.default_levelpack_info.copy()
                    history = [(
                        copy.deepcopy(levelpack),
                        levelpack_info.copy()
                    )]
                    level_changed = True
                    display_refresh = True
                    press_key_to_continue = False
                del restart_failed
            elif keys["O"]:
                bmp.lang.print(bmp.lang.seperator_line(bmp.lang.fformat("title.savepoint")))
                savepoint_name = ""
                if keys["LCTRL"] or keys["RCTRL"]:
                    savepoint_name = bmp.lang.input_str(bmp.lang.fformat("input.savepoint.name"))
                if keys["LALT"] or keys["RALT"]:
                    savepoint_name += "" if bmp.opt.options["debug"] or savepoint_name.endswith(".json") else ".json"
                    if not os.path.isfile(os.path.join("levelpacks", savepoint_name)):
                        bmp.lang.fwarn("warn.savepoint.not_found", value=savepoint_name)
                    else:
                        with open(os.path.join("levelpacks", savepoint_name), "r", encoding="utf-8") as file:
                            levelpack_json = json.load(file)
                        levelpack = bmp.levelpack.json_to_levelpack(levelpack_json)
                        levelpack_info = bmp.levelpack.default_levelpack_info.copy()
                        bmp.lang.fprint("play.savepoint.loaded", value=savepoint_name)
                        level_changed = True
                        display_refresh = True
                        press_key_to_continue = False
                else:
                    savepoint_name = savepoint_name if savepoint_name != "" else default_savepoint_name
                    savepoint = savepoint_dict.get(savepoint_name)
                    if savepoint is not None:
                        levelpack = savepoint[0]
                        levelpack_info = savepoint[1]
                        bmp.lang.fprint("play.savepoint.loaded", value=savepoint_name)
                        level_changed = True
                        display_refresh = True
                        press_key_to_continue = False
                    else:
                        bmp.lang.fwarn("warn.savepoint.not_found", value=savepoint_name)
            elif keys["P"]:
                bmp.lang.print(bmp.lang.seperator_line(bmp.lang.fformat("title.savepoint")))
                savepoint_name = ""
                if keys["LCTRL"] or keys["RCTRL"]:
                    savepoint_name = bmp.lang.input_str(bmp.lang.fformat("input.savepoint.name"))
                if keys["LALT"] or keys["RALT"]:
                    savepoint_name = savepoint_name if savepoint_name != "" else default_savepoint_name
                    savepoint_name += "" if bmp.opt.options["debug"] or savepoint_name.endswith(".json") else ".json"
                    with open(os.path.join("levelpacks", savepoint_name), "w", encoding="utf-8") as file:
                        json.dump(levelpack.to_json(), file, **bmp.opt.get_json_dump_kwds())
                else:
                    savepoint_name = savepoint_name if savepoint_name != "" else default_savepoint_name
                    savepoint_dict[savepoint_name] = (copy.deepcopy(levelpack), levelpack_info.copy())
                bmp.lang.fprint("play.savepoint.saved", value=savepoint_name)
            elif keys["TAB"]:
                bmp.lang.print(bmp.lang.seperator_line(bmp.lang.fformat("title.info")))
                bmp.lang.fprint("play.level.current.name", value=levelpack.current_level_id.name)
                bmp.lang.fprint("play.space.current.name", value=levelpack.current_level.current_space_id.name)
                bmp.lang.fprint("play.space.current.infinite_tier", value=levelpack.current_level.current_space_id.infinite_tier)
                if len(levelpack.current_level.current_space.rule_list):
                    bmp.lang.print(bmp.lang.seperator_line(bmp.lang.fformat("title.space.rule_list")))
                    for rule in levelpack.current_level.current_space.rule_list:
                        str_list = []
                        for object_type in rule:
                            str_list.append(object_type.get_name())
                        bmp.lang.print(" ".join(str_list))
                    bmp.lang.print(bmp.lang.seperator_line(bmp.lang.fformat("title.level.rule_list")))
                recursion_rule_list: list[bmp.rule.Rule] = levelpack.current_level.recursion_rules(levelpack.current_level.current_space)[0]
                if len(recursion_rule_list):
                    for rule in recursion_rule_list:
                        str_list = []
                        for object_type in rule:
                            str_list.append(object_type.get_name())
                        bmp.lang.print(" ".join(str_list))
                if len(levelpack.rule_list):
                    bmp.lang.print(bmp.lang.seperator_line(bmp.lang.fformat("title.levelpack.rule_list")))
                    for rule in levelpack.rule_list:
                        str_list = []
                        for object_type in rule:
                            str_list.append(object_type.get_name())
                        bmp.lang.print(" ".join(str_list))
                if len(levelpack.collectibles) != 0:
                    bmp.lang.print(bmp.lang.seperator_line(bmp.lang.fformat("title.collectibles")))
                    collectible_counts: dict[type[bmp.obj.Object], int] = {}
                    for collectible in levelpack.collectibles:
                        collectible_counts.setdefault(collectible.object_type, 0)
                        collectible_counts[collectible.object_type] += 1
                    for object_type, collect_count in collectible_counts.items():
                        bmp.lang.fprint("play.levelpack.collectibles", key=object_type.get_name(), value=collect_count)
        if levelpack.current_level.game_properties:
            offset_used = False
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextStop):
                wiggle = 1
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextShift):
                game_offset[0] += window.get_width() / bmp.opt.options["render"]["fps"]
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextMove):
                game_offset[1] += window.get_height() / (4 * bmp.opt.options["render"]["fps"])
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextSink):
                game_offset_speed[1] += window.get_height() / (16 * bmp.opt.options["render"]["fps"])
                offset_used = True
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextFloat):
                game_offset_speed[1] -= window.get_height() / (64 * bmp.opt.options["render"]["fps"])
                offset_used = True
            if not offset_used:
                game_offset_speed[0] = game_offset_speed[0] / 2
                game_offset_speed[1] = game_offset_speed[1] / 2
            del offset_used
        if levelpack_refresh:
            display_refresh = True
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextWin):
                bmp.lang.fprint("play.win")
                bmp.audio.play("win")
                game_running = False
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextDefeat):
                bmp.audio.play("defeat")
                game_running = False
                raise GameIsDefeatError()
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextBonus):
                bmp.audio.play("bonus")
                bmp.lang.print("VVd4WmVGTnRXVEJOYWtaVFRqQmtWZz09")
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextEnd):
                bmp.lang.fprint("play.end")
                bmp.audio.play("end")
                bmp.opt.options["gameplay"]["game_is_end"] = True
                bmp.opt.save()
                game_running = False
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextDone):
                bmp.audio.play("done")
                bmp.opt.options["gameplay"]["game_is_done"] = True
                bmp.opt.save()
                game_running = False
                raise GameIsDoneError()
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextOpen):
                if bmp.base.current_os == bmp.base.windows:
                    if os.path.exists("bmp.exe"):
                            os.system("start bmp.exe")
                    elif os.path.exists("bmp.py"):
                        os.system("start python bmp.py")
                elif bmp.base.current_os == bmp.base.linux:
                    os.system("python ./bmp.py &")
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextShut):
                game_running = False
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextTele):
                bmp.audio.play("tele")
                game_offset = [float(random.randrange(window.get_width())), float(random.randrange(window.get_height()))]
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextHot) \
                and levelpack.current_level.game_properties.enabled(bmp.obj.TextMelt):
                bmp.audio.play("melt")
                game_running = False
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextYou) \
                and levelpack.current_level.game_properties.enabled(bmp.obj.TextDefeat):
                bmp.audio.play("defeat")
                game_running = False
            for space in levelpack.current_level.space_list:
                for game_obj in space.get_objs_from_type(bmp.obj.Game):
                    if bmp.base.current_os == bmp.base.windows:
                        if os.path.exists("bmp.exe"):
                            os.system(f"start submp.exe {game_obj.ref_type.json_name}")
                        elif os.path.exists("bmp.py"):
                            os.system(f"start python submp.py {game_obj.ref_type.json_name}")
                    elif bmp.base.current_os == bmp.base.linux:
                        os.system(f"python ./submp.py {game_obj.ref_type.json_name} &")
            if not press_key_to_continue:
                frame_since_last_move = 0
                press_key_to_continue = True
                for event in levelpack.current_level.sound_events:
                    bmp.audio.play(event)
                if levelpack_info["win"]:
                    bmp.audio.play("win")
                    bmp.lang.fprint("play.level.win")
                    monochrome = bmp.obj.TextWin.get_color()
                elif levelpack_info["end"]:
                    bmp.audio.play("end")
                    bmp.lang.fprint("play.levelpack.end")
                    monochrome = bmp.obj.TextEnd.get_color()
                elif levelpack_info["done"]:
                    bmp.audio.play("done")
                    bmp.lang.fprint("play.levelpack.done")
                    monochrome = bmp.obj.TextDone.get_color()
                elif levelpack_info["transform"]:
                    bmp.audio.play("restart")
                    bmp.lang.fprint("play.level.transform")
                    monochrome = bmp.obj.TextLevel.get_color()
                elif levelpack_info["select"] is not None:
                    bmp.audio.play("level")
                    bmp.lang.fprint("play.level.enter")
                    monochrome = bmp.obj.TextSelect.get_color()
                else:
                    press_key_to_continue = False
                if press_key_to_continue:
                    bmp.lang.fprint("press_any_key_to_continue")
            else:
                press_key_to_continue = False
                level_changed = True
                select = levelpack_info["select"]
                if levelpack_info["win"]:
                    levelpack.reset_level(levelpack.current_level_id)
                    if levelpack.current_level.super_level_id is not None and levelpack.current_level.super_level_id in levelpack.level_dict.keys():
                        levelpack.current_level_id = levelpack.current_level.super_level_id
                elif levelpack_info["end"]:
                    game_running = False
                elif levelpack_info["done"]:
                    game_running = False
                elif levelpack_info["transform"]:
                    if levelpack.current_level.super_level_id is not None and levelpack.current_level.super_level_id in levelpack.level_dict.keys():
                        levelpack.current_level_id = levelpack.current_level.super_level_id
                elif select is not None:
                    selected_level_id: bmp.ref.LevelID = random.choice(select)
                    if selected_level_id in levelpack.level_dict.keys():
                        levelpack.current_level_id = selected_level_id
                    del selected_level_id
                levelpack.prepare()
            levelpack_refresh = False
        if display_refresh:
            for level in levelpack.level_list:
                for space in levelpack.current_level.space_list:
                    space.set_sprite_states(len(history))
            display_refresh = False
        if not press_key_to_continue:
            monochrome = None
        if level_changed:
            space_changed = True
            # bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.level")))
            # bmp.lang.lang_print("play.level.current.name", value=current_level.level_id.name)
            level_changed = False
        if space_changed:
            # bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.space")))
            # bmp.lang.lang_print("play.space.current.name", value=current_space.space_id.name)
            # bmp.lang.lang_print("play.space.current.infinite_tier", value=current_space.space_id.infinite_tier)
            space_changed = False
        pygame.mixer.music.set_volume(1.0 if levelpack.current_level.have_you() else 0.5)
        # display
        window.fill(bmp.color.current_palette[0, 4])
        space_surface_size = window.get_size()
        space_surface_pos = (0, 0)
        match levelpack.current_level.current_space.static_transform["direct"]:
            case "W" | "S":
                if window.get_width() // levelpack.current_level.current_space.width > window.get_height() // levelpack.current_level.current_space.height:
                    space_surface_size = (window.get_height() * levelpack.current_level.current_space.width // levelpack.current_level.current_space.height, window.get_height())
                    space_surface_pos = ((window.get_width() - space_surface_size[0]) // 2, 0)
                elif window.get_width() // levelpack.current_level.current_space.width < window.get_height() // levelpack.current_level.current_space.height:
                    space_surface_size = (window.get_width(), window.get_width() * levelpack.current_level.current_space.height // levelpack.current_level.current_space.width)
                    space_surface_pos = (0, (window.get_height() - space_surface_size[1]) // 2)
            case "A" | "D":
                if window.get_width() // levelpack.current_level.current_space.height > window.get_height() // levelpack.current_level.current_space.width:
                    space_surface_size = (window.get_height() * levelpack.current_level.current_space.height // levelpack.current_level.current_space.width, window.get_height())
                    space_surface_pos = ((window.get_width() - space_surface_size[0]) // 2, 0)
                elif window.get_width() // levelpack.current_level.current_space.height < window.get_height() // levelpack.current_level.current_space.width:
                    space_surface_size = (window.get_width(), window.get_width() * levelpack.current_level.current_space.width // levelpack.current_level.current_space.height)
                    space_surface_pos = (0, (window.get_height() - space_surface_size[1]) // 2)
        if not levelpack.current_level.game_properties.enabled(bmp.obj.TextHide):
            if not levelpack.current_level.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextHide):
                smooth_value = bmp.render.calc_smooth(frame_since_last_move)
                if levelpack.current_level.game_properties.enabled(bmp.obj.TextStop):
                    smooth_value = None
                space_surface = levelpack.current_level.space_to_surface(
                    levelpack.current_level.current_space, wiggle, space_surface_size, smooth=smooth_value, debug=bmp.opt.options["debug"]
                )
                # monochrome when paused
                if monochrome is not None:
                    monochrome_rgb = bmp.color.hex_to_rgb(monochrome)
                    monochrome_new = bmp.color.rgb_to_hex(
                        int(monochrome_rgb[0] * 0.25),
                        int(monochrome_rgb[1] * 0.25),
                        int(monochrome_rgb[2] * 0.25),
                    )
                    space_surface.fill(monochrome_new, special_flags=pygame.BLEND_RGBA_ADD)
                    del monochrome_rgb, monochrome_new
                window.blit(pygame.transform.scale(space_surface, space_surface_size), space_surface_pos)
                del smooth_value
            # game transform
            game_transform_to = [t for t, n in levelpack.current_level.game_properties.enabled_count().items() if issubclass(t, bmp.obj.Noun) and not n]
            if len(game_transform_to) != 0:
                window.fill("#00000080", (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            game_transform_to = [o.ref_type for o in game_transform_to if o is not None]
            for object_type in game_transform_to:
                window.blit(pygame.transform.scale(bmp.render.current_sprites.get(object_type.sprite_name, 0, wiggle), window.get_size()), (0, 0))
            del game_transform_to
            if levelpack.current_level.game_properties.enabled(bmp.obj.TextSelect):
                select_surface = bmp.render.current_sprites.get(bmp.obj.Cursor.sprite_name, 0, wiggle, raw=True)
                select_surface = bmp.render.set_surface_color_dark(select_surface, bmp.color.float_to_hue((frame / bmp.opt.options["render"]["fps"] / 6) % 1.0))
                window.blit(pygame.transform.scale(select_surface, window.get_size()), (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                del select_surface
            # offset
            game_offset_speed[0] = bmp.base.absclampf(game_offset_speed[0], window.get_width() / bmp.opt.options["render"]["fps"] * 4)
            game_offset_speed[1] = bmp.base.absclampf(game_offset_speed[1], window.get_height() / bmp.opt.options["render"]["fps"] * 4)
            game_offset[0] += game_offset_speed[0]
            game_offset[1] += game_offset_speed[1]
            game_offset[0] %= float(window.get_width())
            game_offset[1] %= float(window.get_height())
            if game_offset[0] != 0.0 or game_offset[1] != 0.0:
                window_surface = pygame.display.get_surface().copy()
                window.blit(window_surface, [int(game_offset[0]), int(game_offset[1])])
                window.blit(window_surface, [int(game_offset[0] - window.get_width()), int(game_offset[1])])
                window.blit(window_surface, [int(game_offset[0]), int(game_offset[1] - window.get_height())])
                window.blit(window_surface, [int(game_offset[0] - window.get_width()), int(game_offset[1] - window.get_height())])
        # fps
        real_fps = min(1000 / milliseconds, (real_fps * (bmp.opt.options["render"]["fps"] - 1) + 1000 / milliseconds) / bmp.opt.options["render"]["fps"])
        if keys["F1"]:
            show_fps = not show_fps
        if show_fps:
            real_fps_string = str(int(real_fps))
            real_fps_surface = bmp.render.line_to_surface(real_fps_string, wiggle=wiggle)
            real_fps_surface = pygame.transform.scale_by(real_fps_surface, bmp.render.smaller_gui_scalar)
            window.blit(real_fps_surface, (0, 0))
            del real_fps_string, real_fps_surface
        if keys["F12"]:
            bmp.opt.options["debug"] = not bmp.opt.options["debug"]
        pygame.display.flip()
        milliseconds = clock.tick(bmp.opt.options["render"]["fps"])
    pygame.mixer.music.stop()
    pygame.display.quit()
    return levelpack