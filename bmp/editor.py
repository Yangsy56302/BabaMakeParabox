import os
import copy
import random
import string

import bmp.base
import bmp.color
import bmp.lang
import bmp.level
import bmp.levelpack
import bmp.loc
import bmp.obj
import bmp.ref
import bmp.render
import bmp.rule
import bmp.space

import pygame

def levelpack_editor(levelpack: bmp.levelpack.Levelpack) -> bmp.levelpack.Levelpack:
    for level in levelpack.level_list:
        for space in level.space_list:
            space.set_sprite_states(0)
    history = [copy.deepcopy(levelpack)]
    current_level_index: int = 0
    current_level = levelpack.level_list[current_level_index]
    current_space_index: int = 0
    current_space = current_level.space_list[current_space_index]
    current_object_type = bmp.obj.TextSpace
    current_orient = bmp.loc.Orient.S
    current_cursor_pos: bmp.loc.Coord[int] = (0, 0)
    cursor_pos_changed: bool
    current_clipboard = []
    window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption(f"Baba Make Parabox Editor Version {bmp.base.versions}")
    pygame.display.set_icon(pygame.image.load(os.path.join(".", "logo", "c8icon.png")))
    pygame.key.stop_text_input()
    pygame.key.set_repeat(bmp.base.options["long_press"]["delay"], bmp.base.options["long_press"]["interval"])
    clock = pygame.time.Clock()
    keybinds = {
        pygame.K_w: "W",
        pygame.K_s: "S",
        pygame.K_a: "A",
        pygame.K_d: "D",
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_LEFT: "LEFT",
        pygame.K_RIGHT: "RIGHT",
        pygame.K_n: "N",
        pygame.K_m: "M",
        pygame.K_r: "R",
        pygame.K_t: "T",
        pygame.K_z: "Z",
        pygame.K_x: "X",
        pygame.K_c: "C",
        pygame.K_v: "V",
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
    mouse_pos: bmp.loc.Coord
    mouse_pos_in_space: bmp.loc.Coord
    space_surface_size = window.get_size()
    space_surface_pos = (0, 0)
    bmp.color.set_palette(os.path.join(".", "palettes", bmp.base.options["palette"]))
    bmp.render.current_sprites.update()
    window.fill("#000000")
    object_type_shortcuts: dict[int, type[bmp.obj.Object]] = {k: bmp.obj.name_to_class[v] for k, v in enumerate(bmp.base.options["object_type_shortcuts"])}
    level_changed = True
    space_changed = True
    frame = 0
    wiggle = 1
    editor_running = True
    milliseconds = 1000 // bmp.base.options["fps"]
    real_fps = bmp.base.options["fps"]
    show_fps = False
    while editor_running:
        frame += 1
        if frame % (bmp.base.options["fps"] // 6) == 0:
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
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_in_space = (
            (mouse_pos[0] - space_surface_pos[0]) * current_space.width // space_surface_size[0],
            (mouse_pos[1] - space_surface_pos[1]) * current_space.height // space_surface_size[1]
        )
        if not current_space.out_of_range(mouse_pos_in_space):
            cursor_pos_changed = False
            if current_cursor_pos != mouse_pos_in_space:
                cursor_pos_changed = True
            current_cursor_pos = mouse_pos_in_space
        if any(mouses):
            if not current_space.out_of_range(mouse_pos_in_space):
                if mouses[0] != 0:
                    if mouses[0] and (keys["LALT"] or keys["RALT"]):
                        # enter space; enter level (shift)
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            sub_level_objs: list[bmp.obj.LevelObject] = current_space.get_levels_from_pos(mouse_pos_in_space)
                            sub_levels = [levelpack.get_level(o.level_id) for o in sub_level_objs]
                            sub_levels = [w for w in sub_levels if w is not None]
                            if len(sub_levels) != 0:
                                level = random.choice(sub_levels)
                                if level is not None:
                                    current_level = level
                                    level_changed = True
                        else:
                            sub_space_objs: list[bmp.obj.SpaceObject] = current_space.get_spaces_from_pos(mouse_pos_in_space)
                            sub_spaces = [current_level.get_space(o.space_id) for o in sub_space_objs]
                            sub_spaces = [w for w in sub_spaces if w is not None]
                            if len(sub_spaces) != 0:
                                space = random.choice(sub_spaces)
                                if space is not None:
                                    current_space = space
                                    space_changed = True
                    elif mouses[0] == 1 or cursor_pos_changed:
                        # place object; with detail (shift); allow overlap (ctrl)
                        if keys["LSHIFT"] or keys["RSHIFT"] or len(current_space.get_objs_from_pos(current_cursor_pos)) == 0:
                            history.append(copy.deepcopy(levelpack))
                            if issubclass(current_object_type, bmp.obj.LevelObject):
                                if keys["LCTRL"] or keys["RCTRL"]:
                                    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.new")))
                                    name = bmp.lang.lang_input("edit.level.new.name")
                                    level_id: bmp.ref.LevelID = bmp.ref.LevelID(name)
                                    if levelpack.get_level(level_id) is None:
                                        level_id = current_level.level_id
                                    icon_name = bmp.lang.lang_input("edit.level.new.icon.name")
                                    icon_name = icon_name if icon_name != "" else "empty"
                                    while True:
                                        icon_color = bmp.lang.lang_input("edit.level.new.icon.color")
                                        if color == "":
                                            color = bmp.color.current_palette[0, 3]
                                        else:
                                            try:
                                                icon_color = bmp.color.str_to_hex(icon_color)
                                            except ValueError:
                                                try:
                                                    icon_palette_str = icon_color.lstrip("([").rstrip("])").split(",")
                                                    icon_color = bmp.color.current_palette[int(icon_palette_str[0].strip()), int(icon_palette_str[1].strip())]
                                                except ValueError:
                                                    bmp.lang.lang_warn("warn.value.invalid", value=icon_color, cls="color")
                                                else:
                                                    break
                                            else:
                                                break
                                else:
                                    level_id: bmp.ref.LevelID = current_level.level_id
                                    icon_name = "empty"
                                    icon_color = bmp.color.current_palette[0, 3]
                                level_extra: bmp.obj.LevelObjectExtra = {"icon": {"name": icon_name, "color": icon_color}}
                                current_space.new_obj(current_object_type(current_cursor_pos, current_orient, level_id=level_id, level_extra=level_extra))
                            elif issubclass(current_object_type, bmp.obj.SpaceObject):
                                space_id: bmp.ref.SpaceID = current_space.space_id
                                if keys["LCTRL"] or keys["RCTRL"]:
                                    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.new")))
                                    name = bmp.lang.lang_input("edit.space.new.name")
                                    while True:
                                        infinite_tier = bmp.lang.lang_input("edit.space.new.infinite_tier")
                                        try:
                                            infinite_tier = int(infinite_tier) if infinite_tier != "" else 0
                                        except ValueError:
                                            bmp.lang.lang_warn("warn.value.invalid", value=infinite_tier, cls="int")
                                        else:
                                            break
                                    if current_level.get_space(bmp.ref.SpaceID(name, infinite_tier)) is not None:
                                        space_id = bmp.ref.SpaceID(name, infinite_tier)
                                current_space.new_obj(current_object_type(current_cursor_pos, current_orient, space_id=space_id))
                            elif issubclass(current_object_type, bmp.obj.Path):
                                unlocked = False
                                conditions: dict[type[bmp.obj.Object], int] = {}
                                if keys["LCTRL"] or keys["RCTRL"]:
                                    bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.new")))
                                    unlocked = bmp.lang.lang_input("edit.path.new.unlocked") in bmp.lang.yes
                                    more_condition = bmp.lang.lang_input("edit.path.new.condition") in bmp.lang.yes
                                    while more_condition:
                                        while True:
                                            collects_type = bmp.obj.name_to_class[bmp.lang.lang_input("input.string")]
                                            if collects_type is None:
                                                bmp.lang.lang_warn("warn.value.invalid", value=collects_type, cls=bmp.obj.Object.__name__)
                                                continue
                                            break
                                        while True:
                                            collects_count = bmp.lang.lang_input("input.number")
                                            try:
                                                collects_count = int(collects_count)
                                            except ValueError:
                                                bmp.lang.lang_warn("warn.value.invalid", value=collects_count, cls="int")
                                            else:
                                                break
                                        conditions[collects_type] = collects_count
                                        more_condition = bmp.lang.lang_input("edit.path.new.condition") in bmp.lang.yes
                                current_space.new_obj(current_object_type(current_cursor_pos, current_orient, unlocked=unlocked, conditions=conditions))
                            else:
                                current_space.new_obj(current_object_type(current_cursor_pos, current_orient))
                elif mouses[2] != 0:
                    if mouses[2] == 1 and (keys["LALT"] or keys["RALT"]):
                        # leave space; leave level (shift)
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            level = levelpack.get_level(current_level.super_level_id if current_level.super_level_id is not None else levelpack.main_level_id)
                            current_level = level if level is not None else levelpack.get_exact_level(levelpack.main_level_id)
                            level_changed = True
                        else:
                            super_spaces = [t[0] for t in current_level.find_super_spaces(current_space.space_id)]
                            if len(super_spaces) != 0:
                                current_space = random.choice(super_spaces)
                                space_changed = True
                    elif mouses[2] == 1 or cursor_pos_changed:
                        # new space; new level (alt)
                        history.append(copy.deepcopy(levelpack))
                        current_space.del_objs_from_pos(current_cursor_pos)
                elif mouses[1] == 1:
                    # object select from cursor
                    objects_under_cursor = current_space.get_objs_from_pos(current_cursor_pos)
                    classes_under_cursor = [type(o) for o in objects_under_cursor if type(o) not in bmp.obj.instance_exclusive]
                    if len(classes_under_cursor) != 0:
                        current_object_type = random.choice(classes_under_cursor)
                # object select from list
                elif mouses[3]:
                    if keys["LALT"] or keys["RALT"]:
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            current_level_index -= 1
                            current_space_index = 0
                            level_changed = True
                        else:
                            current_space_index -= 1
                            space_changed = True
                    elif keys["LSHIFT"] or keys["RSHIFT"]:
                        obj_to_noun = bmp.obj.get_noun_from_type(current_object_type)
                        if obj_to_noun not in bmp.obj.instance_exclusive:
                            current_object_type = obj_to_noun
                    else:
                        current_object_type_list = [t for t in bmp.obj.object_class_list if t not in bmp.obj.instance_exclusive]
                        current_object_type_index = current_object_type_list.index(current_object_type)
                        current_object_type = current_object_type_list[current_object_type_index - 1 if current_object_type_index >= 0 else len(current_object_type_list) - 1]
                elif mouses[4]:
                    if keys["LALT"] or keys["RALT"]:
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            current_level_index += 1
                            current_space_index = 0
                            level_changed = True
                        else:
                            current_space_index += 1
                            space_changed = True
                    elif keys["LSHIFT"] or keys["RSHIFT"]:
                        if issubclass(current_object_type, bmp.obj.GeneralNoun) and current_object_type.ref_type not in bmp.obj.instance_exclusive:
                            current_object_type = current_object_type.ref_type
                    else:
                        current_object_type_list = [t for t in bmp.obj.object_class_list if t not in bmp.obj.instance_exclusive]
                        current_object_type_index = current_object_type_list.index(current_object_type)
                        current_object_type = current_object_type_list[current_object_type_index + 1 if current_object_type_index < len(current_object_type_list) - 1 else 0]
        # cursor move; object facing change (alt)
        if keys["W"] or keys["UP"]:
            current_orient = bmp.loc.Orient.W
        elif keys["S"] or keys["DOWN"]:
            current_orient = bmp.loc.Orient.S
        elif keys["A"] or keys["LEFT"]:
            current_orient = bmp.loc.Orient.A
        elif keys["D"] or keys["RIGHT"]:
            current_orient = bmp.loc.Orient.D
        # object select from palette / save to palette (shift)
        elif any(map(lambda i: keys[str(i)], range(10))):
            for i in range(10):
                if keys[str(i)]:
                    if keys["LSHIFT"] or keys["RSHIFT"]:
                        object_type_shortcuts[(i - 1) % 10] = current_object_type
                        bmp.base.options["object_type_shortcuts"][(i - 1) % 10] = current_object_type.json_name
                    else:
                        current_object_type = object_type_shortcuts[(i - 1) % 10]
        elif keys["N"]:
            if keys["LALT"] or keys["RALT"]:
                bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.new")))
                if bmp.lang.lang_input("edit.level.new") not in bmp.lang.no:
                    history.append(copy.deepcopy(levelpack))
                    level_name = bmp.lang.lang_input("edit.level.new.name")
                    level_id: bmp.ref.LevelID = bmp.ref.LevelID(level_name)
                    super_level_name = bmp.lang.lang_input("edit.level.new.super_level.name")
                    super_level_id: bmp.ref.LevelID = bmp.ref.LevelID(super_level_name) if super_level_name != "" else current_level.level_id
                    name = bmp.lang.lang_input("edit.space.new.name")
                    while True:
                        width = bmp.lang.lang_input("edit.space.new.width")
                        try:
                            width = int(width) if width != "" else bmp.base.options["default_new_space"]["width"]
                        except ValueError:
                            bmp.lang.lang_warn("warn.value.invalid", value=width, cls="int")
                        else:
                            break
                    while True:
                        height = bmp.lang.lang_input("edit.space.new.height")
                        try:
                            height = int(height) if height != "" else bmp.base.options["default_new_space"]["height"]
                        except ValueError:
                            bmp.lang.lang_warn("warn.value.invalid", value=height, cls="int")
                        else:
                            break
                    size = (width, height)
                    while True:
                        infinite_tier = bmp.lang.lang_input("edit.space.new.infinite_tier")
                        try:
                            infinite_tier = int(infinite_tier) if infinite_tier != "" else 0
                        except ValueError:
                            bmp.lang.lang_warn("warn.value.invalid", value=infinite_tier, cls="int")
                        else:
                            break
                    while True:
                        color = bmp.lang.lang_input("edit.space.new.color")
                        if color == "":
                            color = bmp.color.current_palette[0, 3]
                        else:
                            try:
                                color = bmp.color.str_to_hex(color)
                            except ValueError:
                                try:
                                    palette_str = color.lstrip("([").rstrip("])").split(",")
                                    color = bmp.color.current_palette[int(palette_str[0].strip()), int(palette_str[1].strip())]
                                except ValueError:
                                    bmp.lang.lang_warn("warn.value.invalid", value=color, cls="color")
                                else:
                                    break
                            else:
                                break
                    default_space = bmp.space.Space(bmp.ref.SpaceID(name, infinite_tier), size, color)
                    if bmp.lang.lang_input("edit.level.new.is_map") in bmp.lang.yes:
                        pass
                    levelpack.level_list.append(bmp.level.Level(level_id, [default_space], super_level_id=super_level_id, main_space_id=bmp.ref.SpaceID(name, infinite_tier), map_info=None))
                    current_level_index = len(levelpack.level_list) - 1
                    current_space_index = 0
                    level_changed = True
            else:
                if bmp.lang.lang_input("edit.space.new") not in bmp.lang.no:
                    history.append(copy.deepcopy(levelpack))
                    name = bmp.lang.lang_input("edit.space.new.name")
                    while True:
                        width = bmp.lang.lang_input("edit.space.new.width")
                        try:
                            width = int(width) if width != "" else bmp.base.options["default_new_space"]["width"]
                        except ValueError:
                            bmp.lang.lang_warn("warn.value.invalid", value=width, cls="int")
                        else:
                            break
                    while True:
                        height = bmp.lang.lang_input("edit.space.new.height")
                        try:
                            height = int(height) if height != "" else bmp.base.options["default_new_space"]["height"]
                        except ValueError:
                            bmp.lang.lang_warn("warn.value.invalid", value=height, cls="int")
                        else:
                            break
                    size = (width, height)
                    while True:
                        infinite_tier = bmp.lang.lang_input("edit.space.new.infinite_tier")
                        try:
                            infinite_tier = int(infinite_tier) if infinite_tier != "" else 0
                        except ValueError:
                            bmp.lang.lang_warn("warn.value.invalid", value=infinite_tier, cls="int")
                        else:
                            break
                    while True:
                        color = bmp.lang.lang_input("edit.space.new.color")
                        if color == "":
                            color = bmp.color.current_palette[0, 3]
                        else:
                            try:
                                color = bmp.color.str_to_hex(color)
                            except ValueError:
                                try:
                                    palette_str = color.lstrip("([").rstrip("])").split(",")
                                    color = bmp.color.current_palette[int(palette_str[0].strip()), int(palette_str[1].strip())]
                                except ValueError:
                                    bmp.lang.lang_warn("warn.value.invalid", value=color, cls="color")
                                else:
                                    break
                            else:
                                break
                    current_level.space_list.append(bmp.space.Space(bmp.ref.SpaceID(name, infinite_tier), size, color))
                    current_space_index = len(current_level.space_list) - 1
                    space_changed = True
        # delete current space / level (alt)
        elif keys["M"]:
            bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.delete")))
            if keys["LALT"] or keys["RALT"]:
                if bmp.lang.lang_input("edit.level.delete") in bmp.lang.yes:
                    levelpack.level_list.pop(current_level_index)
                    current_level_index -= 1
                    current_space_index = 0
                    level_changed = True
            else:
                if bmp.lang.lang_input("edit.space.delete") in bmp.lang.yes:
                    current_level.space_list.pop(current_space_index)
                    current_space_index -= 1
                    space_changed = True
        # add global rule; remove global rule (shift)
        elif keys["R"]:
            bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.levelpack.rule_list")))
            text_rule = bmp.lang.lang_input("edit.levelpack.new.rule").upper().split()
            type_rule: bmp.rule.Rule = []
            valid_input = True
            for text in text_rule:
                object_type = bmp.obj.name_to_class.get(text)
                if object_type is not None:
                    if issubclass(object_type, bmp.obj.Text):
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
            bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.levelpack.rule_list")))
            for rule in levelpack.rule_list:
                str_list: list[str] = []
                for object_type in rule:
                    str_list.append(object_type.get_name())
                print(" ".join(str_list))
        # edit id for current space / level (alt)
        elif keys["T"]:
            bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.rename")))
            if keys["LALT"] or keys["RALT"]:
                current_level.level_id.name = bmp.lang.lang_input("edit.level.rename")
            else:
                current_space.space_id.name = bmp.lang.lang_input("edit.space.rename")
                while True:
                    infinite_tier = bmp.lang.lang_input("edit.space.new.infinite_tier")
                    try:
                        current_space.space_id.infinite_tier = int(infinite_tier)
                    except ValueError:
                        bmp.lang.lang_warn("warn.value.invalid", value=infinite_tier, cls="int")
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
            current_clipboard = current_space.get_objs_from_pos(current_cursor_pos)
            current_clipboard = copy.deepcopy(current_clipboard)
            current_space.del_objs_from_pos(current_cursor_pos)
        elif keys["C"] and (keys["LCTRL"] or keys["RCTRL"]):
            history.append(copy.deepcopy(levelpack))
            current_clipboard = current_space.get_objs_from_pos(current_cursor_pos)
            current_clipboard = copy.deepcopy(current_clipboard)
        elif keys["V"] and (keys["LCTRL"] or keys["RCTRL"]):
            history.append(copy.deepcopy(levelpack))
            current_clipboard = copy.deepcopy(current_clipboard)
            for obj in current_clipboard:
                obj.reset_uuid()
                obj.pos = current_cursor_pos
                current_space.new_obj(obj)
                if isinstance(obj, bmp.obj.SpaceObject):
                    for level in levelpack.level_list:
                        space = level.get_space(obj.space_id)
                        if space is not None:
                            for new_space in level.space_list:
                                current_level.set_space(new_space)
        elif keys["TAB"]:
            bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.level")))
            bmp.lang.lang_print("edit.level.current.name", value=current_level.level_id.name)
            bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.space")))
            bmp.lang.lang_print("edit.space.current.name", value=current_space.space_id.name)
            bmp.lang.lang_print("edit.space.current.infinite_tier", value=current_space.space_id.infinite_tier)
        if level_changed:
            space_changed = True
            current_level_index = current_level_index % len(levelpack.level_list) if current_level_index >= 0 else len(levelpack.level_list) - 1
            current_level = levelpack.level_list[current_level_index]
            # bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.level")))
            # bmp.lang.lang_print("edit.level.current.name", value=current_level.level_id.name)
            level_changed = False
        if space_changed:
            if current_cursor_pos[0] > current_space.width:
                current_cursor_pos = (current_space.width, current_cursor_pos[1])
            if current_cursor_pos[1] > current_space.height:
                current_cursor_pos = (current_cursor_pos[0], current_space.height)
            current_space_index = current_space_index % len(current_level.space_list) if current_space_index >= 0 else len(current_level.space_list) - 1
            current_space = current_level.space_list[current_space_index]
            # bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.space")))
            # bmp.lang.lang_print("edit.space.current.name", value=current_space.space_id.name)
            # bmp.lang.lang_print("edit.space.current.infinite_tier", value=current_space.space_id.infinite_tier)
            space_changed = False
        # display
        for space in current_level.space_list:
            space.set_sprite_states(0)
        window.fill(bmp.color.current_palette[0, 4])
        space_surface_size = (window.get_height() * current_space.width // current_space.height, window.get_height())
        space_surface_pos = (0, 0)
        space_surface = current_level.space_to_surface(current_space, wiggle, space_surface_size, cursor=current_cursor_pos, debug=True)
        window.blit(pygame.transform.scale(space_surface, space_surface_size), space_surface_pos)
        gui_scaled_sprite_size = (bmp.render.sprite_size * bmp.render.gui_scale, bmp.render.sprite_size * bmp.render.gui_scale)
        half_gui_scaled_sprite_size = (bmp.render.sprite_size * bmp.render.half_gui_scale, bmp.render.sprite_size * bmp.render.half_gui_scale)
        # current object type
        obj_surface = bmp.render.simple_type_to_surface(current_object_type, wiggle=wiggle, debug=True)
        if issubclass(current_object_type, bmp.obj.SpaceObject):
            space = current_level.get_space(current_space.space_id)
            if space is not None:
                obj_surface = bmp.render.simple_type_to_surface(current_object_type, wiggle=wiggle, default_surface=space_surface, debug=True)
        obj_surface = pygame.transform.scale(obj_surface, gui_scaled_sprite_size)
        window.blit(obj_surface, (window.get_width() - bmp.render.sprite_size * bmp.render.gui_scale, 0))
        # display name
        line_list: list[str] = [
            current_object_type.get_name(language_name=bmp.lang.english).lower(),
            "text" if issubclass(current_object_type, bmp.obj.Text) else "object",
            bmp.lang.lang_format("orient.name." + current_orient.name.lower(), language_name=bmp.lang.english).lower(),
        ]
        if bmp.base.options["debug"]:
            line_list.append(current_object_type.json_name.lower())
        for line_index, line in enumerate(line_list):
            for char_index, char in enumerate(line):
                if char in string.ascii_lowercase:
                    obj_surface = bmp.render.current_sprites.get("text_" + char, 0, wiggle, raw=True)
                elif char == "_":
                    obj_surface = bmp.render.current_sprites.get("text_underline", 0, wiggle, raw=True)
                else:
                    continue
                obj_surface = pygame.transform.scale(obj_surface, half_gui_scaled_sprite_size)
                obj_surface_pos = (
                    window.get_width() + (char_index - len(line)) * bmp.render.sprite_size * bmp.render.half_gui_scale,
                    (bmp.render.sprite_size * bmp.render.gui_scale) + (line_index * bmp.render.sprite_size * bmp.render.half_gui_scale)
                )
                window.blit(obj_surface, obj_surface_pos)
        # shortcuts
        for index, object_type in object_type_shortcuts.items():
            obj_surface = bmp.render.simple_type_to_surface(object_type, wiggle=wiggle, debug=True)
            if issubclass(object_type, bmp.obj.SpaceObject):
                space = current_level.get_space(current_space.space_id)
                if space is not None:
                    obj_surface = bmp.render.simple_type_to_surface(object_type, wiggle=wiggle, default_surface=space_surface, debug=True)
            obj_surface = pygame.transform.scale(obj_surface, gui_scaled_sprite_size)
            obj_surface_pos = (
                window.get_width() + (index % 5 * bmp.render.sprite_size * bmp.render.gui_scale) - (bmp.render.sprite_size * bmp.render.gui_scale * 5),
                window.get_height() + (index // 5 * bmp.render.sprite_size * bmp.render.gui_scale) - (bmp.render.sprite_size * bmp.render.gui_scale * 2)
            )
            # slot number
            obj_surface.blit(
                pygame.transform.scale(
                    bmp.render.set_alpha(
                        bmp.render.current_sprites.get("text_" + str((index + 1) % 10), 0, wiggle, raw=True), 0x80
                    ), half_gui_scaled_sprite_size
                ),
                (bmp.render.sprite_size * (bmp.render.gui_scale - bmp.render.half_gui_scale), bmp.render.sprite_size * (bmp.render.gui_scale - bmp.render.half_gui_scale))
            )
            window.blit(obj_surface, obj_surface_pos)
        # fps
        real_fps = min(1000 / milliseconds, (real_fps * (bmp.base.options["fps"] - 1) + 1000 / milliseconds) / bmp.base.options["fps"])
        if keys["F1"]:
            show_fps = not show_fps
        if show_fps:
            real_fps_string = str(int(real_fps))
            for i in range(len(real_fps_string)):
                window.blit(bmp.render.current_sprites.get(f"text_{real_fps_string[i]}", 0, wiggle), (i * bmp.render.sprite_size, 0))
        pygame.display.flip()
        milliseconds = clock.tick(bmp.base.options["fps"])
    pygame.display.quit()
    return levelpack