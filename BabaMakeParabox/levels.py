import os
from typing import Any, NotRequired, Optional, TypedDict
import random
import copy
import uuid

from BabaMakeParabox import basics, colors, refs, spaces, objects, collects, rules, worlds, displays

import pygame

class MapLevelExtraJson(TypedDict):
    minimum_clear_for_blossom: int

class LevelJson(TypedDict):
    id: refs.LevelIDJson
    super_level: NotRequired[refs.LevelIDJson]
    map_info: NotRequired[MapLevelExtraJson]
    main_world: refs.WorldIDJson
    world_list: list[worlds.WorldJson]

max_move_count: int = 16

class Level(object):
    def __init__(self, level_id: refs.LevelID, world_list: list[worlds.World], *, super_level_id: Optional[refs.LevelID] = None, main_world_id: Optional[refs.WorldID] = None, map_info: Optional[MapLevelExtraJson] = None, collected: Optional[dict[type[collects.Collectible], bool]] = None, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.level_id: refs.LevelID = level_id
        self.world_list: list[worlds.World] = list(world_list)
        self.super_level_id: Optional[refs.LevelID] = super_level_id
        self.main_world_id: refs.WorldID = main_world_id if main_world_id is not None else world_list[0].world_id
        self.collected: dict[type[collects.Collectible], bool] = collected if collected is not None else {k: False for k in collects.collectible_dict.keys()}
        self.rule_list: list[rules.Rule] = rule_list if rule_list is not None else []
        self.map_info: Optional[MapLevelExtraJson] = map_info
        self.properties: dict[type[objects.LevelObject], objects.Properties] = {p: objects.Properties() for p in objects.level_object_types}
        self.special_operator_properties: dict[type[objects.LevelObject], dict[type[objects.Operator], objects.Properties]] = {p: {o: objects.Properties() for o in objects.special_operators} for p in objects.level_object_types}
        self.game_properties: objects.Properties = objects.Properties()
        self.created_levels: list["Level"] = []
        self.all_list: list[type[objects.Noun]] = []
        self.sound_events: list[str] = []
    def __eq__(self, level: "Level") -> bool:
        return self.level_id == level.level_id
    @property
    def main_world(self) -> worlds.World:
        return self.get_exact_world(self.main_world_id)
    def get_world(self, world_object_info: refs.WorldID) -> Optional[worlds.World]:
        for world in self.world_list:
            if world.world_id == world_object_info:
                return world
        return None
    def get_world_or_default(self, world_object_info: refs.WorldID, *, default: worlds.World) -> worlds.World:
        world = self.get_world(world_object_info)
        if world is None:
            return default
        return world
    def get_exact_world(self, world_object_info: refs.WorldID) -> worlds.World:
        world = self.get_world(world_object_info)
        if world is None:
            raise KeyError(world_object_info)
        return world
    def set_world(self, world: worlds.World) -> None:
        for i in range(len(self.world_list)):
            if world.world_id == self.world_list[i].world_id:
                self.world_list[i] = world
                return
        self.world_list.append(world)
    def find_super_worlds(self, world_object_info: refs.WorldID) -> list[tuple[worlds.World, objects.WorldObject]]:
        return_value: list[tuple[worlds.World, objects.WorldObject]] = []
        for super_world in self.world_list:
            for obj in super_world.get_worlds():
                if world_object_info == obj.world_id:
                    return_value.append((super_world, obj))
        return return_value
    def all_list_set(self) -> None:
        for world in self.world_list:
            for obj in world.object_list:
                noun_type = objects.get_noun_from_type(type(obj))
                in_not_in_all = False
                for not_all in objects.not_in_all:
                    if isinstance(obj, not_all):
                        in_not_in_all = True
                if noun_type not in self.all_list and not in_not_in_all:
                    self.all_list.append(noun_type)
    def meet_prefix_conditions(self, world: worlds.World, obj: objects.Object, prefix_info_list: list[rules.PrefixInfo], is_meta: bool = False) -> bool:
        return_value = True
        for prefix_info in prefix_info_list:
            meet_prefix_condition = True
            if prefix_info.prefix_type == objects.TextMeta:
                meet_prefix_condition = is_meta
            elif prefix_info.prefix_type == objects.TextOften:
                meet_prefix_condition = random.choice((True, True, True, False))
            elif prefix_info.prefix_type == objects.TextSeldom:
                meet_prefix_condition = random.choice((True, False, False, False, False, False))
            return_value = return_value and (meet_prefix_condition if not prefix_info.negated else not meet_prefix_condition)
        return return_value
    def meet_infix_conditions(self, world: worlds.World, obj: objects.Object, infix_info_list: list[rules.InfixInfo], old_feeling: Optional[objects.Properties] = None) -> bool:
        for infix_info in infix_info_list:
            meet_infix_condition = True
            if infix_info.infix_type in (objects.TextOn, objects.TextNear, objects.TextNextto):
                matched_objs: list[objects.Object] = [obj]
                find_range: list[spaces.Coord]
                if infix_info.infix_type == objects.TextOn:
                    find_range = [spaces.Coord(obj.pos.x, obj.pos.y)]
                elif infix_info.infix_type == objects.TextNear:
                    find_range = [spaces.Coord(obj.pos.x - 1, obj.pos.y - 1), spaces.Coord(obj.pos.x, obj.pos.y - 1), spaces.Coord(obj.pos.x + 1, obj.pos.y - 1),
                                  spaces.Coord(obj.pos.x - 1, obj.pos.y), spaces.Coord(obj.pos.x, obj.pos.y), spaces.Coord(obj.pos.x + 1, obj.pos.y),
                                  spaces.Coord(obj.pos.x - 1, obj.pos.y + 1), spaces.Coord(obj.pos.x, obj.pos.y + 1), spaces.Coord(obj.pos.x + 1, obj.pos.y + 1)]
                elif infix_info.infix_type == objects.TextNextto:
                    find_range = [spaces.Coord(obj.pos.x, obj.pos.y - 1), spaces.Coord(obj.pos.x - 1, obj.pos.y), spaces.Coord(obj.pos.x + 1, obj.pos.y), spaces.Coord(obj.pos.x, obj.pos.y + 1)]
                for match_negated, match_type_text in infix_info[2]: # type: ignore
                    match_type_text: type[objects.Noun]
                    match_type = match_type_text.ref_type
                    if match_type == objects.All:
                        if match_negated:
                            match_objs: list[objects.Object] = []
                            for new_match_type in [o for o in self.all_list if issubclass(o, objects.in_not_all)]:
                                for pos in find_range:
                                    match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
                                if len(match_objs) == 0:
                                    meet_infix_condition = False
                                    break
                                matched_objs.append(match_objs[0])
                        else:
                            match_objs: list[objects.Object] = []
                            for new_match_type in [o for o in self.all_list if not issubclass(o, objects.not_in_all)]:
                                for pos in find_range:
                                    match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
                                if len(match_objs) == 0:
                                    meet_infix_condition = False
                                    break
                                matched_objs.append(match_objs[0])
                    else:
                        if match_negated:
                            match_objs: list[objects.Object] = []
                            for new_match_type in [o for o in self.all_list if (not issubclass(o, objects.not_in_all)) and not issubclass(o, match_type)]:
                                for pos in find_range:
                                    match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
                            if len(match_objs) == 0:
                                meet_infix_condition = False
                            else:
                                matched_objs.append(match_objs[0])
                        else:
                            match_objs: list[objects.Object] = []
                            for pos in find_range:
                                match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, match_type) if o not in matched_objs])
                            if len(match_objs) == 0:
                                meet_infix_condition = False
                            else:
                                matched_objs.append(match_objs[0])
                    if not meet_infix_condition:
                        break
            elif infix_info.infix_type == objects.TextFeeling:
                if old_feeling is None:
                    meet_infix_condition = False
                else:
                    for infix_noun_info in infix_info.infix_noun_info_list:
                        if old_feeling.has(infix_noun_info.infix_noun_type) == infix_noun_info.negated:
                            meet_infix_condition = False
            elif infix_info.infix_type == objects.TextWithout:
                meet_infix_condition = True
                matched_objs: list[objects.Object] = [obj]
                match_type_count: dict[tuple[bool, type[objects.Noun]], int] = {}
                for match_negated, match_type_text in infix_info[2]: # type: ignore
                    match_type_text: type[objects.Noun]
                    match_type_count.setdefault((match_negated, match_type_text), 0)
                    match_type_count[(match_negated, match_type_text)] += 1
                for (match_negated, match_type_text), match_count in match_type_count.items():
                    match_type_text: type[objects.Noun]
                    match_type = match_type_text.ref_type
                    if match_type == objects.All:
                        if match_negated:
                            match_objs: list[objects.Object] = []
                            for new_match_type in [o for o in self.all_list if issubclass(o, objects.in_not_all)]:
                                match_objs.extend(world.get_objs_from_type(new_match_type))
                                if len(match_objs) >= match_count:
                                    meet_infix_condition = False
                                    break
                        else:
                            match_objs: list[objects.Object] = []
                            for new_match_type in [o for o in self.all_list if not issubclass(o, objects.not_in_all)]:
                                match_objs.extend(world.get_objs_from_type(new_match_type))
                                if len(match_objs) >= match_count:
                                    meet_infix_condition = False
                                    break
                    else:
                        if match_negated:
                            match_objs: list[objects.Object] = []
                            for new_match_type in [o for o in self.all_list if (not issubclass(o, objects.not_in_all)) and not issubclass(o, match_type)]:
                                match_objs.extend(world.get_objs_from_type(new_match_type))
                            if len(match_objs) >= match_count:
                                meet_infix_condition = False
                        else:
                            match_objs: list[objects.Object] = world.get_objs_from_type(match_type)
                            if len(match_objs) >= match_count:
                                meet_infix_condition = False
                    if not meet_infix_condition:
                        break
            if meet_infix_condition == infix_info.negated:
                return False
        return True
    def recursion_rules(self, world: worlds.World, passed: Optional[list[refs.WorldID]] = None) -> list[rules.Rule]:
        passed = passed if passed is not None else []
        if world.world_id in passed:
            return []
        passed.append(world.world_id)
        rule_list = copy.deepcopy(world.rule_list)
        for super_world in self.world_list:
            for world_obj in super_world.get_worlds():
                if world.world_id == world_obj.world_id:
                    rule_list.extend(self.recursion_rules(super_world, passed))
                    passed.append(super_world.world_id)
        return rule_list
    def update_rules(self, old_prop_dict: dict[uuid.UUID, objects.Properties]) -> None:
        self.game_properties = objects.Properties()
        for level_object_type in objects.level_object_types:
            self.properties[level_object_type] = objects.Properties()
            self.special_operator_properties[level_object_type] = {o: objects.Properties() for o in objects.special_operators}
        for world in self.world_list:
            for object_type in objects.world_object_types:
                world.properties[object_type] = objects.Properties()
                world.special_operator_properties[object_type] = {o: objects.Properties() for o in objects.special_operators}
            for obj in world.object_list:
                obj.properties = objects.Properties()
                obj.special_operator_properties = {o: objects.Properties() for o in objects.special_operators}
        for world in self.world_list:
            world.rule_list = world.get_rules()
        new_prop_list: list[tuple[objects.Object, tuple[type[objects.Text], int]]] = []
        for world in self.world_list:
            for rule in world.rule_list + self.rule_list + self.recursion_rules(world):
                for atom_rule in rules.to_atom_rules(rule):
                    for rule_info in rules.analysis_rule(atom_rule):
                        prefix_info_list = rule_info.prefix_info_list
                        noun_negated_tier = rule_info.noun_negated_tier
                        noun_type = rule_info.noun_type
                        infix_info_list = rule_info.infix_info_list
                        oper_type = rule_info.oper_type
                        prop_negated_tier = rule_info.prop_negated_tier
                        prop_type = rule_info.prop_type
                        if oper_type != objects.TextIs:
                            continue
                        if prop_type != objects.TextWord:
                            continue
                        object_type = noun_type.ref_type
                        if object_type == objects.All:
                            if noun_negated_tier % 2 == 1:
                                for obj in [o for o in world.object_list if isinstance(o, objects.in_not_all)]:
                                    if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                        new_prop_list.append((obj, (objects.TextWord, prop_negated_tier)))
                            else:
                                for obj in [o for o in world.object_list if not isinstance(o, objects.not_in_all)]:
                                    if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                        new_prop_list.append((obj, (objects.TextWord, prop_negated_tier)))
                        else:
                            if noun_negated_tier % 2 == 1:
                                for obj in [o for o in world.object_list if (not isinstance(o, objects.not_in_all)) and not isinstance(o, object_type)]:
                                    if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                        new_prop_list.append((obj, (objects.TextWord, prop_negated_tier)))
                            else:
                                for obj in world.get_objs_from_type(object_type):
                                    if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                        new_prop_list.append((obj, (objects.TextWord, prop_negated_tier)))
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.properties.update(prop_type, prop_negated_count)
        for world in self.world_list:
            for object_type in objects.world_object_types:
                world.properties[object_type] = objects.Properties()
                world.special_operator_properties[object_type] = {o: objects.Properties() for o in objects.special_operators}
            for obj in world.object_list:
                obj.properties = objects.Properties()
                obj.special_operator_properties = {o: objects.Properties() for o in objects.special_operators}
        for world in self.world_list:
            world.rule_list = world.get_rules()
        new_prop_list = []
        for world in self.world_list:
            for rule in world.rule_list + self.rule_list:
                for atom_rule in rules.to_atom_rules(rule):
                    for rule_info in rules.analysis_rule(atom_rule):
                        prefix_info_list = rule_info.prefix_info_list
                        noun_negated_tier = rule_info.noun_negated_tier
                        noun_type = rule_info.noun_type
                        infix_info_list = rule_info.infix_info_list
                        oper_type = rule_info.oper_type
                        prop_negated_tier = rule_info.prop_negated_tier
                        prop_type = rule_info.prop_type
                        object_type = noun_type.ref_type
                        if object_type == objects.All:
                            if noun_negated_tier % 2 == 1:
                                obj_list = [o for o in world.object_list if isinstance(o, objects.in_not_all)]
                            else:
                                obj_list = [o for o in world.object_list if not isinstance(o, objects.not_in_all)]
                            for obj in obj_list:
                                if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                    if oper_type == objects.TextIs:
                                        new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                    else:
                                        obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
                        elif object_type == objects.Game and oper_type == objects.TextIs:
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and self.meet_prefix_conditions(world, objects.Object(spaces.Coord(0, 0)), prefix_info_list, True):
                                self.game_properties.update(prop_type, prop_negated_tier)
                        elif issubclass(object_type, objects.LevelObject):
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and self.meet_prefix_conditions(world, objects.Object(spaces.Coord(0, 0)), prefix_info_list, True):
                                if oper_type == objects.TextIs:
                                    self.properties[object_type].update(prop_type, prop_negated_tier)
                                else:
                                    self.special_operator_properties[object_type][oper_type].update(prop_type, prop_negated_tier)
                        elif issubclass(object_type, objects.WorldObject):
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and self.meet_prefix_conditions(world, objects.Object(spaces.Coord(0, 0)), prefix_info_list, True):
                                if oper_type == objects.TextIs:
                                    world.properties[object_type].update(prop_type, prop_negated_tier)
                                else:
                                    world.special_operator_properties[object_type][oper_type].update(prop_type, prop_negated_tier)
                        if noun_negated_tier % 2 == 1:
                            obj_list = [o for o in world.object_list if (not isinstance(o, objects.not_in_all)) and not isinstance(o, object_type)]
                        else:
                            obj_list = world.get_objs_from_type(object_type)
                        for obj in obj_list:
                            if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                if oper_type == objects.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                else:
                                    obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
            for rule in self.recursion_rules(world):
                for atom_rule in rules.to_atom_rules(rule):
                    for rule_info in rules.analysis_rule(atom_rule):
                        prefix_info_list = rule_info.prefix_info_list
                        noun_negated_tier = rule_info.noun_negated_tier
                        noun_type = rule_info.noun_type
                        infix_info_list = rule_info.infix_info_list
                        oper_type = rule_info.oper_type
                        prop_negated_tier = rule_info.prop_negated_tier
                        prop_type = rule_info.prop_type
                        object_type = noun_type.ref_type
                        if object_type == objects.All:
                            if noun_negated_tier % 2 == 1:
                                obj_list = [o for o in world.object_list if isinstance(o, objects.in_not_all)]
                            else:
                                obj_list = [o for o in world.object_list if not isinstance(o, objects.not_in_all)]
                            for obj in obj_list:
                                if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                    if oper_type == objects.TextIs:
                                        new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                    else:
                                        obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
                        elif object_type == objects.Game and oper_type == objects.TextIs:
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and self.meet_prefix_conditions(world, objects.Object(spaces.Coord(0, 0)), prefix_info_list, True):
                                self.game_properties.update(prop_type, prop_negated_tier)
                        if noun_negated_tier % 2 == 1:
                            obj_list = [o for o in world.object_list if (not isinstance(o, objects.not_in_all)) and not isinstance(o, object_type)]
                        else:
                            obj_list = world.get_objs_from_type(object_type)
                        for obj in obj_list:
                            if self.meet_infix_conditions(world, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_info_list):
                                if oper_type == objects.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                else:
                                    obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.properties.update(prop_type, prop_negated_count)
    def move_obj_between_worlds(self, old_world: worlds.World, obj: objects.Object, new_world: worlds.World, pos: spaces.Coord) -> None:
        if obj in old_world.object_list:
            old_world.del_obj(obj)
        obj = copy.deepcopy(obj)
        obj.reset_uuid()
        obj.old_state.world = old_world.world_id
        obj.old_state.pos = obj.pos
        obj.pos = pos
        new_world.new_obj(obj)
    def move_obj_in_world(self, world: worlds.World, obj: objects.Object, pos: spaces.Coord) -> None:
        if obj in world.object_list:
            world.del_obj(obj)
        obj = copy.deepcopy(obj)
        obj.reset_uuid()
        obj.old_state.pos = obj.pos
        obj.pos = pos
        world.new_obj(obj)
    def destroy_obj(self, world: worlds.World, obj: objects.Object) -> None:
        world.del_obj(obj)
        for new_noun_type, new_noun_count in obj.special_operator_properties[objects.TextHas].enabled_dict().items(): # type: ignore
            new_noun_type: type[objects.Noun]
            new_object_type: type[objects.Object] = new_noun_type.ref_type
            if issubclass(new_object_type, objects.Game):
                if isinstance(obj, (objects.LevelObject, objects.WorldObject)):
                    for _ in range(new_noun_count):
                        world.new_obj(objects.Game(obj.pos, obj.orient, ref_type=objects.get_noun_from_type(type(obj))))
                else:
                    for _ in range(new_noun_count):
                        world.new_obj(objects.Game(obj.pos, obj.orient, ref_type=type(obj)))
            elif issubclass(new_object_type, objects.LevelObject):
                if obj.level_id is not None:
                    for _ in range(new_noun_count):
                        world.new_obj(new_object_type(obj.pos, obj.orient, world_id=obj.world_id, level_id=obj.level_id))
                else:
                    world_id: refs.WorldID = refs.WorldID(obj.uuid.hex)
                    world_color = colors.to_background_color(obj.sprite_color)
                    new_world = worlds.World(world_id, spaces.Coord(3, 3), world_color)
                    obj.pos = spaces.Coord(1, 1)
                    obj.reset_uuid()
                    new_world.new_obj(obj)
                    level_id: refs.LevelID = refs.LevelID(obj.uuid.hex)
                    self.created_levels.append(Level(level_id, [new_world], super_level_id=self.level_id, rule_list=self.rule_list))
                    level_object_extra: objects.LevelObjectExtra = {"icon": {"name": obj.json_name, "color": obj.sprite_color}}
                    for _ in range(new_noun_count):
                        world.new_obj(new_object_type(obj.pos, obj.orient, level_id=level_id, level_object_extra=level_object_extra))
            elif issubclass(new_object_type, objects.WorldObject):
                if obj.world_id is not None:
                    for _ in range(new_noun_count):
                        world.new_obj(new_object_type(obj.pos, obj.orient, world_id=obj.world_id, level_id=obj.level_id))
                else:
                    world_id: refs.WorldID = refs.WorldID(obj.uuid.hex)
                    world_color = colors.to_background_color(obj.sprite_color)
                    new_world = worlds.World(world_id, spaces.Coord(3, 3), world_color)
                    obj.pos = spaces.Coord(1, 1)
                    obj.reset_uuid()
                    new_world.new_obj(obj)
                    self.set_world(new_world)
                    world_object_info: refs.WorldID = refs.WorldID(obj.uuid.hex)
                    for _ in range(new_noun_count):
                        world.new_obj(new_object_type(obj.pos, obj.orient, world_id=world_object_info))
            elif new_noun_type == objects.TextText:
                new_object_type = objects.get_noun_from_type(type(obj))
                for _ in range(new_noun_count):
                    world.new_obj(new_object_type(obj.pos, obj.orient, world_id=obj.world_id, level_id=obj.level_id))
            else:
                new_object_type = new_noun_type.ref_type
                for _ in range(new_noun_count):
                    world.new_obj(new_object_type(obj.pos, obj.orient, world_id=obj.world_id, level_id=obj.level_id))
    def get_move_list(self, world: worlds.World, obj: objects.Object, orient: spaces.Orient, pos: Optional[spaces.Coord] = None, pushed: Optional[list[objects.Object]] = None, passed: Optional[list[refs.WorldID]] = None, transnum: Optional[float] = None, depth: int = 0) -> Optional[list[tuple[objects.Object, worlds.World, spaces.Coord, spaces.Orient]]]:
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
        if world.out_of_range(new_pos) and not obj.properties.disabled(objects.TextLeave):
            exit_world = True
            # infinite exit
            if passed.count(world.world_id) > 3:
                inf_super_world_list = self.find_super_worlds(world.world_id + 1)
                for inf_super_world, world_obj in inf_super_world_list:
                    if inf_super_world.properties[type(world_obj)].disabled(objects.TextLeave):
                        continue
                    new_transnum = inf_super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, orient) if transnum is not None else world.pos_to_transnum(obj.pos, orient)
                    new_move_list = self.get_move_list(inf_super_world, obj, orient, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
                if len(inf_super_world_list) == 0:
                    exit_world = False
            # exit
            else:
                super_world_list = self.find_super_worlds(world.world_id)
                for super_world, world_obj in super_world_list:
                    if super_world.properties[type(world_obj)].disabled(objects.TextLeave):
                        continue
                    new_transnum = super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, orient) if transnum is not None else world.pos_to_transnum(obj.pos, orient)
                    passed.append(world.world_id)
                    new_move_list = self.get_move_list(super_world, obj, orient, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
                if len(super_world_list) == 0:
                    exit_world = False
        # push
        push_objects = [o for o in world.get_objs_from_pos(new_pos) if o.properties.enabled(objects.TextPush)]
        objects_that_cant_push: list[objects.Object] = []
        push = False
        push_list = []
        if len(push_objects) != 0 and not world.out_of_range(new_pos):
            push = True
            for push_object in push_objects:
                pushed.append(obj)
                new_move_list = self.get_move_list(world, push_object, orient, pushed=pushed, depth=depth)
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
            stop_objects = [o for o in world.get_objs_from_pos(new_pos) if o.properties.enabled(objects.TextStop) and not o.properties.enabled(objects.TextPush)]
            stop_objects.extend(objects_that_cant_push)
            if len(stop_objects) != 0:
                if obj.properties.enabled(objects.TextOpen):
                    simple = True
                    for stop_object in stop_objects:
                        if not stop_object.properties.enabled(objects.TextShut):
                            simple = False
                elif obj.properties.enabled(objects.TextShut):
                    simple = True
                    for stop_object in stop_objects:
                        if not stop_object.properties.enabled(objects.TextOpen):
                            simple = False
            else:
                simple = True
        if simple:
            not_stop_list.append((obj, world, new_pos, orient))
        # squeeze
        squeeze = False
        squeeze_list = []
        if isinstance(obj, objects.WorldObject) and obj.properties.enabled(objects.TextPush) and not world.out_of_range(new_pos):
            sub_world = self.get_world(obj.world_id)
            if sub_world is None:
                pass
            elif sub_world.properties[type(obj)].disabled(objects.TextEnter):
                pass
            else:
                new_push_objects = list(filter(lambda o: objects.Properties.enabled(o.properties, objects.TextPush), world.get_objs_from_pos(new_pos)))
                if len(new_push_objects) != 0:
                    squeeze = True
                    temp_stop_object = objects.TextStop(spaces.pos_facing(pos, spaces.swap_orientation(orient)))
                    temp_stop_object.properties.update(objects.TextStop, 0)
                    world.new_obj(temp_stop_object)
                    for new_push_object in new_push_objects:
                        if new_push_object.properties.disabled(objects.TextEnter):
                            squeeze = False
                            break
                        input_pos = sub_world.default_input_position(orient)
                        pushed.append(obj)
                        test_move_list = self.get_move_list(sub_world, new_push_object, spaces.swap_orientation(orient), input_pos, pushed=pushed, depth=depth)
                        pushed.pop()
                        if test_move_list is None:
                            squeeze = False
                            break
                        squeeze_list.extend(test_move_list)
                    if squeeze:
                        squeeze_list.append((obj, world, new_pos, orient))
                    world.del_obj(temp_stop_object)
        enter_world = False
        enter_list = []
        worlds_that_cant_push = [o for o in objects_that_cant_push if isinstance(o, objects.WorldObject)]
        if len(worlds_that_cant_push) != 0 and (not world.out_of_range(new_pos)) and not obj.properties.disabled(objects.TextEnter):
            enter_world = True
            enter_atleast_one_world = False
            for world_obj in worlds_that_cant_push:
                sub_world = self.get_world(world_obj.world_id)
                if sub_world is None:
                    enter_world = False
                    break
                elif sub_world.properties[type(world_obj)].disabled(objects.TextEnter):
                    enter_world = False
                    break
                else:
                    new_move_list = None
                    # infinite enter
                    if passed.count(sub_world.world_id) > 3:
                        inf_sub_world = self.get_world(sub_world.world_id - 1)
                        if inf_sub_world is None:
                            enter_world = False
                            break
                        elif inf_sub_world.properties[type(world_obj)].disabled(objects.TextEnter):
                            enter_world = False
                            break
                        else:
                            new_transnum = 0.5
                            input_pos = inf_sub_world.default_input_position(spaces.swap_orientation(orient))
                            passed.append(world.world_id)
                            new_move_list = self.get_move_list(inf_sub_world, obj, orient, input_pos, pushed, passed, new_transnum, depth)
                    # enter
                    else:
                        new_transnum = world.transnum_to_smaller_transnum(transnum, world_obj.pos, spaces.swap_orientation(orient)) if transnum is not None else 0.5
                        input_pos = sub_world.transnum_to_pos(transnum, spaces.swap_orientation(orient)) if transnum is not None else sub_world.default_input_position(spaces.swap_orientation(orient))
                        passed.append(world.world_id)
                        new_move_list = self.get_move_list(sub_world, obj, orient, input_pos, pushed, passed, new_transnum, depth)
                    if new_move_list is not None:
                        enter_list.extend(new_move_list)
                        enter_atleast_one_world = True
                    else:
                        enter_world = False
                        break
            enter_world &= enter_atleast_one_world
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
    def move_objs_from_move_list(self, move_list: list[tuple[objects.Object, worlds.World, spaces.Coord, spaces.Orient]]) -> None:
        move_list = basics.remove_same_elements(move_list)
        for move_obj, new_world, new_pos, new_orient in move_list:
            move_obj.move_number += 1
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
        pushing_game = False
        finished = False
        for i in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for world in self.world_list:
                you_objs = [o for o in world.object_list if i < o.properties.get(objects.TextYou)]
                if len(you_objs) != 0:
                    finished = False
                for obj in you_objs:
                    obj.orient = orient
                    new_move_list = self.get_move_list(world, obj, obj.orient)
                    if new_move_list is not None:
                        move_list.extend(new_move_list)
                    else:
                        pushing_game = True
            move_list = basics.remove_same_elements(move_list)
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def select(self, orient: spaces.PlayerOperation) -> Optional[refs.LevelID]:
        if orient == spaces.NullOrient.O:
            level_objs: list[objects.LevelObject] = []
            for world in self.world_list:
                select_objs = [o for o in world.object_list if o.properties.enabled(objects.TextSelect)]
                for obj in select_objs:
                    level_objs.extend(world.get_levels_from_pos(obj.pos))
            if len(level_objs) != 0:
                self.sound_events.append("level")
                return random.choice(level_objs).level_id
        else:
            for world in self.world_list:
                select_objs = [o for o in world.object_list if o.properties.enabled(objects.TextSelect)]
                for obj in select_objs:
                    new_pos = spaces.pos_facing(obj.pos, orient)
                    if not world.out_of_range(new_pos):
                        level_objs = world.get_levels_from_pos(new_pos)
                        path_objs = world.get_objs_from_pos_and_type(new_pos, objects.Path)
                        if any(map(lambda p: p.unlocked, path_objs)) or len(level_objs) != 0:
                            self.move_obj_in_world(world, obj, new_pos)
            return None
    def move(self) -> bool:
        pushing_game = False
        for world in self.world_list:
            global_move_count = world.properties[objects.default_world_object_type].get(objects.TextMove) + self.properties[objects.default_level_object_type].get(objects.TextMove)
            for i in range(global_move_count):
                move_list = []
                for obj in world.object_list:
                    if not obj.properties.enabled(objects.TextFloat):
                        new_move_list = self.get_move_list(world, obj, spaces.Orient.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
                move_list = basics.remove_same_elements(move_list)
                self.move_objs_from_move_list(move_list)
        finished = False
        for i in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for world in self.world_list:
                move_objs = [o for o in world.object_list if i < o.properties.get(objects.TextMove)]
                if len(move_objs) != 0:
                    finished = False
                for obj in move_objs:
                    new_move_list = self.get_move_list(world, obj, obj.orient)
                    if new_move_list is not None:
                        move_list = new_move_list
                    else:
                        obj.orient = spaces.swap_orientation(obj.orient)
                        new_move_list = self.get_move_list(world, obj, obj.orient)
                        if new_move_list is not None:
                            move_list = new_move_list
                        else:
                            pushing_game = True
            move_list = basics.remove_same_elements(move_list)
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def shift(self) -> bool:
        pushing_game = False
        for world in self.world_list:
            global_shift_count = world.properties[objects.default_world_object_type].get(objects.TextShift) + self.properties[objects.default_level_object_type].get(objects.TextShift)
            for i in range(global_shift_count):
                move_list = []
                for obj in world.object_list:
                    if not obj.properties.enabled(objects.TextFloat):
                        new_move_list = self.get_move_list(world, obj, spaces.Orient.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
                move_list = basics.remove_same_elements(move_list)
                self.move_objs_from_move_list(move_list)
        finished = False
        for i in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for world in self.world_list:
                shifter_objs = [o for o in world.object_list if i < o.properties.get(objects.TextShift)]
                for shifter_obj in shifter_objs:
                    shifted_objs = [o for o in world.get_objs_from_pos(shifter_obj.pos) if obj != shifter_obj and objects.same_float_prop(obj, shifter_obj)]
                    for obj in shifted_objs:
                        new_move_list = self.get_move_list(world, obj, shifter_obj.orient)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                            finished = False
                        else:
                            pushing_game = True
            move_list = basics.remove_same_elements(move_list)
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def tele(self) -> None:
        if self.properties[objects.default_level_object_type].enabled(objects.TextTele):
            pass
        for world in self.world_list:
            if world.properties[objects.default_world_object_type].enabled(objects.TextTele):
                pass
        tele_list: list[tuple[worlds.World, objects.Object, worlds.World, spaces.Coord]] = []
        object_list: list[tuple[worlds.World, objects.Object]] = []
        for world in self.world_list:
            object_list.extend([(world, o) for o in world.object_list])
        tele_objs = [t for t in object_list if t[1].properties.enabled(objects.TextTele)]
        tele_object_types: dict[type[objects.Object], list[tuple[worlds.World, objects.Object]]] = {}
        for object_type in [n.ref_type for n in objects.noun_class_list]:
            for tele_obj in tele_objs:
                if isinstance(tele_obj[1], object_type):
                    tele_object_types[object_type] = tele_object_types.get(object_type, []) + [tele_obj]
        for new_tele_objs in tele_object_types.values():
            if len(new_tele_objs) <= 1:
                continue
            for tele_world, tele_obj in new_tele_objs:
                other_tele_objs = new_tele_objs[:]
                other_tele_objs.remove((tele_world, tele_obj))
                for obj in world.get_objs_from_pos(tele_obj.pos):
                    if obj == tele_obj:
                        continue
                    if objects.same_float_prop(obj, tele_obj):
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
            sink_objs = [o for o in world.object_list if o.properties.enabled(objects.TextSink)]
            if world.properties[objects.default_world_object_type].has(objects.TextSink) or self.properties[objects.default_level_object_type].enabled(objects.TextSink):
                for obj in world.object_list:
                    if not obj.properties.enabled(objects.TextFloat):
                        delete_list.append(obj)
            for sink_obj in sink_objs:
                for obj in world.get_objs_from_pos(sink_obj.pos):
                    if obj == sink_obj:
                        continue
                    if obj.pos == sink_obj.pos:
                        if objects.same_float_prop(obj, sink_obj):
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
            melt_objs = [o for o in world.object_list if o.properties.enabled(objects.TextMelt)]
            hot_objs = [o for o in world.object_list if o.properties.enabled(objects.TextHot)]
            if len(hot_objs) != 0 and (world.properties[objects.default_world_object_type].has(objects.TextMelt) or self.properties[objects.default_level_object_type].enabled(objects.TextMelt)):
                for melt_obj in melt_objs:
                    if not melt_obj.properties.enabled(objects.TextFloat):
                        delete_list.extend(world.object_list)
                continue
            if len(melt_objs) != 0 and (world.properties[objects.default_world_object_type].has(objects.TextHot) or self.properties[objects.default_level_object_type].enabled(objects.TextHot)):
                for melt_obj in melt_objs:
                    if not melt_obj.properties.enabled(objects.TextFloat):
                        delete_list.append(melt_obj)
                continue
            for hot_obj in hot_objs:
                for melt_obj in melt_objs:
                    if hot_obj.pos == melt_obj.pos:
                        if objects.same_float_prop(hot_obj, melt_obj):
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
            you_objs = [o for o in world.object_list if o.properties.enabled(objects.TextYou)]
            defeat_objs = [o for o in world.object_list if o.properties.enabled(objects.TextDefeat)]
            if len(defeat_objs) != 0 and (world.properties[objects.default_world_object_type].has(objects.TextYou) or self.properties[objects.default_level_object_type].enabled(objects.TextYou)):
                delete_list.extend(world.object_list)
                continue
            for you_obj in you_objs:
                if world.properties[objects.default_world_object_type].has(objects.TextDefeat) or self.properties[objects.default_level_object_type].enabled(objects.TextDefeat):
                    if you_obj not in delete_list:
                        delete_list.append(you_obj)
                        continue
                for defeat_obj in defeat_objs:
                    if you_obj.pos == defeat_obj.pos:
                        if objects.same_float_prop(defeat_obj, you_obj):
                            if you_obj not in delete_list:
                                delete_list.append(you_obj)
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("defeat")
    def bonus(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            bonus_objs = [o for o in world.object_list if o.properties.enabled(objects.TextBonus)]
            you_objs = [o for o in world.object_list if o.properties.enabled(objects.TextYou)]
            if len(you_objs) != 0 and (world.properties[objects.default_world_object_type].has(objects.TextBonus) or self.properties[objects.default_level_object_type].enabled(objects.TextBonus)):
                delete_list.extend(world.object_list)
                continue
            for bonus_obj in bonus_objs:
                if world.properties[objects.default_world_object_type].has(objects.TextYou) or self.properties[objects.default_level_object_type].enabled(objects.TextYou):
                    if bonus_obj not in delete_list:
                        delete_list.append(bonus_obj)
                        continue
                for you_obj in you_objs:
                    if bonus_obj.pos == you_obj.pos:
                        if objects.same_float_prop(you_obj, bonus_obj):
                            if bonus_obj not in delete_list:
                                delete_list.append(bonus_obj)
            for obj in delete_list:
                self.destroy_obj(world, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.collected[collects.Bonus] = True
            self.sound_events.append("bonus")
    def open_and_shut(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            shut_objs = [o for o in world.object_list if o.properties.enabled(objects.TextShut)]
            open_objs = [o for o in world.object_list if o.properties.enabled(objects.TextOpen)]
            if len(open_objs) != 0 and (world.properties[objects.default_world_object_type].has(objects.TextShut) or self.properties[objects.default_level_object_type].enabled(objects.TextShut)):
                delete_list.extend(world.object_list)
                continue
            if len(shut_objs) != 0 and (world.properties[objects.default_world_object_type].has(objects.TextOpen) or self.properties[objects.default_level_object_type].enabled(objects.TextOpen)):
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
                for make_noun_type, make_noun_count in obj.special_operator_properties[objects.TextMake].enabled_dict().items(): # type: ignore
                    make_noun_type: type[objects.Noun]
                    make_object_type: type[objects.Object] = make_noun_type.ref_type
                    if issubclass(make_object_type, objects.Game):
                        if isinstance(obj, (objects.LevelObject, objects.WorldObject)):
                            for _ in range(make_noun_count):
                                world.new_obj(objects.Game(obj.pos, obj.orient, ref_type=objects.get_noun_from_type(type(obj))))
                        else:
                            for _ in range(make_noun_count):
                                world.new_obj(objects.Game(obj.pos, obj.orient, ref_type=type(obj)))
                    elif issubclass(make_object_type, objects.LevelObject):
                        if len(world.get_objs_from_pos_and_type(obj.pos, make_object_type)) != 0:
                            pass
                        elif obj.level_id is not None:
                            for _ in range(make_noun_count):
                                world.new_obj(make_object_type(obj.pos, obj.orient, world_id=obj.world_id, level_id=obj.level_id))
                        else:
                            world_id: refs.WorldID = refs.WorldID(obj.uuid.hex)
                            world_color = colors.to_background_color(obj.sprite_color)
                            new_world = worlds.World(world_id, spaces.Coord(3, 3), world_color)
                            new_obj = copy.deepcopy(obj)
                            new_obj.pos = spaces.Coord(1, 1)
                            new_obj.reset_uuid()
                            new_world.new_obj(new_obj)
                            level_id: refs.LevelID = refs.LevelID(obj.uuid.hex)
                            self.created_levels.append(Level(level_id, [new_world], super_level_id=self.level_id, rule_list=self.rule_list))
                            level_object_extra: objects.LevelObjectExtra = {"icon": {"name": obj.json_name, "color": obj.sprite_color}}
                            for _ in range(make_noun_count):
                                world.new_obj(make_object_type(obj.pos, obj.orient, world_id=obj.world_id, level_id=level_id, level_object_extra=level_object_extra))
                    elif issubclass(make_object_type, objects.WorldObject):
                        if len(world.get_objs_from_pos_and_type(obj.pos, make_object_type)) != 0:
                            pass
                        if obj.world_id is not None:
                            for _ in range(make_noun_count):
                                world.new_obj(make_object_type(obj.pos, obj.orient, world_id=obj.world_id, level_id=obj.level_id))
                        else:
                            world_id: refs.WorldID = refs.WorldID(obj.uuid.hex)
                            world_color = colors.to_background_color(obj.sprite_color)
                            new_world = worlds.World(world_id, spaces.Coord(3, 3), world_color)
                            new_obj = copy.deepcopy(obj)
                            new_obj.pos = spaces.Coord(1, 1)
                            new_obj.reset_uuid()
                            new_world.new_obj(new_obj)
                            self.set_world(new_world)
                            for _ in range(make_noun_count):
                                world.new_obj(make_object_type(obj.pos, obj.orient, world_id=world_id, level_id=obj.level_id))
                    elif make_noun_type == objects.TextText:
                        make_object_type = objects.get_noun_from_type(type(obj))
                        if len(world.get_objs_from_pos_and_type(obj.pos, make_object_type)) != 0:
                            pass
                        for _ in range(make_noun_count):
                            world.new_obj(make_object_type(obj.pos, obj.orient, world_id=obj.world_id, level_id=obj.level_id))
                    else:
                        make_object_type = make_noun_type.ref_type
                        if len(world.get_objs_from_pos_and_type(obj.pos, make_object_type)) != 0:
                            pass
                        for _ in range(make_noun_count):
                            world.new_obj(make_object_type(obj.pos, obj.orient, world_id=obj.world_id, level_id=obj.level_id))
    def text_plus_and_text_minus(self) -> None:
        for world in self.world_list:
            delete_list = []
            text_plus_objs = [o for o in world.object_list if o.properties.enabled(objects.TextTextPlus)]
            text_minus_objs = [o for o in world.object_list if o.properties.enabled(objects.TextTextMinus)]
            for text_plus_obj in text_plus_objs:
                if text_plus_obj in text_minus_objs:
                    continue
                new_type = objects.get_noun_from_type(type(text_plus_obj))
                if new_type != objects.TextText:
                    delete_list.append(text_plus_obj)
                    world.new_obj(new_type(text_plus_obj.pos, text_plus_obj.orient, world_id=text_plus_obj.world_id, level_id=text_plus_obj.level_id))
            for text_minus_obj in text_minus_objs:
                if text_minus_obj in text_plus_objs:
                    continue
                if not isinstance(text_minus_obj, objects.Noun):
                    continue
                new_type = text_minus_obj.ref_type
                if new_type == objects.Text:
                    continue
                delete_list.append(text_minus_obj)
                if issubclass(new_type, objects.Game):
                    world.new_obj(objects.Game(text_minus_obj.pos, text_minus_obj.orient, ref_type=objects.TextGame))
                elif issubclass(new_type, objects.LevelObject):
                    if text_minus_obj.level_id is not None:
                        world.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, world_id=text_minus_obj.world_id, level_id=text_minus_obj.level_id))
                    else:
                        world_id: refs.WorldID = refs.WorldID(text_minus_obj.uuid.hex)
                        world_color = colors.to_background_color(text_minus_obj.sprite_color)
                        new_world = worlds.World(world_id, spaces.Coord(3, 3), world_color)
                        level_id: refs.LevelID = refs.LevelID(text_minus_obj.uuid.hex)
                        self.created_levels.append(Level(level_id, [new_world], super_level_id=self.level_id, rule_list=self.rule_list))
                        new_world.new_obj(type(text_minus_obj)(spaces.Coord(1, 1), text_minus_obj.orient))
                        level_object_extra: objects.LevelObjectExtra = {"icon": {"name": text_minus_obj.json_name, "color": text_minus_obj.sprite_color}}
                        new_obj = new_type(text_minus_obj.pos, text_minus_obj.orient, level_id=level_id, level_object_extra=level_object_extra)
                        world.new_obj(new_obj)
                elif issubclass(new_type, objects.WorldObject):
                    if text_minus_obj.world_id is not None:
                        world.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, world_id=text_minus_obj.world_id, level_id=text_minus_obj.level_id))
                    else:
                        world_id: refs.WorldID = refs.WorldID(text_minus_obj.uuid.hex)
                        world_color = colors.to_background_color(text_minus_obj.sprite_color)
                        new_world = worlds.World(world_id, spaces.Coord(3, 3), world_color)
                        new_world.new_obj(type(text_minus_obj)(spaces.Coord(1, 1), text_minus_obj.orient))
                        self.set_world(new_world)
                        new_obj = new_type(text_minus_obj.pos, text_minus_obj.orient, world_id=world_id)
                        world.new_obj(new_obj)
                else:
                    world.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, world_id=text_minus_obj.world_id, level_id=text_minus_obj.level_id))
            for obj in delete_list:
                self.destroy_obj(world, obj)
    def game(self) -> None:
        for world in self.world_list:
            for game_obj in world.get_objs_from_type(objects.Game):
                if basics.current_os == basics.windows:
                    if os.path.exists("submp.exe"):
                        os.system(f"start submp.exe {game_obj.ref_type.json_name}")
                    elif os.path.exists("submp.py"):
                        os.system(f"start /b python submp.py {game_obj.ref_type.json_name}")
                elif basics.current_os == basics.linux:
                    os.system(f"python ./submp.py {game_obj.ref_type.json_name} &")
    def win(self) -> bool:
        for world in self.world_list:
            you_objs = [o for o in world.object_list if o.properties.enabled(objects.TextYou)]
            win_objs = [o for o in world.object_list if o.properties.enabled(objects.TextWin)]
            for you_obj in you_objs:
                if you_obj in win_objs:
                    self.collected[collects.Spore] = True
                    self.sound_events.append("win")
                    return True
                if world.properties[objects.default_world_object_type].has(objects.TextWin) or self.properties[objects.default_level_object_type].enabled(objects.TextWin):
                    if not you_obj.properties.enabled(objects.TextFloat):
                        self.collected[collects.Spore] = True
                        self.sound_events.append("win")
                        return True
                for win_obj in win_objs:
                    if you_obj.pos == win_obj.pos:
                        if objects.same_float_prop(you_obj, win_obj):
                            self.collected[collects.Spore] = True
                            self.sound_events.append("win")
                            return True
        return False
    def end(self) -> bool:
        for world in self.world_list:
            you_objs = [o for o in world.object_list if o.properties.enabled(objects.TextYou)]
            end_objs = [o for o in world.object_list if o.properties.enabled(objects.TextEnd)]
            for you_obj in you_objs:
                if you_obj in end_objs:
                    self.sound_events.append("end")
                    return True
                if world.properties[objects.default_world_object_type].has(objects.TextEnd) or self.properties[objects.default_level_object_type].enabled(objects.TextEnd):
                    if not you_obj.properties.enabled(objects.TextFloat):
                        self.sound_events.append("end")
                        return True
                for end_obj in end_objs:
                    if you_obj.pos == end_obj.pos:
                        if objects.same_float_prop(you_obj, end_obj):
                            self.sound_events.append("end")
                            return True
        return False
    def done(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            if world.properties[objects.default_world_object_type].has(objects.TextDone) or self.properties[objects.default_level_object_type].enabled(objects.TextDone):
                delete_list.extend(world.object_list)
            for obj in world.object_list:
                if obj.properties.enabled(objects.TextDone):
                    delete_list.append(obj)
            for obj in delete_list:
                world.del_obj(obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("done")
    def have_you(self) -> bool:
        for world in self.world_list:
            for obj in world.object_list:
                if obj.properties.enabled(objects.TextYou):
                    return True
        return False
    def recursion_get_object_surface_info(self, old_pos: spaces.Coord, old_world_id: refs.WorldID, current_world_id: refs.WorldID, depth: int = 0, passed: Optional[list[refs.WorldID]] = None) -> list[tuple[int, tuple[float, float], tuple[float, float]]]:
        current_world = self.get_world(current_world_id)
        if current_world is None:
            return []
        if current_world_id == old_world_id:
            return [(
                depth + 1,
                (old_pos[0] / current_world.width, old_pos[1] / current_world.height),
                (1 / current_world.width, 1 / current_world.height)
            )]
        passed = copy.deepcopy(passed) if passed is not None else []
        new_passed = copy.deepcopy(passed)
        return_list: list[tuple[int, tuple[float, float], tuple[float, float]]] = []
        if current_world_id in passed:
            inf_sub_world = self.get_world(current_world_id - 1)
            if inf_sub_world is None:
                return []
            for world_obj in current_world.get_worlds():
                if current_world_id - 1 != world_obj.world_id:
                    continue
                for new_depth, new_pos, new_size in self.recursion_get_object_surface_info(old_pos, old_world_id, current_world_id - 1, passed=new_passed):
                    return_list.append((
                        new_depth + 1,
                        ((new_pos[0] + world_obj.pos.x) / current_world.width, (new_pos[1] + world_obj.pos.y) / current_world.height),
                        (new_size[0] / current_world.width, new_size[1] / current_world.height)
                    ))
            return return_list
        new_passed.append(copy.deepcopy(current_world_id))
        for world_obj in current_world.get_worlds():
            if world_obj.world_id in passed:
                continue
            sub_world = self.get_world(world_obj.world_id)
            if sub_world is None:
                continue
            for new_depth, new_pos, new_size in self.recursion_get_object_surface_info(old_pos, old_world_id, world_obj.world_id, passed=new_passed):
                return_list.append((
                    new_depth + 1,
                    ((new_pos[0] + world_obj.pos.x) / current_world.width, (new_pos[1] + world_obj.pos.y) / current_world.height),
                    (new_size[0] / current_world.width, new_size[1] / current_world.height)
                ))
        return return_list
    def world_to_surface(self, world: worlds.World, wiggle: int, depth: int = 0, smooth: Optional[float] = None, cursor: Optional[spaces.Coord] = None, debug: bool = False) -> pygame.Surface:
        if depth > basics.options["world_display_recursion_depth"]:
            world_surface = pygame.Surface((displays.pixel_sprite_size, displays.pixel_sprite_size))
            world_surface.fill(world.color)
            return world_surface
        world_surface_size = (world.width * displays.pixel_sprite_size, world.height * displays.pixel_sprite_size)
        world_surface = pygame.Surface(world_surface_size, pygame.SRCALPHA)
        object_list: list[tuple[Optional[refs.WorldID], objects.Object]] = []
        obj_surface_list: list[tuple[spaces.Coord, spaces.Coord, pygame.Surface, objects.Object]] = []
        for other_world in self.world_list:
            for other_object in other_world.object_list:
                if (smooth is not None) and other_object.old_state.world == world.world_id and isinstance(other_object, displays.order):
                    object_list.append((other_world.world_id, other_object))
        object_list.extend([(None, o) for o in world.object_list if isinstance(o, displays.order) and (world.world_id, o) not in object_list])
        for super_world_id, obj in object_list:
            if not isinstance(obj, displays.order):
                continue
            obj_surface: pygame.Surface = displays.simple_object_to_surface(obj, wiggle=wiggle, debug=debug)
            obj_surface_pos: spaces.Coord = spaces.Coord(obj.pos.x * displays.pixel_sprite_size, obj.pos.y * displays.pixel_sprite_size)
            obj_surface_size: spaces.Coord = spaces.Coord(displays.pixel_sprite_size, displays.pixel_sprite_size)
            if isinstance(obj, objects.WorldObject):
                world_of_object = self.get_world(obj.world_id)
                if world_of_object is not None:
                    obj_surface = displays.simple_object_to_surface(obj, wiggle=wiggle, default_surface=self.world_to_surface(world_of_object, wiggle, depth + 1, smooth), debug=debug)
            if isinstance(obj, objects.Cursor):
                obj_surface_pos = spaces.Coord(obj.pos.x * displays.pixel_sprite_size - (obj_surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                                   obj.pos.y * displays.pixel_sprite_size - (obj_surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
                obj_surface_size = spaces.Coord(displays.pixel_size * obj_surface.get_width(), displays.pixel_size * obj_surface.get_height())
            if (smooth is not None) and (obj.old_state.pos is not None):
                if smooth >= 0.0 and smooth <= 1.0:
                    if obj.old_state.world is None:
                        obj_surface_pos = spaces.Coord(
                            int((obj.pos.x + (obj.old_state.pos[0] - obj.pos.x) * smooth) * displays.pixel_sprite_size),
                            int((obj.pos.y + (obj.old_state.pos[1] - obj.pos.y) * smooth) * displays.pixel_sprite_size)
                        )
                        obj_surface_list.append((obj_surface_pos, obj_surface_size, obj_surface, obj))
                    else:
                        new_surface_info = self.recursion_get_object_surface_info(obj.old_state.pos, obj.old_state.world, world.world_id)
                        if len(new_surface_info) != 0:
                            new_surface_info = sorted(new_surface_info, key=lambda t: t[0])
                            min_world_depth = new_surface_info[0][0]
                            for world_depth, old_pos, old_size in new_surface_info:
                                if world_depth > min_world_depth:
                                    break
                                if super_world_id is not None:
                                    old_super_world = self.get_exact_world(super_world_id)
                                    for old_super_world_object in [o for o in world.get_worlds() if o.world_id == super_world_id]:
                                        old_pos = (obj.old_state.pos[0] * displays.pixel_sprite_size, obj.old_state.pos[1] * displays.pixel_sprite_size)
                                        old_size = (displays.pixel_sprite_size, displays.pixel_sprite_size)
                                        new_pos = ((obj.pos.x / old_super_world.width + old_super_world_object.pos.x) * displays.pixel_sprite_size, (obj.pos.y / old_super_world.height + old_super_world_object.pos.y) * displays.pixel_sprite_size)
                                        new_size = (displays.pixel_sprite_size / old_super_world.width, displays.pixel_sprite_size / old_super_world.height)
                                        obj_surface_pos = spaces.Coord(int(new_pos[0] + (old_pos[0] - new_pos[0]) * smooth), int(new_pos[1] + (old_pos[1] - new_pos[1]) * smooth))
                                        obj_surface_size = spaces.Coord(int(new_size[0] + (old_size[0] - new_size[0]) * smooth), int(new_size[1] + (old_size[1] - new_size[1]) * smooth))
                                        obj_surface_list.append((obj_surface_pos, obj_surface_size, obj_surface, obj))
                                else:
                                    old_pos = spaces.Coord(old_pos[0] * world_surface_size[0], old_pos[1] * world_surface_size[1])
                                    old_size = spaces.Coord(old_size[0] * displays.pixel_sprite_size, old_size[1] * displays.pixel_sprite_size)
                                    obj_surface_pos = spaces.Coord(int(obj_surface_pos[0] + (old_pos[0] - obj_surface_pos[0]) * smooth), int(obj_surface_pos[1] + (old_pos[1] - obj_surface_pos[1]) * smooth))
                                    obj_surface_size = spaces.Coord(int(obj_surface_size[0] + (old_size[0] - obj_surface_size[0]) * smooth), int(obj_surface_size[1] + (old_size[1] - obj_surface_size[1]) * smooth))
                                    obj_surface_list.append((obj_surface_pos, obj_surface_size, obj_surface, obj))
                else:
                    raise ValueError(smooth)
            else:
                obj_surface_list.append((obj_surface_pos, obj_surface_size, obj_surface, obj))
        obj_surface_list.sort(key=lambda o: [isinstance(o[-1], t) for t in displays.order].index(True), reverse=True)
        for pos, size, surface, obj in obj_surface_list:
            world_surface.blit(pygame.transform.scale(surface, size), pos)
        if cursor is not None:
            surface = displays.sprites.get("cursor", 0, wiggle, raw=True).copy()
            pos = (cursor[0] * displays.pixel_sprite_size - (surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                   cursor[1] * displays.pixel_sprite_size - (surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
            world_surface.blit(pygame.transform.scale(surface, (displays.pixel_size * surface.get_width(), displays.pixel_size * surface.get_height())), pos)
        world_background = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA)
        world_background.fill(pygame.Color(*colors.hex_to_rgb(world.color)))
        world_background.blit(world_surface, (0, 0))
        world_surface = world_background
        if world.world_id.infinite_tier != 0:
            infinite_text_surface = displays.sprites.get("text_infinite" if world.world_id.infinite_tier > 0 else "text_epsilon", 0, wiggle, raw=True)
            infinite_tier_surface = pygame.Surface((infinite_text_surface.get_width(), infinite_text_surface.get_height() * abs(world.world_id.infinite_tier)), pygame.SRCALPHA)
            infinite_tier_surface.fill("#00000000")
            for i in range(abs(world.world_id.infinite_tier)):
                infinite_tier_surface.blit(infinite_text_surface, (0, i * infinite_text_surface.get_height()))
            infinite_tier_surface = displays.set_alpha(infinite_tier_surface, 0x80)
            if depth == 0:
                infinite_tier_surface = pygame.transform.scale_by(infinite_tier_surface, world.height * displays.pixel_size / abs(world.world_id.infinite_tier))
                world_surface.blit(infinite_tier_surface, ((world_surface.get_width() - infinite_tier_surface.get_width()) // 2, 0))
            else:
                infinite_tier_surface = pygame.transform.scale(infinite_tier_surface, world_surface_size)
                world_surface.blit(infinite_tier_surface, (0, 0))
        return world_surface
    def to_json(self) -> LevelJson:
        json_object: LevelJson = {"id": self.level_id.to_json(), "world_list": [], "main_world": self.main_world_id.to_json()}
        if self.super_level_id is not None:
            json_object["super_level"] = self.super_level_id.to_json()
        if self.map_info is not None:
            json_object["map_info"] = self.map_info
        for world in self.world_list:
            json_object["world_list"].append(world.to_json())
        return json_object

def json_to_level(json_object: LevelJson, ver: Optional[str] = None) -> Level:
    world_list = []
    super_level_id: Optional[refs.LevelID] = None
    if basics.compare_versions(ver if ver is not None else "0.0", "3.8") == -1:
        level_id: refs.LevelID = refs.LevelID(json_object["name"]) # type: ignore
        super_level_id = refs.LevelID(json_object["super_level"]) # type: ignore
        main_world_id: refs.WorldID = refs.WorldID(json_object["main_world"]) # type: ignore
    else:
        level_id: refs.LevelID = refs.LevelID(**json_object["id"])
        super_level_json = json_object.get("super_level")
        if super_level_json is not None:
            super_level_id = refs.LevelID(**super_level_json)
        main_world_id: refs.WorldID = refs.WorldID(**json_object["main_world"])
    for world in json_object["world_list"]:
        world_list.append(worlds.json_to_world(world, ver))
    return Level(level_id=level_id,
                 world_list=world_list,
                 super_level_id=super_level_id,
                 main_world_id=main_world_id,
                 map_info=json_object.get("map_info"))