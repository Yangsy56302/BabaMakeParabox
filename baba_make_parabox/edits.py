import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.levels as levels
import baba_make_parabox.displays as displays
import baba_make_parabox.worlds as worlds

import copy
import pygame

def level_editor(world: worlds.world) -> worlds.world:
    history = [copy.deepcopy(world)]
    window = pygame.display.set_mode((1280, 720))
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
                "R": pygame.K_r,
                "-": pygame.K_MINUS,
                "=": pygame.K_EQUALS,
                "\n": pygame.K_RETURN,
                "\b": pygame.K_BACKSPACE,
                "\t": pygame.K_TAB}
    keys = {v: False for v in keybinds.values()}
    cooldowns = {v: 0 for v in keybinds.values()}
    window.fill("#000000")
    current_level_index = 0
    current_level = world.level_list[current_level_index]
    object_list = list(objects.object_name.values())
    current_object_index = 0
    current_object_type = object_list[current_object_index]
    current_facing = "W"
    current_cursor_pos = (0, 0)
    current_clipboard = []
    yes = ["y", "Y", "yes", "Yes", "YES"]
    window.fill("#000000")
    window.blit(pygame.transform.scale(world.show_level(current_level, basics.options["level_display_recursion_depth"], current_cursor_pos), (720, 720)), (0, 0))
    window.blit(pygame.transform.scale(basics.game_data.sprites[current_object_type.sprite_name], (72, 72)), (1208, 0))
    pygame.display.flip()
    editor_running = True
    while editor_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editor_running = False
            if event.type == pygame.KEYDOWN and event.key in keybinds.values():
                keys[event.key] = True
            elif event.type == pygame.KEYUP and event.key in keybinds.values():
                keys[event.key] = False
        refresh = False
        if keys[keybinds["W"]] and cooldowns[keybinds["W"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, "W")
            if not current_level.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
            refresh = True
        elif keys[keybinds["S"]] and cooldowns[keybinds["S"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, "S")
            if not current_level.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
            refresh = True
        elif keys[keybinds["A"]] and cooldowns[keybinds["A"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, "A")
            if not current_level.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
            refresh = True
        elif keys[keybinds["D"]] and cooldowns[keybinds["D"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, "D")
            if not current_level.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
            refresh = True
        elif keys[keybinds["I"]] and cooldowns[keybinds["I"]] == 0:
            current_facing = "W"
        elif keys[keybinds["K"]] and cooldowns[keybinds["K"]] == 0:
            current_facing = "S"
        elif keys[keybinds["J"]] and cooldowns[keybinds["J"]] == 0:
            current_facing = "A"
        elif keys[keybinds["L"]] and cooldowns[keybinds["L"]] == 0:
            current_facing = "D"
        elif keys[keybinds["Q"]] and cooldowns[keybinds["Q"]] == 0:
            current_object_index -= 1
            refresh = True
        elif keys[keybinds["E"]] and cooldowns[keybinds["E"]] == 0:
            current_object_index += 1
            refresh = True
        elif keys[keybinds["\n"]] and cooldowns[keybinds["\n"]] == 0:
            history.append(copy.deepcopy(world))
            if current_object_type == objects.Level:
                current_level.new_obj(objects.Level(current_cursor_pos, current_level.name, current_level.inf_tier, current_facing))
            elif current_object_type == objects.Clone:
                current_level.new_obj(objects.Clone(current_cursor_pos, current_level.name, current_level.inf_tier, current_facing))
            else:
                current_level.new_obj(current_object_type(current_cursor_pos, current_facing))
            refresh = True
        elif keys[keybinds["P"]] and cooldowns[keybinds["P"]] == 0:
            if input("Are you sure you want to create a new level? [y/N]: ") in yes:
                history.append(copy.deepcopy(world))
                name = input("Level's Name: ")
                size = (int(input("Level's width: ")), int(input("Level's height: ")))
                inf_tier = input("Level's infinite tier: ")
                inf_tier = int(inf_tier if inf_tier != "" else 0)
                color = input("Level's color: ")
                color = pygame.Color(color if color != "" else displays.random_level_color())
                world.level_list.append(levels.level(name, size, inf_tier, color))
                current_level_index = len(world.level_list) - 1
                refresh = True
        elif keys[keybinds["O"]] and cooldowns[keybinds["O"]] == 0:
            if input("Are you sure you want to delete this level? [y/N]: ") in yes:
                world.level_list.pop(current_level_index)
                current_level_index -= 1
                refresh = True
        elif keys[keybinds["R"]] and cooldowns[keybinds["R"]] == 0:
            text_rule = input("New Global Rule: ").upper().split()
            type_rule: list[type[objects.Object]] = []
            valid_input = True
            for text in text_rule:
                obj_type = objects.object_name.get(text)
                if obj_type is not None:
                    type_rule.append(obj_type)
                else:
                    valid_input = False
                    break
            if valid_input:
                world.rule_list.append(tuple(type_rule))
        elif keys[keybinds["\b"]] and cooldowns[keybinds["\b"]] == 0:
            history.append(copy.deepcopy(world))
            current_level.del_objs_from_pos(current_cursor_pos)
            refresh = True
        elif keys[keybinds["\t"]] and cooldowns[keybinds["\t"]] == 0:
            obj_to_noun = rules.nouns_objs_dicts.get_noun(current_object_type) # type: ignore
            noun_to_obj = rules.nouns_objs_dicts.get_obj(current_object_type) # type: ignore
            new_object_type = obj_to_noun if obj_to_noun is not None else (noun_to_obj if noun_to_obj is not None else None)
            try:
                new_object_index = object_list.index(new_object_type) # type: ignore
                current_object_index = new_object_index
            except ValueError:
                pass
            refresh = True
        elif keys[keybinds["Z"]] and cooldowns[keybinds["Z"]] == 0:
            if len(history) > 1:
                world = copy.deepcopy(history.pop())
            else:
                world = copy.deepcopy(history[0])
            refresh = True
        elif keys[keybinds["X"]] and cooldowns[keybinds["X"]] == 0:
            history.append(copy.deepcopy(world))
            current_clipboard = current_level.get_objs_from_pos(current_cursor_pos)
            current_level.del_objs_from_pos(current_cursor_pos)
            refresh = True
        elif keys[keybinds["C"]] and cooldowns[keybinds["C"]] == 0:
            history.append(copy.deepcopy(world))
            current_clipboard = current_level.get_objs_from_pos(current_cursor_pos)
        elif keys[keybinds["V"]] and cooldowns[keybinds["V"]] == 0:
            history.append(copy.deepcopy(world))
            for obj in current_clipboard:
                new_obj = copy.deepcopy(obj)
                new_obj.x, new_obj.y = current_cursor_pos
                current_level.new_obj(new_obj)
            refresh = True
        elif keys[keybinds["-"]] and cooldowns[keybinds["-"]] == 0:
            current_level_index -= 1
            current_cursor_pos = (0, 0)
            refresh = True
        elif keys[keybinds["="]] and cooldowns[keybinds["="]] == 0:
            current_level_index += 1
            current_cursor_pos = (0, 0)
            refresh = True
        for key, value in keys.items():
            if value and cooldowns[key] == 0:
                cooldowns[key] = basics.options["input_cooldown"]
        current_level_index = current_level_index % len(world.level_list) if current_level_index >= 0 else len(world.level_list) - 1
        current_level = world.level_list[current_level_index]
        current_object_index = current_object_index % len(object_list) if current_object_index >= 0 else len(object_list) - 1
        current_object_type = object_list[current_object_index]
        if refresh:
            window.fill("#000000")
            window.blit(pygame.transform.scale(world.show_level(current_level, basics.options["level_display_recursion_depth"], current_cursor_pos), (720, 720)), (0, 0))
            window.blit(pygame.transform.scale(basics.game_data.sprites[current_object_type.sprite_name], (72, 72)), (1208, 0))
            pygame.display.flip()
        for key in cooldowns:
            if cooldowns[key] > 0:
                cooldowns[key] -= 1
        if len(history) > 100:
            history = history[1:]
        clock.tick(basics.options["fps"])
    return world