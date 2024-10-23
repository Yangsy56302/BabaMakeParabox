from typing import Any, NotRequired, Optional, TypedDict
import random
import copy
import uuid

from BabaMakeParabox import basics, colors, spaces, objects, rules, worlds, displays

import pygame

class LevelMainWorldJson(TypedDict):
    name: str
    infinite_tier: int

class LevelJson(TypedDict):
    name: str
    super_level: Optional[str]
    is_map: NotRequired[bool]
    main_world: LevelMainWorldJson
    world_list: list[worlds.WorldJson]

class Level(object):
    def __init__(self, name: str, world_list: list[worlds.World], *, super_level: Optional[str] = None, main_world_name: Optional[str] = None, main_world_tier: Optional[int] = None, is_map: bool = False, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name
        self.world_list: list[worlds.World] = list(world_list)
        self.super_level: Optional[str] = super_level
        self.main_world_name: str = main_world_name if main_world_name is not None else world_list[0].name
        self.main_world_tier: int = main_world_tier if main_world_tier is not None else world_list[0].infinite_tier
        self.rule_list: list[rules.Rule] = rule_list if rule_list is not None else rules.default_rule_list
        self.is_map: bool = is_map
        self.game_properties: rules.PropertyDict = {}
        self.new_games: list[type[objects.BmpObject]] = []
        self.properties: rules.PropertyDict = {}
        self.write_text: list[type[objects.Noun] | type[objects.Property]] = []
        self.created_levels: list["Level"] = []
        self.all_list: list[type[objects.Noun]] = []
        self.sound_events: list[str] = []
    def __eq__(self, level: "Level") -> bool:
        return self.name == level.name
    def new_prop(self, prop: type[objects.Text], negated_count: int = 0) -> None:
        if self.properties.get(prop, -1) < negated_count:
            self.properties[prop] = negated_count
    def del_prop(self, prop: type[objects.Text], negated_count: Optional[int] = 0) -> None:
        if self.properties.get(prop) == negated_count or negated_count is None:
            self.properties.pop(prop)
    def has_prop(self, prop: type[objects.Text], negated: bool = False) -> bool:
        negated_count = self.properties.get(prop)
        return negated_count is not None and negated_count % 2 == int(negated)
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
    def get_world(self, world_info: objects.WorldPointerExtraJson) -> Optional[worlds.World]:
        world = list(filter(lambda l: l.name == world_info["name"] and l.infinite_tier == world_info["infinite_tier"], self.world_list))
        return world[0] if len(world) != 0 else None
    def get_exist_world(self, world_info: objects.WorldPointerExtraJson) -> worlds.World:
        world = list(filter(lambda l: l.name == world_info["name"] and l.infinite_tier == world_info["infinite_tier"], self.world_list))
        return world[0]
    def set_world(self, world: worlds.World) -> None:
        for i in range(len(self.world_list)):
            if world.name == self.world_list[i].name:
                self.world_list[i] = world
                return
        self.world_list.append(world)
    def find_super_worlds(self, world_info: objects.WorldPointerExtraJson) -> list[tuple[worlds.World, objects.World]]:
        return_value: list[tuple[worlds.World, objects.World]] = []
        for super_world in self.world_list:
            for obj in super_world.get_worlds():
                if world_info == obj.world_info:
                    return_value.append((super_world, obj))
        return return_value
    def all_list_set(self) -> None:
        for world in self.world_list:
            for obj in world.object_list:
                noun_type = objects.get_noun_from_obj(type(obj))
                in_not_in_all = False
                for not_all in objects.not_in_all:
                    if isinstance(obj, not_all):
                        in_not_in_all = True
                if noun_type not in self.all_list and not in_not_in_all:
                    self.all_list.append(noun_type)
    def meet_prefix_conditions(self, world: worlds.World, obj: objects.BmpObject, prefix_info_list: list[rules.PrefixInfo], is_meta: bool = False) -> bool:
        return_value = True
        for prefix_info in prefix_info_list:
            meet_prefix_condition = True
            if prefix_info[1] == objects.TextMeta:
                meet_prefix_condition = is_meta
            elif prefix_info[1] == objects.TextOften:
                meet_prefix_condition = random.choice((True, True, True, False))
            elif prefix_info[1] == objects.TextSeldom:
                meet_prefix_condition = random.choice((True, False, False, False, False, False))
            return_value = return_value and (meet_prefix_condition if not prefix_info[0] else not meet_prefix_condition)
        return return_value
    def meet_infix_conditions(self, world: worlds.World, obj: objects.BmpObject, infix_info_list: list[rules.InfixInfo], old_feeling: Optional[list[tuple[type[objects.Text], int]]] = None) -> bool:
        for infix_info in infix_info_list:
            meet_infix_condition = True
            if infix_info[1] in (objects.TextOn, objects.TextNear, objects.TextNextto):
                matched_objs: list[objects.BmpObject] = [obj]
                if infix_info[1] == objects.TextOn:
                    find_range = [(obj.x, obj.y)]
                elif infix_info[1] == objects.TextNear:
                    find_range = [(obj.x - 1, obj.y - 1), (obj.x, obj.y - 1), (obj.x + 1, obj.y - 1),
                                  (obj.x - 1, obj.y), (obj.x, obj.y), (obj.x + 1, obj.y),
                                  (obj.x - 1, obj.y + 1), (obj.x, obj.y + 1), (obj.x + 1, obj.y + 1)]
                elif infix_info[1] == objects.TextNextto:
                    find_range = [(obj.x, obj.y - 1), (obj.x - 1, obj.y), (obj.x + 1, obj.y), (obj.x, obj.y + 1)]
                for match_negated, match_type_text in infix_info[2]: # type: ignore
                    match_type_text: type[objects.Noun]
                    match_type = match_type_text.obj_type
                    if match_type == objects.All:
                        if match_negated:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if issubclass(o, objects.in_not_all)]:
                                for pos in find_range:
                                    match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
                                if len(match_objs) == 0:
                                    meet_infix_condition = False
                                    break
                                matched_objs.append(match_objs[0])
                        else:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if not issubclass(o, objects.not_in_all)]:
                                for pos in find_range:
                                    match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
                                if len(match_objs) == 0:
                                    meet_infix_condition = False
                                    break
                                matched_objs.append(match_objs[0])
                    else:
                        if match_negated:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if (not issubclass(o, objects.not_in_all)) and not issubclass(o, match_type)]:
                                for pos in find_range:
                                    match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
                            if len(match_objs) == 0:
                                meet_infix_condition = False
                            else:
                                matched_objs.append(match_objs[0])
                        else:
                            match_objs: list[objects.BmpObject] = []
                            for pos in find_range:
                                match_objs.extend([o for o in world.get_objs_from_pos_and_type(pos, match_type) if o not in matched_objs])
                            if len(match_objs) == 0:
                                meet_infix_condition = False
                            else:
                                matched_objs.append(match_objs[0])
                    if not meet_infix_condition:
                        break
            elif infix_info[1] == objects.TextFeeling:
                if old_feeling is None:
                    meet_infix_condition = False
                else:
                    for match_negated, match_prop in infix_info[2]:
                        if match_prop not in [t[0] for t in old_feeling if t[1] % 2 == int(match_negated)]:
                            meet_infix_condition = False
            elif infix_info[1] == objects.TextWithout:
                meet_infix_condition = True
                matched_objs: list[objects.BmpObject] = [obj]
                match_type_count: dict[tuple[bool, type[objects.Noun]], int] = {}
                for match_negated, match_type_text in infix_info[2]: # type: ignore
                    match_type_text: type[objects.Noun]
                    match_type_count.setdefault((match_negated, match_type_text), 0)
                    match_type_count[(match_negated, match_type_text)] += 1
                for (match_negated, match_type_text), match_count in match_type_count.items():
                    match_type_text: type[objects.Noun]
                    match_type = match_type_text.obj_type
                    if match_type == objects.All:
                        if match_negated:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if issubclass(o, objects.in_not_all)]:
                                match_objs.extend(world.get_objs_from_type(new_match_type))
                                if len(match_objs) >= match_count:
                                    meet_infix_condition = False
                                    break
                        else:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if not issubclass(o, objects.not_in_all)]:
                                match_objs.extend(world.get_objs_from_type(new_match_type))
                                if len(match_objs) >= match_count:
                                    meet_infix_condition = False
                                    break
                    else:
                        if match_negated:
                            match_objs: list[objects.BmpObject] = []
                            for new_match_type in [o for o in self.all_list if (not issubclass(o, objects.not_in_all)) and not issubclass(o, match_type)]:
                                match_objs.extend(world.get_objs_from_type(new_match_type))
                            if len(match_objs) >= match_count:
                                meet_infix_condition = False
                        else:
                            match_objs: list[objects.BmpObject] = world.get_objs_from_type(match_type)
                            if len(match_objs) >= match_count:
                                meet_infix_condition = False
                    if not meet_infix_condition:
                        break
            if meet_infix_condition == infix_info[0]:
                return False
        return True
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
            sub_world = self.get_exist_world(sub_world_obj.world_info)
            self.recursion_rules(sub_world, rule_list, passed)
    def update_rules(self, old_prop_dict: dict[uuid.UUID, list[tuple[type[objects.Text], int]]]) -> None:
        self.game_properties = {}
        self.properties = {}
        self.write_text = []
        for world in self.world_list:
            world.world_properties = {}
            world.clone_properties = {}
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
                    if oper_type != objects.TextIs:
                        continue
                    if prop_type != objects.TextWord:
                        continue
                    obj_type = noun_type.obj_type
                    if obj_type == objects.All:
                        if noun_negated:
                            for obj in [o for o in world.object_list if isinstance(o, objects.in_not_all)]:
                                if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                    new_prop_list.append((obj, (objects.TextWord, prop_negated_count)))
                        else:
                            for obj in [o for o in world.object_list if not isinstance(o, objects.not_in_all)]:
                                if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                    new_prop_list.append((obj, (objects.TextWord, prop_negated_count)))
                    else:
                        if noun_negated:
                            for obj in [o for o in world.object_list if (not isinstance(o, objects.not_in_all)) and not isinstance(o, obj_type)]:
                                if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                    new_prop_list.append((obj, (objects.TextWord, prop_negated_count)))
                        else:
                            for obj in world.get_objs_from_type(obj_type):
                                if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                    new_prop_list.append((obj, (objects.TextWord, prop_negated_count)))
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.new_prop(prop_type, prop_negated_count)
        for world in self.world_list:
            world.world_properties = {}
            world.clone_properties = {}
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
                    obj_type = noun_type.obj_type
                    if obj_type == objects.All:
                        if noun_negated:
                            for obj in [o for o in world.object_list if isinstance(o, objects.in_not_all)]:
                                if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                    if oper_type == objects.TextIs:
                                        new_prop_list.append((obj, (prop_type, prop_negated_count)))
                                    elif oper_type == objects.TextHas:
                                        if prop_type == objects.TextAll and noun_negated == False:
                                            obj.has_object.extend(self.all_list)
                                        else:
                                            obj.has_object.append(prop_type) # type: ignore
                                    elif oper_type == objects.TextMake:
                                        if prop_type == objects.TextAll and noun_negated == False:
                                            obj.make_object.extend(self.all_list)
                                        else:
                                            obj.make_object.append(prop_type) # type: ignore
                                    elif oper_type == objects.TextWrite:
                                        obj.write_text.append(prop_type)
                        else:
                            for obj in [o for o in world.object_list if not isinstance(o, objects.not_in_all)]:
                                if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                    if oper_type == objects.TextIs:
                                        new_prop_list.append((obj, (prop_type, prop_negated_count)))
                                    elif oper_type == objects.TextHas and prop_negated_count % 2 == 0:
                                        if prop_type == objects.TextAll and noun_negated == False:
                                            obj.has_object.extend(self.all_list)
                                        else:
                                            obj.has_object.append(prop_type) # type: ignore
                                    elif oper_type == objects.TextMake and prop_negated_count % 2 == 0:
                                        if prop_type == objects.TextAll and noun_negated == False:
                                            obj.make_object.extend(self.all_list)
                                        else:
                                            obj.make_object.append(prop_type) # type: ignore
                                    elif oper_type == objects.TextWrite and prop_negated_count % 2 == 0:
                                        obj.write_text.append(prop_type)
                    elif obj_type == objects.Game and oper_type == objects.TextIs:
                        if (not noun_negated) and len(infix_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_list, True):
                            if self.game_properties.get(prop_type, -1) < prop_negated_count:
                                self.game_properties[prop_type] = prop_negated_count
                    elif obj_type == objects.Level:
                        if (not noun_negated) and len(infix_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_list, True):
                            if oper_type == objects.TextIs:
                                self.new_prop(prop_type, prop_negated_count)
                            elif oper_type == objects.TextWrite and prop_negated_count % 2 == 0:
                                self.write_text.append(prop_type)
                    elif obj_type == objects.World:
                        if (not noun_negated) and len(infix_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_list, True):
                            if oper_type == objects.TextIs:
                                world.new_world_prop(prop_type, prop_negated_count)
                            elif oper_type == objects.TextWrite and prop_negated_count % 2 == 0:
                                world.world_write_text.append(prop_type)
                    elif obj_type == objects.Clone:
                        if (not noun_negated) and len(infix_list) == 0 and self.meet_prefix_conditions(world, objects.BmpObject((0, 0)), prefix_list, True):
                            if oper_type == objects.TextIs:
                                world.new_clone_prop(prop_type, prop_negated_count)
                            elif oper_type == objects.TextWrite and prop_negated_count % 2 == 0:
                                world.clone_write_text.append(prop_type)
                    if noun_negated:
                        for obj in [o for o in world.object_list if (not isinstance(o, objects.not_in_all)) and not isinstance(o, obj_type)]:
                            if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                if oper_type == objects.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_count)))
                                elif oper_type == objects.TextHas and prop_negated_count % 2 == 0:
                                    if prop_type == objects.TextAll and noun_negated == False:
                                        obj.has_object.extend(self.all_list)
                                    else:
                                        obj.has_object.append(prop_type) # type: ignore
                                elif oper_type == objects.TextMake and prop_negated_count % 2 == 0:
                                    if prop_type == objects.TextAll and noun_negated == False:
                                        obj.make_object.extend(self.all_list)
                                    else:
                                        obj.make_object.append(prop_type) # type: ignore
                                elif oper_type == objects.TextWrite and prop_negated_count % 2 == 0:
                                    obj.write_text.append(prop_type)
                    else:
                        for obj in world.get_objs_from_type(obj_type):
                            if self.meet_infix_conditions(world, obj, infix_list, old_prop_dict.get(obj.uuid)) and self.meet_prefix_conditions(world, obj, prefix_list):
                                if oper_type == objects.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_count)))
                                elif oper_type == objects.TextHas and prop_negated_count % 2 == 0:
                                    if prop_type == objects.TextAll and noun_negated == False:
                                        obj.has_object.extend(self.all_list)
                                    else:
                                        obj.has_object.append(prop_type) # type: ignore
                                elif oper_type == objects.TextMake and prop_negated_count % 2 == 0:
                                    if prop_type == objects.TextAll and noun_negated == False:
                                        obj.make_object.extend(self.all_list)
                                    else:
                                        obj.make_object.append(prop_type) # type: ignore
                                elif oper_type == objects.TextWrite and prop_negated_count % 2 == 0:
                                    obj.write_text.append(prop_type)
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.new_prop(prop_type, prop_negated_count)
    def move_obj_between_worlds(self, old_world: worlds.World, obj: objects.BmpObject, new_world: worlds.World, pos: spaces.Coord) -> None:
        if obj in old_world.object_list:
            old_world.del_obj(obj)
        obj = copy.deepcopy(obj)
        obj.reset_uuid()
        obj.pos = pos
        new_world.new_obj(obj)
    def move_obj_in_world(self, world: worlds.World, obj: objects.BmpObject, pos: spaces.Coord) -> None:
        if obj in world.object_list:
            world.del_obj(obj)
        obj = copy.deepcopy(obj)
        obj.reset_uuid()
        obj.pos = pos
        world.new_obj(obj)
    def destroy_obj(self, world: worlds.World, obj: objects.BmpObject) -> None:
        world.del_obj(obj)
        for new_noun_type in obj.has_object:
            if new_noun_type == objects.TextGame:
                pass
            elif new_noun_type == objects.TextLevel:
                if obj.level_info is not None:
                    world.new_obj(objects.Level(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                else:
                    world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                    new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                    obj.pos = (1, 1)
                    obj.reset_uuid()
                    new_world.new_obj(obj)
                    self.created_levels.append(Level(obj.uuid.hex, [new_world], super_level=self.name, rule_list=self.rule_list))
                    level_info: objects.LevelPointerExtraJson = {"name": obj.uuid.hex, "icon": {"name": obj.sprite_name, "color": displays.sprite_colors[obj.sprite_name]}}
                    world.new_obj(objects.Level(obj.pos, obj.orient, level_info=level_info))
            elif new_noun_type == objects.TextWorld:
                if obj.world_info is not None:
                    world.new_obj(objects.World(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                else:
                    world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                    new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                    obj.pos = (1, 1)
                    obj.reset_uuid()
                    new_world.new_obj(obj)
                    self.set_world(new_world)
                    world_info: objects.WorldPointerExtraJson = {"name": obj.uuid.hex, "infinite_tier": 0}
                    world.new_obj(objects.World(obj.pos, obj.orient, world_info=world_info))
            elif new_noun_type == objects.TextClone:
                if obj.world_info is not None:
                    world.new_obj(objects.Clone(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                else:
                    world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                    new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                    obj.pos = (1, 1)
                    obj.reset_uuid()
                    new_world.new_obj(obj)
                    self.set_world(new_world)
                    world_info: objects.WorldPointerExtraJson = {"name": obj.uuid.hex, "infinite_tier": 0}
                    world.new_obj(objects.Clone(obj.pos, obj.orient, world_info=world_info))
            elif new_noun_type == objects.TextText:
                new_obj_type = objects.get_noun_from_obj(type(obj))
                world.new_obj(new_obj_type(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
            else:
                new_obj_type = new_noun_type.obj_type
                world.new_obj(new_obj_type(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
    def get_move_list(self, world: worlds.World, obj: objects.BmpObject, orient: spaces.Orient, pos: Optional[spaces.Coord] = None, pushed: Optional[list[objects.BmpObject]] = None, passed: Optional[list[worlds.World]] = None, transnum: Optional[float] = None, depth: int = 0) -> Optional[list[tuple[objects.BmpObject, worlds.World, spaces.Coord, spaces.Orient]]]:
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
        if world.out_of_range(new_pos) and not obj.has_prop(objects.TextLeave, negate=True):
            exit_world = True
            # infinite exit
            if world in passed:
                super_world_list = self.find_super_worlds({"name": world.name, "infinite_tier": world.infinite_tier + 1})
                for super_world, world_obj in super_world_list:
                    if isinstance(world_obj, objects.World) and not super_world.has_world_prop(objects.TextLeave):
                        continue
                    if isinstance(world_obj, objects.Clone) and not super_world.has_clone_prop(objects.TextLeave):
                        continue
                    new_transnum = super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, orient) if transnum is not None else world.pos_to_transnum(obj.pos, orient)
                    new_move_list = self.get_move_list(super_world, obj, orient, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
                if len(super_world_list) == 0:
                    exit_world = False
            # exit
            else:
                inf_super_world_list = self.find_super_worlds({"name": world.name, "infinite_tier": world.infinite_tier})
                for inf_super_world, world_obj in inf_super_world_list:
                    if isinstance(world_obj, objects.World) and not inf_super_world.has_world_prop(objects.TextLeave):
                        continue
                    if isinstance(world_obj, objects.Clone) and not inf_super_world.has_clone_prop(objects.TextLeave):
                        continue
                    new_transnum = inf_super_world.transnum_to_bigger_transnum(transnum, world_obj.pos, orient) if transnum is not None else world.pos_to_transnum(obj.pos, orient)
                    passed.append(world)
                    new_move_list = self.get_move_list(inf_super_world, obj, orient, world_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is None:
                        exit_world = False
                    else:
                        exit_list.extend(new_move_list)
                if len(inf_super_world_list) == 0:
                    exit_world = False
        # push
        push_objects = [o for o in world.get_objs_from_pos(new_pos) if o.has_prop(objects.TextPush)]
        objects_that_cant_push: list[objects.BmpObject] = []
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
            stop_objects = [o for o in world.get_objs_from_pos(new_pos) if o.has_prop(objects.TextStop) and not o.has_prop(objects.TextPush)]
            stop_objects.extend(objects_that_cant_push)
            if len(stop_objects) != 0:
                if obj.has_prop(objects.TextOpen):
                    simple = True
                    for stop_object in stop_objects:
                        if not stop_object.has_prop(objects.TextShut):
                            simple = False
                elif obj.has_prop(objects.TextShut):
                    simple = True
                    for stop_object in stop_objects:
                        if not stop_object.has_prop(objects.TextOpen):
                            simple = False
            else:
                simple = True
        if simple:
            not_stop_list.append((obj, world, new_pos, orient))
        # squeeze
        squeeze = False
        squeeze_list = []
        if isinstance(obj, objects.WorldPointer) and obj.has_prop(objects.TextPush) and not world.out_of_range(new_pos):
            sub_world = self.get_world(obj.world_info)
            if sub_world is None:
                pass
            elif isinstance(obj, objects.World) and not sub_world.has_world_prop(objects.TextEnter):
                pass
            elif isinstance(obj, objects.Clone) and not sub_world.has_clone_prop(objects.TextEnter):
                pass
            else:
                new_push_objects = list(filter(lambda o: objects.BmpObject.has_prop(o, objects.TextPush), world.get_objs_from_pos(new_pos)))
                if len(new_push_objects) != 0:
                    squeeze = True
                    temp_stop_object = objects.TextStop(spaces.pos_facing(pos, spaces.swap_orientation(orient)))
                    temp_stop_object.new_prop(objects.TextStop)
                    world.new_obj(temp_stop_object)
                    for new_push_object in new_push_objects:
                        if new_push_object.has_prop(objects.TextEnter, negate=True):
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
        worlds_that_cant_push = [o for o in objects_that_cant_push if isinstance(o, objects.WorldPointer)]
        if len(worlds_that_cant_push) != 0 and (not world.out_of_range(new_pos)) and not obj.has_prop(objects.TextEnter, negate=True):
            enter_world = True
            enter_atleast_one_world = False
            for world_obj in worlds_that_cant_push:
                sub_world = self.get_world(world_obj.world_info)
                if sub_world is None:
                    enter_world = False
                    break
                elif isinstance(world_obj, objects.World) and not sub_world.has_world_prop(objects.TextEnter):
                    pass
                elif isinstance(world_obj, objects.Clone) and not sub_world.has_clone_prop(objects.TextEnter):
                    pass
                else:
                    new_move_list = None
                    # infinite enter
                    if sub_world in passed:
                        inf_sub_world = self.get_world({"name": sub_world.name, "infinite_tier": sub_world.infinite_tier - 1})
                        if inf_sub_world is None:
                            enter_world = False
                            break
                        elif isinstance(world_obj, objects.World) and not inf_sub_world.has_world_prop(objects.TextEnter):
                            pass
                        elif isinstance(world_obj, objects.Clone) and not inf_sub_world.has_clone_prop(objects.TextEnter):
                            pass
                        else:
                            new_transnum = 0.5
                            input_pos = inf_sub_world.default_input_position(spaces.swap_orientation(orient))
                            passed.append(world)
                            new_move_list = self.get_move_list(inf_sub_world, obj, orient, input_pos, pushed, passed, new_transnum, depth)
                    # enter
                    else:
                        new_transnum = world.transnum_to_smaller_transnum(transnum, world_obj.pos, spaces.swap_orientation(orient)) if transnum is not None else 0.5
                        input_pos = sub_world.transnum_to_pos(transnum, spaces.swap_orientation(orient)) if transnum is not None else sub_world.default_input_position(spaces.swap_orientation(orient))
                        passed.append(world)
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
            you_objs = [o for o in world.object_list if o.has_prop(objects.TextYou)]
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
    def select(self, orient: spaces.PlayerOperation) -> Optional[str]:
        if orient == spaces.NullOrient.O:
            level_objs: list[objects.LevelPointer] = []
            for world in self.world_list:
                select_objs = [o for o in world.object_list if o.has_prop(objects.TextSelect)]
                for obj in select_objs:
                    level_objs.extend(world.get_levels_from_pos(obj.pos))
            if len(level_objs) != 0:
                self.sound_events.append("level")
                return random.choice(level_objs).level_info["name"]
        else:
            for world in self.world_list:
                select_objs = [o for o in world.object_list if o.has_prop(objects.TextSelect)]
                for obj in select_objs:
                    new_pos = spaces.pos_facing(obj.pos, orient)
                    if not world.out_of_range(new_pos):
                        self.move_obj_in_world(world, obj, new_pos)
            return None
    def move(self) -> bool:
        pushing_game = False
        for world in self.world_list:
            if world.has_world_prop(objects.TextMove) or self.has_prop(objects.TextMove):
                for obj in world.object_list:
                    if not obj.has_prop(objects.TextFloat):
                        new_move_list = self.get_move_list(world, obj, spaces.Orient.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
                continue
            move_objs = [o for o in world.object_list if o.has_prop(objects.TextMove)]
            for obj in move_objs:
                move_list = []
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
        move_list = []
        pushing_game = False
        for world in self.world_list:
            if world.has_world_prop(objects.TextShift) or self.has_prop(objects.TextShift):
                for obj in world.object_list:
                    if not obj.has_prop(objects.TextFloat):
                        new_move_list = self.get_move_list(world, obj, spaces.Orient.D)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
                continue
            shift_objs = [o for o in world.object_list if o.has_prop(objects.TextShift)]
            for shift_obj in shift_objs:
                for obj in world.get_objs_from_pos(shift_obj.pos):
                    if obj == shift_obj:
                        continue
                    if objects.same_float_prop(obj, shift_obj):
                        new_move_list = self.get_move_list(world, obj, shift_obj.orient)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            pushing_game = True
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
        return pushing_game
    def tele(self) -> None:
        if self.has_prop(objects.TextTele):
            pass
        for world in self.world_list:
            if world.has_world_prop(objects.TextTele):
                pass
        tele_list: list[tuple[worlds.World, objects.BmpObject, worlds.World, spaces.Coord]] = []
        object_list: list[tuple[worlds.World, objects.BmpObject]] = []
        for world in self.world_list:
            object_list.extend([(world, o) for o in world.object_list])
        tele_objs = [t for t in object_list if t[1].has_prop(objects.TextTele)]
        tele_obj_types: dict[type[objects.BmpObject], list[tuple[worlds.World, objects.BmpObject]]] = {}
        for obj_type in [n.obj_type for n in objects.noun_class_list]:
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
            sink_objs = [o for o in world.object_list if o.has_prop(objects.TextSink)]
            if world.has_world_prop(objects.TextSink) or self.has_prop(objects.TextSink):
                for obj in world.object_list:
                    if not obj.has_prop(objects.TextFloat):
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
            melt_objs = [o for o in world.object_list if o.has_prop(objects.TextMelt)]
            hot_objs = [o for o in world.object_list if o.has_prop(objects.TextHot)]
            if len(hot_objs) != 0 and (world.has_world_prop(objects.TextMelt) or self.has_prop(objects.TextMelt)):
                for melt_obj in melt_objs:
                    if not melt_obj.has_prop(objects.TextFloat):
                        delete_list.extend(world.object_list)
                continue
            if len(melt_objs) != 0 and (world.has_world_prop(objects.TextHot) or self.has_prop(objects.TextHot)):
                for melt_obj in melt_objs:
                    if not melt_obj.has_prop(objects.TextFloat):
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
            you_objs = [o for o in world.object_list if o.has_prop(objects.TextYou)]
            defeat_objs = [o for o in world.object_list if o.has_prop(objects.TextDefeat)]
            if len(defeat_objs) != 0 and (world.has_world_prop(objects.TextYou) or self.has_prop(objects.TextYou)):
                delete_list.extend(world.object_list)
                continue
            for you_obj in you_objs:
                if world.has_world_prop(objects.TextDefeat) or self.has_prop(objects.TextDefeat):
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
    def open_and_shut(self) -> None:
        success = False
        for world in self.world_list:
            delete_list = []
            shut_objs = [o for o in world.object_list if o.has_prop(objects.TextShut)]
            open_objs = [o for o in world.object_list if o.has_prop(objects.TextOpen)]
            if len(open_objs) != 0 and (world.has_world_prop(objects.TextShut) or self.has_prop(objects.TextShut)):
                delete_list.extend(world.object_list)
                continue
            if len(shut_objs) != 0 and (world.has_world_prop(objects.TextOpen) or self.has_prop(objects.TextOpen)):
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
                    if make_noun_type == objects.TextGame:
                        pass
                    elif make_noun_type == objects.TextLevel:
                        if obj.level_info is not None:
                            world.new_obj(objects.Level(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                        else:
                            world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                            new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                            new_obj = copy.deepcopy(obj)
                            new_obj.pos = (1, 1)
                            new_obj.reset_uuid()
                            new_world.new_obj(new_obj)
                            self.created_levels.append(Level(obj.uuid.hex, [new_world], super_level=self.name, rule_list=self.rule_list))
                            level_info: objects.LevelPointerExtraJson = {"name": obj.uuid.hex, "icon": {"name": obj.sprite_name, "color": displays.sprite_colors[obj.sprite_name]}}
                            world.new_obj(objects.Level(obj.pos, obj.orient, world_info=obj.world_info, level_info=level_info))
                    elif make_noun_type == objects.TextWorld:
                        if obj.world_info is not None:
                            world.new_obj(objects.World(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                        else:
                            world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                            new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                            new_obj = copy.deepcopy(obj)
                            new_obj.pos = (1, 1)
                            new_obj.reset_uuid()
                            new_world.new_obj(new_obj)
                            self.set_world(new_world)
                            world_info: objects.WorldPointerExtraJson = {"name": obj.uuid.hex, "infinite_tier": 0}
                            world.new_obj(objects.World(obj.pos, obj.orient, world_info=world_info, level_info=obj.level_info))
                    elif make_noun_type == objects.TextClone:
                        if obj.world_info is not None:
                            world.new_obj(objects.Clone(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                        else:
                            world_color = colors.to_background_color(displays.sprite_colors[obj.sprite_name])
                            new_world = worlds.World(obj.uuid.hex, (3, 3), 0, world_color)
                            new_obj = copy.deepcopy(obj)
                            new_obj.pos = (1, 1)
                            new_obj.reset_uuid()
                            new_world.new_obj(new_obj)
                            self.set_world(new_world)
                            world_info: objects.WorldPointerExtraJson = {"name": obj.uuid.hex, "infinite_tier": 0}
                            world.new_obj(objects.Clone(obj.pos, obj.orient, world_info=world_info, level_info=obj.level_info))
                    elif make_noun_type == objects.TextText:
                        make_obj_type = objects.get_noun_from_obj(type(obj))
                        world.new_obj(make_obj_type(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
                    else:
                        make_obj_type = make_noun_type.obj_type
                        world.new_obj(make_obj_type(obj.pos, obj.orient, world_info=obj.world_info, level_info=obj.level_info))
    def text_plus_and_text_minus(self) -> None:
        for world in self.world_list:
            delete_list = []
            text_plus_objs = [o for o in world.object_list if o.has_prop(objects.TextTextPlus)]
            text_minus_objs = [o for o in world.object_list if o.has_prop(objects.TextTextMinus)]
            for text_plus_obj in text_plus_objs:
                if text_plus_obj in text_minus_objs:
                    continue
                new_type = objects.get_noun_from_obj(type(text_plus_obj))
                if new_type != objects.TextText:
                    delete_list.append(text_plus_obj)
                    world.new_obj(new_type(text_plus_obj.pos, text_plus_obj.orient, world_info=text_plus_obj.world_info, level_info=text_plus_obj.level_info))
            for text_minus_obj in text_minus_objs:
                if text_minus_obj in text_plus_objs:
                    continue
                if not isinstance(text_minus_obj, objects.Noun):
                    continue
                new_type = text_minus_obj.obj_type
                if new_type == objects.Text:
                    continue
                delete_list.append(text_minus_obj)
                if issubclass(new_type, objects.Game):
                    self.new_games.append(objects.TextGame)
                elif issubclass(new_type, objects.LevelPointer):
                    if text_minus_obj.level_info is not None:
                        world.new_obj(objects.Level(text_minus_obj.pos, text_minus_obj.orient, world_info=text_minus_obj.world_info, level_info=text_minus_obj.level_info))
                    else:
                        world_color = colors.to_background_color(displays.sprite_colors[text_minus_obj.sprite_name])
                        new_world = worlds.World(text_minus_obj.uuid.hex, (3, 3), 0, world_color)
                        self.created_levels.append(Level(text_minus_obj.uuid.hex, [new_world], super_level=self.name, rule_list=self.rule_list))
                        new_world.new_obj(type(text_minus_obj)((1, 1), text_minus_obj.orient))
                        level_info: objects.LevelPointerExtraJson = {"name": text_minus_obj.uuid.hex, "icon": {"name": text_minus_obj.sprite_name, "color": displays.sprite_colors[text_minus_obj.sprite_name]}}
                        new_obj = objects.Level(text_minus_obj.pos, text_minus_obj.orient, level_info=level_info)
                        world.new_obj(new_obj)
                elif issubclass(new_type, objects.WorldPointer):
                    if text_minus_obj.world_info is not None:
                        world.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, world_info=text_minus_obj.world_info, level_info=text_minus_obj.level_info))
                    else:
                        world_color = colors.to_background_color(displays.sprite_colors[text_minus_obj.sprite_name])
                        new_world = worlds.World(text_minus_obj.uuid.hex, (3, 3), 0, world_color)
                        new_world.new_obj(type(text_minus_obj)((1, 1), text_minus_obj.orient))
                        self.set_world(new_world)
                        world_info: objects.WorldPointerExtraJson = {"name": text_minus_obj.uuid.hex, "infinite_tier": 0}
                        new_obj = new_type(text_minus_obj.pos, text_minus_obj.orient, world_info=world_info)
                        world.new_obj(new_obj)
                else:
                    world.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, world_info=text_minus_obj.world_info, level_info=text_minus_obj.level_info))
            for obj in delete_list:
                self.destroy_obj(world, obj)
    def win(self) -> bool:
        for world in self.world_list:
            you_objs = [o for o in world.object_list if o.has_prop(objects.TextYou)]
            win_objs = [o for o in world.object_list if o.has_prop(objects.TextWin)]
            for you_obj in you_objs:
                if world.has_world_prop(objects.TextWin) or self.has_prop(objects.TextWin):
                    if not you_obj.has_prop(objects.TextFloat):
                        self.sound_events.append("win")
                        return True
                for win_obj in win_objs:
                    if you_obj.pos == win_obj.pos:
                        if objects.same_float_prop(you_obj, win_obj):
                            self.sound_events.append("win")
                            return True
        return False
    def end(self) -> bool:
        for world in self.world_list:
            you_objs = [o for o in world.object_list if o.has_prop(objects.TextYou)]
            end_objs = [o for o in world.object_list if o.has_prop(objects.TextEnd)]
            for you_obj in you_objs:
                if world.has_world_prop(objects.TextEnd) or self.has_prop(objects.TextEnd):
                    if not you_obj.has_prop(objects.TextFloat):
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
            if world.has_world_prop(objects.TextDone) or self.has_prop(objects.TextDone):
                delete_list.extend(world.object_list)
            for obj in world.object_list:
                if obj.has_prop(objects.TextDone):
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
                if obj.has_prop(objects.TextYou):
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
                obj_world = self.get_world(obj.world_info)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, frame, layer + 1)
                    obj_surface = displays.set_surface_color_dark(obj_surface, 0xC0C0C0)
                else:
                    obj_surface = displays.sprites.get("level", 0, frame).copy()
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Clone):
                obj_world = self.get_world(obj.world_info)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, frame, layer + 1)
                    obj_surface = displays.set_surface_color_light(obj_surface, 0x404040)
                else:
                    obj_surface = displays.sprites.get("clone", 0, frame).copy()
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Level):
                obj_surface = displays.set_surface_color_dark(displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy(), obj.level_info["icon"]["color"])
                icon_surface = displays.set_surface_color_light(displays.sprites.get(obj.level_info["icon"]["name"], 0, frame).copy(), 0xFFFFFF)
                icon_surface_pos = ((obj_surface.get_width() - icon_surface.get_width()) // 2,
                                    (obj_surface.get_height() - icon_surface.get_height()) // 2)
                obj_surface.blit(icon_surface, icon_surface_pos)
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Metatext):
                obj_surface = displays.sprites.get(obj.sprite_name, 0, frame).copy()
                obj_surface = pygame.transform.scale(obj_surface, (displays.sprite_size * len(str(obj.meta_tier)), displays.sprite_size * len(str(obj.meta_tier))))
                tier_surface = pygame.Surface((displays.sprite_size * len(str(obj.meta_tier)), displays.sprite_size), pygame.SRCALPHA)
                tier_surface.fill("#00000000")
                for digit, char in enumerate(str(obj.meta_tier)):
                    tier_surface.blit(displays.sprites.get("text_" + char, 0, frame), (displays.sprite_size * digit, 0))
                tier_surface = displays.set_alpha(tier_surface, 0x80)
                tier_surface_pos = ((obj_surface.get_width() - tier_surface.get_width()) // 2,
                                    (obj_surface.get_height() - tier_surface.get_height()) // 2)
                obj_surface.blit(tier_surface, tier_surface_pos)
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            elif isinstance(obj, objects.Cursor):
                obj_surface = displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy()
                obj_surface_pos = (obj.x * pixel_sprite_size - (obj_surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                                   obj.y * pixel_sprite_size - (obj_surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
            else:
                obj_surface = displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy()
                obj_surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
                obj_surface_list.append((obj_surface_pos, obj_surface, obj))
        sorted_obj_surface_list = map(lambda o: list(map(lambda t: isinstance(o[-1], t), displays.order)).index(True), obj_surface_list)
        sorted_obj_surface_list = map(lambda t: t[1], sorted(zip(sorted_obj_surface_list, obj_surface_list), key=lambda t: t[0], reverse=True))
        for pos, surface, obj in sorted_obj_surface_list:
            if isinstance(obj, objects.Cursor):
                world_surface.blit(pygame.transform.scale(surface, (displays.pixel_size * surface.get_width(), displays.pixel_size * surface.get_height())), pos)
            else:
                world_surface.blit(pygame.transform.scale(surface, (pixel_sprite_size, pixel_sprite_size)), pos)
        if cursor is not None:
            surface = displays.sprites.get("cursor", 0, frame).copy()
            pos = (cursor[0] * pixel_sprite_size - (surface.get_width() - displays.sprite_size) * displays.pixel_size // 2,
                   cursor[1] * pixel_sprite_size - (surface.get_height() - displays.sprite_size) * displays.pixel_size // 2)
            world_surface.blit(pygame.transform.scale(surface, (displays.pixel_size * surface.get_width(), displays.pixel_size * surface.get_height())), pos)
        world_background = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA)
        world_background.fill(pygame.Color(*colors.hex_to_rgb(world.color)))
        world_background.blit(world_surface, (0, 0))
        world_surface = world_background
        if world.infinite_tier > 0:
            infinite_surface = displays.sprites.get("text_infinite", 0, frame)
            multi_infinite_surface = pygame.Surface((infinite_surface.get_width(), infinite_surface.get_height() * world.infinite_tier), pygame.SRCALPHA)
            multi_infinite_surface.fill("#00000000")
            for i in range(world.infinite_tier):
                multi_infinite_surface.blit(infinite_surface, (0, i * infinite_surface.get_height()))
            multi_infinite_surface = pygame.transform.scale_by(multi_infinite_surface, world.height * displays.pixel_size / world.infinite_tier)
            multi_infinite_surface = displays.set_alpha(multi_infinite_surface, 0x80)
            world_surface.blit(multi_infinite_surface, ((world_surface.get_width() - multi_infinite_surface.get_width()) // 2, 0))
        elif world.infinite_tier < 0:
            epsilon_surface = displays.sprites.get("text_epsilon", 0, frame)
            multi_epsilon_surface = pygame.Surface((epsilon_surface.get_width(), epsilon_surface.get_height() * -world.infinite_tier), pygame.SRCALPHA)
            multi_epsilon_surface.fill("#00000000")
            for i in range(-world.infinite_tier):
                multi_epsilon_surface.blit(epsilon_surface, (0, i * epsilon_surface.get_height()))
            multi_epsilon_surface = pygame.transform.scale_by(multi_epsilon_surface, world.height * displays.pixel_size / -world.infinite_tier)
            multi_epsilon_surface = displays.set_alpha(multi_epsilon_surface, 0x80)
            world_surface.blit(multi_epsilon_surface, ((world_surface.get_width() - multi_epsilon_surface.get_width()) // 2, 0))
        return world_surface
    def to_json(self) -> LevelJson:
        json_object: LevelJson = {"name": self.name, "world_list": [], "super_level": self.super_level, "is_map": self.is_map, "main_world": {"name": self.main_world_name, "infinite_tier": self.main_world_tier}}
        for world in self.world_list:
            json_object["world_list"].append(world.to_json())
        return json_object

def json_to_level(json_object: LevelJson, ver: Optional[str] = None) -> Level:
    world_list = []
    for world in json_object["world_list"]:
        world_list.append(worlds.json_to_world(world, ver))
    return Level(name=json_object["name"],
                 world_list=world_list,
                 super_level=json_object["super_level"],
                 main_world_name=json_object["main_world"]["name"],
                 main_world_tier=json_object["main_world"]["infinite_tier"],
                 is_map=json_object.get("is_map", False))