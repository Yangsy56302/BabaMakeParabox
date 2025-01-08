import random
import copy
import os

from bmp import Audio, Base, Collect, Color, Lang, Level, Levelpack, Locate, Object, Ref, Render, Space

import pygame

class GameIsDefeatError(Exception):
    pass

class GameIsDoneError(Exception):
    pass

movements: dict[str, tuple[str, Locate.NullableDirection, Locate.Coordinate]] = {
    "W": ("S", Locate.Direction.W, Locate.Coordinate(0, -1)),
    "S": ("W", Locate.Direction.S, Locate.Coordinate(0, 1)),
    "A": ("D", Locate.Direction.A, Locate.Coordinate(-1, 0)),
    "D": ("A", Locate.Direction.D, Locate.Coordinate(1, 0)),
    " ": ("None", Locate.NullDirection.O, Locate.Coordinate(0, 0))
}

def play(levelpack: Levelpack.Levelpack) -> Levelpack.Levelpack:
    for level in levelpack.level_list:
        for space in level.space_list:
            space.set_sprite_states(0)
    levelpack.prepare(levelpack.get_exact_level(levelpack.main_level_id))
    levelpack_backup = copy.deepcopy(levelpack)
    current_level: Level.Level = levelpack.get_exact_level(levelpack.main_level_id)
    current_space: Space.Space = current_level.get_exact_space(current_level.main_space_id)
    levelpack_info: Levelpack.ReturnInfo = Levelpack.default_levelpack_info.copy()
    history: list[tuple[Levelpack.Levelpack, Levelpack.ReturnInfo, Ref.LevelID, Ref.SpaceID]] = [(
        copy.deepcopy(levelpack),
        levelpack_info.copy(),
        current_level.level_id,
        current_space.space_id
    )]
    savepoint_dict: dict[str, tuple[Levelpack.Levelpack, Levelpack.ReturnInfo, Ref.LevelID, Ref.SpaceID]] = {}
    default_savepoint_name = "_"
    window = pygame.display.set_mode((720, 720), pygame.RESIZABLE)
    display_offset = [0.0, 0.0]
    display_offset_speed = [0.0, 0.0]
    pygame.display.set_caption(f"Baba Make Parabox Version {Base.versions}")
    pygame.display.set_icon(pygame.image.load(os.path.join(".", "logo", "a8icon.png")))
    window.fill("#000000")
    pygame.key.stop_text_input()
    pygame.key.set_repeat(500, 200)
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
    mouse_pos: Locate.Coordinate
    mouse_pos_in_space: Locate.Coordinate
    space_surface_size: Locate.CoordTuple = window.get_size()
    space_surface_pos: Locate.CoordTuple = (0, 0)
    Color.set_palette(os.path.join(".", "palettes", Base.options["palette"]))
    Render.current_sprites.update()
    level_changed = False
    space_changed = False
    frame = 0
    frame_since_last_move = 0
    wiggle = 1
    milliseconds = 1000 // Base.options["fps"]
    real_fps = Base.options["fps"]
    show_fps = False
    if Base.options["bgm"]["enabled"] and Base.current_os == Base.windows:
        pygame.mixer.music.load(os.path.join("midi", Base.options["bgm"]["name"]))
        pygame.mixer.music.play(-1)
    game_running = True
    display_refresh = False
    levelpack_refresh = False
    press_key_to_continue = False
    while game_running:
        frame += 1
        frame_since_last_move += 1
        if frame % (Base.options["fps"] // 6) == 0:
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
        mouse_pos = Locate.Coordinate(*pygame.mouse.get_pos())
        mouse_pos_in_space = Locate.Coordinate(
            (mouse_pos[0] - space_surface_pos[0]) * current_space.width // space_surface_size[0],
            (mouse_pos[1] - space_surface_pos[1]) * current_space.height // space_surface_size[1]
        )
        if not press_key_to_continue:
            for key, (negative_key, op, (dx, dy)) in movements.items():
                if keys[key] and not keys.get(negative_key, False):
                    new_history: tuple[Levelpack.Levelpack, Levelpack.ReturnInfo, Ref.LevelID, Ref.SpaceID] = (
                        copy.deepcopy(levelpack),
                        levelpack.tick(current_level, op),
                        current_level.level_id,
                        current_space.space_id
                    )
                    history.append(new_history)
                    levelpack_info, current_level_id, current_space_id = new_history[1:]
                    current_level = levelpack.get_exact_level(current_level_id)
                    current_space = current_level.get_exact_space(current_space_id)
                    if current_level.game_properties.enabled(Object.TextYou):
                        display_offset[0] += dx * window.get_width() / current_space.width
                        display_offset[1] += dy * window.get_height() / current_space.height
                    if current_level.game_properties.enabled(Object.TextPush) and levelpack_info["game_push"]:
                        display_offset[0] += dx * window.get_width() / current_space.width
                        display_offset[1] += dy * window.get_height() / current_space.height
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
                if mouses[0] == 1:
                    sub_space_objs: list[Object.SpaceObject] = current_space.get_spaces_from_pos(mouse_pos_in_space)
                    sub_spaces = [current_level.get_space(o.space_id) for o in sub_space_objs]
                    sub_spaces = [w for w in sub_spaces if w is not None]
                    if len(sub_spaces) != 0:
                        space = random.choice(sub_spaces)
                        if space is not None:
                            current_space = space
                            space_changed = True
                            display_refresh = True
                elif mouses[2] == 1:
                    super_spaces = [t[0] for t in current_level.find_super_spaces(current_space.space_id)]
                    if len(super_spaces) != 0:
                        current_space = random.choice(super_spaces)
                        space_changed = True
                elif mouses[1] == 1:
                    pass
                elif mouses[3]:
                    current_space_index = current_level.space_list.index(current_space)
                    current_space_index -= 1
                    current_space_index = current_space_index % len(current_level.space_list) if current_space_index >= 0 else len(current_level.space_list) - 1
                    current_space = current_level.space_list[current_space_index]
                    space_changed = True
                    display_refresh = True
                elif mouses[4]:
                    current_space_index = current_level.space_list.index(current_space)
                    current_space_index += 1
                    current_space_index = current_space_index % len(current_level.space_list) if current_space_index >= 0 else len(current_level.space_list) - 1
                    current_space = current_level.space_list[current_space_index]
                    space_changed = True
                    display_refresh = True
            elif keys["ESCAPE"]:
                for index, (old_levelpack, old_levelpack_info, old_level_id, old_space_id) in reversed(list(enumerate(history))):
                    if old_levelpack_info["selected_level"] is not None:
                        levelpack = copy.deepcopy(old_levelpack)
                        levelpack_info = Levelpack.default_levelpack_info.copy()
                        current_level = levelpack.get_exact_level(old_level_id)
                        current_space = current_level.get_exact_space(old_space_id)
                        history = history[:index]
                        level_changed = True
                        display_refresh = True
                        press_key_to_continue = False
            elif keys["Z"]:
                if len(history) >= 1:
                    levelpack = copy.deepcopy(history[-1][0])
                    levelpack_info = Levelpack.default_levelpack_info.copy()
                    current_level = levelpack.get_exact_level(history[-1][2])
                    current_space = current_level.get_exact_space(history[-1][3])
                    if len(history) != 1:
                        history.pop()
                    level_changed = True
                    display_refresh = True
                    press_key_to_continue = False
            elif keys["R"]:
                if keys["LCTRL"] or keys["RCTRL"]:
                    Lang.lang_print("play.level.restart")
                    Audio.play("restart")
                    levelpack = copy.deepcopy(levelpack_backup)
                    levelpack_info = Levelpack.default_levelpack_info.copy()
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
            elif keys["O"]:
                Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.savepoint")))
                savepoint_name = ""
                if keys["LCTRL"] or keys["RCTRL"]:
                    savepoint_name = Lang.lang_input("input.savepoint.name")
                savepoint_name = savepoint_name if savepoint_name != "" else default_savepoint_name
                savepoint = savepoint_dict.get(savepoint_name)
                if savepoint is not None:
                    levelpack = savepoint[0]
                    levelpack_info = Levelpack.default_levelpack_info.copy()
                    current_level = copy.deepcopy(levelpack.get_exact_level(savepoint[2]))
                    current_space = current_level.get_exact_space(savepoint[3])
                    Lang.lang_print("play.savepoint.loaded", value=savepoint_name)
                    level_changed = True
                    display_refresh = True
                    press_key_to_continue = False
                else:
                    Lang.lang_print("warn.savepoint.not_found", value=savepoint_name)
            elif keys["P"]:
                Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.savepoint")))
                savepoint_name = ""
                if keys["LCTRL"] or keys["RCTRL"]:
                    savepoint_name = Lang.lang_input("input.savepoint.name")
                savepoint_name = savepoint_name if savepoint_name != "" else default_savepoint_name
                savepoint_dict[savepoint_name] = (copy.deepcopy(levelpack), levelpack_info.copy(), current_level.level_id, current_space.space_id)
                Lang.lang_print("play.savepoint.saved", value=savepoint_name)
            elif keys["TAB"]:
                Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.info")))
                Lang.lang_print("play.level.current.name", value=current_level.level_id.name)
                Lang.lang_print("play.space.current.name", value=current_space.space_id.name)
                Lang.lang_print("play.space.current.infinite_tier", value=current_space.space_id.infinite_tier)
                Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.space.rule_list")))
                for rule in current_space.rule_list:
                    str_list = []
                    for object_type in rule:
                        str_list.append(object_type.display_name)
                    print(" ".join(str_list))
                Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.level.rule_list")))
                for rule in current_level.recursion_rules(current_space)[0]:
                    str_list = []
                    for object_type in rule:
                        str_list.append(object_type.display_name)
                    print(" ".join(str_list))
                Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.levelpack.rule_list")))
                for rule in levelpack.rule_list:
                    str_list = []
                    for object_type in rule:
                        str_list.append(object_type.display_name)
                    print(" ".join(str_list))
                Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.collectibles")))
                if len(levelpack.collectibles) == 0:
                    Lang.lang_print("play.levelpack.collectibles.empty")
                else:
                    for collects_type in Collect.collectible_dict.keys():
                        collects_number = len({c for c in levelpack.collectibles if isinstance(c, collects_type)})
                        if collects_number != 0:
                            Lang.lang_print("play.levelpack.collectibles", key=collects_type.json_name, value=collects_number)
        if current_level.game_properties:
            offset_used = False
            if current_level.game_properties.enabled(Object.TextStop):
                wiggle = 1
            if current_level.game_properties.enabled(Object.TextShift):
                display_offset[0] += window.get_width() / Base.options["fps"]
            if current_level.game_properties.enabled(Object.TextMove):
                display_offset[1] += window.get_height() / (4 * Base.options["fps"])
            if current_level.game_properties.enabled(Object.TextSink):
                display_offset_speed[1] += window.get_height() / (16 * Base.options["fps"])
                offset_used = True
            if current_level.game_properties.enabled(Object.TextFloat):
                display_offset_speed[1] -= window.get_height() / (64 * Base.options["fps"])
                offset_used = True
            if not offset_used:
                display_offset_speed[0] = display_offset_speed[0] / 2
                display_offset_speed[1] = display_offset_speed[1] / 2
            del offset_used
        if display_refresh:
            # NotImplemented
            display_refresh = False
        if levelpack_refresh:
            if current_level.game_properties.enabled(Object.TextWin):
                Lang.lang_print("play.win")
                Audio.play("win")
                game_running = False
            if current_level.game_properties.enabled(Object.TextDefeat):
                Audio.play("defeat")
                game_running = False
                raise GameIsDefeatError()
            if current_level.game_properties.enabled(Object.TextBonus):
                Audio.play("bonus")
                print("VVd4WmVGTnRXVEJOYWtaVFRqQmtWZz09")
            if current_level.game_properties.enabled(Object.TextEnd):
                Lang.lang_print("play.end")
                Audio.play("end")
                Base.options["game_is_end"] = True
                Base.save_options(Base.options)
                game_running = False
            if current_level.game_properties.enabled(Object.TextDone):
                Audio.play("done")
                Base.options["game_is_done"] = True
                Base.save_options(Base.options)
                game_running = False
                raise GameIsDoneError()
            if current_level.game_properties.enabled(Object.TextOpen):
                if Base.current_os == Base.windows:
                    if os.path.exists("bmp.exe"):
                            os.system("start bmp.exe")
                    elif os.path.exists("bmp.py"):
                        os.system("start python bmp.py")
                elif Base.current_os == Base.linux:
                    os.system("python ./bmp.py &")
            if current_level.game_properties.enabled(Object.TextShut):
                game_running = False
            if current_level.game_properties.enabled(Object.TextTele):
                Audio.play("tele")
                display_offset = [float(random.randrange(window.get_width())), float(random.randrange(window.get_height()))]
            if current_level.game_properties.enabled(Object.TextHot) and current_level.game_properties.enabled(Object.TextMelt):
                Audio.play("melt")
                game_running = False
            if current_level.game_properties.enabled(Object.TextYou) and current_level.game_properties.enabled(Object.TextDefeat):
                Audio.play("defeat")
                game_running = False
            for space in current_level.space_list:
                for game_obj in space.get_objs_from_type(Object.Game):
                    if Base.current_os == Base.windows:
                        if os.path.exists("bmp.exe"):
                            os.system(f"start submp.exe {game_obj.ref_type.json_name}")
                        elif os.path.exists("bmp.py"):
                            os.system(f"start python submp.py {game_obj.ref_type.json_name}")
                    elif Base.current_os == Base.linux:
                        os.system(f"python ./submp.py {game_obj.ref_type.json_name} &")
            if not press_key_to_continue:
                frame_since_last_move = 0
                for event in current_level.sound_events:
                    Audio.play(event)
                if levelpack_info["win"]:
                    Audio.play("win")
                    Lang.lang_print("play.level.win")
                    Lang.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["end"]:
                    Audio.play("end")
                    Lang.lang_print("play.levelpack.end")
                    Lang.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["done"]:
                    Audio.play("done")
                    Lang.lang_print("play.levelpack.done")
                    Lang.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["transform"]:
                    Audio.play("restart")
                    Lang.lang_print("play.level.transform")
                    Lang.lang_print("press_any_key_to_continue")
                    press_key_to_continue = True
                elif levelpack_info["selected_level"] is not None:
                    Audio.play("level")
                    Lang.lang_print("play.level.enter")
                    Lang.lang_print("press_any_key_to_continue")
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
        if level_changed:
            space_changed = True
            Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.level")))
            Lang.lang_print("play.level.current.name", value=current_level.level_id.name)
            level_changed = False
        if space_changed:
            Lang.lang_print(Lang.seperator_line(Lang.lang_format("title.space")))
            Lang.lang_print("play.space.current.name", value=current_space.space_id.name)
            Lang.lang_print("play.space.current.infinite_tier", value=current_space.space_id.infinite_tier)
            space_changed = False
        pygame.mixer.music.set_volume(1.0 if current_level.have_you() else 0.5)
        # display
        window.fill("#000000")
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
        if not current_level.game_properties.enabled(Object.TextHide):
            if not current_level.properties[Object.default_level_object_type].enabled(Object.TextHide):
                smooth_value = Render.calc_smooth(frame_since_last_move)
                if current_level.game_properties.enabled(Object.TextStop):
                    smooth_value = None
                space_surface = current_level.space_to_surface(current_space, wiggle, space_surface_size, smooth=smooth_value, debug=Base.options["debug"])
                window.blit(pygame.transform.scale(space_surface, space_surface_size), space_surface_pos)
                del smooth_value
            # game transform
            game_transform_to = [t for t, n in current_level.game_properties.enabled_dict().items() if issubclass(t, Object.Noun) and not n]
            if len(game_transform_to) != 0:
                transparent_black_background = pygame.Surface(window.get_size(), pygame.SRCALPHA)
                transparent_black_background.fill("#00000080")
                window.blit(transparent_black_background, (0, 0))
            game_transform_to = [o.ref_type for o in game_transform_to if o is not None]
            for object_type in game_transform_to:
                window.blit(pygame.transform.scale(Render.current_sprites.get(object_type.json_name, 0, wiggle), window.get_size()), (0, 0))
            del game_transform_to
            if current_level.game_properties.enabled(Object.TextSelect):
                select_surface = Render.current_sprites.get(Object.Cursor.json_name, 0, wiggle, raw=True)
                select_surface = Render.set_surface_color_dark(select_surface, Color.float_to_hue((frame / Base.options["fps"] / 6) % 1.0))
                window.blit(pygame.transform.scale(select_surface, window.get_size()), (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                del select_surface
            # offset
            display_offset_speed[0] = Base.absclampf(display_offset_speed[0], window.get_width() / Base.options["fps"] * 4)
            display_offset_speed[1] = Base.absclampf(display_offset_speed[1], window.get_height() / Base.options["fps"] * 4)
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
        # fps
        real_fps = min(1000 / milliseconds, (real_fps * (Base.options["fps"] - 1) + 1000 / milliseconds) / Base.options["fps"])
        if keys["F1"]:
            show_fps = not show_fps
        if show_fps:
            real_fps_string = str(int(real_fps))
            for i in range(len(real_fps_string)):
                window.blit(Render.current_sprites.get(f"text_{real_fps_string[i]}", 0, wiggle), (i * Render.sprite_size, 0))
            del real_fps_string
        pygame.display.flip()
        milliseconds = clock.tick(Base.options["fps"])
    pygame.mixer.music.stop()
    pygame.display.quit()
    return levelpack