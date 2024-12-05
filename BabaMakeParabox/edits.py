import copy
import random

from BabaMakeParabox import basics, languages, colors, refs, spaces, objects, collects, rules, worlds, displays, levels, levelpacks

import pygame

def levelpack_editor(levelpack: levelpacks.Levelpack) -> levelpacks.Levelpack:
    for level in levelpack.level_list:
        for world in level.world_list:
            world.set_sprite_states(0)
    history = [copy.deepcopy(levelpack)]
    current_level_index: int = 0
    current_level = levelpack.level_list[current_level_index]
    current_world_index: int = 0
    current_world = current_level.world_list[current_world_index]
    current_object_type = objects.Baba
    current_orient = spaces.Orient.S
    current_cursor_pos = spaces.Coord(0, 0)
    current_clipboard = []
    window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption(f"Baba Make Parabox Editor Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("bmp.png"))
    pygame.key.stop_text_input()
    clock = pygame.time.Clock()
    keybinds = {
        pygame.K_w: "W",
        pygame.K_s: "S",
        pygame.K_a: "A",
        pygame.K_d: "D",
        pygame.K_z: "Z",
        pygame.K_x: "X",
        pygame.K_c: "C",
        pygame.K_v: "V",
        pygame.K_n: "N",
        pygame.K_m: "M",
        pygame.K_r: "R",
        pygame.K_t: "T",
        pygame.K_1: "1",
        pygame.K_2: "2",
        pygame.K_3: "3",
        pygame.K_4: "4",
        pygame.K_5: "5",
        pygame.K_6: "6",
        pygame.K_7: "7",
        pygame.K_8: "8",
        pygame.K_9: "9",
        pygame.K_0: "0",
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_LEFT: "LEFT",
        pygame.K_RIGHT: "RIGHT",
        pygame.K_MINUS: "-",
        pygame.K_EQUALS: "=",
        pygame.K_RETURN: "RETURN",
        pygame.K_BACKSPACE: "BACKSPACE",
        pygame.K_TAB: "TAB",
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
    mouse_pos: spaces.Coord
    mouse_pos_in_world: spaces.Coord
    world_surface_size = window.get_size()
    world_surface_pos = (0, 0)
    displays.sprites.update()
    window.fill("#000000")
    object_type_shortcuts: dict[int, type[objects.Object]] = {k: objects.object_name[v] for k, v in enumerate(basics.options["object_type_shortcuts"])}
    level_changed = True
    world_changed = True
    frame = 0
    wiggle = 1
    editor_running = True
    milliseconds = 1000 // basics.options["fps"]
    real_fps = basics.options["fps"]
    show_fps = False
    while editor_running:
        frame += 1
        if frame >= basics.options["fpw"]:
            frame = 0
            wiggle = wiggle % 3 + 1
        for key in keybinds.values():
            keys[key] = False
        for key in keymods.values():
            keys[key] = False
        mouse_scroll: tuple[bool, bool] = (False, False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editor_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in keybinds.keys():
                    keys[keybinds[event.key]] = True
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
        mouse_pos = spaces.Coord(*pygame.mouse.get_pos())
        mouse_pos_in_world = spaces.Coord(
            (mouse_pos[0] - world_surface_pos[0]) * current_world.width // world_surface_size[0],
            (mouse_pos[1] - world_surface_pos[1]) * current_world.height // world_surface_size[1]
        )
        if not current_world.out_of_range(mouse_pos_in_world):
            current_cursor_pos = mouse_pos_in_world
        if any(mouses):
            if not current_world.out_of_range(mouse_pos_in_world):
                if mouses[0] == 1:
                    if keys["LALT"] or keys["RALT"]: # enter world; enter level (shift)
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            sub_level_objs: list[objects.LevelObject] = current_world.get_levels_from_pos(mouse_pos_in_world)
                            sub_levels = [levelpack.get_level(o.level_id) for o in sub_level_objs]
                            sub_levels = [w for w in sub_levels if w is not None]
                            if len(sub_levels) != 0:
                                level = random.choice(sub_levels)
                                if level is not None:
                                    current_level = level
                                    level_changed = True
                        else:
                            sub_world_objs: list[objects.WorldObject] = current_world.get_worlds_from_pos(mouse_pos_in_world)
                            sub_worlds = [current_level.get_world(o.world_id) for o in sub_world_objs]
                            sub_worlds = [w for w in sub_worlds if w is not None]
                            if len(sub_worlds) != 0:
                                world = random.choice(sub_worlds)
                                if world is not None:
                                    current_world = world
                                    world_changed = True
                    else: # place object; with detail (shift); allow overlap (ctrl)
                        if keys["LSHIFT"] or keys["RSHIFT"] or len(current_world.get_objs_from_pos(current_cursor_pos)) == 0:
                            history.append(copy.deepcopy(levelpack))
                            if issubclass(current_object_type, objects.LevelObject):
                                if keys["LCTRL"] or keys["RCTRL"]:
                                    languages.lang_print("seperator.title", text=languages.lang_format("title.new"))
                                    name = languages.lang_input("edit.level.new.name")
                                    level_id: refs.LevelID = refs.LevelID(name)
                                    if levelpack.get_level(level_id) is None:
                                        level_id = current_level.level_id
                                    icon_name = languages.lang_input("edit.level.new.icon.name")
                                    icon_name = icon_name if icon_name != "" else "empty"
                                    while True:
                                        icon_color = languages.lang_input("edit.level.new.icon.color")
                                        try:
                                            icon_color = colors.str_to_hex(icon_color) if icon_color != "" else colors.WHITE
                                        except ValueError:
                                            languages.lang_print("warn.value.invalid", value=icon_color, cls="color")
                                        else:
                                            break
                                else:
                                    level_id: refs.LevelID = current_level.level_id
                                    icon_name = "empty"
                                    icon_color = colors.WHITE
                                level_object_extra: objects.LevelObjectExtra = {"icon": {"name": icon_name, "color": icon_color}}
                                current_world.new_obj(current_object_type(current_cursor_pos, current_orient, level_id=level_id, level_object_extra=level_object_extra))
                            elif issubclass(current_object_type, objects.WorldObject):
                                world_id: refs.WorldID = current_world.world_id
                                if keys["LCTRL"] or keys["RCTRL"]:
                                    languages.lang_print("seperator.title", text=languages.lang_format("title.new"))
                                    name = languages.lang_input("edit.world.new.name")
                                    while True:
                                        infinite_tier = languages.lang_input("edit.world.new.infinite_tier")
                                        try:
                                            infinite_tier = int(infinite_tier) if infinite_tier != "" else 0
                                        except ValueError:
                                            languages.lang_print("warn.value.invalid", value=infinite_tier, cls="int")
                                        else:
                                            break
                                    if current_level.get_world(refs.WorldID(name, infinite_tier)) is not None:
                                        world_id = refs.WorldID(name, infinite_tier)
                                current_world.new_obj(current_object_type(current_cursor_pos, current_orient, world_id=world_id))
                            elif issubclass(current_object_type, objects.Path):
                                unlocked = False
                                conditions: dict[type[collects.Collectible], int] = {}
                                if keys["LCTRL"] or keys["RCTRL"]:
                                    languages.lang_print("seperator.title", text=languages.lang_format("title.new"))
                                    unlocked = languages.lang_input("edit.path.new.unlocked") in languages.yes
                                    more_condition = languages.lang_input("edit.path.new.condition") in languages.yes
                                    while more_condition:
                                        while True:
                                            for collects_type, collects_name in collects.collectible_dict.items():
                                                languages.lang_print("edit.path.new.condition.type", key=collects_type, value=collects_name)
                                            collects_type = {v: k for k, v in collects.collectible_dict.items()}.get(languages.lang_input("input.string"))
                                            if collects_type is None:
                                                languages.lang_print("warn.value.invalid", value=collects_type, cls=collects.Collectible.__name__)
                                                continue
                                            break
                                        while True:
                                            collects_count = languages.lang_input("input.number")
                                            try:
                                                collects_count = int(collects_count)
                                            except ValueError:
                                                languages.lang_print("warn.value.invalid", value=collects_count, cls="int")
                                            else:
                                                break
                                        conditions[collects_type] = collects_count
                                        more_condition = languages.lang_input("edit.path.new.condition") in languages.yes
                                current_world.new_obj(current_object_type(current_cursor_pos, current_orient, unlocked=unlocked, conditions=conditions))
                            else:
                                current_world.new_obj(current_object_type(current_cursor_pos, current_orient))
                elif mouses[2] == 1:
                    if keys["LALT"] or keys["RALT"]: # leave world; leave level (shift)
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            level = levelpack.get_level(current_level.super_level_id if current_level.super_level_id is not None else levelpack.main_level_id)
                            current_level = level if level is not None else levelpack.get_exact_level(levelpack.main_level_id)
                            level_changed = True
                        else:
                            super_worlds = [t[0] for t in current_level.find_super_worlds(current_world.world_id)]
                            if len(super_worlds) != 0:
                                current_world = random.choice(super_worlds)
                                world_changed = True
                    else: # new world; new level (alt)
                        history.append(copy.deepcopy(levelpack))
                        current_world.del_objs_from_pos(current_cursor_pos)
                elif mouses[1] == 1:
                    pass
                # object select from list
                elif mouses[3]:
                    if keys["LALT"] or keys["RALT"]:
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            current_level_index -= 1
                            current_world_index = 0
                            level_changed = True
                        else:
                            current_world_index -= 1
                            world_changed = True
                    elif keys["LSHIFT"] or keys["RSHIFT"]:
                        obj_to_noun = objects.get_noun_from_type(current_object_type)
                        if obj_to_noun not in objects.not_in_editor:
                            current_object_type = obj_to_noun
                    else:
                        current_object_type_list = [t for t in objects.object_name.values() if t not in objects.not_in_editor]
                        current_object_type_index = current_object_type_list.index(current_object_type)
                        current_object_type = current_object_type_list[current_object_type_index - 1 if current_object_type_index >= 0 else len(current_object_type_list) - 1]
                elif mouses[4]:
                    if keys["LALT"] or keys["RALT"]:
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            current_level_index += 1
                            current_world_index = 0
                            level_changed = True
                        else:
                            current_world_index += 1
                            world_changed = True
                    elif keys["LSHIFT"] or keys["RSHIFT"]:
                        if issubclass(current_object_type, objects.Noun) and current_object_type.ref_type not in objects.not_in_editor:
                            current_object_type = current_object_type.ref_type
                    else:
                        current_object_type_list = [t for t in objects.object_name.values() if t not in objects.not_in_editor]
                        current_object_type_index = current_object_type_list.index(current_object_type)
                        current_object_type = current_object_type_list[current_object_type_index + 1 if current_object_type_index < len(current_object_type_list) - 1 else 0]
        # cursor move; object facing change (alt)
        if keys["W"] or keys["UP"]:
            current_orient = spaces.Orient.W
        elif keys["S"] or keys["DOWN"]:
            current_orient = spaces.Orient.S
        elif keys["A"] or keys["LEFT"]:
            current_orient = spaces.Orient.A
        elif keys["D"] or keys["RIGHT"]:
            current_orient = spaces.Orient.D
        # object select from palette / save to palette (shift)
        elif any(map(lambda i: keys[str(i)], range(10))):
            for i in range(10):
                if keys[str(i)]:
                    if keys["LSHIFT"] or keys["RSHIFT"]:
                        object_type_shortcuts[(i - 1) % 10] = current_object_type
                        basics.options["object_type_shortcuts"][(i - 1) % 10] = {v: k for k, v in objects.object_name.items()}[current_object_type]
                    else:
                        current_object_type = object_type_shortcuts[(i - 1) % 10]
        elif keys["N"]:
            if keys["LALT"] or keys["RALT"]:
                languages.lang_print("seperator.title", text=languages.lang_format("title.new"))
                if languages.lang_input("edit.level.new") not in languages.no:
                    history.append(copy.deepcopy(levelpack))
                    level_name = languages.lang_input("edit.level.new.name")
                    level_id: refs.LevelID = refs.LevelID(level_name)
                    super_level_name = languages.lang_input("edit.level.new.super_level.name")
                    super_level_id: refs.LevelID = refs.LevelID(super_level_name) if super_level_name != "" else current_level.level_id
                    name = languages.lang_input("edit.world.new.name")
                    while True:
                        width = languages.lang_input("edit.world.new.width")
                        try:
                            width = int(width) if width != "" else basics.options["default_new_world"]["width"]
                        except ValueError:
                            languages.lang_print("warn.value.invalid", value=width, cls="int")
                        else:
                            break
                    while True:
                        height = languages.lang_input("edit.world.new.height")
                        try:
                            height = int(height) if height != "" else basics.options["default_new_world"]["height"]
                        except ValueError:
                            languages.lang_print("warn.value.invalid", value=height, cls="int")
                        else:
                            break
                    size = spaces.Coord(width, height)
                    while True:
                        infinite_tier = languages.lang_input("edit.world.new.infinite_tier")
                        try:
                            infinite_tier = int(infinite_tier) if infinite_tier != "" else 0
                        except ValueError:
                            languages.lang_print("warn.value.invalid", value=infinite_tier, cls="int")
                        else:
                            break
                    while True:
                        color = languages.lang_input("edit.world.new.color")
                        try:
                            color = colors.str_to_hex(color) if color != "" else basics.options["default_new_world"]["color"]
                        except ValueError:
                            languages.lang_print("warn.value.invalid", value=color, cls="color")
                        else:
                            break
                    default_world = worlds.World(refs.WorldID(name, infinite_tier), size, color)
                    if languages.lang_input("edit.level.new.is_map") in languages.yes:
                        pass
                    levelpack.level_list.append(levels.Level(level_id, [default_world], super_level_id=super_level_id, main_world_id=refs.WorldID(name, infinite_tier), map_info=None, rule_list=levelpack.rule_list))
                    current_level_index = len(levelpack.level_list) - 1
                    current_world_index = 0
                    level_changed = True
            else:
                if languages.lang_input("edit.world.new") not in languages.no:
                    history.append(copy.deepcopy(levelpack))
                    name = languages.lang_input("edit.world.new.name")
                    while True:
                        width = languages.lang_input("edit.world.new.width")
                        try:
                            width = int(width) if width != "" else basics.options["default_new_world"]["width"]
                        except ValueError:
                            languages.lang_print("warn.value.invalid", value=width, cls="int")
                        else:
                            break
                    while True:
                        height = languages.lang_input("edit.world.new.height")
                        try:
                            height = int(height) if height != "" else basics.options["default_new_world"]["height"]
                        except ValueError:
                            languages.lang_print("warn.value.invalid", value=height, cls="int")
                        else:
                            break
                    size = spaces.Coord(width, height)
                    while True:
                        infinite_tier = languages.lang_input("edit.world.new.infinite_tier")
                        try:
                            infinite_tier = int(infinite_tier) if infinite_tier != "" else 0
                        except ValueError:
                            languages.lang_print("warn.value.invalid", value=infinite_tier, cls="int")
                        else:
                            break
                    while True:
                        color = languages.lang_input("edit.world.new.color")
                        try:
                            color = colors.str_to_hex(color) if color != "" else basics.options["default_new_world"]["color"]
                        except ValueError:
                            languages.lang_print("warn.value.invalid", value=color, cls="color")
                        else:
                            break
                    current_level.world_list.append(worlds.World(refs.WorldID(name, infinite_tier), size, color))
                    current_world_index = len(current_level.world_list) - 1
                    world_changed = True
        # delete current world / level (alt)
        elif keys["M"]:
            languages.lang_print("seperator.title", text=languages.lang_format("title.delete"))
            if keys["LALT"] or keys["RALT"]:
                if languages.lang_input("edit.level.delete") in languages.yes:
                    levelpack.level_list.pop(current_level_index)
                    current_level_index -= 1
                    current_world_index = 0
                    level_changed = True
            else:
                if languages.lang_input("edit.world.delete") in languages.yes:
                    current_level.world_list.pop(current_world_index)
                    current_world_index -= 1
                    world_changed = True
        # add global rule; remove global rule (shift)
        elif keys["R"]:
            languages.lang_print("seperator.title", text=languages.lang_format("title.levelpack.rule_list"))
            text_rule = languages.lang_input("edit.levelpack.new.rule").upper().split()
            type_rule: rules.Rule = []
            valid_input = True
            for text in text_rule:
                object_type = objects.object_name.get(text)
                if object_type is not None:
                    if issubclass(object_type, objects.Text):
                        type_rule.append(object_type)
                    else:
                        valid_input = False
                        break
                else:
                    valid_input = False
                    break
            if valid_input:
                if keys["LSHIFT"] or keys["RSHIFT"]:
                    levelpack.rule_list.remove(type_rule)
                else:
                    levelpack.rule_list.append(type_rule)
            languages.lang_print("seperator.title", text=languages.lang_format("title.levelpack.rule_list"))
            for rule in levelpack.rule_list:
                str_list = []
                for object_type in rule:
                    str_list.append(object_type.display_name)
                print(" ".join(str_list))
        # edit id for current world / level (alt)
        elif keys["T"]:
            languages.lang_print("seperator.title", text=languages.lang_format("title.rename"))
            if keys["LALT"] or keys["RALT"]:
                current_level.level_id.name = languages.lang_input("edit.level.rename")
            else:
                current_world.world_id.name = languages.lang_input("edit.world.rename")
                while True:
                    infinite_tier = languages.lang_input("edit.world.new.infinite_tier")
                    try:
                        current_world.world_id.infinite_tier = int(infinite_tier)
                    except ValueError:
                        languages.lang_print("warn.value.invalid", value=infinite_tier, cls="int")
                    else:
                        break
        # undo
        elif keys["Z"] and (keys["LCTRL"] or keys["RCTRL"]):
            if len(history) > 1:
                levelpack = copy.deepcopy(history.pop())
            else:
                levelpack = copy.deepcopy(history[0])
            level_changed = True
        # cut, copy, paste
        elif keys["X"] and (keys["LCTRL"] or keys["RCTRL"]):
            history.append(copy.deepcopy(levelpack))
            current_clipboard = current_world.get_objs_from_pos(current_cursor_pos)
            current_clipboard = copy.deepcopy(current_clipboard)
            list(map(objects.Object.reset_uuid, current_clipboard))
            current_world.del_objs_from_pos(current_cursor_pos)
        elif keys["C"] and (keys["LCTRL"] or keys["RCTRL"]):
            history.append(copy.deepcopy(levelpack))
            current_clipboard = current_world.get_objs_from_pos(current_cursor_pos)
            current_clipboard = copy.deepcopy(current_clipboard)
            list(map(objects.Object.reset_uuid, current_clipboard))
        elif keys["V"] and (keys["LCTRL"] or keys["RCTRL"]):
            history.append(copy.deepcopy(levelpack))
            current_clipboard = copy.deepcopy(current_clipboard)
            list(map(objects.Object.reset_uuid, current_clipboard))
            for obj in current_clipboard:
                obj.pos = current_cursor_pos
                current_world.new_obj(obj)
                if isinstance(obj, objects.WorldObject):
                    for level in levelpack.level_list:
                        world = level.get_world(obj.world_id)
                        if world is not None:
                            for new_world in level.world_list:
                                current_level.set_world(new_world)
        if level_changed:
            world_changed = True
            languages.lang_print("seperator.title", text=languages.lang_format("title.level"))
            current_level_index = current_level_index % len(levelpack.level_list) if current_level_index >= 0 else len(levelpack.level_list) - 1
            current_level = levelpack.level_list[current_level_index]
            languages.lang_print("edit.level.current.name", value=current_level.level_id.name)
            level_changed = False
        if world_changed:
            languages.lang_print("seperator.title", text=languages.lang_format("title.world"))
            if current_cursor_pos[0] > current_world.width:
                current_cursor_pos = spaces.Coord(current_world.width, current_cursor_pos[1])
            if current_cursor_pos[1] > current_world.height:
                current_cursor_pos = spaces.Coord(current_cursor_pos[0], current_world.height)
            current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
            current_world = current_level.world_list[current_world_index]
            languages.lang_print("edit.world.current.name", value=current_world.world_id.name)
            languages.lang_print("edit.world.current.infinite_tier", value=current_world.world_id.infinite_tier)
            world_changed = False
        # display
        for world in current_level.world_list:
            world.set_sprite_states(0)
        window.fill("#000000")
        displays.set_pixel_size(spaces.Coord(*window.get_size()))
        world_surface = current_level.world_to_surface(current_world, wiggle, cursor=current_cursor_pos, debug=True)
        world_surface_size = (window.get_height() * current_world.width // current_world.height, window.get_height())
        world_surface_pos = (0, 0)
        window.blit(pygame.transform.scale(world_surface, world_surface_size), world_surface_pos)
        obj_surface = displays.simple_type_to_surface(current_object_type, wiggle=wiggle, debug=True)
        if issubclass(current_object_type, objects.WorldObject):
            world = current_level.get_world(current_world.world_id)
            if world is not None:
                obj_surface = displays.simple_type_to_surface(current_object_type, wiggle=wiggle, default_surface=world_surface, debug=True)
        obj_surface = pygame.transform.scale(obj_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
        window.blit(obj_surface, (window.get_width() - displays.pixel_sprite_size, 0))
        for index, object_type in object_type_shortcuts.items():
            obj_surface = displays.simple_type_to_surface(object_type, wiggle=wiggle, debug=True)
            if issubclass(object_type, objects.WorldObject):
                world = current_level.get_world(current_world.world_id)
                if world is not None:
                    obj_surface = displays.simple_type_to_surface(object_type, wiggle=wiggle, default_surface=world_surface, debug=True)
            obj_surface = pygame.transform.scale(obj_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
            obj_surface_pos = (window.get_width() + (index % 5 * displays.pixel_sprite_size) - (displays.pixel_sprite_size * 5),
                               window.get_height() + (index // 5 * displays.pixel_sprite_size) - (displays.pixel_sprite_size * 2))
            obj_surface.blit(
                displays.set_alpha(displays.sprites.get("text_" + str((index + 1) % 10), 0, wiggle), 0x80),
                (displays.pixel_sprite_size - displays.sprite_size, displays.pixel_sprite_size - displays.sprite_size)
            )
            window.blit(obj_surface, obj_surface_pos)
        real_fps = min(1000 / milliseconds, (real_fps * (basics.options["fps"] - 1) + 1000 / milliseconds) / basics.options["fps"])
        if keys["F1"]:
            show_fps = not show_fps
        if show_fps:
            real_fps_string = str(int(real_fps))
            for i in range(len(real_fps_string)):
                window.blit(displays.sprites.get(f"text_{real_fps_string[i]}", 0, wiggle), (i * displays.sprite_size, 0))
        pygame.display.flip()
        milliseconds = clock.tick(basics.options["fps"])
    pygame.display.quit()
    return levelpack