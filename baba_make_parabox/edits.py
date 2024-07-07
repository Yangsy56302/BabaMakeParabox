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
                "-": pygame.K_MINUS,
                "+": pygame.K_EQUALS,
                "\n": pygame.K_RETURN,
                "\b": pygame.K_BACKSPACE,
                "\t": pygame.K_TAB}
    keys = {v: False for k, v in keybinds.items()}
    cooldowns = {value: 0 for value in keybinds.values()}
    default_cooldown = 3
    window.fill("#000000")
    current_level_index = 0
    current_level = world.level_list[current_level_index]
    object_list = list(objects.object_name.values())
    current_object_index = 0
    current_object_type = object_list[current_object_index]
    current_facing = "W"
    current_cursor_pos = (0, 0)
    current_clipboard = []
    window.fill("#000000")
    window.blit(pygame.transform.scale(world.show_level(current_level, 2, current_cursor_pos), (720, 720)), (0, 0))
    window.blit(pygame.transform.scale(basics.game_data.sprites[current_object_type.sprite_name], (72, 72)), (1208, 0))
    pygame.display.flip()
    editor_running = True
    while editor_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editor_running = False
            if event.type == pygame.KEYDOWN:
                keys[event.key] = True
                if event.mod & pygame.KMOD_LSHIFT:
                    keys[keybinds["LSHIFT"]] = True
                elif event.mod & pygame.KMOD_RSHIFT:
                    keys[keybinds["RSHIFT"]] = True
            elif event.type == pygame.KEYUP:
                keys[event.key] = False
                if event.mod & pygame.KMOD_LSHIFT:
                    keys[keybinds["LSHIFT"]] = False
                elif event.mod & pygame.KMOD_RSHIFT:
                    keys[keybinds["RSHIFT"]] = False
        refresh = False
        if keys[keybinds["W"]] and cooldowns[keybinds["W"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, "W")
            if not current_level.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
            cooldowns[keybinds["W"]] = default_cooldown
            refresh = True
        elif keys[keybinds["S"]] and cooldowns[keybinds["S"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, "S")
            if not current_level.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
            cooldowns[keybinds["S"]] = default_cooldown
            refresh = True
        elif keys[keybinds["A"]] and cooldowns[keybinds["A"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, "A")
            if not current_level.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
            cooldowns[keybinds["A"]] = default_cooldown
            refresh = True
        elif keys[keybinds["D"]] and cooldowns[keybinds["D"]] == 0:
            new_cursor_pos = spaces.pos_facing(current_cursor_pos, "D")
            if not current_level.out_of_range(new_cursor_pos):
                current_cursor_pos = new_cursor_pos
            cooldowns[keybinds["D"]] = default_cooldown
            refresh = True
        elif keys[keybinds["I"]] and cooldowns[keybinds["I"]] == 0:
            current_facing = "W"
            cooldowns[keybinds["I"]] = default_cooldown
            refresh = True
        elif keys[keybinds["K"]] and cooldowns[keybinds["K"]] == 0:
            current_facing = "S"
            cooldowns[keybinds["K"]] = default_cooldown
            refresh = True
        elif keys[keybinds["J"]] and cooldowns[keybinds["J"]] == 0:
            current_facing = "A"
            cooldowns[keybinds["J"]] = default_cooldown
            refresh = True
        elif keys[keybinds["L"]] and cooldowns[keybinds["L"]] == 0:
            current_facing = "D"
            cooldowns[keybinds["L"]] = default_cooldown
            refresh = True
        elif keys[keybinds["Q"]] and cooldowns[keybinds["Q"]] == 0:
            current_object_index -= 1
            cooldowns[keybinds["Q"]] = default_cooldown
            refresh = True
        elif keys[keybinds["E"]] and cooldowns[keybinds["E"]] == 0:
            current_object_index += 1
            cooldowns[keybinds["E"]] = default_cooldown
            refresh = True
        elif keys[keybinds["\n"]] and cooldowns[keybinds["\n"]] == 0:
            history.append(copy.deepcopy(world))
            if current_object_type == objects.Level:
                current_level.new_obj(objects.Level(current_cursor_pos, current_level.name, current_level.inf_tier, current_facing))
            elif current_object_type == objects.Clone:
                current_level.new_obj(objects.Clone(current_cursor_pos, current_level.name, current_level.inf_tier, current_facing))
            else:
                current_level.new_obj(current_object_type(current_cursor_pos, current_facing))
            cooldowns[keybinds["\n"]] = default_cooldown
            refresh = True
        elif keys[keybinds["P"]] and cooldowns[keybinds["P"]] == 0:
            if input("Are you sure you want to create a new level? [y/N]: ") in ["y", "Y", "yes", "Yes", "YES"]:
                history.append(copy.deepcopy(world))
                world.level_list.append(levels.level(input("Level's Name: "),
                                                    (int(input("Level's width: ")), int(input("Level's height: "))),
                                                    int(input("Level's infinite tier: ")),
                                                    pygame.Color(input("Level's color: "))))
            current_level_index = len(world.level_list) - 1
            cooldowns[keybinds["P"]] = default_cooldown
            refresh = True
        elif keys[keybinds["O"]] and cooldowns[keybinds["O"]] == 0:
            if input("Are you sure you want to delete this level? [y/N]: ") in ["y", "Y", "yes", "Yes", "YES"]:
                world.level_list.pop(current_level_index)
                current_level_index -= 1
            cooldowns[keybinds["O"]] = default_cooldown
            refresh = True
        elif keys[keybinds["\b"]] and cooldowns[keybinds["\b"]] == 0:
            history.append(copy.deepcopy(world))
            current_level.del_objs_from_pos(current_cursor_pos)
            cooldowns[keybinds["\b"]] = default_cooldown
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
            cooldowns[keybinds["\t"]] = default_cooldown
            refresh = True
        elif keys[keybinds["Z"]] and cooldowns[keybinds["Z"]] == 0:
            if len(history) > 1:
                world = copy.deepcopy(history.pop())
            else:
                world = copy.deepcopy(history[0])
            cooldowns[keybinds["Z"]] = default_cooldown
            refresh = True
        elif keys[keybinds["X"]] and cooldowns[keybinds["X"]] == 0:
            history.append(copy.deepcopy(world))
            current_clipboard = current_level.get_objs_from_pos(current_cursor_pos)
            current_level.del_objs_from_pos(current_cursor_pos)
            cooldowns[keybinds["X"]] = default_cooldown
            refresh = True
        elif keys[keybinds["C"]] and cooldowns[keybinds["C"]] == 0:
            history.append(copy.deepcopy(world))
            current_clipboard = current_level.get_objs_from_pos(current_cursor_pos)
            cooldowns[keybinds["C"]] = default_cooldown
            refresh = True
        elif keys[keybinds["V"]] and cooldowns[keybinds["V"]] == 0:
            history.append(copy.deepcopy(world))
            for obj in current_clipboard:
                new_obj = copy.deepcopy(obj)
                new_obj.x, new_obj.y = current_cursor_pos
                current_level.new_obj(new_obj)
            cooldowns[keybinds["V"]] = default_cooldown
            refresh = True
        elif keys[keybinds["-"]] and cooldowns[keybinds["-"]] == 0:
            current_level_index -= 1
            current_cursor_pos = (0, 0)
            cooldowns[keybinds["-"]] = default_cooldown
            refresh = True
        elif keys[keybinds["+"]] and cooldowns[keybinds["+"]] == 0:
            current_level_index += 1
            current_cursor_pos = (0, 0)
            cooldowns[keybinds["+"]] = default_cooldown
            refresh = True
        current_level_index = current_level_index % len(world.level_list) if current_level_index >= 0 else len(world.level_list) - 1
        current_level = world.level_list[current_level_index]
        current_object_index = current_object_index % len(object_list) if current_object_index >= 0 else len(object_list) - 1
        current_object_type = object_list[current_object_index]
        if refresh:
            window.fill("#000000")
            window.blit(pygame.transform.scale(world.show_level(current_level, 2, current_cursor_pos), (720, 720)), (0, 0))
            window.blit(pygame.transform.scale(basics.game_data.sprites[current_object_type.sprite_name], (72, 72)), (1208, 0))
            pygame.display.flip()
        for key in cooldowns:
            if cooldowns[key] > 0:
                cooldowns[key] -= 1
        if len(history) > 100:
            history = history[1:]
        clock.tick(15)
    return world