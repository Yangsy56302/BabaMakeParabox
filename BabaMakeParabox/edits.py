import copy

from BabaMakeParabox import basics, languages, colors, refs, spaces, objects, collects, rules, worlds, displays, levels, levelpacks

import pygame

def levelpack_editor(levelpack: levelpacks.Levelpack) -> levelpacks.Levelpack:
    for level in levelpack.level_list:
        for world in level.world_list:
            world.set_sprite_states(0)
    history = [copy.deepcopy(levelpack)]
    window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption(f"Baba Make Parabox Editor Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("bmp.png"))
    displays.sprites.update()
    pygame.key.set_repeat()
    pygame.key.stop_text_input()
    clock = pygame.time.Clock()
    keybinds = {
        pygame.K_w: "W",
        pygame.K_a: "A",
        pygame.K_s: "S",
        pygame.K_d: "D",
        pygame.K_q: "Q",
        pygame.K_e: "E",
        pygame.K_z: "Z",
        pygame.K_x: "X",
        pygame.K_c: "C",
        pygame.K_v: "V",
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
        pygame.K_MINUS: "-",
        pygame.K_EQUALS: "=",
        pygame.K_RETURN: "RETURN",
        pygame.K_BACKSLASH: "BACKSLASH",
        pygame.K_BACKSPACE: "BACKSPACE",
        pygame.K_DELETE: "DELETE",
        pygame.K_TAB: "TAB",
        pygame.K_F1: "F1"
    }
    keymods = {pygame.KMOD_LSHIFT: "LSHIFT",
               pygame.KMOD_RSHIFT: "RSHIFT",
               pygame.KMOD_LCTRL: "LCTRL",
               pygame.KMOD_RCTRL: "RCTRL"}
    keys = {v: False for v in keybinds.values()}
    keys.update({v: False for v in keymods.values()})
    window.fill("#000000")
    current_level_index: int = 0
    current_level = levelpack.level_list[current_level_index]
    current_world_index: int = 0
    current_world = current_level.world_list[current_world_index]
    current_object_type = objects.Baba
    current_orient = spaces.Orient.S
    current_cursor_pos = (0, 0)
    current_clipboard = []
    object_type_shortcuts: dict[int, type[objects.BmpObject]] = {k: objects.object_name[v] for k, v in enumerate(basics.options["object_type_shortcuts"])}
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editor_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in keybinds.keys():
                    keys[keybinds[event.key]] = True
                for n, key in keymods.items():
                    if event.mod & n:
                        keys[key] = True
        # cursor move; object facing change (shift)
        if keys["W"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                current_orient = spaces.Orient.W
            else:
                new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.Orient.W)
                if not current_world.out_of_range(new_cursor_pos):
                    current_cursor_pos = new_cursor_pos
        elif keys["S"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                current_orient = spaces.Orient.S
            else:
                new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.Orient.S)
                if not current_world.out_of_range(new_cursor_pos):
                    current_cursor_pos = new_cursor_pos
        elif keys["A"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                current_orient = spaces.Orient.A
            else:
                new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.Orient.A)
                if not current_world.out_of_range(new_cursor_pos):
                    current_cursor_pos = new_cursor_pos
        elif keys["D"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                current_orient = spaces.Orient.D
            else:
                new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.Orient.D)
                if not current_world.out_of_range(new_cursor_pos):
                    current_cursor_pos = new_cursor_pos
        # object select from list
        elif keys["Q"]:
            current_object_type_list = [t for t in objects.object_name.values() if t not in objects.not_in_editor]
            current_object_type_index = current_object_type_list.index(current_object_type)
            current_object_type = current_object_type_list[current_object_type_index - 1 if current_object_type_index >= 0 else len(current_object_type_list) - 1]
        elif keys["E"]:
            current_object_type_list = [t for t in objects.object_name.values() if t not in objects.not_in_editor]
            current_object_type_index = current_object_type_list.index(current_object_type)
            current_object_type = current_object_type_list[current_object_type_index + 1 if current_object_type_index < len(current_object_type_list) - 1 else 0]
        # object select from palette / save to palette (ctrl)
        elif keys["1"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[0] = current_object_type
                basics.options["object_type_shortcuts"][0] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[0]
        elif keys["2"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[1] = current_object_type
                basics.options["object_type_shortcuts"][1] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[1]
        elif keys["3"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[2] = current_object_type
                basics.options["object_type_shortcuts"][2] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[2]
        elif keys["4"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[3] = current_object_type
                basics.options["object_type_shortcuts"][3] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[3]
        elif keys["5"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[4] = current_object_type
                basics.options["object_type_shortcuts"][4] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[4]
        elif keys["6"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[5] = current_object_type
                basics.options["object_type_shortcuts"][5] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[5]
        elif keys["7"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[6] = current_object_type
                basics.options["object_type_shortcuts"][6] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[6]
        elif keys["8"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[7] = current_object_type
                basics.options["object_type_shortcuts"][7] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[7]
        elif keys["9"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[8] = current_object_type
                basics.options["object_type_shortcuts"][8] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[8]
        elif keys["0"]:
            if keys["LCTRL"] or keys["RCTRL"]:
                object_type_shortcuts[9] = current_object_type
                basics.options["object_type_shortcuts"][9] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_type = object_type_shortcuts[9]
        # place object; with detail (shift); allow overlap (ctrl)
        elif keys["RETURN"]:
            if keys["LCTRL"] or keys["RCTRL"] or len(current_world.get_objs_from_pos(current_cursor_pos)) == 0:
                history.append(copy.deepcopy(levelpack))
                if issubclass(current_object_type, objects.LevelPointer):
                    if keys["LSHIFT"] or keys["RSHIFT"]:
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
                    level_pointer_extra: objects.LevelPointerExtra = {"icon": {"name": icon_name, "color": icon_color}}
                    current_world.new_obj(current_object_type(current_cursor_pos, current_orient, level_id=level_id, level_pointer_extra=level_pointer_extra))
                elif issubclass(current_object_type, objects.WorldPointer):
                    world_id: refs.WorldID = current_world.world_id
                    if keys["LSHIFT"] or keys["RSHIFT"]:
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
                    if keys["LSHIFT"] or keys["RSHIFT"]:
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
        # new world; new level (shift)
        elif keys["BACKSLASH"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
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
                    size = (width, height)
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
                    world_changed = True
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
                    size = (width, height)
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
        # delete current world / level (shift)
        elif keys["DELETE"]:
            languages.lang_print("seperator.title", text=languages.lang_format("title.delete"))
            if keys["LSHIFT"] or keys["RSHIFT"]:
                if languages.lang_input("edit.level.delete") in languages.yes:
                    levelpack.level_list.pop(current_level_index)
                    current_level_index -= 1
                    current_world_index = 0
                    level_changed = True
                    world_changed = True
            else:
                if languages.lang_input("edit.world.delete") in languages.yes:
                    current_level.world_list.pop(current_world_index)
                    current_world_index -= 1
                    world_changed = True
        # change global rule
        elif keys["R"]:
            languages.lang_print("seperator.title", text=languages.lang_format("title.levelpack.rule_list"))
            text_rule = languages.lang_input("edit.levelpack.new.rule").upper().split()
            type_rule: rules.Rule = []
            valid_input = True
            for text in text_rule:
                obj_type = objects.object_name.get(text)
                if obj_type is not None:
                    if issubclass(obj_type, objects.Text):
                        type_rule.append(obj_type)
                    else:
                        valid_input = False
                        break
                else:
                    valid_input = False
                    break
            if valid_input:
                dupe_list = []
                for rule in levelpack.rule_list:
                    duplicated = False
                    if len(type_rule) == len(rule):
                        duplicated = all(map(lambda x, y: x == y, type_rule, rule))
                    dupe_list.append(duplicated)
                if any(dupe_list):
                    if keys["LSHIFT"] or keys["RSHIFT"]:
                        levelpack.rule_list.pop(dupe_list.index(True))
                else:
                    if not (keys["LSHIFT"] or keys["RSHIFT"]):
                        levelpack.rule_list.append(list(type_rule))
            languages.lang_print("seperator.title", text=languages.lang_format("title.levelpack.rule_list"))
            for rule in levelpack.rule_list:
                str_list = []
                for obj_type in rule:
                    str_list.append(obj_type.display_name)
                print(" ".join(str_list))
        # edit id for current world / level (shift)
        elif keys["T"]:
            languages.lang_print("seperator.title", text=languages.lang_format("title.rename"))
            if keys["LSHIFT"] or keys["RSHIFT"]:
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
        # remove objects on cursor
        elif keys["BACKSPACE"]:
            history.append(copy.deepcopy(levelpack))
            current_world.del_objs_from_pos(current_cursor_pos)
        # object to noun; noun to object (shift)
        elif keys["TAB"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                if issubclass(current_object_type, objects.Noun) and current_object_type.obj_type not in objects.not_in_editor:
                    current_object_type = current_object_type.obj_type
            else:
                obj_to_noun = objects.get_noun_from_type(current_object_type)
                if obj_to_noun not in objects.not_in_editor:
                    current_object_type = obj_to_noun
        # undo
        elif keys["Z"]:
            if len(history) > 1:
                levelpack = copy.deepcopy(history.pop())
            else:
                levelpack = copy.deepcopy(history[0])
            world_changed = True
            level_changed = True
        # cut, copy, paste
        elif keys["X"]:
            history.append(copy.deepcopy(levelpack))
            current_clipboard = current_world.get_objs_from_pos(current_cursor_pos)
            current_clipboard = copy.deepcopy(current_clipboard)
            list(map(objects.BmpObject.reset_uuid, current_clipboard))
            current_world.del_objs_from_pos(current_cursor_pos)
        elif keys["C"]:
            history.append(copy.deepcopy(levelpack))
            current_clipboard = current_world.get_objs_from_pos(current_cursor_pos)
            current_clipboard = copy.deepcopy(current_clipboard)
            list(map(objects.BmpObject.reset_uuid, current_clipboard))
        elif keys["V"]:
            history.append(copy.deepcopy(levelpack))
            current_clipboard = copy.deepcopy(current_clipboard)
            list(map(objects.BmpObject.reset_uuid, current_clipboard))
            for obj in current_clipboard:
                obj.pos = current_cursor_pos
                current_world.new_obj(obj)
                if isinstance(obj, objects.WorldPointer):
                    for level in levelpack.level_list:
                        world = level.get_world(obj.world_id)
                        if world is not None:
                            for new_world in level.world_list:
                                current_level.set_world(new_world)
        # change world / level
        elif keys["-"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                current_level_index -= 1
                current_world_index = 0
                level_changed = True
                world_changed = True
            else:
                current_world_index -= 1
                world_changed = True
        elif keys["="]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                current_level_index += 1
                current_world_index = 0
                level_changed = True
                world_changed = True
            else:
                current_world_index += 1
                world_changed = True
        if level_changed:
            languages.lang_print("seperator.title", text=languages.lang_format("title.level"))
            current_cursor_pos = (0, 0)
            current_level_index = current_level_index % len(levelpack.level_list) if current_level_index >= 0 else len(levelpack.level_list) - 1
            current_level = levelpack.level_list[current_level_index]
            languages.lang_print(languages.current_language["edit.level.current.name"], value=current_level.level_id.name)
            level_changed = False
        if world_changed:
            languages.lang_print("seperator.title", text=languages.lang_format("title.world"))
            current_cursor_pos = (0, 0)
            current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
            current_world = current_level.world_list[current_world_index]
            languages.lang_print(languages.current_language["edit.world.current.name"], value=current_world.world_id.name)
            languages.lang_print(languages.current_language["edit.world.current.infinite_tier"], value=current_world.world_id.infinite_tier)
            world_changed = False
        # display
        for world in current_level.world_list:
            world.set_sprite_states(0)
        window.fill("#000000")
        displays.set_pixel_size(window.get_size())
        current_world_surface = current_level.show_world(current_world, wiggle, cursor=current_cursor_pos, debug=True)
        window.blit(pygame.transform.scale(current_world_surface, (window.get_height() * current_world.width // current_world.height, window.get_height())), (0, 0))
        if issubclass(current_object_type, objects.WorldPointer):
            if issubclass(current_object_type, objects.World):
                current_object_surface = displays.set_surface_color_dark(current_world_surface, 0xC0C0C0)
            elif issubclass(current_object_type, objects.Clone):
                current_object_surface = displays.set_surface_color_light(current_world_surface, 0x404040)
            current_object_surface = pygame.transform.scale(current_object_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
        elif issubclass(current_object_type, objects.LevelPointer):
            current_object_surface = displays.sprites.get(current_object_type.sprite_name, 0, wiggle)
            current_object_surface = pygame.transform.scale(current_object_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
        elif issubclass(current_object_type, objects.Metatext):
            current_object_surface = displays.sprites.get(current_object_type.sprite_name, 0, wiggle)
            current_object_surface = pygame.transform.scale(current_object_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
            tier_surface = pygame.Surface((displays.sprite_size * len(str(current_object_type.meta_tier)), displays.sprite_size), pygame.SRCALPHA)
            tier_surface.fill("#00000000")
            for digit, char in enumerate(str(current_object_type.meta_tier)):
                tier_surface.blit(displays.sprites.get("text_" + char, 0, wiggle), (displays.sprite_size * digit, 0))
            tier_surface = displays.set_alpha(tier_surface, 0x80)
            tier_surface = pygame.transform.scale(tier_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size / len(str(current_object_type.meta_tier))))
            tier_surface_pos = ((current_object_surface.get_width() - tier_surface.get_width()) // 2,
                                (current_object_surface.get_height() - tier_surface.get_height()) // 2)
            current_object_surface.blit(tier_surface, tier_surface_pos)
        else:
            current_object_surface = displays.sprites.get(current_object_type.sprite_name, 0, wiggle)
            current_object_surface = pygame.transform.scale(current_object_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
        window.blit(current_object_surface, (window.get_width() - displays.pixel_sprite_size, 0))
        for index, obj_type in object_type_shortcuts.items():
            obj = obj_type((0, 0), spaces.Orient.S)
            obj.set_sprite()
            obj_surface = displays.sprites.get(obj_type.sprite_name, obj.sprite_state, wiggle)
            obj_surface = pygame.transform.scale(obj_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
            obj_surface_pos = (window.get_width() + (index % 5 * displays.pixel_sprite_size) - (displays.pixel_sprite_size * 5),
                               window.get_height() + (index // 5 * displays.pixel_sprite_size) - (displays.pixel_sprite_size * 2))
            if isinstance(obj, objects.World):
                obj_surface = displays.set_surface_color_dark(current_world_surface, 0xC0C0C0)
                obj_surface = pygame.transform.scale(obj_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
            elif isinstance(obj, objects.Clone):
                obj_surface = displays.set_surface_color_light(current_world_surface, 0x404040)
                obj_surface = pygame.transform.scale(obj_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
            elif isinstance(obj, objects.Metatext):
                tier_surface = pygame.Surface((displays.sprite_size * len(str(obj.meta_tier)), displays.sprite_size), pygame.SRCALPHA)
                tier_surface.fill("#00000000")
                for digit, char in enumerate(str(obj.meta_tier)):
                    tier_surface.blit(displays.sprites.get("text_" + char, 0, wiggle), (displays.sprite_size * digit, 0))
                tier_surface = displays.set_alpha(tier_surface, 0x88)
                tier_surface = pygame.transform.scale(tier_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size / len(str(obj.meta_tier))))
                tier_surface_pos = ((obj_surface.get_width() - tier_surface.get_width()) // 2,
                                    (obj_surface.get_height() - tier_surface.get_height()) // 2)
                obj_surface.blit(tier_surface, tier_surface_pos)
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