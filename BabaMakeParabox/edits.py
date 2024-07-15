import BabaMakeParabox.basics as basics
import BabaMakeParabox.spaces as spaces
import BabaMakeParabox.objects as objects
import BabaMakeParabox.rules as rules
import BabaMakeParabox.worlds as worlds
import BabaMakeParabox.displays as displays
import BabaMakeParabox.levels as levels
import BabaMakeParabox.levelpacks as levelpacks

import copy
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
    window = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption(f"Baba Make Parabox In-game Editor Version {basics.versions}")
    pygame.display.set_icon(pygame.image.load("BabaMakeParabox.png"))
    displays.sprites.update()
    pygame.key.stop_text_input()
    clock = pygame.time.Clock()
    keybinds = {"W": pygame.K_w,
                "A": pygame.K_a,
                "S": pygame.K_s,
                "D": pygame.K_d,
                "I": pygame.K_i,
                "K": pygame.K_k,
                "J": pygame.K_j,
                "L": pygame.K_l,
                "Q": pygame.K_q,
                "E": pygame.K_e,
                "Z": pygame.K_z,
                "X": pygame.K_x,
                "C": pygame.K_c,
                "V": pygame.K_v,
                "O": pygame.K_o,
                "P": pygame.K_p,
                "N": pygame.K_n,
                "M": pygame.K_m,
                "R": pygame.K_r,
                "-": pygame.K_MINUS,
                "=": pygame.K_EQUALS,
                "RETURN": pygame.K_RETURN,
                "BACKSPACE": pygame.K_BACKSPACE,
                "TAB": pygame.K_TAB,
                "LSHIFT": pygame.K_LSHIFT,
                "RSHIFT": pygame.K_RSHIFT,
                "LCTRL": pygame.K_LCTRL,
                "RCTRL": pygame.K_RCTRL}
    keys = {v: False for v in keybinds.values()}
    cooldowns = {v: 0 for v in keybinds.values()}
    window.fill("#000000")
    current_level_index = 0
    current_level = levelpack.level_list[current_level_index]
    current_world_index = 0
    current_world = current_level.world_list[current_world_index]
    object_list = [t for t in objects.object_name.values() if t not in objects.not_in_editor]
    current_object_index = 0
    current_object_type = object_list[current_object_index]
    current_facing = spaces.S
    current_cursor_pos = (0, 0)
    current_clipboard = []
    level_changed = True
    world_changed = True
    yes = ["y", "Y", "yes", "Yes", "YES"]
    window.fill("#000000")
    window.blit(pygame.transform.scale(current_level.show_world(current_world, 1, cursor=current_cursor_pos), (720, 720)), (0, 0))
    current_object = displays.set_sprite_state(current_object_type((0, 0), current_facing))
    window.blit(pygame.transform.scale(displays.sprites.get(current_object_type.sprite_name, current_object.sprite_state, 1), (72, 72)), (1208, 0))
    pygame.display.flip()
    frame = 0
    wiggle = 1
    editor_running = True
    while editor_running:
        frame += 1
        if frame >= basics.options.setdefault("fpw", 5):
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
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.W)
            if not current_world.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
        elif keys[keybinds["S"]] and cooldowns[keybinds["S"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.S)
            if not current_world.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
        elif keys[keybinds["A"]] and cooldowns[keybinds["A"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.A)
            if not current_world.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
        elif keys[keybinds["D"]] and cooldowns[keybinds["D"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, spaces.D)
            if not current_world.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
        elif keys[keybinds["I"]] and cooldowns[keybinds["I"]] == 0:
            current_facing = spaces.W
        elif keys[keybinds["K"]] and cooldowns[keybinds["K"]] == 0:
            current_facing = spaces.S
        elif keys[keybinds["J"]] and cooldowns[keybinds["J"]] == 0:
            current_facing = spaces.A
        elif keys[keybinds["L"]] and cooldowns[keybinds["L"]] == 0:
            current_facing = spaces.D
        elif keys[keybinds["Q"]] and cooldowns[keybinds["Q"]] == 0:
            current_object_index -= 1
        elif keys[keybinds["E"]] and cooldowns[keybinds["E"]] == 0:
            current_object_index += 1
        elif keys[keybinds["RETURN"]] and cooldowns[keybinds["RETURN"]] == 0:
            history.append(copy.deepcopy(levelpack))
            if issubclass(current_object_type, objects.Level):
                icon_name = input("Level's Icon Name (like: \"baba\", \"text_baba\"...): ")
                icon_name = icon_name if icon_name is not None else "empty"
                icon_color = input("Level's Icon Color: ")
                icon_color = pygame.Color(icon_color) if icon_color != "" else displays.WHITE
                current_world.new_obj(current_object_type(current_cursor_pos, current_level.name, icon_name, icon_color, current_facing))
            elif issubclass(current_object_type, objects.World):
                for world in current_level.world_list:
                    for world_obj in [o for o in world.object_list if isinstance(o, objects.World)]:
                        if current_world.name == world_obj.name and current_world.inf_tier == world_obj.inf_tier:
                            world.new_obj(objects.Clone(world_obj.pos, world_obj.name, world_obj.inf_tier, world_obj.facing))
                            world.del_obj(world_obj.uuid)
                current_world.new_obj(current_object_type(current_cursor_pos, current_world.name, current_world.inf_tier, current_facing))
            elif issubclass(current_object_type, objects.Clone):
                current_world.new_obj(current_object_type(current_cursor_pos, current_world.name, current_world.inf_tier, current_facing))
            else:
                current_world.new_obj(current_object_type(current_cursor_pos, current_facing))
        elif keys[keybinds["P"]] and cooldowns[keybinds["P"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                if input("Are you sure you want to create a new level? [y/N]: ") in yes:
                    history.append(copy.deepcopy(levelpack))
                    level_name = input("Level's Name: ")
                    super_level = input("Superlevel's Name: ")
                    super_level = super_level if super_level != "" else current_level.name
                    name = input("World's Name: ")
                    width = input("World's Width: ")
                    width = int(width) if width != "" else basics.options.setdefault("default_new_world", {"width": 9}).get("width", 9)
                    height = input("World's Height: ")
                    height = int(height) if height != "" else basics.options.setdefault("default_new_world", {"height": 9}).get("height", 9)
                    size = (width, height)
                    inf_tier = input("World's Infinite Tier: ")
                    inf_tier = int(inf_tier) if inf_tier != "" else 0
                    color = input("World's color: ")
                    color = pygame.Color(color if color != "" else basics.options.setdefault("default_new_world", {"color": "#000000"}).get("color", "#000000"))
                    default_world = worlds.world(name, size, inf_tier, color)
                    levelpack.level_list.append(levels.level(level_name, [default_world], super_level, name, inf_tier, levelpack.rule_list))
                    current_level_index = len(levelpack.level_list) - 1
                    current_world_index = 0
                    level_changed = True
                    world_changed = True
            else:
                if input("Are you sure you want to create a new world? [y/N]: ") in yes:
                    history.append(copy.deepcopy(levelpack))
                    name = input("World's Name: ")
                    width = input("World's width: ")
                    width = int(width) if width != "" else basics.options.setdefault("default_new_world", {"width": 9}).get("width", 9)
                    height = input("World's height: ")
                    height = int(height) if height != "" else basics.options.setdefault("default_new_world", {"height": 9}).get("height", 9)
                    size = (width, height)
                    inf_tier = input("World's infinite tier: ")
                    inf_tier = int(inf_tier) if inf_tier != "" else 0
                    color = input("World's color: ")
                    color = pygame.Color(color if color != "" else basics.options.setdefault("default_new_world", {"color": "#000000"}).get("color", "#000000"))
                    current_level.world_list.append(worlds.world(name, size, inf_tier, color))
                    current_world_index = len(current_level.world_list) - 1
                    world_changed = True
        elif keys[keybinds["O"]] and cooldowns[keybinds["O"]] == 0:
            if keys[keybinds["LSHIFT"]] or keys[keybinds["RSHIFT"]]:
                if input("Are you sure you want to delete this level? [y/N]: ") in yes:
                    levelpack.level_list.pop(current_level_index)
                    current_level_index -= 1
                    current_world_index = 0
                    level_changed = True
                    world_changed = True
            else:
                if input("Are you sure you want to delete this world? [y/N]: ") in yes:
                    current_level.world_list.pop(current_world_index)
                    current_world_index -= 1
                    world_changed = True
        elif keys[keybinds["R"]] and cooldowns[keybinds["R"]] == 0:
            text_rule = input("Levelpack's Global Rule: ").upper().split()
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
            print("Levelpack's Global Rule List:")
            for rule in levelpack.rule_list:
                str_list = []
                for obj_type in rule:
                    str_list.append(obj_type.class_name)
                print(" ".join(str_list))
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
                cooldowns[key] = basics.options.setdefault("input_cooldown", 5)
        if level_changed:
            current_cursor_pos = (0, 0)
            current_level_index = current_level_index % len(levelpack.level_list) if current_level_index >= 0 else len(levelpack.level_list) - 1
            current_level = levelpack.level_list[current_level_index]
            print("Current Level:", current_level.name)
            level_changed = False
        if world_changed:
            current_cursor_pos = (0, 0)
            current_world_index = current_world_index % len(current_level.world_list) if current_world_index >= 0 else len(current_level.world_list) - 1
            current_world = current_level.world_list[current_world_index]
            print("Current World:", current_world.name)
            world_changed = False
        current_object_index = current_object_index % len(object_list) if current_object_index >= 0 else len(object_list) - 1
        current_object_type = object_list[current_object_index]
        for world in current_level.world_list:
            world.set_sprite_states(0)
        window.fill("#000000")
        window.blit(pygame.transform.scale(current_level.show_world(current_world, wiggle, cursor=current_cursor_pos), (720, 720)), (0, 0))
        current_object = displays.set_sprite_state(current_object_type((0, 0), current_facing))
        window.blit(pygame.transform.scale(displays.sprites.get(current_object_type.sprite_name, current_object.sprite_state, wiggle), (72, 72)), (1208, 0))
        pygame.display.flip()
        for key in cooldowns:
            if cooldowns[key] > 0:
                cooldowns[key] -= 1
        clock.tick(basics.options.setdefault("fps", 30))
    return levelpack