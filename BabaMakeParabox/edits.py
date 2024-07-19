import copy

from BabaMakeParabox import basics
from BabaMakeParabox import languages
from BabaMakeParabox import colors
from BabaMakeParabox import spaces
from BabaMakeParabox import objects
from BabaMakeParabox import rules
from BabaMakeParabox import worlds
from BabaMakeParabox import displays
from BabaMakeParabox import levels
from BabaMakeParabox import levelpacks

import pygame

def levelpack_editor(levelpack: levelpacks.levelpack) -> levelpacks.levelpack:
    print("Global Rule List:")
    for rule in levelpack.rule_list:
        str_list = []
        for obj_type in rule:
            str_list.append(obj_type.class_name)
        print(" ".join(str_list))
    for level in levelpack.level_list:
        level.rule_list = levelpack.rule_list
        level.update_rules()
        for world in level.world_list:
            world.set_sprite_states(0)
    history = [copy.deepcopy(levelpack)]
    window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption(f"Baba Make Parabox In-game Editor Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("BabaMakeParabox.png"))
    displays.sprites.update()
    pygame.key.stop_text_input()
    clock = pygame.time.Clock()
    keybinds = {"W": pygame.K_w,
                "A": pygame.K_a,
                "S": pygame.K_s,
                "D": pygame.K_d,
                "Q": pygame.K_q,
                "E": pygame.K_e,
                "Z": pygame.K_z,
                "X": pygame.K_x,
                "C": pygame.K_c,
                "V": pygame.K_v,
                "R": pygame.K_r,
                "T": pygame.K_t,
                "1": pygame.K_1,
                "2": pygame.K_2,
                "3": pygame.K_3,
                "4": pygame.K_4,
                "5": pygame.K_5,
                "6": pygame.K_6,
                "7": pygame.K_7,
                "8": pygame.K_8,
                "9": pygame.K_9,
                "0": pygame.K_0,
                "-": pygame.K_MINUS,
                "=": pygame.K_EQUALS,
                "RETURN": pygame.K_RETURN,
                "BACKSLASH": pygame.K_BACKSLASH,
                "BACKSPACE": pygame.K_BACKSPACE,
                "DELETE": pygame.K_DELETE,
                "TAB": pygame.K_TAB,
                "LSHIFT": pygame.K_LSHIFT,
                "RSHIFT": pygame.K_RSHIFT,
                "LCTRL": pygame.K_LCTRL,
                "RCTRL": pygame.K_RCTRL,
                "F1": pygame.K_F1}
    keys = {v: False for v in keybinds.values()}
    cooldowns = {v: 0 for v in keybinds.values()}
    window.fill("#000000")
    current_level_index: int = 0
    current_level = levelpack.level_list[current_level_index]
    current_world_index: int = 0
    current_world = current_level.world_list[current_world_index]
    object_list = [t for t in objects.object_name.values() if t not in objects.not_in_editor]
    current_object_index = 0
    current_object_type = object_list[current_object_index]
    current_facing = spaces.S
    current_object = displays.set_sprite_state(current_object_type((0, 0), current_facing))
    current_cursor_pos = (0, 0)
    current_clipboard = []
    object_type_shortcuts: dict[int, type[objects.Object]] = {k: objects.object_name[v] for k, v in enumerate(basics.options["object_type_shortcuts"])}
    level_changed = True
    world_changed = True
    yes = ["y", "Y", "yes", "Yes", "YES"]
    frame = 0
    wiggle = 1
    editor_running = True
    milliseconds = 1000 // basics.options["fps"]
    real_fps = basics.options["fps"]
    while editor_running:
        frame += 1
        if frame >= basics.options["fpw"]:
            frame = 0
            wiggle = wiggle % 3 + 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editor_running = False
            if event.type == pygame.KEYDOWN and event.key in keybinds.values():
                keys[event.key] = True
            elif event.type == pygame.KEYUP and event.key in keybinds.values():
                keys[event.key] = False
        if keys[keybinds["W"]] and cooldowns[keybinds["W"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                current_facing = spaces.W
            else:
                new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.W)
                if not current_world.out_of_range(new_cursor_pos):
                    current_cursor_pos = new_cursor_pos
        elif keys[keybinds["S"]] and cooldowns[keybinds["S"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                current_facing = spaces.S
            else:
                new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.S)
                if not current_world.out_of_range(new_cursor_pos):
                    current_cursor_pos = new_cursor_pos
        elif keys[keybinds["A"]] and cooldowns[keybinds["A"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                current_facing = spaces.A
            else:
                new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.A)
                if not current_world.out_of_range(new_cursor_pos):
                    current_cursor_pos = new_cursor_pos
        elif keys[keybinds["D"]] and cooldowns[keybinds["D"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                current_facing = spaces.D
            else:
                new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.D)
                if not current_world.out_of_range(new_cursor_pos):
                    current_cursor_pos = new_cursor_pos
        elif keys[keybinds["Q"]] and cooldowns[keybinds["Q"]] == 0:
            current_object_index -= 1
        elif keys[keybinds["E"]] and cooldowns[keybinds["E"]] == 0:
            current_object_index += 1
        elif keys[keybinds["1"]] and cooldowns[keybinds["1"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[0] = current_object_type
                basics.options["object_type_shortcuts"][0] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[0])
        elif keys[keybinds["2"]] and cooldowns[keybinds["2"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[1] = current_object_type
                basics.options["object_type_shortcuts"][1] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[1])
        elif keys[keybinds["3"]] and cooldowns[keybinds["3"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[2] = current_object_type
                basics.options["object_type_shortcuts"][2] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[2])
        elif keys[keybinds["4"]] and cooldowns[keybinds["4"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[3] = current_object_type
                basics.options["object_type_shortcuts"][3] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[3])
        elif keys[keybinds["5"]] and cooldowns[keybinds["5"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[4] = current_object_type
                basics.options["object_type_shortcuts"][4] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[4])
        elif keys[keybinds["6"]] and cooldowns[keybinds["6"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[5] = current_object_type
                basics.options["object_type_shortcuts"][5] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[5])
        elif keys[keybinds["7"]] and cooldowns[keybinds["7"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[6] = current_object_type
                basics.options["object_type_shortcuts"][6] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[6])
        elif keys[keybinds["8"]] and cooldowns[keybinds["8"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[7] = current_object_type
                basics.options["object_type_shortcuts"][7] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[7])
        elif keys[keybinds["9"]] and cooldowns[keybinds["9"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[8] = current_object_type
                basics.options["object_type_shortcuts"][8] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[8])
        elif keys[keybinds["0"]] and cooldowns[keybinds["0"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                object_type_shortcuts[9] = current_object_type
                basics.options["object_type_shortcuts"][9] = {v: k for k, v in objects.object_name.items()}[current_object_type]
            else:
                current_object_index = object_list.index(object_type_shortcuts[9])
        elif keys[keybinds["RETURN"]] and cooldowns[keybinds["RETURN"]] == 0:
            history.append(copy.deepcopy(levelpack))
            if issubclass(current_object_type, objects.Level):
                if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
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
                current_world.new_obj(current_object_type(current_cursor_pos, name, icon_name, icon_color, current_facing))
            elif issubclass(current_object_type, objects.WorldPointer):
                if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                    name = input(languages.current_language["editor.world.new.name"])
                    inf_tier = input(languages.current_language["editor.world.new.inf_tier"])
                    inf_tier = int(inf_tier) if inf_tier != "" else 0
                    name, inf_tier = (name, inf_tier) if current_level.get_world(name, inf_tier) is not None else (current_world.name, current_world.inf_tier)
                else:
                    name = current_world.name
                    inf_tier = current_world.inf_tier
                current_world.new_obj(current_object_type(current_cursor_pos, name, inf_tier, current_facing))
            else:
                current_world.new_obj(current_object_type(current_cursor_pos, current_facing))
        elif keys[keybinds["BACKSLASH"]] and cooldowns[keybinds["BACKSLASH"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                if input(languages.current_language["editor.level.new"]) in yes:
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
                    inf_tier = input(languages.current_language["editor.world.new.inf_tier"])
                    inf_tier = int(inf_tier) if inf_tier != "" else 0
                    color = input(languages.current_language["editor.world.new.color"])
                    color = colors.str_to_hex(color) if color != "" else basics.options["default_new_world"]["color"]
                    default_world = worlds.world(name, size, inf_tier, color)
                    levelpack.level_list.append(levels.level(level_name, [default_world], super_level, name, inf_tier, levelpack.rule_list))
                    current_level_index = len(levelpack.level_list) - 1
                    current_world_index = 0
                    level_changed = True
                    world_changed = True
            else:
                if input(languages.current_language["editor.world.new"]) in yes:
                    history.append(copy.deepcopy(levelpack))
                    name = input(languages.current_language["editor.world.new.name"])
                    width = input(languages.current_language["editor.world.new.width"])
                    width = int(width) if width != "" else basics.options["default_new_world"]["width"]
                    height = input(languages.current_language["editor.world.new.height"])
                    height = int(height) if height != "" else basics.options["default_new_world"]["height"]
                    size = (width, height)
                    inf_tier = input(languages.current_language["editor.world.new.inf_tier"])
                    inf_tier = int(inf_tier) if inf_tier != "" else 0
                    color = input(languages.current_language["editor.world.new.color"])
                    color = colors.str_to_hex(color) if color != "" else basics.options["default_new_world"]["color"]
                    current_level.world_list.append(worlds.world(name, size, inf_tier, color))
                    current_world_index = len(current_level.world_list) - 1
                    world_changed = True
        elif keys[keybinds["DELETE"]] and cooldowns[keybinds["DELETE"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                if input(languages.current_language["editor.level.delete"]) in yes:
                    levelpack.level_list.pop(current_level_index)
                    current_level_index -= 1
                    current_world_index = 0
                    level_changed = True
                    world_changed = True
            else:
                if input(languages.current_language["editor.world.delete"]) in yes:
                    current_level.world_list.pop(current_world_index)
                    current_world_index -= 1
                    world_changed = True
        elif keys[keybinds["R"]] and cooldowns[keybinds["R"]] == 0:
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
                    if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                        levelpack.rule_list.pop(dupe_list.index(True))
                else:
                    if not (keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]):
                        levelpack.rule_list.append(list(type_rule))
            print(languages.current_language["editor.levelpack.rule_list"])
            for rule in levelpack.rule_list:
                str_list = []
                for obj_type in rule:
                    str_list.append(obj_type.class_name)
                print(" ".join(str_list))
        elif keys[keybinds["T"]] and cooldowns[keybinds["T"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                current_level.name = input(languages.current_language["editor.level.rename"])
            else:
                current_world.name = input(languages.current_language["editor.world.rename"])
        elif keys[keybinds["BACKSPACE"]] and cooldowns[keybinds["BACKSPACE"]] == 0:
            history.append(copy.deepcopy(levelpack))
            current_world.del_objs_from_pos(current_cursor_pos)
        elif keys[keybinds["TAB"]] and cooldowns[keybinds["TAB"]] == 0:
            try:
                obj_to_noun = None
                if not issubclass(current_object_type, objects.Noun):
                    obj_to_noun = objects.nouns_objs_dicts.get_noun(current_object_type)
            except KeyError:
                pass
            try:
                noun_to_obj = None
                if issubclass(current_object_type, objects.Noun):
                    noun_to_obj = objects.nouns_objs_dicts.get_obj(current_object_type)
            except KeyError:
                pass
            new_object_type = obj_to_noun if obj_to_noun is not None else (noun_to_obj if noun_to_obj is not None else None)
            if new_object_type is not None:
                try:
                    new_object_index = object_list.index(new_object_type)
                    current_object_index = new_object_index
                except ValueError:
                    pass
        elif keys[keybinds["Z"]] and cooldowns[keybinds["Z"]] == 0:
            if len(history) > 1:
                levelpack = copy.deepcopy(history.pop())
            else:
                levelpack = copy.deepcopy(history[0])
            world_changed = True
            level_changed = True
        elif keys[keybinds["X"]] and cooldowns[keybinds["X"]] == 0:
            history.append(copy.deepcopy(levelpack))
            current_clipboard = current_world.get_objs_from_pos(current_cursor_pos)
            current_world.del_objs_from_pos(current_cursor_pos)
        elif keys[keybinds["C"]] and cooldowns[keybinds["C"]] == 0:
            history.append(copy.deepcopy(levelpack))
            current_clipboard = current_world.get_objs_from_pos(current_cursor_pos)
        elif keys[keybinds["V"]] and cooldowns[keybinds["V"]] == 0:
            history.append(copy.deepcopy(levelpack))
            for obj in current_clipboard:
                new_obj = copy.deepcopy(obj)
                new_obj.pos = current_cursor_pos
                current_world.new_obj(new_obj)
                if isinstance(obj, objects.WorldPointer):
                    name = obj.name
                    inf_tier = obj.inf_tier
                    for level in levelpack.level_list:
                        world = level.get_world(name, inf_tier)
                        if world is not None:
                            for new_world in level.world_list:
                                current_level.set_world(new_world)
        elif keys[keybinds["-"]] and cooldowns[keybinds["-"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                current_level_index -= 1
                current_world_index = 0
                level_changed = True
                world_changed = True
            else:
                current_world_index -= 1
                world_changed = True
        elif keys[keybinds["="]] and cooldowns[keybinds["="]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                current_level_index += 1
                current_world_index = 0
                level_changed = True
                world_changed = True
            else:
                current_world_index += 1
                world_changed = True
        for key, value in keys.items():
            if value and cooldowns[key] == 0:
                cooldowns[key] = basics.options["input_cooldown"]
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
            print(languages.current_language["editor.world.current.inf_tier"], current_world.inf_tier, sep="")
            world_changed = False
        current_object_index = current_object_index % len(object_list) if current_object_index >= 0 else len(object_list) - 1
        current_object_type = object_list[current_object_index]
        for world in current_level.world_list:
            world.set_sprite_states(0)
        window.fill("#000000")
        displays.set_pixel_size(window.get_size())
        window.blit(pygame.transform.scale(current_level.show_world(current_world, wiggle, cursor=current_cursor_pos),
                                           (window.get_height(), window.get_height() * current_world.height // current_world.width)), (0, 0))
        current_object = displays.set_sprite_state(current_object_type((0, 0), current_facing))
        window.blit(pygame.transform.scale(displays.sprites.get(current_object_type.sprite_name, current_object.sprite_state, wiggle),
                                           (displays.pixel_sprite_size, displays.pixel_sprite_size)), (window.get_width() - displays.pixel_sprite_size, 0))
        for index, obj_type in object_type_shortcuts.items():
            obj = displays.set_sprite_state(obj_type((0, 0), spaces.S))
            window.blit(pygame.transform.scale(displays.sprites.get(obj_type.sprite_name, obj.sprite_state, wiggle),
                                               (displays.pixel_sprite_size, displays.pixel_sprite_size)),
                        (window.get_width() + (index % 5 * displays.pixel_sprite_size) - (displays.pixel_sprite_size * 5),
                         window.get_height() + (index // 5 * displays.pixel_sprite_size) - (displays.pixel_sprite_size * 2)))
        real_fps = min(1000 / milliseconds, (real_fps * (basics.options["fps"] - 1) + 1000 / milliseconds) / basics.options["fps"])
        if keys[keybinds["F1"]]:
            real_fps_string = str(int(real_fps))
            for i in range(len(real_fps_string)):
                window.blit(displays.sprites.get(f"text_{real_fps_string[i]}", 0, wiggle), (i * displays.sprite_size, 0))
        pygame.display.flip()
        for key in cooldowns:
            if cooldowns[key] > 0:
                cooldowns[key] -= 1
        milliseconds = clock.tick(basics.options["fps"])
    return levelpack