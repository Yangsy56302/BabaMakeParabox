import copy

from BabaMakeParabox import basics, languages, colors, spaces, objects, rules, worlds, displays, levels, levelpacks

import pygame

def levelpack_editor(levelpack: levelpacks.Levelpack) -> levelpacks.Levelpack:
    for level in levelpack.level_list:
        for world in level.world_list:
            world.set_sprite_states(0)
    history = [copy.deepcopy(levelpack)]
    window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption(f"Baba Make Parabox In-game Editor Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("BabaMakeParabox.png"))
    displays.sprites.update()
    pygame.key.set_repeat()
    pygame.key.stop_text_input()
    clock = pygame.time.Clock()
    keybinds = {pygame.K_w: "W",
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
                pygame.K_F1: "F1"}
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
    current_object = displays.set_sprite_state(current_object_type((0, 0), current_orient))
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
            if event.type == pygame.KEYDOWN:
                if event.key in keybinds.keys():
                    keys[keybinds[event.key]] = True
                for n, key in keymods.items():
                    if event.mod & n:
                        keys[key] = True
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
        elif keys["Q"]:
            current_object_type_list = list(objects.object_name.values())
            current_object_type_index = current_object_type_list.index(current_object_type)
            current_object_type = current_object_type_list[current_object_type_index - 1 if current_object_type_index >= 0 else len(current_object_type_list) - 1]
        elif keys["E"]:
            current_object_type_list = list(objects.object_name.values())
            current_object_type_index = current_object_type_list.index(current_object_type)
            current_object_type = current_object_type_list[current_object_type_index + 1 if current_object_type_index < len(current_object_type_list) else 0]
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
        elif keys["RETURN"]:
            if keys["LCTRL"] or keys["RCTRL"] or len(current_world.get_objs_from_pos(current_cursor_pos)) == 0:
                history.append(copy.deepcopy(levelpack))
                if issubclass(current_object_type, objects.LevelPointer):
                    if keys["LSHIFT"] or keys["RSHIFT"]:
                        name = input(languages.current_language["editor.level.new.name"])
                        name = name if levelpack.get_level(name) is not None else current_level.name
                        icon_name = input(languages.current_language["editor.level.new.icon.name"])
                        icon_name = icon_name if icon_name != "" else "empty"
                        icon_color = input(languages.current_language["editor.level.new.icon.color"])
                        icon_color = colors.str_to_hex(icon_color) if icon_color != "" else colors.WHITE
                    else:
                        name = current_level.name
                        icon_name = "empty"
                        icon_color = colors.WHITE
                    level_info: objects.LevelPointerExtraJson = {"name": name, "icon": {"name": icon_name, "color": icon_color}}
                    current_world.new_obj(current_object_type(current_cursor_pos, current_orient, level_info=level_info))
                elif issubclass(current_object_type, objects.WorldPointer):
                    if keys["LSHIFT"] or keys["RSHIFT"]:
                        name = input(languages.current_language["editor.world.new.name"])
                        infinite_tier = input(languages.current_language["editor.world.new.infinite_tier"])
                        infinite_tier = int(infinite_tier) if infinite_tier != "" else 0
                        name, infinite_tier = (name, infinite_tier) if current_level.get_world({"name": name, "infinite_tier": infinite_tier}) is not None else (current_world.name, current_world.infinite_tier)
                    else:
                        name = current_world.name
                        infinite_tier = current_world.infinite_tier
                    if current_object_type == objects.World:
                        current_level.selected_world_to_clone(name, infinite_tier)
                    world_info: objects.WorldPointerExtraJson = {"name": name, "infinite_tier": infinite_tier}
                    current_world.new_obj(current_object_type(current_cursor_pos, current_orient, world_info=world_info))
                else:
                    current_world.new_obj(current_object_type(current_cursor_pos, current_orient))
        elif keys["BACKSLASH"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                if input(languages.current_language["editor.level.new"]) in languages.yes:
                    history.append(copy.deepcopy(levelpack))
                    level_name = input(languages.current_language["editor.level.new.name"])
                    super_level = input(languages.current_language["editor.level.new.super_level.name"])
                    super_level = super_level if super_level != "" else current_level.name
                    name = input(languages.current_language["editor.world.new.name"])
                    width = input(languages.current_language["editor.world.new.width"])
                    width = int(width) if width != "" else basics.options["default_new_world"]["width"]
                    height = input(languages.current_language["editor.world.new.height"])
                    height = int(height) if height != "" else basics.options["default_new_world"]["height"]
                    size = (width, height)
                    infinite_tier = input(languages.current_language["editor.world.new.infinite_tier"])
                    infinite_tier = int(infinite_tier) if infinite_tier != "" else 0
                    color = input(languages.current_language["editor.world.new.color"])
                    color = colors.str_to_hex(color) if color != "" else basics.options["default_new_world"]["color"]
                    default_world = worlds.World(name, size, infinite_tier, color)
                    levelpack.level_list.append(levels.Level(level_name, [default_world], super_level, name, infinite_tier, levelpack.rule_list))
                    current_level_index = len(levelpack.level_list) - 1
                    current_world_index = 0
                    level_changed = True
                    world_changed = True
            else:
                if input(languages.current_language["editor.world.new"]) in languages.yes:
                    history.append(copy.deepcopy(levelpack))
                    name = input(languages.current_language["editor.world.new.name"])
                    width = input(languages.current_language["editor.world.new.width"])
                    width = int(width) if width != "" else basics.options["default_new_world"]["width"]
                    height = input(languages.current_language["editor.world.new.height"])
                    height = int(height) if height != "" else basics.options["default_new_world"]["height"]
                    size = (width, height)
                    infinite_tier = input(languages.current_language["editor.world.new.infinite_tier"])
                    infinite_tier = int(infinite_tier) if infinite_tier != "" else 0
                    color = input(languages.current_language["editor.world.new.color"])
                    color = colors.str_to_hex(color) if color != "" else basics.options["default_new_world"]["color"]
                    current_level.world_list.append(worlds.World(name, size, infinite_tier, color))
                    current_world_index = len(current_level.world_list) - 1
                    world_changed = True
        elif keys["DELETE"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                if input(languages.current_language["editor.level.delete"]) in languages.yes:
                    levelpack.level_list.pop(current_level_index)
                    current_level_index -= 1
                    current_world_index = 0
                    level_changed = True
                    world_changed = True
            else:
                if input(languages.current_language["editor.world.delete"]) in languages.yes:
                    current_level.world_list.pop(current_world_index)
                    current_world_index -= 1
                    world_changed = True
        elif keys["R"]:
            text_rule = input(languages.current_language["editor.levelpack.new.rule"]).upper().split()
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
            print(languages.current_language["editor.levelpack.rule_list"])
            for rule in levelpack.rule_list:
                str_list = []
                for obj_type in rule:
                    str_list.append(obj_type.display_name)
                print(" ".join(str_list))
        elif keys["T"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                current_level.name = input(languages.current_language["editor.level.rename"])
            else:
                current_world.name = input(languages.current_language["editor.world.rename"])
        elif keys["BACKSPACE"]:
            history.append(copy.deepcopy(levelpack))
            current_world.del_objs_from_pos(current_cursor_pos)
        elif keys["TAB"]:
            if keys["LSHIFT"] or keys["RSHIFT"]:
                if issubclass(current_object_type, objects.Noun) and current_object_type.obj_type not in objects.not_in_editor:
                    current_object_type = current_object_type.obj_type
            else:
                obj_to_noun = objects.get_noun_from_obj(current_object_type)
                if obj_to_noun not in objects.not_in_editor:
                    current_object_type = obj_to_noun
        elif keys["Z"]:
            if len(history) > 1:
                levelpack = copy.deepcopy(history.pop())
            else:
                levelpack = copy.deepcopy(history[0])
            world_changed = True
            level_changed = True
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
                if type(obj) == objects.World:
                    current_level.selected_world_to_clone(obj.world_info["name"], obj.world_info["infinite_tier"])
                current_world.new_obj(obj)
                if isinstance(obj, objects.WorldPointer):
                    name = obj.world_info["name"]
                    infinite_tier = obj.world_info["infinite_tier"]
                    for level in levelpack.level_list:
                        world = level.get_world({"name": name, "infinite_tier": infinite_tier})
                        if world is not None:
                            for new_world in level.world_list:
                                current_level.set_world(new_world)
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
            current_cursor_pos = (0, 0)
            current_level_index = current_level_index % len(levelpack.level_list) if current_level_index >= 0 else len(levelpack.level_list) - 1
            current_level = levelpack.level_list[current_level_index]
            print(languages.current_language["editor.level.current.name"], current_level.name, sep="")
            level_changed = False
        if world_changed:
            current_cursor_pos = (0, 0)
            current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
            current_world = current_level.world_list[current_world_index]
            print(languages.current_language["editor.world.current.name"], current_world.name, sep="")
            print(languages.current_language["editor.world.current.infinite_tier"], current_world.infinite_tier, sep="")
            world_changed = False
        for world in current_level.world_list:
            world.set_sprite_states(0)
        window.fill("#000000")
        displays.set_pixel_size(window.get_size())
        current_world_surface = current_level.show_world(current_world, wiggle, cursor=current_cursor_pos)
        window.blit(pygame.transform.scale(current_world_surface, (window.get_height() * current_world.width // current_world.height, window.get_height())), (0, 0))
        if issubclass(current_object_type, objects.WorldPointer):
            if issubclass(current_object_type, objects.World):
                current_object_surface = displays.set_surface_color_dark(current_world_surface, 0xCCCCCC)
                current_object_surface = pygame.transform.scale(current_object_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
            elif issubclass(current_object_type, objects.Clone):
                current_object_surface = displays.set_surface_color_light(current_world_surface, 0x444444)
                current_object_surface = pygame.transform.scale(current_object_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
        elif issubclass(current_object_type, objects.LevelPointer):
            current_object_surface = displays.sprites.get(current_object_type.sprite_name, 0, wiggle)
            current_object_surface = pygame.transform.scale(current_object_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
        elif issubclass(current_object_type, objects.Metatext):
            current_object = displays.set_sprite_state(current_object_type((0, 0), current_orient, level_info=None, world_info=None))
            current_object_surface = displays.sprites.get(current_object_type.sprite_name, current_object.sprite_state, wiggle)
            current_object_surface = pygame.transform.scale(current_object_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
            tier_surface = pygame.Surface((displays.sprite_size * len(str(current_object_type.meta_tier)), displays.sprite_size), pygame.SRCALPHA)
            tier_surface.fill("#00000000")
            for digit, char in enumerate(str(current_object_type.meta_tier)):
                tier_surface.blit(displays.sprites.get("text_" + char, 0, wiggle), (displays.sprite_size * digit, 0))
            tier_surface = displays.set_alpha(tier_surface, 0x88)
            tier_surface = pygame.transform.scale(tier_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size / len(str(current_object_type.meta_tier))))
            tier_surface_pos = ((current_object_surface.get_width() - tier_surface.get_width()) // 2,
                                (current_object_surface.get_height() - tier_surface.get_height()) // 2)
            current_object_surface.blit(tier_surface, tier_surface_pos)
        else:
            current_object = displays.set_sprite_state(current_object_type((0, 0), current_orient, level_info=None, world_info=None))
            current_object_surface = displays.sprites.get(current_object_type.sprite_name, current_object.sprite_state, wiggle)
            current_object_surface = pygame.transform.scale(current_object_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
        window.blit(current_object_surface, (window.get_width() - displays.pixel_sprite_size, 0))
        for index, obj_type in object_type_shortcuts.items():
            obj = displays.set_sprite_state(obj_type((0, 0), spaces.Orient.S))
            obj_surface = displays.sprites.get(obj_type.sprite_name, obj.sprite_state, wiggle)
            obj_surface = pygame.transform.scale(obj_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
            obj_surface_pos = (window.get_width() + (index % 5 * displays.pixel_sprite_size) - (displays.pixel_sprite_size * 5),
                               window.get_height() + (index // 5 * displays.pixel_sprite_size) - (displays.pixel_sprite_size * 2))
            if isinstance(obj, objects.World):
                obj_surface = displays.set_surface_color_dark(current_world_surface, 0xCCCCCC)
                obj_surface = pygame.transform.scale(obj_surface, (displays.pixel_sprite_size, displays.pixel_sprite_size))
            elif isinstance(obj, objects.Clone):
                obj_surface = displays.set_surface_color_light(current_world_surface, 0x444444)
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
    return levelpack