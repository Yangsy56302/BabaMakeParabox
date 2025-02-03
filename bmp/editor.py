from typing import Optional
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
    current_object_type: type[bmp.obj.Object] = bmp.obj.TextSpace
    current_orient = bmp.loc.Orient.S
    current_cursor_pos: bmp.loc.Coord[int] = (0, 0)
    cursor_pos_changed: bool
    current_clipboard = []
    window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption(bmp.lang.fformat(
        "title.window.edit",
        ver=bmp.base.version,
        debug=bmp.lang.fformat("debug.name") if bmp.opt.options["debug"] else "",
    ))
    pygame.display.set_icon(pygame.image.load(os.path.join(".", "logo", "c8icon.png")))
    pygame.key.stop_text_input()
    pygame.key.set_repeat(bmp.opt.options["gameplay"]["repeat"]["delay"], bmp.opt.options["gameplay"]["repeat"]["interval"])
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
    bmp.color.set_palette(os.path.join(".", "palettes", bmp.opt.options["render"]["palette"]))
    bmp.render.current_sprites.update()
    window.fill("#000000")
    object_type_shortcuts: dict[int, type[bmp.obj.Object]] = {k: bmp.obj.name_to_class[v] for k, v in enumerate(bmp.opt.options["editor"]["shortcuts"])}
    level_changed = True
    space_changed = True
    frame = 0
    wiggle = 1
    editor_running = True
    milliseconds = 1000 // bmp.opt.options["render"]["fps"]
    real_fps = bmp.opt.options["render"]["fps"]
    show_fps = False
    while editor_running:
        frame += 1
        if frame % (bmp.opt.options["render"]["fps"] // 6) == 0:
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
            (mouse_pos[0] - space_surface_pos[0]) * levelpack.current_level.current_space.width // space_surface_size[0],
            (mouse_pos[1] - space_surface_pos[1]) * levelpack.current_level.current_space.height // space_surface_size[1]
        )
        if not levelpack.current_level.current_space.out_of_range(mouse_pos_in_space):
            cursor_pos_changed = False
            if current_cursor_pos != mouse_pos_in_space:
                cursor_pos_changed = True
            current_cursor_pos = mouse_pos_in_space
        if any(mouses):
            if not levelpack.current_level.current_space.out_of_range(mouse_pos_in_space):
                if mouses[0] != 0:
                    if mouses[0] and (keys["LALT"] or keys["RALT"]):
                        # enter space; enter level (shift)
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            sub_level_objs: list[bmp.obj.LevelObject] = levelpack.current_level.current_space.get_levels_from_pos(mouse_pos_in_space)
                            sub_levels = [levelpack.get_level(o.level_id) for o in sub_level_objs]
                            sub_levels = [w for w in sub_levels if w is not None]
                            if len(sub_levels) != 0:
                                level = random.choice(sub_levels)
                                if level is not None:
                                    levelpack.current_level_id = level.level_id
                                    level_changed = True
                        else:
                            sub_space_objs: list[bmp.obj.SpaceObject] = levelpack.current_level.current_space.get_spaces_from_pos(mouse_pos_in_space)
                            sub_spaces = [levelpack.current_level.get_space(o.space_id) for o in sub_space_objs]
                            sub_spaces = [w for w in sub_spaces if w is not None]
                            if len(sub_spaces) != 0:
                                space = random.choice(sub_spaces)
                                if space is not None:
                                    levelpack.current_level.current_space_id = space.space_id
                                    space_changed = True
                    elif mouses[0] == 1 or cursor_pos_changed:
                        # place object; with detail (shift); allow overlap (ctrl)
                        if keys["LSHIFT"] or keys["RSHIFT"] or len(levelpack.current_level.current_space.get_objs_from_pos(current_cursor_pos)) == 0:
                            history.append(copy.deepcopy(levelpack))
                            if issubclass(current_object_type, bmp.obj.LevelObject):
                                if keys["LCTRL"] or keys["RCTRL"]:
                                    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.new")))
                                    name = bmp.lang.input_str(bmp.lang.fformat("edit.level.new.name"))
                                    level_id: bmp.ref.LevelID = bmp.ref.LevelID(name)
                                    icon_name = bmp.lang.input_str(bmp.lang.fformat("edit.level.new.icon.name"))
                                    icon_name = icon_name if icon_name != "" else "text_level"
                                    icon_color: bmp.color.ColorHex = bmp.lang.input_color(
                                        bmp.lang.fformat("edit.level.new.icon.color"),
                                        default = bmp.color.current_palette[bmp.obj.default_level_object_type.sprite_palette],
                                    )
                                else:
                                    level_id: bmp.ref.LevelID = levelpack.current_level_id
                                    icon_name = "text_level"
                                    icon_color = bmp.color.current_palette[bmp.obj.default_level_object_type.sprite_palette]
                                level_extra: bmp.obj.LevelObjectExtra = {"icon": {"name": icon_name, "color": icon_color}}
                                levelpack.current_level.current_space.new_obj(current_object_type(current_cursor_pos, current_orient, level_id=level_id, level_extra=level_extra))
                            elif issubclass(current_object_type, bmp.obj.SpaceObject):
                                space_id: bmp.ref.SpaceID = levelpack.current_level.current_space_id
                                if keys["LCTRL"] or keys["RCTRL"]:
                                    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.new")))
                                    name = bmp.lang.input_str(bmp.lang.fformat("edit.space.new.name"))
                                    infinite_tier = bmp.lang.input_int(bmp.lang.fformat("edit.space.new.infinite_tier"))
                                    space_id = bmp.ref.SpaceID(name, infinite_tier)
                                levelpack.current_level.current_space.new_obj(current_object_type(current_cursor_pos, current_orient, space_id=space_id))
                            elif issubclass(current_object_type, bmp.obj.Path):
                                unlocked = False
                                conditions: dict[type[bmp.obj.Object], int] = {}
                                if keys["LCTRL"] or keys["RCTRL"]:
                                    bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.new")))
                                    unlocked = bmp.lang.input_yes(bmp.lang.fformat("edit.path.new.unlocked"))
                                    more_condition = bmp.lang.input_yes(bmp.lang.fformat("edit.path.new.condition"))
                                    while more_condition:
                                        while True:
                                            collects_type = bmp.obj.name_to_class[bmp.lang.input_str(bmp.lang.fformat("input.string"))]
                                            if collects_type is None:
                                                bmp.lang.fwarn("warn.value.invalid", value=collects_type, cls=bmp.obj.Object.__name__)
                                                continue
                                            break
                                        collects_count = bmp.lang.input_int(bmp.lang.fformat("input.number"))
                                        conditions[collects_type] = collects_count
                                        more_condition = bmp.lang.input_yes(bmp.lang.fformat("edit.path.new.condition"))
                                levelpack.current_level.current_space.new_obj(current_object_type(current_cursor_pos, current_orient, unlocked=unlocked, conditions=conditions))
                            else:
                                levelpack.current_level.current_space.new_obj(current_object_type(current_cursor_pos, current_orient))
                elif mouses[2] != 0:
                    if mouses[2] == 1 and (keys["LALT"] or keys["RALT"]):
                        # leave space; leave level (shift)
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            level = levelpack.get_level(levelpack.current_level.super_level_id if levelpack.current_level.super_level_id is not None else levelpack.current_level_id)
                            levelpack.current_level_id = level.level_id if level is not None else levelpack.current_level_id
                            level_changed = True
                        else:
                            super_spaces = [t[0] for t in levelpack.current_level.find_super_spaces(levelpack.current_level.current_space_id)]
                            if len(super_spaces) != 0:
                                levelpack.current_level.current_space_id = random.choice(super_spaces).space_id
                                space_changed = True
                    elif mouses[2] == 1 or cursor_pos_changed:
                        # new space; new level (alt)
                        history.append(copy.deepcopy(levelpack))
                        levelpack.current_level.current_space.del_objs_from_pos(current_cursor_pos)
                elif mouses[1] == 1:
                    # object select from cursor
                    objects_under_cursor = levelpack.current_level.current_space.get_objs_from_pos(current_cursor_pos)
                    classes_under_cursor: list[type[bmp.obj.Object]] = [type(o) for o in objects_under_cursor if type(o) not in bmp.obj.instance_exclusive]
                    if len(classes_under_cursor) != 0:
                        current_object_type = random.choice(classes_under_cursor)
                # object select from list
                elif mouses[3]:
                    if keys["LALT"] or keys["RALT"]:
                        if keys["LSHIFT"] or keys["RSHIFT"]:
                            current_level_index = levelpack.level_list.index(levelpack.current_level) - 1
                            levelpack.current_level_id = levelpack.level_list[current_level_index % len(levelpack.level_list)].level_id
                            level_changed = True
                            del current_level_index
                        else:
                            current_space_index = levelpack.current_level.space_list.index(levelpack.current_level.current_space) - 1
                            levelpack.current_level.current_space_id = levelpack.current_level.space_list[current_space_index % len(levelpack.current_level.space_list)].space_id
                            space_changed = True
                            del current_space_index
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
                            current_level_index = levelpack.level_list.index(levelpack.current_level) + 1
                            levelpack.current_level_id = levelpack.level_list[current_level_index % len(levelpack.level_list)].level_id
                            level_changed = True
                            del current_level_index
                        else:
                            current_space_index = levelpack.current_level.space_list.index(levelpack.current_level.current_space) + 1
                            levelpack.current_level.current_space_id = levelpack.current_level.space_list[current_space_index % len(levelpack.current_level.space_list)].space_id
                            space_changed = True
                            del current_space_index
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
                        bmp.opt.options["editor"]["shortcuts"][(i - 1) % 10] = current_object_type.json_name
                    else:
                        current_object_type = object_type_shortcuts[(i - 1) % 10]
        elif keys["N"]:
            if keys["LALT"] or keys["RALT"]:
                bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.new")))
                if not bmp.lang.input_no(bmp.lang.fformat("edit.level.new")):
                    history.append(copy.deepcopy(levelpack))
                    level_name = bmp.lang.input_str(bmp.lang.fformat("edit.level.new.name"))
                    level_id: bmp.ref.LevelID = bmp.ref.LevelID(level_name)
                    super_level_name = bmp.lang.input_str(bmp.lang.fformat("edit.level.new.super_level.name"))
                    super_level_id: bmp.ref.LevelID = bmp.ref.LevelID(super_level_name) if super_level_name != "" else levelpack.current_level_id
                    name = bmp.lang.input_str(bmp.lang.fformat("edit.space.new.name"))
                    width = bmp.lang.input_int(bmp.lang.fformat("edit.space.new.width"), default=bmp.opt.options["editor"]["default_space"]["width"])
                    height = bmp.lang.input_int(bmp.lang.fformat("edit.space.new.height"), default=bmp.opt.options["editor"]["default_space"]["height"])
                    infinite_tier = bmp.lang.input_int(bmp.lang.fformat("edit.space.new.infinite_tier"))
                    space_color = bmp.lang.input_color(
                        bmp.lang.fformat("edit.space.new.color"),
                        default = bmp.opt.options["editor"]["default_space"]["color"],
                    )
                    space_id = bmp.ref.SpaceID(name, infinite_tier)
                    levelpack.space_dict[space_id] = bmp.space.Space(space_id, (width, height), space_color)
                    map_info: Optional[bmp.level.MapLevelExtraJson] = None
                    if bmp.lang.input_yes(bmp.lang.fformat("edit.level.new.is_map")):
                        map_info = {}
                        spore_for_blossom = bmp.lang.input_int_optional(bmp.lang.fformat("edit.level.new.spore_for_blossom"))
                        if spore_for_blossom is not None:
                            map_info["spore_for_blossom"] = spore_for_blossom
                    levelpack.level_dict[level_id] = bmp.level.Level(
                        level_id, [space_id], space_id,
                        super_level_id = super_level_id,
                        map_info = map_info,
                    )
                    levelpack.level_dict[level_id].space_dict = levelpack.space_dict
                    levelpack.current_level_id = level_id
                    level_changed = True
                    del level_id, space_id
            else:
                if bmp.lang.input_str(bmp.lang.fformat("edit.space.new")) not in bmp.lang.no:
                    history.append(copy.deepcopy(levelpack))
                    name = bmp.lang.input_str(bmp.lang.fformat("edit.space.new.name"))
                    width = bmp.lang.input_int(bmp.lang.fformat("edit.space.new.width"), default=bmp.opt.options["editor"]["default_space"]["width"])
                    height = bmp.lang.input_int(bmp.lang.fformat("edit.space.new.height"), default=bmp.opt.options["editor"]["default_space"]["height"])
                    infinite_tier = bmp.lang.input_int(bmp.lang.fformat("edit.space.new.infinite_tier"))
                    space_color = bmp.lang.input_color(
                        bmp.lang.fformat("edit.space.new.color"),
                        default = bmp.opt.options["editor"]["default_space"]["color"],
                    )
                    space_id = bmp.ref.SpaceID(name, infinite_tier)
                    levelpack.current_level.space_dict[space_id] = bmp.space.Space(space_id, (width, height), space_color)
                    levelpack.current_level.current_space_id = space_id
                    space_changed = True
                    del space_id
        # delete current space / level (alt)
        elif keys["M"]:
            bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.delete")))
            if keys["LALT"] or keys["RALT"]:
                if bmp.lang.input_yes(bmp.lang.fformat("edit.level.delete")):
                    levelpack.del_level(levelpack.current_level_id)
                    levelpack.current_level_id = random.choice(list(levelpack.level_dict.keys()))
                    level_changed = True
            else:
                if bmp.lang.input_yes(bmp.lang.fformat("edit.space.delete")):
                    levelpack.current_level.space_included.remove(levelpack.current_level.current_space_id)
                    if all(map(
                        lambda l: levelpack.current_level.current_space_id not in l.space_included,
                        levelpack.level_dict.values()
                    )):
                        levelpack.space_dict.pop(levelpack.current_level.current_space_id)
                    levelpack.current_level.current_space_id = random.choice(levelpack.current_level.space_included)
                    space_changed = True
        # add global rule; remove global rule (shift)
        elif keys["R"]:
            bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.levelpack.rule_list")))
            text_rule = bmp.lang.input_str(bmp.lang.fformat("edit.levelpack.new.rule")).upper().split()
            type_rule: bmp.rule.Rule = []
            valid_input = True
            for text in text_rule:
                object_type = bmp.obj.name_to_class.get(text)
                if object_type is not None:
                    if issubclass(object_type, bmp.obj.Text):
                        type_rule.append(object_type())
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
            bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.levelpack.rule_list")))
            for rule in levelpack.rule_list:
                str_list: list[str] = []
                for object_type in rule:
                    str_list.append(object_type.get_name())
                bmp.lang.print(" ".join(str_list))
        # edit id for current space / level (alt)
        elif keys["T"]:
            bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.rename")))
            if keys["LALT"] or keys["RALT"]:
                levelpack.current_level_id.name = bmp.lang.input_str(bmp.lang.fformat("edit.level.rename"))
            else:
                levelpack.current_level.current_space_id.name = bmp.lang.input_str(bmp.lang.fformat("edit.space.rename"))
                levelpack.current_level.current_space_id.infinite_tier = bmp.lang.input_int(bmp.lang.fformat("edit.space.new.infinite_tier"))
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
            current_clipboard = levelpack.current_level.current_space.get_objs_from_pos(current_cursor_pos)
            current_clipboard = copy.deepcopy(current_clipboard)
            levelpack.current_level.current_space.del_objs_from_pos(current_cursor_pos)
        elif keys["C"] and (keys["LCTRL"] or keys["RCTRL"]):
            history.append(copy.deepcopy(levelpack))
            current_clipboard = levelpack.current_level.current_space.get_objs_from_pos(current_cursor_pos)
            current_clipboard = copy.deepcopy(current_clipboard)
        elif keys["V"] and (keys["LCTRL"] or keys["RCTRL"]):
            history.append(copy.deepcopy(levelpack))
            current_clipboard = copy.deepcopy(current_clipboard)
            for obj in current_clipboard:
                obj.reset_uuid()
                obj.pos = current_cursor_pos
                levelpack.current_level.current_space.new_obj(obj)
                if isinstance(obj, bmp.obj.SpaceObject):
                    for level in levelpack.level_list:
                        space = level.get_space(obj.space_id)
                        if space is not None:
                            for new_space in level.space_list:
                                levelpack.current_level.set_space(new_space)
        elif keys["TAB"]:
            bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.level")))
            bmp.lang.fprint("edit.level.current.name", value=levelpack.current_level_id.name)
            bmp.lang.fprint(bmp.lang.seperator_line(bmp.lang.fformat("title.space")))
            bmp.lang.fprint("edit.space.current.name", value=levelpack.current_level.current_space_id.name)
            bmp.lang.fprint("edit.space.current.infinite_tier", value=levelpack.current_level.current_space_id.infinite_tier)
        if level_changed:
            space_changed = True
            # bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.level")))
            # bmp.lang.lang_print("edit.level.current.name", value=current_level.level_id.name)
            level_changed = False
        if space_changed:
            if current_cursor_pos[0] > levelpack.current_level.current_space.width:
                current_cursor_pos = (levelpack.current_level.current_space.width, current_cursor_pos[1])
            if current_cursor_pos[1] > levelpack.current_level.current_space.height:
                current_cursor_pos = (current_cursor_pos[0], levelpack.current_level.current_space.height)
            # bmp.lang.lang_print(bmp.lang.seperator_line(bmp.lang.lang_format("title.space")))
            # bmp.lang.lang_print("edit.space.current.name", value=current_space.space_id.name)
            # bmp.lang.lang_print("edit.space.current.infinite_tier", value=current_space.space_id.infinite_tier)
            space_changed = False
        # display
        for level in levelpack.level_list:
            for space in levelpack.current_level.space_list:
                space.set_sprite_states(0)
        window.fill(bmp.color.current_palette[0, 4])
        space_surface_size = (window.get_height() * levelpack.current_level.current_space.width // levelpack.current_level.current_space.height, window.get_height())
        space_surface_pos = (0, 0)
        space_surface = levelpack.current_level.space_to_surface(levelpack.current_level.current_space, wiggle, space_surface_size, cursor=current_cursor_pos, debug=True)
        window.blit(pygame.transform.scale(space_surface, space_surface_size), space_surface_pos)
        gui_scaled_sprite_size = (bmp.render.sprite_size * bmp.render.gui_scale, bmp.render.sprite_size * bmp.render.gui_scale)
        half_gui_scaled_sprite_size = (bmp.render.sprite_size * bmp.render.half_gui_scale, bmp.render.sprite_size * bmp.render.half_gui_scale)
        # current object type
        obj_surface = bmp.render.simple_type_to_surface(current_object_type, wiggle=wiggle, debug=True)
        if issubclass(current_object_type, bmp.obj.SpaceObject):
            space = levelpack.current_level.get_space(levelpack.current_level.current_space_id)
            if space is not None:
                obj_surface = bmp.render.simple_type_to_surface(current_object_type, wiggle=wiggle, default_surface=space_surface, debug=True)
        obj_surface = pygame.transform.scale(obj_surface, gui_scaled_sprite_size)
        window.blit(obj_surface, (window.get_width() - bmp.render.sprite_size * bmp.render.gui_scale, 0))
        # display name
        line_list: list[str] = [
            current_object_type.get_name(language_name=bmp.lang.english).lower(),
            "text" if issubclass(current_object_type, bmp.obj.Text) else "object",
            bmp.lang.fformat("orient.name." + current_orient.name.lower(), language_name=bmp.lang.english).lower(),
        ]
        if bmp.opt.options["debug"]:
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
                space = levelpack.current_level.get_space(levelpack.current_level.current_space_id)
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
        real_fps = min(1000 / milliseconds, (real_fps * (bmp.opt.options["render"]["fps"] - 1) + 1000 / milliseconds) / bmp.opt.options["render"]["fps"])
        if keys["F1"]:
            show_fps = not show_fps
        if show_fps:
            real_fps_string = str(int(real_fps))
            for i in range(len(real_fps_string)):
                window.blit(bmp.render.current_sprites.get(f"text_{real_fps_string[i]}", 0, wiggle), (i * bmp.render.sprite_size, 0))
        pygame.display.flip()
        milliseconds = clock.tick(bmp.opt.options["render"]["fps"])
    pygame.display.quit()
    return levelpack