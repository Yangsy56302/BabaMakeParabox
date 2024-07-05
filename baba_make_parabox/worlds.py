from typing import Any, Optional
import pygame

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.levels as levels
import baba_make_parabox.displays as displays

class world(object):
    class_name: str = "World"
    name: str
    level_list: list[levels.level]
    rule_list: list[rules.Rule]
    def __init__(self, *level_list: levels.level, rule_list: Optional[list[rules.Rule]] = None, **kwds: Any) -> None:
        self.level_list = list(level_list)
        self.rule_list = rule_list if rule_list is not None else []
    def __str__(self) -> str:
        return self.class_name
    def __repr__(self) -> str:
        return self.class_name
    def find_rules(self, *match_rule: Optional[type[objects.Text]]) -> list[rules.Rule]:
        found_rules = []
        for rule in self.rule_list:
            if len(rule) != len(match_rule):
                continue
            not_match = False
            for i in range(len(rule)):
                if rule[i] != match_rule[i] and match_rule[i] is not None:
                    not_match = True
                    break
            if not_match:
                continue
            found_rules.append(rule)
        return found_rules
    def get_level(self, name: str, inf_tier: int) -> levels.level:
        return list(filter(lambda l: l.name == name and l.inf_tier == inf_tier, self.level_list))[0]
    def find_super_level(self, name: str, inf_tier: int) -> Optional[tuple[levels.level, objects.Object]]:
        for super_level in self.level_list:
            for obj in super_level.get_levels():
                if name == obj.name and inf_tier == obj.inf_tier:
                    return (super_level, obj)
        return None
    def get_move_list(self, level: levels.level, obj: objects.Object, pos: spaces.Coord, facing: spaces.Direction, passed: Optional[list[levels.level]] = None) -> list[tuple[objects.Object, levels.level, spaces.Coord]]:
        passed = passed[:] if passed is not None else []
        move_list = []
        new_pos = spaces.pos_facing(pos, facing)
        # push out
        if level.out_of_range(new_pos):
            # inf out
            if level in passed:
                ret = self.find_super_level(level.name, level.inf_tier + 1)
                if ret is None:
                    return []
                super_level, level_obj = ret
                move_list.extend(self.get_move_list(super_level, obj, (level_obj.x, level_obj.y), facing, passed))
            else:
                ret = self.find_super_level(level.name, level.inf_tier)
                if ret is None:
                    return []
                super_level, level_obj = ret
                passed.append(level)
                move_list.extend(self.get_move_list(super_level, obj, (level_obj.x, level_obj.y), facing, passed))
            move_list = basics.remove_same_elements(move_list)
            return move_list
        level_objects = level.get_levels_from_pos(new_pos)
        clone_objects = level.get_clones_from_pos(new_pos)
        level_like_objects = level_objects + clone_objects
        # level
        if len(level_like_objects) != 0:
            push_level = True
            for level_like_object in level_like_objects:
                if len(self.get_move_list(level, level_like_object, new_pos, facing, passed)) == 0:
                    push_level = False
                if len(level.find_rules(rules.nouns_objs_dicts.get_noun(type(level_like_object)), objects.IS, objects.PUSH)) == 0:
                    if len(self.find_rules(rules.nouns_objs_dicts.get_noun(type(level_like_object)), objects.IS, objects.PUSH)) == 0:
                        push_level = False
            # level push
            if push_level:
                for level_like_object in level_like_objects:
                    move_list.extend(self.get_move_list(level, level_like_object, new_pos, facing, passed))
                move_list.append((obj, level, new_pos))
            else:
                for level_like_object in level_like_objects:
                    sub_level = self.get_level(level_like_object.name, level_like_object.inf_tier)
                    # inf in
                    if sub_level in passed:
                        sub_sub_level = self.get_level(sub_level.name, sub_level.inf_tier - 1)
                        input_pos = sub_sub_level.default_input_position(spaces.swap_direction(facing))
                        passed.append(level)
                        new_move_list = self.get_move_list(sub_sub_level, obj, input_pos, facing, passed)
                    # push in
                    else:
                        input_pos = sub_level.default_input_position(spaces.swap_direction(facing))
                        passed.append(level)
                        new_move_list = self.get_move_list(sub_level, obj, input_pos, facing, passed)
                    if len(new_move_list) == 0:
                        return []
                    move_list.extend(new_move_list)
            move_list = basics.remove_same_elements(move_list)
            return move_list
        # box push
        push_rules = level.find_rules(None, objects.IS, objects.PUSH) + self.find_rules(None, objects.IS, objects.PUSH)
        if len(push_rules) != 0:
            push_objects = []
            for push_type in [t[0] for t in push_rules]:
                push_objects.extend(level.get_objs_from_pos_and_type(new_pos, rules.nouns_objs_dicts.get_obj(push_type)))
            if len(push_objects) != 0:
                for push_object in push_objects:
                    new_move_list = self.get_move_list(level, push_object, (push_object.x, push_object.y), facing)
                    if len(new_move_list) == 0:
                        return []
                    move_list.extend(new_move_list)
                move_list.append((obj, level, new_pos))
                move_list = basics.remove_same_elements(move_list)
                return move_list
        # wall stop
        stop_rules = level.find_rules(None, objects.IS, objects.STOP) + self.find_rules(None, objects.IS, objects.STOP)
        if len(stop_rules) != 0:
            stop_objects = []
            for stop_type in [t[0] for t in stop_rules]:
                stop_objects.extend(level.get_objs_from_pos_and_type(new_pos, rules.nouns_objs_dicts.get_obj(stop_type)))
            if len(stop_objects) != 0:
                return []
        return [(obj, level, new_pos)]
    def move(self, move_list: list[tuple[objects.Object, levels.level, spaces.Coord]]) -> None:
        move_list = basics.remove_same_elements(move_list)
        for move_obj, new_level, new_pos in move_list:
            for level in self.level_list:
                if level.get_obj(move_obj.uuid) is not None:
                    old_level = level
            if old_level == new_level:
                move_obj.x, move_obj.y = new_pos
            else:
                old_level.del_obj(move_obj.uuid)
                move_obj.x, move_obj.y = new_pos
                new_level.new_obj(move_obj)
    def you(self, facing: spaces.Direction) -> None:
        move_list = []
        for level in self.level_list:
            you_rules = level.find_rules(None, objects.IS, objects.YOU) + self.find_rules(None, objects.IS, objects.YOU)
            for you_type in [t[0] for t in you_rules]:
                for you_obj in level.get_objs_from_type(rules.nouns_objs_dicts.get_obj(you_type)):
                    move_list.extend(self.get_move_list(level, you_obj, (you_obj.x, you_obj.y), facing))
        self.move(move_list)
    def round(self, op: spaces.PlayerOperation) -> None:
        for level in self.level_list:
            level.update_rules()
        if op != "_":
            self.you(op)
    def show_level(self, level: levels.level, layer: int) -> pygame.Surface:
        if layer <= 0:
            return basics.game_data.sprites["text_level"].copy()
        level_surface_size = (level.width * displays.sprite_size, level.height * displays.sprite_size)
        level_surface = pygame.Surface(level_surface_size, pygame.SRCALPHA)
        for i in range(len(level.objects)):
            obj = level.objects[i]
            if isinstance(obj, objects.Level):
                obj_level = self.get_level(obj.name, obj.inf_tier)
                obj_surface = self.show_level(obj_level, layer - 1)
                obj_surface = displays.set_color_dark(obj_surface, pygame.Color("#CCCCCC"))
                obj_background = pygame.Surface(obj_surface.get_size(), pygame.SRCALPHA)
                obj_background.fill("#00000044")
                obj_background = displays.set_color_dark(obj_background, pygame.Color("#CCCCCC"))
                obj_background.blit(obj_surface, (0, 0))
                obj_surface = obj_background
            elif isinstance(obj, objects.Clone):
                obj_level = self.get_level(obj.name, obj.inf_tier)
                obj_surface = self.show_level(obj_level, layer - 1)
                obj_surface = displays.set_color_light(obj_surface, pygame.Color("#444444"))
                obj_background = pygame.Surface(obj_surface.get_size(), pygame.SRCALPHA)
                obj_background.fill("#FFFFFF44")
                obj_background = displays.set_color_light(obj_background, pygame.Color("#444444"))
                obj_background.blit(obj_surface, (0, 0))
                obj_surface = obj_background
            else:
                obj_surface = basics.game_data.sprites[obj.sprite_name].copy()
            pos = (obj.x * displays.sprite_size, obj.y * displays.sprite_size)
            level_surface.blit(pygame.transform.scale(obj_surface, (displays.sprite_size, displays.sprite_size)), pos)
        return level_surface