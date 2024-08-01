from typing import Any, Optional, TypedDict
import random
import copy
import uuid

from BabaMakeParabox import basics, colors, spaces, objects, rules, worlds, displays

import pygame

class ReTurnValue(TypedDict):
    win: bool
    end: bool
    game_push: bool
    selected_level: Optional[str]
    transform_to: Optional[list[objects.BmpObject]]

class Level(object):
    def __init__(self, name: str, world_list: list[worlds.World], super_level: Optional[str] = None, main_world_name: Optional[str] = None, main_world_tier: Optional[int] = None, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name
        self.world_list: list[worlds.World] = list(world_list)
        self.super_level: Optional[str] = super_level
        self.main_world_name: str = main_world_name if main_world_name is not None else world_list[0].name
        self.main_world_tier: int = main_world_tier if main_world_tier is not None else world_list[0].inf_tier
        self.rule_list: list[rules.Rule] = rule_list if rule_list is not None else rules.default_rule_list
        self.game_properties: list[tuple[type[objects.BmpObject], int]] = []
        self.new_games: list[type[objects.BmpObject]] = []
        self.properties: list[tuple[type[objects.BmpObject], int]] = []
        self.write_text: list[type[objects.Noun] | type[objects.Property]] = []
        self.created_levels: list["Level"] = []
        self.all_list: list[type[objects.Noun]] = []
        self.sound_events: list[str] = []
    def __eq__(self, level: "Level") -> bool:
        return self.name == level.name
    def new_prop(self, prop: type[objects.Text], negated_count: int = 0) -> None:
        del_props = []
        for old_prop, old_negated_count in self.properties:
            if prop == old_prop:
                if old_negated_count > negated_count:
                    return
                del_props.append((old_prop, old_negated_count))
        for old_prop, old_negated_count in del_props:
            self.properties.remove((old_prop, old_negated_count))
        self.properties.append((prop, negated_count))
    def del_prop(self, prop: type[objects.Text], negated_count: int = 0) -> None:
        if (prop, negated_count) in self.properties:
            self.properties.remove((prop, negated_count))
    def has_prop(self, prop: type[objects.Text], negate: bool = False) -> bool:
        for get_prop, get_negated_count in self.properties:
            if get_prop == prop and get_negated_count % 2 == int(negate):
                return True
        return False
    def find_rules(self, *match_rule: Optional[type[objects.Text]]) -> list[rules.Rule]:
        found_rules = []
        for rule in self.rule_list:
            if len(rule) != len(match_rule):
                continue
            not_match = False
            for i in range(len(rule)):
                text_type = match_rule[i]
                if text_type is not None:
                    if not issubclass(rule[i], text_type):
                        not_match = True
                        break
            if not_match:
                continue
            found_rules.append(rule)
        return found_rules
    def get_world(self, name: str, inf_tier: int) -> Optional[worlds.World]:
        world = list(filter(lambda l: l.name == name and l.inf_tier == inf_tier, self.world_list))
        return world[0] if len(world) != 0 else None
    def get_exist_world(self, name: str, inf_tier: int) -> worlds.World:
        world = list(filter(lambda l: l.name == name and l.inf_tier == inf_tier, self.world_list))
        return world[0]
    def set_world(self, world: worlds.World) -> None:
        for i in range(len(self.world_list)):
            if world.name == self.world_list[i].name:
                self.world_list[i] = world
                return
        self.world_list.append(world)
    def find_super_world(self, name: str, inf_tier: int) -> Optional[tuple[worlds.World, objects.BmpObject]]:
        for super_world in self.world_list:
            for obj in super_world.get_worlds():
                if name == obj.name and inf_tier == obj.inf_tier:
                    return (super_world, obj)
        return None
    def all_list_set(self) -> None:
        for world in self.world_list:
            for obj in world.object_list:
                noun_type = objects.nouns_objs_dicts.swapped().get(type(obj))
                in_not_in_all = False
                for not_all in objects.not_in_all:
                    if isinstance(obj, not_all):
                        in_not_in_all = True
                if noun_type is not None and noun_type not in self.all_list and not in_not_in_all:
                    self.all_list.append(noun_type)
    def meet_prefix_conditions(self, world: worlds.World, obj: objects.BmpObject, prefix_info_list: list[rules.PrefixInfo], is_meta: bool = False) -> bool:
        return_value = True
        for prefix_info in prefix_info_list:
            meet_prefix_condition = True
            if prefix_info[1] == objects.META:
                meet_prefix_condition = is_meta
            return_value = return_value and (meet_prefix_condition if not prefix_info[0] else not meet_prefix_condition)
        return return_value
    def meet_infix_conditions(self, world: worlds.World, obj: objects.BmpObject, infix_info_list: list[rules.InfixInfo], old_feeling: Optional[list[tuple[type[objects.Text], int]]] = None) -> bool:
        return_value = True
        for infix_info in infix_info_list:
            meet_infix_condition = True
            if infix_info[1] == objects.ON:
                find_range = [(obj.x, obj.y)]
            elif infix_info[1] == objects.NEAR:
                find_range = [(obj.x - 1, obj.y - 1), (obj.x, obj.y - 1), (obj.x + 1, obj.y - 1),
                              (obj.x - 1, obj.y), (obj.x, obj.y), (obj.x + 1, obj.y),
                              (obj.x - 1, obj.y + 1), (obj.x, obj.y + 1), (obj.x + 1, obj.y + 1)]
            elif infix_info[1] == objects.NEXTTO:
                find_range = [(obj.x, obj.y - 1), (obj.x - 1, obj.y), (obj.x + 1, obj.y), (obj.x, obj.y + 1)]
            if infix_info[1] in (objects.ON, objects.NEAR, objects.NEXTTO):
                match_type = objects.nouns_objs_dicts.get(infix_info[3]) # type: ignore
                if match_type is not None:
                    if match_type == objects.All:
                        if infix_info[2]:
                            for new_match_type in [o for o in self.all_list if issubclass(o, objects.in_not_all)]:
                                match_objs = []
                                for pos in find_range:
                                    match_objs.extend(world.get_objs_from_pos_and_type(pos, new_match_type))
                                if obj in match_objs:
                                    match_objs.remove(obj)
                                if len(match_objs) == 0:
                                    meet_infix_condition = False
                        else:
                            for new_match_type in [o for o in self.all_list if not issubclass(o, objects.not_in_all)]:
                                match_objs = []
                                for pos in find_range:
                                    match_objs.extend(world.get_objs_from_pos_and_type(pos, new_match_type))
                                if obj in match_objs:
                                    match_objs.remove(obj)
                                if len(match_objs) == 0:
                                    meet_infix_condition = False
                    else:
                        if infix_info[2]:
                            for new_match_type in [o for o in self.all_list if (not issubclass(o, objects.not_in_all)) and not issubclass(o, match_type)]:
                                match_objs = []
                                for pos in find_range:
                                    match_objs.extend(world.get_objs_from_pos_and_type(pos, new_match_type))
                                if obj in match_objs:
                                    match_objs.remove(obj)
                                if len(match_objs) == 0:
                                    meet_infix_condition = False
                        else:
                            match_objs = []
                            for pos in find_range:
                                match_objs.extend(world.get_objs_from_pos_and_type(pos, match_type))
                            if obj in match_objs:
                                match_objs.remove(obj)
                            if len(match_objs) == 0:
                                meet_infix_condition = False
            elif infix_info[1] == objects.FEELING:
                if old_feeling is None:
                    meet_infix_condition = False
                else:
                    match_prop: type[objects.Property] = infix_info[3] # type: ignore
                    if infix_info[2]:
                        if match_prop not in [t[0] for t in old_feeling if t[1] % 2 == 1]:
                            meet_infix_condition = False
                    else:
                        if match_prop not in [t[0] for t in old_feeling if t[1] % 2 == 0]:
                            meet_infix_condition = False
            return_value = return_value and (meet_infix_condition if not infix_info[0] else not meet_infix_condition)
        return return_value
    def recursion_rules(self, world: worlds.World, rule_list: Optional[list[rules.Rule]] = None, passed: Optional[list[worlds.World]] = None) -> None:
        passed = passed if passed is not None else []
        if world in passed:
            return
        passed.append(world)
        rule_list = rule_list if rule_list is not None else []
        world.rule_list.extend(rule_list)
        rule_list = world.rule_list
        sub_world_objs = world.get_worlds()
        if len(sub_world_objs) == 0:
            return
        for sub_world_obj in sub_world_objs:
            sub_world = self.get_exist_world(sub_world_obj.name, sub_world_obj.inf_tier)
            self.recursion_rules(sub_world, rule_list, passed)
    def update_rules(self, old_prop_dict: dict[uuid.UUID, list[tuple[type[objects.Text], int]]]) -> None:
        self.game_properties = []
        self.properties = []
        self.write_text = []
        for world in self.world_list:
            world.world_properties = []
            for obj in world.object_list:
                obj.clear_prop()
                obj.has_object = []
                obj.make_object = []
                obj.write_text = []
        for world in self.world_list:
            self.recursion_rules(world)
        for world in self.world_list:
            world.rule_list = rules.to_atom_rules(world.get_rules())
            world.rule_list.extend(rules.to_atom_rules(self.rule_list))
            world.rule_list = basics.remove_same_elements(world.rule_list)
        new_prop_list: list[tuple[objects.BmpObject, tuple[type[objects.Text], int]]] = []
        for world in self.world_list:
            for rule in world.rule_list:
                for prefix_list, noun_negated, noun_type, infix_list, oper_type, prop_negated_count, prop_type in rules.analysis_rule(rule):
                    if oper_type != objects.IS:
                        continue
                    if prop_type != objects.WORD:
                        continue
                    obj_type = objects.nouns_objs_dicts.get(noun_type)
                    if obj_type is not None:
                        if obj_type == objects.All:
                            if noun_negated:
                                for obj in [o for o in world.object_list if isinstance(o, objects.in_not_all)]:
                                    if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                        new_prop_list.append((obj, (objects.WORD, prop_negated_count)))
                            else:
                                for obj in [o for o in world.object_list if not isinstance(o, objects.not_in_all)]:
                                    if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                        new_prop_list.append((obj, (objects.WORD, prop_negated_count)))
                        else:
                            if noun_negated:
                                for obj in [o for o in world.object_list if (not isinstance(o, objects.not_in_all)) and not isinstance(o, obj_type)]:
                                    if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                        new_prop_list.append((obj, (objects.WORD, prop_negated_count)))
                            else:
                                for obj in world.get_objs_from_type(obj_type):
                                    if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                        new_prop_list.append((obj, (objects.WORD, prop_negated_count)))
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.new_prop(prop_type, prop_negated_count)
        for world in self.world_list:
            world.world_properties = []
            world.rule_list = rules.to_atom_rules(world.get_rules())
            for obj in world.object_list:
                obj.clear_prop()
                obj.has_object = []
                obj.make_object = []
                obj.write_text = []
        for world in self.world_list:
            self.recursion_rules(world)
        for world in self.world_list:
            world.rule_list.extend(rules.to_atom_rules(self.rule_list))
            world.rule_list = basics.remove_same_elements(world.rule_list)
        new_prop_list = []
        for world in self.world_list:
            for rule in world.rule_list:
                for prefix_list, noun_negated, noun_type, infix_list, oper_type, prop_negated_count, prop_type in rules.analysis_rule(rule):
                    obj_type = objects.nouns_objs_dicts.get(noun_type)
                    if obj_type is not None:
                        if obj_type == objects.All:
                            if noun_negated:
                                for obj in [o for o in world.object_list if isinstance(o, objects.in_not_all)]:
                                    if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                        if oper_type == objects.IS:
                                            new_prop_list.append((obj, (prop_type, prop_negated_count)))
                                        elif oper_type == objects.HAS:
                                            if prop_type == objects.ALL and noun_negated == False:
                                                obj.has_object.extend(self.all_list)
                                            else:
                                                obj.has_object.append(prop_type) # type: ignore
                                        elif oper_type == objects.MAKE:
                                            if prop_type == objects.ALL and noun_negated == False:
                                                obj.make_object.extend(self.all_list)
                                            else:
                                                obj.make_object.append(prop_type) # type: ignore
                                        elif oper_type == objects.WRITE:
                                            obj.write_text.append(prop_type)
                            else:
                                for obj in [o for o in world.object_list if not isinstance(o, objects.not_in_all)]:
                                    if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                        if oper_type == objects.IS:
                                            new_prop_list.append((obj, (prop_type, prop_negated_count)))
                                        elif oper_type == objects.HAS and prop_negated_count % 2 == 0:
                                            if prop_type == objects.ALL and noun_negated == False:
                                                obj.has_object.extend(self.all_list)
                                            else:
                                                obj.has_object.append(prop_type) # type: ignore
                                        elif oper_type == objects.MAKE and prop_negated_count % 2 == 0:
                                            if prop_type == objects.ALL and noun_negated == False:
                                                obj.make_object.extend(self.all_list)
                                            else:
                                                obj.make_object.append(prop_type) # type: ignore
                                        elif oper_type == objects.WRITE and prop_negated_count % 2 == 0:
                                            obj.write_text.append(prop_type)
                        if obj_type == objects.Game and oper_type == objects.IS:
                            if (not noun_negated) and len(infix_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_list, True):
                                del_props = []
                                for old_prop_type, old_prop_negated_count in self.game_properties:
                                    if prop_type == old_prop_type:
                                        if old_prop_negated_count > prop_negated_count:
                                            return
                                        del_props.append((old_prop_type, old_prop_negated_count))
                                for old_prop_type, old_prop_negated_count in del_props:
                                    self.game_properties.remove((old_prop_type, old_prop_negated_count))
                                self.game_properties.append((prop_type, prop_negated_count))
                        elif obj_type == objects.Level:
                            if (not noun_negated) and len(infix_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_list, True):
                                if oper_type == objects.IS:
                                    self.new_prop(prop_type, prop_negated_count)
                                elif oper_type == objects.WRITE and prop_negated_count % 2 == 0:
                                    self.write_text.append(prop_type)
                        elif obj_type == objects.World:
                            if (not noun_negated) and len(infix_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_list, True):
                                if oper_type == objects.IS:
                                    world.new_world_prop(prop_type, prop_negated_count)
                                elif oper_type == objects.WRITE and prop_negated_count % 2 == 0:
                                    world.world_write_text.append(prop_type)
                        elif obj_type == objects.Clone:
                            if (not noun_negated) and len(infix_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_list, True):
                                if oper_type == objects.IS:
                                    world.new_clone_prop(prop_type, prop_negated_count)
                                elif oper_type == objects.WRITE and prop_negated_count % 2 == 0:
                                    world.clone_write_text.append(prop_type)
                        if noun_negated:
                            for obj in [o for o in world.object_list if (not isinstance(o, objects.not_in_all)) and not isinstance(o, obj_type)]:
                                if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                    if oper_type == objects.IS:
                                        new_prop_list.append((obj, (prop_type, prop_negated_count)))
                                    elif oper_type == objects.HAS and prop_negated_count % 2 == 0:
                                        if prop_type == objects.ALL and noun_negated == False:
                                            obj.has_object.extend(self.all_list)
                                        else:
                                            obj.has_object.append(prop_type) # type: ignore
                                    elif oper_type == objects.MAKE and prop_negated_count % 2 == 0:
                                        if prop_type == objects.ALL and noun_negated == False:
                                            obj.make_object.extend(self.all_list)
                                        else:
                                            obj.make_object.append(prop_type) # type: ignore
                                    elif oper_type == objects.WRITE and prop_negated_count % 2 == 0:
                                        obj.write_text.append(prop_type)
                        else:
                            for obj in world.get_objs_from_type(obj_type):
                                if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                    if oper_type == objects.IS:
                                        new_prop_list.append((obj, (prop_type, prop_negated_count)))
                                    elif oper_type == objects.HAS and prop_negated_count % 2 == 0:
                                        if prop_type == objects.ALL and noun_negated == False:
                                            obj.has_object.extend(self.all_list)
                                        else:
                                            obj.has_object.append(prop_type) # type: ignore
                                    elif oper_type == objects.MAKE and prop_negated_count % 2 == 0:
                                        if prop_type == objects.ALL and noun_negated == False:
                                            obj.make_object.extend(self.all_list)
                                        else:
                                            obj.make_object.append(prop_type) # type: ignore
                                    elif oper_type == objects.WRITE and prop_negated_count % 2 == 0:
                                        obj.write_text.append(prop_type)
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.new_prop(prop_type, prop_negated_count)
    def move_obj_between_worlds(self, old_world: worlds.World, obj: objects.BmpObject, new_world: worlds.World, new_pos: spaces.Coord) -> None:
        old_world.object_pos_index[old_world.pos_to_index(obj.pos)].remove(obj)
        old_world.object_list.remove(obj)
        obj.pos = new_pos
        new_world.object_list.append(obj)
        new_world.object_pos_index[new_world.pos_to_index(obj.pos)].append(obj)
    def move_obj_in_world(self, world: worlds.World, obj: objects.BmpObject, pos: spaces.Coord) -> None:
        world.object_pos_index[world.pos_to_index(obj.pos)].remove(obj)
        obj.pos = pos
        world.object_pos_index[world.pos_to_index(obj.pos)].append(obj)
    def destroy_obj(self, world: worlds.World, obj: objects.BmpObject) -> None:
        world.del_obj(obj)
        for new_noun_type in obj.has_object:
            if new_noun_type == objects.GAME:
                pass
            elif new_noun_type == objects.LEVEL:
                world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                obj.pos = (1, 1)
                obj.reset_uuid()
                new_world.new_obj(obj)
                self.created_levels.append(Level(obj.uuid.hex, [new_world], self.name, rule_list=self.rule_list))
                world.new_obj(objects.LevelPointer(obj.pos, obj.uuid.hex, orient=obj.orient))
            elif new_noun_type == objects.WORLD:
                world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                obj.pos = (1, 1)
                obj.reset_uuid()
                new_world.new_obj(obj)
                self.set_world(new_world)
                world.new_obj(objects.World(obj.pos, obj.uuid.hex, 0, obj.orient))
            elif new_noun_type == objects.CLONE:
                world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                obj.pos = (1, 1)
                obj.reset_uuid()
                new_world.new_obj(obj)
                self.set_world(new_world)
                world.new_obj(objects.Clone(obj.pos, obj.uuid.hex, 0, obj.orient))
            elif new_noun_type == objects.TEXT:
                new_obj_type = objects.nouns_objs_dicts.swapped()[type(obj)]
                world.new_obj(new_obj_type(obj.pos, obj.orient))
            else:
                new_obj_type = objects.nouns_objs_dicts[new_noun_type]
                world.new_obj(new_obj_type(obj.pos, obj.orient))
    def same_float_prop(self, obj_1: objects.BmpObject, obj_2: objects.BmpObject):
        return not (obj_1.has_prop(objects.FLOAT) ^ obj_2.has_prop(objects.FLOAT))
    def get_move_list(self, cause: type[objects.Property], world: worlds.World, obj: objects.BmpObject, orient: spaces.Orient, pos: Optional[spaces.Coord] = None, pushed: Optional[list[objects.BmpObject]] = None, passed: Optional[list[worlds.World]] = None, transnum: Optional[float] = None, depth: int = 0) -> Optional[list[tuple[objects.BmpObject, worlds.World, spaces.Coord, spaces.Orient]]]:
        if depth > 128:
            return None
        depth += 1
        pushed = pushed[:] if pushed is not None else []
        if obj in pushed:
            return None
        passed = passed[:] if passed is not None else []
        pos = pos if pos is not None else obj.pos
        new_pos = spaces.pos_facing(pos, orient)
        exit_world = False
        exit_list = []
        if world.out_of_range(new_pos):
            exit_world = True
            # infinite exit
            if world in passed:
                return_value = self.find_super_world(world.name, world.inf_tier + 1)
                if return_value is None:
                    exit_world = False
                else:
                    super_world, world_obj = return_value
                    new_transnum = super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, orient) if transnum is not None else world.pos_to_transnum(obj.pos, orient)
                    new_move_list = self.get_move_list(cause, super_world, obj, orient, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
            # exit
            else:
                return_value = self.find_super_world(world.name, world.inf_tier)
                if return_value is None:
                    exit_world = False
                else:
                    super_world, world_obj = return_value
                    new_transnum = super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, orient) if transnum is not None else world.pos_to_transnum(obj.pos, orient)
                    passed.append(world)
                    new_move_list = self.get_move_list(cause, super_world, obj, orient, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
        # push
        push_objects = [o for o in world.get_objs_from_pos(new_pos) if o.has_prop(objects.PUSH)]
        you_objects = [o for o in world.get_objs_from_pos(new_pos) if o.has_prop(objects.YOU)]
        if not issubclass(cause, objects.YOU):
            push_objects.extend(you_objects)
        objects_that_cant_push: list[objects.BmpObject] = []
        push = False
        push_list = []
        if len(push_objects) != 0 and not world.out_of_range(new_pos):
            push = True
            for push_object in push_objects:
                pushed.append(obj)
                new_move_list = self.get_move_list(cause, world, push_object, orient, pushed=pushed, depth=depth)
                pushed.pop()
                if new_move_list is None:
                    objects_that_cant_push.append(push_object)
                    push = False
                    break
                else:
                    push_list.extend(new_move_list)
            push_list.append((obj, world, new_pos, orient))
        # stop wall & shut door
        not_stop_list = []
        simple = False
        if not world.out_of_range(new_pos):
            stop_objects = [o for o in world.get_objs_from_pos(new_pos) if o.has_prop(objects.STOP) and not o.has_prop(objects.PUSH)]
            stop_objects.extend(objects_that_cant_push)
            if len(stop_objects) != 0:
                if obj.has_prop(objects.OPEN):
                    simple = True
                    for stop_object in stop_objects:
                        if not stop_object.has_prop(objects.SHUT):
                            simple = False
                elif obj.has_prop(objects.SHUT):
                    simple = True
                    for stop_object in stop_objects:
                        if not stop_object.has_prop(objects.OPEN):
                            simple = False
            else:
                simple = True
        if simple:
            not_stop_list.append((obj, world, new_pos, orient))
        # squeeze
        squeeze = False
        squeeze_list = []
        if isinstance(obj, objects.WorldPointer) and obj.has_prop(objects.PUSH) and not world.out_of_range(new_pos):
            sub_world = self.get_world(obj.name, obj.inf_tier)
            if sub_world is not None:
                new_push_objects = list(filter(lambda o: objects.BmpObject.has_prop(o, objects.PUSH), world.get_objs_from_pos(new_pos)))
                if len(new_push_objects) != 0:
                    squeeze = True
                    temp_stop_object = objects.STOP(spaces.pos_facing(pos, spaces.swap_orientation(orient)))
                    temp_stop_object.new_prop(objects.STOP)
                    world.new_obj(temp_stop_object)
                    for new_push_object in new_push_objects:
                        input_pos = sub_world.default_input_position(orient)
                        pushed.append(obj)
                        test_move_list = self.get_move_list(cause, sub_world, new_push_object, spaces.swap_orientation(orient), input_pos, pushed=pushed, depth=depth)
                        pushed.pop()
                        if test_move_list is None:
                            squeeze = False
                            break
                        else:
                            squeeze_list.extend(test_move_list)
                    if squeeze:
                        squeeze_list.append((obj, world, new_pos, orient))
                    world.del_obj(temp_stop_object)
        enter_world = False
        enter_list = []
        worlds_that_cant_push = [o for o in objects_that_cant_push if isinstance(o, objects.WorldPointer)]
        if len(worlds_that_cant_push) != 0 and not world.out_of_range(new_pos):
            enter_world = True
            for world_object in worlds_that_cant_push:
                sub_world = self.get_world(world_object.name, world_object.inf_tier)
                if sub_world is None:
                    enter_world = False
                    break
                else:
                    new_move_list = None
                    # infinite enter
                    if sub_world in passed:
                        sub_sub_world = self.get_world(sub_world.name, sub_world.inf_tier - 1)
                        if sub_sub_world is not None:
                            new_transnum = 0.5
                            input_pos = sub_sub_world.default_input_position(spaces.swap_orientation(orient))
                            passed.append(world)
                            new_move_list = self.get_move_list(cause, sub_sub_world, obj, orient, input_pos, pushed, passed, new_transnum, depth)
                        else:
                            enter_world = False
                            break
                    # enter
                    else:
                        new_transnum = world.transnum_to_smaller_transnum(transnum, world_object.pos, spaces.swap_orientation(orient)) if transnum is not None else 0.5
                        input_pos = sub_world.transnum_to_pos(transnum, spaces.swap_orientation(orient)) if transnum is not None else sub_world.default_input_position(spaces.swap_orientation(orient))
                        passed.append(world)
                        new_move_list = self.get_move_list(cause, sub_world, obj, orient, input_pos, pushed, passed, new_transnum, depth)
                    if new_move_list is not None:
                        enter_list.extend(new_move_list)
                    else:
                        enter_world = False
                        break
        if exit_world:
            return basics.remove_same_elements(exit_list)
        elif push:
            return basics.remove_same_elements(push_list)
        elif enter_world:
            return basics.remove_same_elements(enter_list)
        elif squeeze:
            return basics.remove_same_elements(squeeze_list)
        elif simple:
            return basics.remove_same_elements(not_stop_list)
        else:
            return None
    def move_objs_from_move_list(self, move_list: list[tuple[objects.BmpObject, worlds.World, spaces.Coord, spaces.Orient]]) -> None:
        move_list = basics.remove_same_elements(move_list)
        for move_obj, new_world, new_pos, new_orient in move_list:
            move_obj.moved = True
            for world in self.world_list:
                if move_obj in world.object_list:
                    old_world = world
            if old_world == new_world:
                self.move_obj_in_world(old_world, move_obj, new_pos)
            else:
                self.move_obj_between_worlds(old_world, move_obj, new_world, new_pos)
            move_obj.orient = new_orient
        if len(move_list) != 0 and "move" not in self.sound_events:
            self.sound_events.append("move")
    def you(self, orient: spaces.PlayerOperation) -> bool:
        if orient == spaces.NullOrient.O:
            return False
        move_list = []
        pushing_game = False
        for world in self.world_list:
            if world.has_world_prop(objects.YOU) or self.has_prop(objects.YOU):
                for obj in world.object_list:
                    new_move_list = self.get_move_list(objects.MOVE, world, obj, spaces.Orient.S)
                    if new_move_list is not None:
                        move_list.extend(new_move_list)
                    else:
                        pushing_game = True
                continue
            you_objs = [o for o in world.object_list if o.has_prop(objects.YOU)]
            for obj in you_objs:
                obj.orient = orient
                new_move_list = self.get_move_list(objects.YOU, world, obj, obj.orient)
                if new_move_list is not None:
                    move_list.extend(new_move_list)
                else:
                    pushing_game = True
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
        return pushing_game
    def select(self, orient: spaces.PlayerOperation) -> Optional[str]:
        if orient == spaces.NullOrient.O:
            for world in self.world_list:
                select_objs = [o for o in world.object_list if o.has_prop(objects.SELECT)]
                levels: list[objects.LevelPointer] = []
                for obj in select_objs:
                    levels.extend(world.get_levels_from_pos(obj.pos))
                    if len(levels) != 0:
                        self.sound_events.append("level")
                        return levels[0].name
        else:
            for world in self.world_list:
                select_objs = [o for o in world.object_list if o.has_prop(objects.SELECT)]
                for obj in select_objs:
                    new_pos = spaces.pos_facing(obj.pos, orient)
                    if not world.out_of_range(new_pos):
                        self.move_obj_in_world(world, obj, new_pos)
            return None
    def move(self) -> bool:
        pushing_game = False
        for world in self.world_list:
            if world.has_world_prop(objects.MOVE) or self.has_prop(objects.MOVE):
                for obj in world.object_list:
                    if not obj.has_prop(objects.FLOAT):
                        new_move_list = self.get_move_list(objects.MOVE, world, obj, spaces.Orient.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
                continue
            move_objs = [o for o in world.object_list if o.has_prop(objects.MOVE)]
            for obj in move_objs:
                move_list = []
                new_move_list = self.get_move_list(objects.MOVE, world, obj, obj.orient)
                if new_move_list is not None:
                    move_list = new_move_list
                else:
                    obj.orient = spaces.swap_orientation(obj.orient)
                    new_move_list = self.get_move_list(objects.MOVE, world, obj, obj.orient)
                    if new_move_list is not None:
                        move_list = new_move_list
                    else:
                        pushing_game = True
                move_list = basics.remove_same_elements(move_list)
                self.move_objs_from_move_list(move_list)
        return pushing_game
    def shift(self) -> bool:
        move_list = []
        pushing_game = False
        for world in self.world_list:
            if world.has_world_prop(objects.SHIFT) or self.has_prop(objects.SHIFT):
                for obj in world.object_list:
                    if not obj.has_prop(objects.FLOAT):
                        new_move_list = self.get_move_list(objects.SHIFT, world, obj, spaces.Orient.D)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
                continue
            shift_objs = [o for o in world.object_list if o.has_prop(objects.SHIFT)]
            for shift_obj in shift_objs:
                for obj in world.get_objs_from_pos(shift_obj.pos):
                    if obj == shift_obj:
                        continue
                    if self.same_float_prop(obj, shift_obj):
                        new_move_list = self.get_move_list(objects.SHIFT, world, obj, shift_obj.orient)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
        return pushing_game
    def tele(self) -> None:
        if self.has_prop(objects.TELE):
            pass
        for world in self.world_list:
            if world.has_world_prop(objects.TELE):
                pass
        tele_list: list[tuple[worlds.World, objects.BmpObject, worlds.World, spaces.Coord]] = []
        object_list: list[tuple[worlds.World, objects.BmpObject]] = []
        for world in self.world_list:
            object_list.extend([(world, o) for o in world.object_list])
        tele_objs = [t for t in object_list if t[1].has_prop(objects.TELE)]
        tele_obj_types: dict[type[objects.BmpObject], list[tuple[worlds.World, objects.BmpObject]]] = {}
        for obj_type in objects.nouns_objs_dicts.pairs.values():
            for tele_obj in tele_objs:
                if isinstance(tele_obj[1], obj_type):
                    tele_obj_types[obj_type] = tele_obj_types.get(obj_type, []) + [tele_obj]
        for new_tele_objs in tele_obj_types.values():
            if len(new_tele_objs) <= 1:
                continue
            for tele_world, tele_obj in new_tele_objs:
                other_tele_objs = new_tele_objs[:]
                other_tele_objs.remove((tele_world, tele_obj))
                for obj in world.get_objs_from_pos(tele_obj.pos):
                    if obj == tele_obj:
                        continue
                    if self.same_float_prop(obj, tele_obj):
                        other_tele_world, other_tele_obj = random.choice(other_tele_objs)
                        tele_list.append((world, obj, other_tele_world, other_tele_obj.pos))
        for old_world, obj, new_world, pos in tele_list:
            self.move_obj_between_worlds(old_world, obj, new_world, pos)
        if len(tele_list) != 0:
            self.sound_events.append("tele")
    def sink(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            sink_objs = [o for o in world.object_list if o.has_prop(objects.SINK)]
            if world.has_world_prop(objects.SINK) or self.has_prop(objects.SINK):
                for obj in world.object_list:
                    if not obj.has_prop(objects.FLOAT):
                        delete_list.append(obj)
            for sink_obj in sink_objs:
                for obj in world.get_objs_from_pos(sink_obj.pos):
                    if obj == sink_obj:
                        continue
                    if obj.pos == sink_obj.pos:
                        if self.same_float_prop(obj, sink_obj):
                            if obj not in delete_list and sink_obj not in delete_list:
                                delete_list.append(obj)
                                delete_list.append(sink_obj)
                                break
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("sink")
    def hot_and_melt(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            melt_objs = [o for o in world.object_list if o.has_prop(objects.MELT)]
            hot_objs = [o for o in world.object_list if o.has_prop(objects.HOT)]
            if len(hot_objs) != 0 and (world.has_world_prop(objects.MELT) or self.has_prop(objects.MELT)):
                for melt_obj in melt_objs:
                    if not melt_obj.has_prop(objects.FLOAT):
                        delete_list.extend(world.object_list)
                continue
            if len(melt_objs) != 0 and (world.has_world_prop(objects.HOT) or self.has_prop(objects.HOT)):
                for melt_obj in melt_objs:
                    if not melt_obj.has_prop(objects.FLOAT):
                        delete_list.append(melt_obj)
                continue
            for hot_obj in hot_objs:
                for melt_obj in melt_objs:
                    if hot_obj.pos == melt_obj.pos:
                        if self.same_float_prop(hot_obj, melt_obj):
                            if melt_obj not in delete_list:
                                delete_list.append(melt_obj)
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("melt")
    def defeat(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            you_objs = [o for o in world.object_list if o.has_prop(objects.YOU)]
            defeat_objs = [o for o in world.object_list if o.has_prop(objects.DEFEAT)]
            if len(defeat_objs) != 0 and (world.has_world_prop(objects.YOU) or self.has_prop(objects.YOU)):
                delete_list.extend(world.object_list)
                continue
            for you_obj in you_objs:
                if world.has_world_prop(objects.DEFEAT) or self.has_prop(objects.DEFEAT):
                    if you_obj not in delete_list:
                        delete_list.append(you_obj)
                        continue
                for defeat_obj in defeat_objs:
                    if you_obj.pos == defeat_obj.pos:
                        if self.same_float_prop(defeat_obj, you_obj):
                            if you_obj not in delete_list:
                                delete_list.append(you_obj)
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("defeat")
    def open_and_shut(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            shut_objs = [o for o in world.object_list if o.has_prop(objects.SHUT)]
            open_objs = [o for o in world.object_list if o.has_prop(objects.OPEN)]
            if len(open_objs) != 0 and (world.has_world_prop(objects.SHUT) or self.has_prop(objects.SHUT)):
                delete_list.extend(world.object_list)
                continue
            if len(shut_objs) != 0 and (world.has_world_prop(objects.OPEN) or self.has_prop(objects.OPEN)):
                delete_list.extend(world.object_list)
                continue
            for open_obj in open_objs:
                for shut_obj in shut_objs:
                    if shut_obj.pos == open_obj.pos:
                        if shut_obj not in delete_list and open_obj not in delete_list:
                            delete_list.append(shut_obj)
                            if shut_obj != open_obj:
                                delete_list.append(open_obj)
                            break
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("open")
    def make(self) -> None:
        for world in self.world_list:
            for obj in world.object_list:
                for make_noun_type in obj.make_object:
                    if make_noun_type == objects.GAME:
                        pass
                    elif make_noun_type == objects.LEVEL:
                        world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                        new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                        new_obj = copy.deepcopy(obj)
                        new_obj.pos = (1, 1)
                        new_obj.reset_uuid()
                        new_world.new_obj(new_obj)
                        self.created_levels.append(Level(obj.uuid.hex, [new_world], self.name, rule_list=self.rule_list))
                        world.new_obj(objects.LevelPointer(obj.pos, obj.uuid.hex, orient=obj.orient))
                    elif make_noun_type == objects.WORLD:
                        world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                        new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                        new_obj = copy.deepcopy(obj)
                        new_obj.pos = (1, 1)
                        new_obj.reset_uuid()
                        new_world.new_obj(new_obj)
                        self.set_world(new_world)
                        world.new_obj(objects.World(obj.pos, obj.uuid.hex, 0, obj.orient))
                    elif make_noun_type == objects.CLONE:
                        world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                        new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                        new_obj = copy.deepcopy(obj)
                        new_obj.pos = (1, 1)
                        new_obj.reset_uuid()
                        new_world.new_obj(new_obj)
                        self.set_world(new_world)
                        world.new_obj(objects.Clone(obj.pos, obj.uuid.hex, 0, obj.orient))
                    elif make_noun_type == objects.TEXT:
                        make_obj_type = objects.nouns_objs_dicts.swapped()[type(obj)]
                        world.new_obj(make_obj_type(obj.pos, obj.orient))
                    else:
                        make_obj_type = objects.nouns_objs_dicts[make_noun_type]
                        world.new_obj(make_obj_type(obj.pos, obj.orient))
    def transform(self) -> Optional[list[objects.BmpObject]]:
        for world in self.world_list:
            delete_object_list = []
            for old_obj in world.object_list: # type: ignore
                old_obj: objects.BmpObject # type: ignore
                old_type = type(old_obj)
                new_nouns = [n for n, c in old_obj.properties if issubclass(n, objects.Noun) and c % 2 == 0]
                new_types = [t for t in map(objects.nouns_objs_dicts.get, new_nouns) if t is not None]
                not_new_nouns = [n for n, c in old_obj.properties if issubclass(n, objects.Noun) and c % 2 == 1]
                not_new_types = [t for t in map(objects.nouns_objs_dicts.get, not_new_nouns) if t is not None]
                transform_success = False
                old_type_is_old_type = False
                old_type_is_not_old_type = False
                for new_type in new_types:
                    if issubclass(old_type, new_type):
                        old_type_is_old_type = True
                for not_new_type in not_new_types:
                    if issubclass(old_type, not_new_type):
                        old_type_is_not_old_type = True
                if old_type_is_not_old_type:
                    transform_success = True
                if not old_type_is_old_type:
                    if objects.All in new_types:
                        new_types.remove(objects.All)
                        all_nouns = [t for t in self.all_list if t not in not_new_types]
                        new_types.extend([t for t in map(objects.nouns_objs_dicts.get, all_nouns) if t is not None])
                    for new_text_type in old_obj.write_text:
                        new_obj = new_text_type(old_obj.pos, old_obj.orient)
                        world.new_obj(new_obj)
                        transform_success = True
                    for new_type in new_types:
                        pass_this_transform = False
                        for not_new_type in not_new_types:
                            if issubclass(new_type, not_new_type):
                                pass_this_transform = True
                        if pass_this_transform:
                            pass
                        elif issubclass(new_type, objects.Game):
                            if issubclass(old_type, objects.LevelPointer):
                                self.new_games.append(objects.LEVEL)
                            elif issubclass(old_type, objects.World):
                                self.new_games.append(objects.WORLD)
                            elif issubclass(old_type, objects.Clone):
                                self.new_games.append(objects.CLONE)
                            else:
                                self.new_games.append(old_type)
                            transform_success = True
                        elif issubclass(new_type, objects.LevelPointer):
                            if issubclass(old_type, objects.LevelPointer):
                                pass
                            elif issubclass(old_type, objects.WorldPointer):
                                old_obj: objects.WorldPointer # type: ignore
                                self.created_levels.append(Level(old_obj.name, self.world_list, self.name, old_obj.name, old_obj.inf_tier, self.rule_list))
                                new_obj = objects.LevelPointer(old_obj.pos, old_obj.name, orient=old_obj.orient)
                                world.new_obj(new_obj)
                                transform_success = True
                            else:
                                world_color = colors.to_background_color(displays.sprite_colors[old_obj.sprite_name])
                                new_world = worlds.World(old_obj.uuid.hex, (3, 3), 0, world_color)
                                self.created_levels.append(Level(old_obj.uuid.hex, [new_world], self.name, rule_list=self.rule_list))
                                new_world.new_obj(old_type((1, 1)))
                                new_obj = objects.LevelPointer(old_obj.pos, old_obj.uuid.hex, orient=old_obj.orient)
                                world.new_obj(new_obj)
                                transform_success = True
                        elif issubclass(new_type, objects.World):
                            if issubclass(old_type, objects.World):
                                pass
                            elif issubclass(old_type, objects.LevelPointer):
                                old_obj: objects.LevelPointer # type: ignore
                                info = {"from": {"type": objects.LevelPointer, "name": old_obj.name}, "to": {"type": new_type}}
                                world.new_obj(objects.Transform(old_obj.pos, info, old_obj.orient))
                                transform_success = True
                            elif issubclass(old_type, objects.Clone):
                                old_obj: objects.Clone # type: ignore
                                world.new_obj(objects.World(old_obj.pos, old_obj.name, old_obj.inf_tier, old_obj.orient))
                                transform_success = True
                            else:
                                world_color = colors.to_background_color(displays.sprite_colors[old_obj.sprite_name])
                                new_world = worlds.World(old_obj.uuid.hex, (3, 3), 0, world_color)
                                new_world.new_obj(old_type((1, 1), old_obj.orient)) # type: ignore
                                self.set_world(new_world)
                                world.new_obj(objects.World(old_obj.pos, old_obj.uuid.hex, 0, old_obj.orient))
                                transform_success = True
                        elif issubclass(new_type, objects.Clone):
                            if issubclass(old_type, objects.Clone):
                                pass
                            elif issubclass(old_type, objects.LevelPointer):
                                old_obj: objects.LevelPointer # type: ignore
                                info = {"from": {"type": objects.LevelPointer, "name": old_obj.name}, "to": {"type": new_type}}
                                world.new_obj(objects.Transform(old_obj.pos, info, old_obj.orient))
                                transform_success = True
                            elif issubclass(old_type, objects.World):
                                old_obj: objects.World # type: ignore
                                world.new_obj(objects.Clone(old_obj.pos, old_obj.name, old_obj.inf_tier, old_obj.orient))
                                transform_success = True
                            else:
                                world_color = colors.to_background_color(displays.sprite_colors[old_obj.sprite_name])
                                new_world = worlds.World(old_obj.uuid.hex, (3, 3), 0, world_color)
                                new_world.new_obj(old_type((1, 1), old_obj.orient)) # type: ignore
                                self.set_world(new_world)
                                world.new_obj(objects.Clone(old_obj.pos, old_obj.uuid.hex, 0, old_obj.orient))
                                transform_success = True
                        elif issubclass(new_type, objects.Text) and not issubclass(old_type, objects.Text):
                            transform_success = True
                            new_obj = objects.nouns_objs_dicts.swapped()[old_type](old_obj.pos, old_obj.orient)
                            world.new_obj(new_obj)
                        else:
                            transform_success = True
                            new_obj = new_type(old_obj.pos, old_obj.orient)
                            world.new_obj(new_obj)
                if transform_success:
                    delete_object_list.append(old_obj)
            for delete_obj in delete_object_list:
                world.del_obj(delete_obj)
        transform_to: dict[type[objects.BmpObject], list[objects.BmpObject]] = {}
        special_new_types: dict[type[objects.BmpObject], list[type[objects.BmpObject]]] = {}
        special_not_new_types: dict[type[objects.BmpObject], list[type[objects.BmpObject]]] = {}
        special_new_types[objects.LevelPointer] = []
        special_not_new_types[objects.LevelPointer] = []
        transform_to[objects.LevelPointer] = []
        for prop_type, prop_negated_count in self.properties:
            if not issubclass(prop_type, objects.Noun):
                continue
            if issubclass(prop_type, objects.ALL):
                if prop_negated_count % 2 == 0:
                    special_new_types[objects.LevelPointer].extend(objects.in_not_all)
                else:
                    special_not_new_types[objects.LevelPointer].extend(objects.in_not_all)
            else:
                new_type = objects.nouns_objs_dicts[prop_type]
                if prop_negated_count % 2 == 0:
                    special_new_types[objects.LevelPointer].append(new_type)
                else:
                    special_not_new_types[objects.LevelPointer].append(new_type)
        for world in self.world_list:
            for old_type in (objects.World, objects.Clone):
                special_new_types[old_type] = []
                special_not_new_types[old_type] = []
                transform_to[old_type] = []
            for prop_type, prop_negated_count in world.world_properties:
                if not issubclass(prop_type, objects.Noun):
                    continue
                if issubclass(prop_type, objects.ALL):
                    if prop_negated_count % 2 == 0:
                        special_new_types[objects.World].extend(objects.in_not_all)
                    else:
                        special_not_new_types[objects.World].extend(objects.in_not_all)
                else:
                    new_type = objects.nouns_objs_dicts[prop_type]
                    if prop_negated_count % 2 == 0:
                        special_new_types[objects.World].append(new_type)
                    else:
                        special_not_new_types[objects.World].append(new_type)
            for prop_type, prop_negated_count in world.clone_properties:
                if not issubclass(prop_type, objects.Noun):
                    continue
                if issubclass(prop_type, objects.ALL):
                    if prop_negated_count % 2 == 0:
                        special_new_types[objects.Clone].extend(objects.in_not_all)
                    else:
                        special_not_new_types[objects.Clone].extend(objects.in_not_all)
                else:
                    new_type = objects.nouns_objs_dicts[prop_type]
                    if prop_negated_count % 2 == 0:
                        special_new_types[objects.Clone].append(new_type)
                    else:
                        special_not_new_types[objects.Clone].append(new_type)
            for new_text_type in self.write_text:
                new_obj = new_text_type(old_obj.pos, old_obj.orient)
                transform_to[objects.LevelPointer].append(new_obj)
            for new_text_type in world.world_write_text:
                new_obj = new_text_type(old_obj.pos, old_obj.orient)
                transform_to[objects.World].append(new_obj)
            for new_text_type in world.clone_write_text:
                new_obj = new_text_type(old_obj.pos, old_obj.orient)
                transform_to[objects.Clone].append(new_obj)
            for old_type in (objects.LevelPointer, objects.World, objects.Clone):
                if old_type in special_not_new_types[old_type]:
                    transform_to[old_type].append(objects.Empty((0, 0)))
                for new_type in special_new_types[old_type]:
                    if issubclass(old_type, objects.LevelPointer):
                        if issubclass(new_type, objects.LevelPointer):
                            transform_to[objects.LevelPointer] = []
                            break
                        elif issubclass(new_type, objects.World):
                            info = {"from": {"type": objects.LevelPointer, "name": self.name}, "to": {"type": objects.World}}
                            transform_to[objects.LevelPointer].append(objects.Transform((0, 0), info))
                        elif issubclass(new_type, objects.Clone):
                            info = {"from": {"type": objects.LevelPointer, "name": self.name}, "to": {"type": objects.Clone}}
                            transform_to[objects.LevelPointer].append(objects.Transform((0, 0), info))
                        elif issubclass(new_type, objects.Game):
                            transform_to[objects.LevelPointer].append(objects.Empty((0, 0)))
                            self.new_games.append(objects.LEVEL)
                        elif issubclass(new_type, objects.Text):
                            transform_to[objects.LevelPointer].append(objects.LEVEL((0, 0)))
                        else:
                            transform_to[objects.LevelPointer].append(new_type((0, 0)))
                    elif issubclass(old_type, objects.World):
                        if issubclass(new_type, objects.World):
                            transform_to[objects.World] = []
                            break
                        elif issubclass(new_type, objects.LevelPointer):
                            self.created_levels.append(Level(world.name, self.world_list, self.name, world.name, world.inf_tier, self.rule_list))
                            transform_to[objects.World].append(objects.LevelPointer((0, 0), world.name))
                        elif issubclass(new_type, objects.Clone):
                            transform_to[objects.World].append(objects.Clone((0, 0), world.name, world.inf_tier))
                        elif issubclass(new_type, objects.Game):
                            transform_to[objects.World].append(objects.Empty((0, 0)))
                            self.new_games.append(objects.WORLD)
                        elif issubclass(new_type, objects.Text):
                            transform_to[objects.World].append(objects.WORLD((0, 0)))
                        else:
                            transform_to[objects.World].append(new_type((0, 0))) # type: ignore
                    elif issubclass(old_type, objects.Clone):
                        if issubclass(new_type, objects.Clone):
                            transform_to[objects.Clone] = []
                            break
                        elif issubclass(new_type, objects.LevelPointer):
                            self.created_levels.append(Level(world.name, self.world_list, self.name, world.name, world.inf_tier, self.rule_list))
                            transform_to[objects.Clone].append(objects.LevelPointer((0, 0), world.name))
                        elif issubclass(new_type, objects.World):
                            transform_to[objects.Clone].append(objects.World((0, 0), world.name, world.inf_tier))
                        elif issubclass(new_type, objects.Game):
                            transform_to[objects.Clone].append(objects.Empty((0, 0)))
                            self.new_games.append(objects.CLONE)
                        elif issubclass(new_type, objects.Text):
                            transform_to[objects.Clone].append(objects.CLONE((0, 0)))
                        else:
                            transform_to[objects.Clone].append(new_type((0, 0))) # type: ignore
            delete_special_object_list: list[objects.BmpObject] = []
            for super_world in self.world_list:
                if len(transform_to[objects.World]) != 0:
                    for world_obj in filter(lambda o: o.name == world.name and o.inf_tier == world.inf_tier, super_world.get_worlds()):
                        delete_special_object_list.append(world_obj)
                        for transform_obj in transform_to[objects.World]:
                            transform_obj.pos = world_obj.pos
                            transform_obj.orient = world_obj.orient
                            super_world.new_obj(transform_obj)
                if len(transform_to[objects.Clone]) != 0:
                    for clone_obj in filter(lambda o: o.name == world.name and o.inf_tier == world.inf_tier, super_world.get_clones()):
                        delete_special_object_list.append(clone_obj)
                        for transform_obj in transform_to[objects.Clone]:
                            transform_obj.pos = clone_obj.pos
                            transform_obj.orient = clone_obj.orient
                            super_world.new_obj(transform_obj)
            for obj in delete_special_object_list:
                super_world.del_obj(obj)
        if len(transform_to[objects.LevelPointer]) != 0:
            return transform_to[objects.LevelPointer]
        else:
            return None
    def win(self) -> bool:
        for world in self.world_list:
            you_objs = [o for o in world.object_list if o.has_prop(objects.YOU)]
            win_objs = [o for o in world.object_list if o.has_prop(objects.WIN)]
            for you_obj in you_objs:
                if world.has_world_prop(objects.WIN) or self.has_prop(objects.WIN):
                    if not you_obj.has_prop(objects.FLOAT):
                        self.sound_events.append("win")
                        return True
                for win_obj in win_objs:
                    if you_obj.pos == win_obj.pos:
                        if self.same_float_prop(you_obj, win_obj):
                            self.sound_events.append("win")
                            return True
        return False
    def end(self) -> bool:
        for world in self.world_list:
            you_objs = [o for o in world.object_list if o.has_prop(objects.YOU)]
            end_objs = [o for o in world.object_list if o.has_prop(objects.END)]
            for you_obj in you_objs:
                if world.has_world_prop(objects.END) or self.has_prop(objects.END):
                    if not you_obj.has_prop(objects.FLOAT):
                        self.sound_events.append("end")
                        return True
                for end_obj in end_objs:
                    if you_obj.pos == end_obj.pos:
                        if self.same_float_prop(you_obj, end_obj):
                            self.sound_events.append("end")
                            return True
        return False
    def done(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            if world.has_world_prop(objects.DONE) or self.has_prop(objects.DONE):
                delete_list.extend(world.object_list)
            for obj in world.object_list:
                if obj.has_prop(objects.DONE):
                    delete_list.append(obj)
            for obj in delete_list:
                world.del_obj(obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("done")
    def turn(self, op: spaces.PlayerOperation) -> ReTurnValue:
        self.new_games = []
        self.sound_events = []
        self.created_levels = []
        old_prop_dict: dict[uuid.UUID, list[tuple[type[objects.Text], int]]] = {}
        for world in self.world_list:
            for obj in world.object_list:
                old_prop_dict[obj.uuid] = [t for t in obj.properties]
                obj.moved = False
        self.update_rules(old_prop_dict)
        game_push = self.you(op)
        game_push |= self.move()
        self.update_rules(old_prop_dict)
        game_push |= self.shift()
        self.update_rules(old_prop_dict)
        transform_to = self.transform()
        self.update_rules(old_prop_dict)
        self.tele()
        selected_level = self.select(op)
        self.update_rules(old_prop_dict)
        self.done()
        self.sink()
        self.hot_and_melt()
        self.defeat()
        self.open_and_shut()
        self.update_rules(old_prop_dict)
        self.make()
        self.update_rules(old_prop_dict)
        self.all_list_set()
        win = self.win()
        end = self.end()
        return {"win": win, "end": end,
                "game_push": game_push,
                "selected_level": selected_level,
                "transform_to": transform_to}
    def have_you(self) -> bool:
        for world in self.world_list:
            for obj in world.object_list:
                if obj.has_prop(objects.YOU):
                    return True
        return False
    def show_world(self, world: worlds.World, frame: int, layer: int = 0, cursor: Optional[spaces.Coord] = None) -> pygame.Surface:
        if layer >= basics.options["world_display_recursion_depth"]:
            return displays.sprites.get("world", 0, frame).copy()
        pixel_sprite_size = displays.sprite_size * displays.pixel_size
        world_surface_size = (world.width * pixel_sprite_size, world.height * pixel_sprite_size)
        world_surface = pygame.Surface(world_surface_size, pygame.SRCALPHA)
        obj_surface_list: list[tuple[spaces.Coord, pygame.Surface, objects.BmpObject]] = []
        for i in range(len(world.object_list)):
            obj = world.object_list[i]
            if isinstance(obj, objects.World):
                obj_world = self.get_world(obj.name, obj.inf_tier)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, frame, layer + 1)
                    obj_surface = displays.set_surface_color_dark(obj_surface, 0xCCCCCC)
                else:
                    obj_surface = displays.sprites.get("level", 0, frame).copy()
                surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Clone):
                obj_world = self.get_world(obj.name, obj.inf_tier)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, frame, layer + 1)
                    obj_surface = displays.set_surface_color_light(obj_surface, 0x444444)
                else:
                    obj_surface = displays.sprites.get("clone", 0, frame).copy()
                surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.LevelPointer):
                obj_surface = displays.set_surface_color_dark(displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy(), obj.icon_color)
                icon_surface = displays.set_surface_color_light(displays.sprites.get(obj.icon_name, 0, frame).copy(), 0xFFFFFF)
                icon_surface_pos = ((obj_surface.get_width() - icon_surface.get_width()) * displays.pixel_size // 2,
                                    (obj_surface.get_height() - icon_surface.get_width()) * displays.pixel_size // 2)
                obj_surface.blit(icon_surface, icon_surface_pos)
                surface_pos = (obj.x * pixel_sprite_size - (obj_surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                               obj.y * pixel_sprite_size - (obj_surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
                obj_surface_list.append((surface_pos, obj_surface, obj))
            else:
                obj_surface = displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy()
                surface_pos = (obj.x * pixel_sprite_size - (obj_surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                               obj.y * pixel_sprite_size - (obj_surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
                obj_surface_list.append((surface_pos, obj_surface, obj))
        sorted_obj_surface_list = map(lambda o: list(map(lambda t: isinstance(o[-1], t), displays.order)).index(True), obj_surface_list)
        sorted_obj_surface_list = map(lambda t: t[1], sorted(zip(sorted_obj_surface_list, obj_surface_list), key=lambda t: t[0], reverse=True))
        for pos, surface, obj in sorted_obj_surface_list:
            if isinstance(obj, objects.WorldPointer):
                world_surface.blit(pygame.transform.scale(surface, (pixel_sprite_size, pixel_sprite_size)), pos)
            else:
                world_surface.blit(pygame.transform.scale(surface, (displays.pixel_size * surface.get_width(), displays.pixel_size * surface.get_height())), pos)
        if cursor is not None:
            surface = displays.sprites.get("cursor", 0, frame).copy()
            pos = (cursor[0] * pixel_sprite_size - (surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                   cursor[1] * pixel_sprite_size - (surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
            world_surface.blit(pygame.transform.scale(surface, (displays.pixel_size * surface.get_width(), displays.pixel_size * surface.get_height())), pos)
        world_background = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA)
        world_background.fill(pygame.Color(*colors.hex_to_rgb(world.color)))
        world_background.blit(world_surface, (0, 0))
        world_surface = world_background
        if world.inf_tier > 0:
            infinite_surface = displays.sprites.get("text_infinite", 0, frame)
            multi_infinite_surface = pygame.Surface((infinite_surface.get_width(), infinite_surface.get_height() * world.inf_tier), pygame.SRCALPHA)
            multi_infinite_surface.fill("#00000000")
            for i in range(world.inf_tier):
                multi_infinite_surface.blit(infinite_surface, (0, i * infinite_surface.get_height()))
            multi_infinite_surface = pygame.transform.scale_by(multi_infinite_surface, world.height * displays.pixel_size / world.inf_tier)
            multi_infinite_surface = displays.set_alpha(multi_infinite_surface, 0x44)
            world_surface.blit(multi_infinite_surface, ((world_surface.get_width() - multi_infinite_surface.get_width()) // 2, 0))
        elif world.inf_tier < 0:
            epsilon_surface = displays.sprites.get("text_epsilon", 0, frame)
            multi_epsilon_surface = pygame.Surface((epsilon_surface.get_width(), epsilon_surface.get_height() * -world.inf_tier), pygame.SRCALPHA)
            multi_epsilon_surface.fill("#00000000")
            for i in range(-world.inf_tier):
                multi_epsilon_surface.blit(epsilon_surface, (0, i * epsilon_surface.get_height()))
            multi_epsilon_surface = pygame.transform.scale_by(multi_epsilon_surface, world.height * displays.pixel_size / -world.inf_tier)
            multi_epsilon_surface = displays.set_alpha(multi_epsilon_surface, 0x44)
            world_surface.blit(multi_epsilon_surface, ((world_surface.get_width() - multi_epsilon_surface.get_width()) // 2, 0))
        return world_surface
    def to_json(self) -> dict[str, Any]:
        json_object = {"name": self.name, "world_list": [], "super_level": self.super_level, "main_world": {"name": self.main_world_name, "infinite_tier": self.main_world_tier}}
        for world in self.world_list:
            json_object["world_list"].append(world.to_json())
        return json_object

class LevelMainWorldJson(TypedDict):
    name: str
    infinite_tier: int

class LevelJson(TypedDict):
    name: str
    super_level: str
    main_world: LevelMainWorldJson
    world_list: list[worlds.WorldJson]

def json_to_level(json_object: LevelJson, ver: Optional[str] = None) -> Level:
    world_list = []
    for world in json_object["world_list"]:
        world_list.append(worlds.json_to_world(world, ver))
    return Level(name=json_object["name"],
                 world_list=world_list,
                 super_level=json_object["super_level"],
                 main_world_name=json_object["main_world"]["name"],
                 main_world_tier=json_object["main_world"]["infinite_tier"])