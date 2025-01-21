from typing import Optional
import random
import copy
import os

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

movements: dict[str, tuple[str, Optional[bmp.loc.Orient], bmp.loc.Coord]] = {
    "W": ("S", bmp.loc.Orient.W, (0, -1)),
    "S": ("W", bmp.loc.Orient.S, (0, 1)),
    "A": ("D", bmp.loc.Orient.A, (-1, 0)),
    "D": ("A", bmp.loc.Orient.D, (1, 0)),
    " ": ("None", None, (0, 0))
}

def play(levelpack: bmp.levelpack.Levelpack) -> bmp.levelpack.Levelpack:
    for level in levelpack.level_list:
        for space in level.space_list:
            space.set_sprite_states(0)
    levelpack.prepare(levelpack.get_exact_level(levelpack.main_level_id))
    levelpack_backup = copy.deepcopy(levelpack)
    current_level: bmp.level.Level = levelpack.get_exact_level(levelpack.main_level_id)
    current_space: bmp.space.Space = current_level.get_exact_space(current_level.main_space_id)
    levelpack_info: bmp.levelpack.ReturnInfo = bmp.levelpack.default_levelpack_info.copy()
    history: list[tuple[
        bmp.levelpack.Levelpack,
        bmp.levelpack.ReturnInfo,
        bmp.ref.LevelID,
        bmp.ref.SpaceID
    ]] = [(
        copy.deepcopy(levelpack),
        levelpack_info.copy(),
        current_level.level_id,
        current_space.space_id
    )]
    savepoint_dict: dict[str, tuple[bmp.levelpack.Levelpack, bmp.levelpack.ReturnInfo, bmp.ref.LevelID, bmp.ref.SpaceID]] = {}
    default_savepoint_name = "_"
    window = pygame.display.set_mode((720, 720), pygame.RESIZABLE)
    game_offset = [0.0, 0.0]
    game_offset_speed = [0.0, 0.0]
    pygame.display.set_caption(f"Baba Make Parabox Version {bmp.base.versions}")
    pygame.display.set_icon(pygame.image.load(os.path.join(".", "logo", "a8icon.png")))
    window.fill("#000000")
    monochrome: Optional[bmp.color.ColorHex] = None
    pygame.key.stop_text_input()
    pygame.key.set_repeat(bmp.base.options["long_press"]["delay"], bmp.base.options["long_press"]["interval"])
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
    mouses: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
    mouse_pos: bmp.loc.Coord[int]
    mouse_pos_in_space: bmp.loc.Coord[int]
    space_surface_size: bmp.loc.Coord[int] = window.get_size()
    space_surface_pos: bmp.loc.Coord[int] = (0, 0)
    bmp.color.set_palette(os.path.join(".", "palettes", bmp.base.options["palette"]))
    bmp.render.current_sprites.update()
    level_changed = False
    space_changed = False
    frame = 0
    frame_since_last_move = 0
    wiggle = 1
    milliseconds = 1000 // bmp.base.options["fps"]
    real_fps = bmp.base.options["fps"]
    show_fps = False
    if bmp.base.options["bgm"]["enabled"] and bmp.base.current_os == bmp.base.windows:
        pygame.mixer.music.load(os.path.join("midi", bmp.base.options["bgm"]["name"]))
        pygame.mixer.music.play(-1)
    game_running = True
    display_refresh = False
    levelpack_refresh = False
    press_key_to_continue = False
    while game_running:
        frame += 1
        frame_since_last_move += 1
        if frame % (bmp.base.options["fps"] // 6) == 0:
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
            (mouse_pos[0] - space_surface_pos[0]) * current_space.width // space_surface_size[0],
            (mouse_pos[1] - space_surface_pos[1]) * current_space.height // space_surface_size[1]
        )
        if not press_key_to_continue:
            for key, (negative_key, op, (dx, dy)) in movements.items():
                if keys[key] and not keys.get(negative_key, False):
                    new_history: tuple[bmp.levelpack.Levelpack, bmp.levelpack.ReturnInfo, bmp.ref.LevelID, bmp.ref.SpaceID] = (
                        copy.deepcopy(levelpack),
                        levelpack.tick(current_level, op),
                        current_level.level_id,
                        current_space.space_id
                    )
                    history.append(new_history)
                    levelpack_info, current_level_id, current_space_id = new_history[1:]
                    current_level = levelpack.get_exact_level(current_level_id)
                    current_space = current_level.get_exact_space(current_space_id)
                    if current_level.game_properties.enabled(bmp.obj.TextYou):
                        game_offset[0] += dx * window.get_width() / current_space.width
                        game_offset[1] += dy * window.get_height() / current_space.height
                    if current_level.game_properties.enabled(bmp.obj.TextPush) and levelpack_info["game_push"]:
                        game_offset[0] += dx * window.get_width() / current_space.width
                        game_offset[1] += dy * window.get_height() / current_space.height
                    for level in levelpack.level_list:
                        for space in current_level.space_list:
                            space.set_sprite_states(len(history))
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
            if any(mouses) and not current_space.out_of_range(mouse_pos_in_space):
                visible_space_list: list[bmp.space.Space] = [
                    s for s in current_level.space_list
                    if not s.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextHide)
                ]
                if mouses[0] == 1:
                    sub_space_objs: list[bmp.obj.SpaceObject] = [
                        o for o in current_space.get_spaces_from_pos(mouse_pos_in_space)
                        if not o.properties.enabled(bmp.obj.TextHide)
                    ]
                    sub_spaces = [current_level.get_space(o.space_id) for o in sub_space_objs]
                    sub_spaces = [
                        s for s in sub_spaces
                        if s is not None
                        and not s.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextHide)
                    ]
                    if len(sub_spaces) != 0:
                        space = random.choice(sub_spaces)
                        current_space = space
                        space_changed = True
                        display_refresh = True
                elif mouses[2] == 1:
                    super_spaces: list[bmp.space.Space] = [
                        s for s, o in current_level.find_super_spaces(current_space.space_id)
                        if not o.properties.enabled(bmp.obj.TextHide)
                        and not s.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextHide)
                    ]
                    if len(super_spaces) != 0:
                        current_space = random.choice(super_spaces)
                        space_changed = True
                elif mouses[1] == 1:
                    pass # maybe print informations of objects on cursor?
                elif bool(mouses[3]) ^ bool(mouses[4]):
                    current_space_index = visible_space_list.index(current_space) if current_space in visible_space_list else 0
                    current_space_index += 1 if mouses[3] else -1
                    current_space_index = current_space_index % len(visible_space_list) if current_space_index >= 0 else len(visible_space_list) - 1
                    current_space = visible_space_list[current_space_index]
                    space_changed = True
                    display_refresh = True
            elif keys["Z"]:
                if len(history) >= 1:
                    levelpack = copy.deepcopy(history[-1][0])
                    levelpack_info = bmp.levelpack.default_levelpack_info.copy()
                    current_level = levelpack.get_exact_level(history[-1][2])
                    current_space = current_level.get_exact_space(history[-1][3])
                    if len(history) != 1:
                        history.pop()
                    level_changed = True
                    display_refresh = True
                    press_key_to_continue = False
            elif keys["R"]:
                reset = True
                if not (keys["LCTRL"] or keys["RCTRL"]):
                    bmp.lang.lang_print("play.level.restart")
                    bmp.audio.play("restart")
                    for index, (old_levelpack, old_levelpack_info, old_level_id, old_space_id) in reversed(list(enumerate(history))):
                        if old_levelpack_info["selected_level"] is not None:
                            levelpack = copy.deepcopy(old_levelpack)
                            levelpack_info = bmp.levelpack.default_levelpack_info.copy()
                            current_level = levelpack.get_exact_level(old_level_id)
                            current_space = current_level.get_exact_space(old_space_id)
                            history = history[:index]
                            level_changed = True
                            display_refresh = True
                            press_key_to_continue = False
                            reset = False
                            break
                if reset or keys["LCTRL"] or keys["RCTRL"]:
                    bmp.lang.lang_print("play.levelpack.restart")
                    bmp.audio.play("restart")
                    levelpack = copy.deepcopy(levelpack_backup)
                    levelpack_info = bmp.levelpack.default_levelpack_info.copy()
                    current_level = copy.deepcopy(levelpack.get_exact_level(levelpack.main_level_id))
                    current_space = current_level.get_exact_space(current_level.main_space_id)
                    history = [(
                        copy.deepcopy(levelpack),
                        levelpack_info.copy(),
                        current_level.level_id,
                        current_space.space_id
                    )]
                    level_changed = True
                    display_refresh = True
                    press_key_to_continue = False
                del reset
            elif keys["O"]:
                bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.savepoint")))
                savepoint_name = ""
                if keys["LCTRL"] or keys["RCTRL"]:
                    savepoint_name = bmp.lang.lang_input("input.savepoint.name")
                savepoint_name = savepoint_name if savepoint_name != "" else default_savepoint_name
                savepoint = savepoint_dict.get(savepoint_name)
                if savepoint is not None:
                    levelpack = savepoint[0]
                    levelpack_info = bmp.levelpack.default_levelpack_info.copy()
                    current_level = copy.deepcopy(levelpack.get_exact_level(savepoint[2]))
                    current_space = current_level.get_exact_space(savepoint[3])
                    bmp.lang.lang_print("play.savepoint.loaded", value=savepoint_name)
                    level_changed = True
                    display_refresh = True
                    press_key_to_continue = False
                else:
                    bmp.lang.lang_warn("warn.savepoint.not_found", value=savepoint_name)
            elif keys["P"]:
                bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.savepoint")))
                savepoint_name = ""
                if keys["LCTRL"] or keys["RCTRL"]:
                    savepoint_name = bmp.lang.lang_input("input.savepoint.name")
                savepoint_name = savepoint_name if savepoint_name != "" else default_savepoint_name
                savepoint_dict[savepoint_name] = (copy.deepcopy(levelpack), levelpack_info.copy(), current_level.level_id, current_space.space_id)
                bmp.lang.lang_print("play.savepoint.saved", value=savepoint_name)
            elif keys["TAB"]:
                bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.info")))
                bmp.lang.lang_print("play.level.current.name", value=current_level.level_id.name)
                bmp.lang.lang_print("play.space.current.name", value=current_space.space_id.name)
                bmp.lang.lang_print("play.space.current.infinite_tier", value=current_space.space_id.infinite_tier)
                if len(current_space.rule_list):
                    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.space.rule_list")))
                    for rule in current_space.rule_list:
                        str_list = []
                        for object_type in rule:
                            str_list.append(object_type.get_name())
                        print(" ".join(str_list))
                    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.level.rule_list")))
                recursion_rule_list: list[bmp.rule.Rule] = current_level.recursion_rules(current_space)[0]
                if len(recursion_rule_list):
                    for rule in recursion_rule_list:
                        str_list = []
                        for object_type in rule:
                            str_list.append(object_type.get_name())
                        print(" ".join(str_list))
                if len(levelpack.rule_list):
                    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.levelpack.rule_list")))
                    for rule in levelpack.rule_list:
                        str_list = []
                        for object_type in rule:
                            str_list.append(object_type.get_name())
                        print(" ".join(str_list))
                if len(levelpack.collectibles) != 0:
                    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.collectibles")))
                    collectible_counts: dict[type[bmp.obj.Object], int] = {}
                    for collectible in levelpack.collectibles:
                        collectible_counts.setdefault(collectible.object_type, 0)
                        collectible_counts[collectible.object_type] += 1
                    for object_type, collect_count in collectible_counts.items():
                        bmp.lang.lang_print("play.levelpack.collectibles", key=object_type.get_name(), value=collect_count)
        if current_level.game_properties:
            offset_used = False
            if current_level.game_properties.enabled(bmp.obj.TextStop):
                wiggle = 1
            if current_level.game_properties.enabled(bmp.obj.TextShift):
                game_offset[0] += window.get_width() / bmp.base.options["fps"]
            if current_level.game_properties.enabled(bmp.obj.TextMove):
                game_offset[1] += window.get_height() / (4 * bmp.base.options["fps"])
            if current_level.game_properties.enabled(bmp.obj.TextSink):
                game_offset_speed[1] += window.get_height() / (16 * bmp.base.options["fps"])
                offset_used = True
            if current_level.game_properties.enabled(bmp.obj.TextFloat):
                game_offset_speed[1] -= window.get_height() / (64 * bmp.base.options["fps"])
                offset_used = True
            if not offset_used:
                game_offset_speed[0] = game_offset_speed[0] / 2
                game_offset_speed[1] = game_offset_speed[1] / 2
            del offset_used
        if display_refresh:
            # NotImplemented
            display_refresh = False
        if levelpack_refresh:
            if current_level.game_properties.enabled(bmp.obj.TextWin):
                bmp.lang.lang_print("play.win")
                bmp.audio.play("win")
                game_running = False
            if current_level.game_properties.enabled(bmp.obj.TextDefeat):
                bmp.audio.play("defeat")
                game_running = False
                raise GameIsDefeatError()
            if current_level.game_properties.enabled(bmp.obj.TextBonus):
                bmp.audio.play("bonus")
                print("VVd4WmVGTnRXVEJOYWtaVFRqQmtWZz09")
            if current_level.game_properties.enabled(bmp.obj.TextEnd):
                bmp.lang.lang_print("play.end")
                bmp.audio.play("end")
                bmp.base.options["game_is_end"] = True
                bmp.base.save_options(bmp.base.options)
                game_running = False
            if current_level.game_properties.enabled(bmp.obj.TextDone):
                bmp.audio.play("done")
                bmp.base.options["game_is_done"] = True
                bmp.base.save_options(bmp.base.options)
                game_running = False
                raise GameIsDoneError()
            if current_level.game_properties.enabled(bmp.obj.TextOpen):
                if bmp.base.current_os == bmp.base.windows:
                    if os.path.exists("bmp.exe"):
                            os.system("start bmp.exe")
                    elif os.path.exists("bmp.py"):
                        os.system("start python bmp.py")
                elif bmp.base.current_os == bmp.base.linux:
                    os.system("python ./bmp.py &")
            if current_level.game_properties.enabled(bmp.obj.TextShut):
                game_running = False
            if current_level.game_properties.enabled(bmp.obj.TextTele):
                bmp.audio.play("tele")
                game_offset = [float(random.randrange(window.get_width())), float(random.randrange(window.get_height()))]
            if current_level.game_properties.enabled(bmp.obj.TextHot) and current_level.game_properties.enabled(bmp.obj.TextMelt):
                bmp.audio.play("melt")
                game_running = False
            if current_level.game_properties.enabled(bmp.obj.TextYou) and current_level.game_properties.enabled(bmp.obj.TextDefeat):
                bmp.audio.play("defeat")
                game_running = False
            for space in current_level.space_list:
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
                for event in current_level.sound_events:
                    bmp.audio.play(event)
                if levelpack_info["win"]:
                    bmp.audio.play("win")
                    bmp.lang.lang_print("play.level.win")
                    monochrome = bmp.obj.TextWin.get_color()
                    bmp.lang.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["end"]:
                    bmp.audio.play("end")
                    bmp.lang.lang_print("play.levelpack.end")
                    monochrome = bmp.obj.TextEnd.get_color()
                    bmp.lang.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["done"]:
                    bmp.audio.play("done")
                    bmp.lang.lang_print("play.levelpack.done")
                    monochrome = bmp.obj.TextDone.get_color()
                    bmp.lang.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["transform"]:
                    bmp.audio.play("restart")
                    bmp.lang.lang_print("play.level.transform")
                    monochrome = bmp.obj.TextLevel.get_color()
                    bmp.lang.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["selected_level"] is not None:
                    bmp.audio.play("level")
                    bmp.lang.lang_print("play.level.enter")
                    monochrome = bmp.obj.TextSelect.get_color()
                    bmp.lang.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
            else:
                press_key_to_continue = False
                level_changed = True
                if levelpack_info["win"]:
                    level = copy.deepcopy(levelpack_backup.get_level(current_level.level_id))
                    if level is not None:
                        levelpack.set_level(level)
                    super_level = levelpack.get_level(current_level.super_level_id) if current_level.super_level_id is not None else levelpack.get_exact_level(levelpack.main_level_id)
                    current_level = super_level if super_level is not None else levelpack.get_exact_level(levelpack.main_level_id)
                    current_space = current_level.main_space
                elif levelpack_info["end"]:
                    game_running = False
                elif levelpack_info["done"]:
                    game_running = False
                elif levelpack_info["transform"]:
                    super_level = levelpack.get_level(current_level.super_level_id) if current_level.super_level_id is not None else levelpack.get_exact_level(levelpack.main_level_id)
                    current_level = super_level if super_level is not None else levelpack.get_exact_level(levelpack.main_level_id)
                    current_space = current_level.main_space
                elif levelpack_info["selected_level"] is not None:
                    current_level = levelpack.get_exact_level(levelpack_info["selected_level"])
                    current_space = current_level.main_space
                levelpack.prepare(current_level)
            levelpack_refresh = False
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
        pygame.mixer.music.set_volume(1.0 if current_level.have_you() else 0.5)
        # display
        window.fill(bmp.color.current_palette[0, 4])
        space_surface_size = window.get_size()
        space_surface_pos = (0, 0)
        match current_space.static_transform["direct"]:
            case "W" | "S":
                if window.get_width() // current_space.width > window.get_height() // current_space.height:
                    space_surface_size = (window.get_height() * current_space.width // current_space.height, window.get_height())
                    space_surface_pos = ((window.get_width() - space_surface_size[0]) // 2, 0)
                elif window.get_width() // current_space.width < window.get_height() // current_space.height:
                    space_surface_size = (window.get_width(), window.get_width() * current_space.height // current_space.width)
                    space_surface_pos = (0, (window.get_height() - space_surface_size[1]) // 2)
            case "A" | "D":
                if window.get_width() // current_space.height > window.get_height() // current_space.width:
                    space_surface_size = (window.get_height() * current_space.height // current_space.width, window.get_height())
                    space_surface_pos = ((window.get_width() - space_surface_size[0]) // 2, 0)
                elif window.get_width() // current_space.height < window.get_height() // current_space.width:
                    space_surface_size = (window.get_width(), window.get_width() * current_space.width // current_space.height)
                    space_surface_pos = (0, (window.get_height() - space_surface_size[1]) // 2)
        if not current_level.game_properties.enabled(bmp.obj.TextHide):
            if not current_level.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextHide):
                smooth_value = bmp.render.calc_smooth(frame_since_last_move)
                if current_level.game_properties.enabled(bmp.obj.TextStop):
                    smooth_value = None
                space_surface = current_level.space_to_surface(current_space, wiggle, space_surface_size, smooth=smooth_value, debug=bmp.base.options["debug"])
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
            game_transform_to = [t for t, n in current_level.game_properties.enabled_dict().items() if issubclass(t, bmp.obj.Noun) and not n]
            if len(game_transform_to) != 0:
                window.fill("#00000080", (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            game_transform_to = [o.ref_type for o in game_transform_to if o is not None]
            for object_type in game_transform_to:
                window.blit(pygame.transform.scale(bmp.render.current_sprites.get(object_type.sprite_name, 0, wiggle), window.get_size()), (0, 0))
            del game_transform_to
            if current_level.game_properties.enabled(bmp.obj.TextSelect):
                select_surface = bmp.render.current_sprites.get(bmp.obj.Cursor.sprite_name, 0, wiggle, raw=True)
                select_surface = bmp.render.set_surface_color_dark(select_surface, bmp.color.float_to_hue((frame / bmp.base.options["fps"] / 6) % 1.0))
                window.blit(pygame.transform.scale(select_surface, window.get_size()), (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                del select_surface
            # offset
            game_offset_speed[0] = bmp.base.absclampf(game_offset_speed[0], window.get_width() / bmp.base.options["fps"] * 4)
            game_offset_speed[1] = bmp.base.absclampf(game_offset_speed[1], window.get_height() / bmp.base.options["fps"] * 4)
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
        real_fps = min(1000 / milliseconds, (real_fps * (bmp.base.options["fps"] - 1) + 1000 / milliseconds) / bmp.base.options["fps"])
        if keys["F1"]:
            show_fps = not show_fps
        if show_fps:
            real_fps_string = str(int(real_fps))
            for i in range(len(real_fps_string)):
                window.blit(bmp.render.current_sprites.get(f"text_{real_fps_string[i]}", 0, wiggle), (i * bmp.render.sprite_size, 0))
            del real_fps_string
        pygame.display.flip()
        milliseconds = clock.tick(bmp.base.options["fps"])
    pygame.mixer.music.stop()
    pygame.display.quit()
    return levelpack