from typing import NotRequired, Optional, TypeGuard, TypedDict
import random
import copy
import math
import os
from tqdm import tqdm

import bmp.base
import bmp.color
import bmp.loc
import bmp.obj
import bmp.ref
import bmp.render
import bmp.rule
import bmp.space

import pygame

class MapLevelExtraJson(TypedDict):
    spore_for_blossom: NotRequired[int]

class LevelJson41(TypedDict):
    id: bmp.ref.LevelIDJson
    spaces: list[bmp.ref.SpaceIDJson]
    current_space: bmp.ref.SpaceIDJson
    super_level: NotRequired[bmp.ref.LevelIDJson]
    map_info: NotRequired[MapLevelExtraJson]

type LevelJson = LevelJson41

max_move_count: int = 120
infinite_move_number: int = 6
MoveInfo = tuple[bmp.obj.Object, list[tuple[bmp.ref.SpaceID, bmp.loc.Coord[int], bmp.loc.Orient]]]

class Level(object):
    def __init__(
        self,
        level_id: bmp.ref.LevelID,
        space_included: list[bmp.ref.SpaceID],
        current_space_id: bmp.ref.SpaceID,
        *,
        super_level_id: Optional[bmp.ref.LevelID] = None,
        map_info: Optional[MapLevelExtraJson] = None,
    ) -> None:
        self.level_id: bmp.ref.LevelID = level_id
        self.space_included: list[bmp.ref.SpaceID] = space_included
        self.current_space_id: bmp.ref.SpaceID = current_space_id
        self.super_level_id: Optional[bmp.ref.LevelID] = super_level_id
        self.map_info: Optional[MapLevelExtraJson] = map_info
        # runtime properties
        self.space_dict: dict[bmp.ref.SpaceID, bmp.space.Space]
        self.properties: dict[type[bmp.obj.LevelObject], bmp.obj.PropertyStorage] = {p: bmp.obj.PropertyStorage() for p in bmp.obj.level_object_types}
        self.special_operator_properties: dict[type[bmp.obj.LevelObject], dict[type[bmp.obj.Operator], bmp.obj.PropertyStorage]] = {p: {o: bmp.obj.PropertyStorage() for o in bmp.obj.special_operators} for p in bmp.obj.level_object_types}
        self.game_properties: bmp.obj.PropertyStorage = bmp.obj.PropertyStorage()
        self.created_levels: list["Level"] = []
        self.all_list: list[type[bmp.obj.Object]] = []
        self.group_references: dict[type[bmp.obj.GroupNoun], bmp.obj.PropertyStorage] = {p: bmp.obj.PropertyStorage() for p in bmp.obj.group_noun_types}
        self.sound_events: list[str] = []
    def __eq__(self, level: "Level") -> bool:
        return self.level_id == level.level_id
    def get_space(self, space_id: Optional[bmp.ref.SpaceID]) -> Optional[bmp.space.Space]:
        return None if space_id is None else self.space_dict.get(space_id)
    def get_exact_space(self, space_id: bmp.ref.SpaceID) -> bmp.space.Space:
        return self.space_dict[space_id]
    @property
    def current_space(self) -> bmp.space.Space:
        return self.space_dict[self.current_space_id]
    @current_space.setter
    def current_space(self, space: bmp.space.Space) -> None:
        self.current_space_id = space.space_id
    def set_space(self, space: bmp.space.Space, space_id: Optional[bmp.ref.SpaceID] = None) -> None:
        _space_id: bmp.ref.SpaceID = space_id if space_id is not None else space.space_id
        self.space_dict[_space_id] = space
    @property
    def space_list(self) -> list[bmp.space.Space]:
        return [s for s in self.space_dict.values() if s.space_id in self.space_included]
    @space_list.setter
    def space_list(self, __space_list: list[bmp.space.Space]) -> None:
        self.space_dict.clear()
        self.space_dict.update({s.space_id: s for s in __space_list})
    def find_super_spaces(self, space_object_id: bmp.ref.SpaceID) -> list[tuple[bmp.space.Space, bmp.obj.SpaceObject]]:
        return_value: list[tuple[bmp.space.Space, bmp.obj.SpaceObject]] = []
        for super_space_id, super_space in self.space_dict.items():
            for obj in super_space.get_spaces():
                if space_object_id == obj.space_id:
                    return_value.append((super_space, obj))
        return return_value
    def refresh_all_list(self) -> None:
        self.all_list = []
        for space in self.space_list:
            for obj in space.object_list:
                if not issubclass(type(obj), bmp.obj.types_not_in_all):
                    if type(obj) not in self.all_list:
                        self.all_list.append(type(obj))
    def reset_move_numbers(self) -> None:
        for space in self.space_list:
            for obj in space.object_list:
                obj.move_number = 0
    @staticmethod
    def merge_move_list(move_list: list[MoveInfo]) -> list[MoveInfo]:
        move_dict: dict[bmp.obj.Object, list[tuple[bmp.ref.SpaceID, bmp.loc.Coord[int], bmp.loc.Orient]]] = {}
        for obj, new_info_list in move_list:
            move_dict.setdefault(obj, [])
            move_dict[obj].extend(new_info_list)
        return [(o, l) for o, l in move_dict.items()]
    def move_objs_from_move_list(self, move_list: list[MoveInfo]) -> None:
        move_list = self.merge_move_list(move_list)
        for old_obj, new_info_list in move_list:
            new_info_list = bmp.base.remove_same_elements(new_info_list)
            old_space: Optional[bmp.space.Space] = None
            for space in self.space_list:
                if old_obj in space.object_list:
                    old_space = space
            if old_space is None:
                continue # how did we get here?
            old_obj.move_number += 1
            for new_space_id, new_pos, new_direct in new_info_list:
                new_space = self.get_space(new_space_id)
                if new_space is None:
                    continue
                new_obj = copy.deepcopy(old_obj)
                new_obj.reset_uuid()
                new_obj.pos = new_pos
                new_obj.orient = new_direct
                new_space.new_obj(new_obj)
            old_space.del_obj(old_obj)
        if len(move_list) != 0 and "move" not in self.sound_events:
            self.sound_events.append("move")
    def meet_prefix_conditions(self, space: bmp.space.Space, obj: bmp.obj.Object, prefix_info_list: list[bmp.rule.PrefixInfo], is_meta: bool = False) -> bool:
        return_value = True
        for prefix_info in prefix_info_list:
            meet_prefix_condition = True
            if type(prefix_info.prefix) == bmp.obj.TextMeta:
                meet_prefix_condition = is_meta and obj.space_id == space.space_id
            elif type(prefix_info.prefix) == bmp.obj.TextOften:
                meet_prefix_condition = random.choice((True, True, True, False))
            elif type(prefix_info.prefix) == bmp.obj.TextSeldom:
                meet_prefix_condition = random.choice((True, False, False, False, False, False))
            return_value = return_value and (meet_prefix_condition if not prefix_info.negated else not meet_prefix_condition)
        return return_value
    def meet_infix_conditions(self, space: bmp.space.Space, obj: bmp.obj.Object, infix_info_list: list[bmp.rule.InfixInfo]) -> bool:
        for infix_info in infix_info_list:
            meet_infix_condition = True
            if isinstance(infix_info.infix, bmp.obj.RangeInfix):
                matched_objs: list[bmp.obj.Object] = [obj]
                find_range: list[bmp.loc.Coord[int]] = [
                    p for p in map(
                        lambda t: (obj.x + t[0], obj.y + t[1]), 
                        infix_info.infix.find_range
                    ) if not space.out_of_range(p)
                ]
                for infix_noun_info in infix_info.infix_noun_info_list:
                    match_objs: list[bmp.obj.Object] = []
                    match_negated: bool = infix_noun_info.negated
                    match_noun: type[bmp.obj.Noun | bmp.obj.Property] = type(infix_noun_info.infix_noun)
                    if issubclass(match_noun, bmp.obj.Property):
                        continue # how did we get here?
                    match_noun_list: list[type[bmp.obj.Noun]] = []
                    if match_noun == bmp.obj.TextAll:
                        if match_negated:
                            match_noun_list = list(bmp.obj.nouns_in_not_all)
                        else:
                            match_noun_list = [bmp.obj.get_noun_from_type(o) for o in self.all_list if not issubclass(o, bmp.obj.types_not_in_all)]
                    else:
                        if match_negated:
                            match_noun_list = [bmp.obj.get_noun_from_type(o) for o in self.all_list if (not issubclass(o, bmp.obj.types_not_in_all)) and not bmp.obj.TextAll().isreferenceof(o(), all_list=self.all_list)]
                        else:
                            match_noun_list = [match_noun]
                    for new_match_noun in match_noun_list:
                        for pos in find_range:
                            match_objs.extend([o for o in space.get_objs_from_pos_and_noun(pos, new_match_noun()) if o not in matched_objs])
                        if len(match_objs) == 0:
                            meet_infix_condition = False
                        else:
                            matched_objs.append(match_objs[0])
                    if not meet_infix_condition:
                        break
            elif infix_info.infix == bmp.obj.TextFeeling:
                if obj.old_state.prop is None:
                    meet_infix_condition = False
                else:
                    for infix_noun_info in infix_info.infix_noun_info_list:
                        if obj.old_state.prop.enabled(type(infix_noun_info.infix_noun)) == infix_noun_info.negated:
                            meet_infix_condition = False
            elif infix_info.infix == bmp.obj.TextFacing: # temporary solution, noun not supported yet
                for infix_noun_info in infix_info.infix_noun_info_list: # type: ignore
                    if isinstance(infix_noun_info.infix_noun, bmp.obj.DirectFixProperty):
                        if (obj.orient != infix_noun_info.infix_noun.ref_direct ) and not infix_noun_info.negated:
                            meet_infix_condition = False
                        elif (obj.orient == infix_noun_info.infix_noun.ref_direct ) and infix_noun_info.negated:
                            meet_infix_condition = False
                    elif not infix_noun_info.negated:
                        meet_infix_condition = False
            elif infix_info.infix == bmp.obj.TextWithout:
                meet_infix_condition = True
                matched_objs: list[bmp.obj.Object] = [obj]
                match_type_count: dict[tuple[bool, type[bmp.obj.Noun]], int] = {}
                for match_negated, match_noun in infix_info[2]: # type: ignore
                    match_noun: type[bmp.obj.Noun | bmp.obj.Property]
                    if issubclass(match_noun, bmp.obj.Property):
                        continue # how did we get here?
                    match_type_count.setdefault((match_negated, match_noun), 0)
                    match_type_count[(match_negated, match_noun)] += 1
                for (match_negated, match_noun), match_count in match_type_count.items():
                    match_objs: list[bmp.obj.Object] = []
                    match_noun: type[bmp.obj.Noun | bmp.obj.Property]
                    match_noun_list: list[type[bmp.obj.Noun]] = []
                    if match_noun == bmp.obj.TextAll:
                        if match_negated:
                            match_noun_list = list(bmp.obj.nouns_in_not_all)
                        else:
                            match_noun_list = [bmp.obj.get_noun_from_type(o) for o in self.all_list if not issubclass(o, bmp.obj.types_not_in_all)]
                    else:
                        if match_negated:
                            match_noun_list = [bmp.obj.get_noun_from_type(o) for o in self.all_list if (not issubclass(o, bmp.obj.types_not_in_all)) and not bmp.obj.TextAll().isreferenceof(o(), all_list=self.all_list)]
                        else:
                            match_noun_list = [match_noun]
                    for new_match_noun in match_noun_list:
                        match_objs.extend([o for o in space.get_objs_from_noun(new_match_noun()) if o not in matched_objs])
                        if len(match_objs) >= match_count:
                            meet_infix_condition = False
                        else:
                            matched_objs.append(match_objs[0])
                    if not meet_infix_condition:
                        break
            if meet_infix_condition == infix_info.negated:
                return False
        return True
    def recursion_rules(self, space: bmp.space.Space, passed: Optional[list[bmp.ref.SpaceID]] = None) -> tuple[list[bmp.rule.Rule], list[bmp.rule.RuleInfo]]:
        passed = passed if passed is not None else []
        if space.space_id in passed:
            return [], []
        passed.append(space.space_id)
        rule_list = copy.deepcopy(space.rule_list)
        rule_info = copy.deepcopy(space.rule_info)
        for super_space in self.space_list:
            for space_obj in super_space.get_spaces():
                if space.space_id == space_obj.space_id:
                    new_rule_list, new_rule_info = self.recursion_rules(super_space, passed)
                    rule_list.extend(new_rule_list)
                    rule_info.extend(new_rule_info)
                    passed.append(super_space.space_id)
        return rule_list, rule_info
    def destroy_obj(self, space: bmp.space.Space, obj: bmp.obj.Object) -> None:
        space.del_obj(obj)
        for new_noun_type, new_noun_count in obj.operator_properties[bmp.obj.TextHas].enabled_count().items(): # type: ignore
            new_noun_type: type[bmp.obj.Noun]
            if issubclass(new_noun_type, bmp.obj.RangedNoun):
                continue
            new_object_type: type[bmp.obj.Object] = new_noun_type.ref_type
            if issubclass(new_noun_type, bmp.obj.TextText):
                new_object_type = bmp.obj.get_noun_from_type(type(obj))
            for _ in range(new_noun_count):
                if issubclass(new_object_type, bmp.obj.Game):
                    if isinstance(obj, (bmp.obj.LevelObject, bmp.obj.SpaceObject)):
                        space.new_obj(bmp.obj.Game(obj.pos, obj.orient, ref_type=bmp.obj.get_noun_from_type(type(obj))))
                    else:
                        space.new_obj(bmp.obj.Game(obj.pos, obj.orient, ref_type=type(obj)))
                elif issubclass(new_object_type, bmp.obj.LevelObject):
                    level_extra: bmp.obj.LevelObjectExtra = {"icon": {"name": obj.sprite_name, "color": obj.get_color()}}
                    if obj.level_id is not None:
                        space.new_obj(new_object_type(obj.pos, obj.orient, level_id=obj.level_id, level_extra=level_extra))
                    else:
                        space.new_obj(new_object_type(obj.pos, obj.orient, level_id=self.level_id, level_extra=level_extra))
                elif issubclass(new_object_type, bmp.obj.SpaceObject):
                    if obj.space_id is not None:
                        space.new_obj(new_object_type(obj.pos, obj.orient, space_id=obj.space_id))
                    else:
                        space.new_obj(new_object_type(obj.pos, obj.orient, space_id=space.space_id))
                else:
                    space.new_obj(new_object_type(obj.pos, obj.orient, space_id=obj.space_id, level_id=obj.level_id))
    def get_move_list(self, space: bmp.space.Space, obj: bmp.obj.Object, \
        direct: bmp.loc.Orient, pos: Optional[bmp.loc.Coord[int]] = None, \
            pushed: Optional[list[bmp.obj.Object]] = None, passed: Optional[list[bmp.ref.SpaceID]] = None, \
                transnum: Optional[float] = None, depth: int = 0) -> Optional[list[MoveInfo]]:
        if depth > 100:
            return None
        depth += 1
        pushed = pushed[:] if pushed is not None else []
        if obj in pushed:
            return None
        passed = passed[:] if passed is not None else []
        pos = pos if pos is not None else obj.pos
        new_pos = bmp.loc.front_position(pos, direct)
        leave_space = False
        leave_list: list[MoveInfo] = []
        if space.out_of_range(new_pos) and not obj.properties.disabled(bmp.obj.TextLeave):
            old_space_id = space.space_id
            old_space = self.get_space(old_space_id)
            if passed.count(space.space_id) > infinite_move_number:
                old_space_id = space.space_id + 1
            passed.append(space.space_id)
            if old_space is not None:
                super_space_list = self.find_super_spaces(old_space_id)
                for super_space, space_obj in super_space_list:
                    if old_space.properties[type(space_obj)].disabled(bmp.obj.TextLeave):
                        continue
                    transform = space.get_stacked_transform(space_obj.space_extra["static_transform"], space_obj.space_extra["dynamic_transform"])
                    new_direct = bmp.loc.swap_direction(direct) if transform["flip"] and direct in (bmp.loc.Orient.A, bmp.loc.Orient.D) else direct
                    new_direct = bmp.loc.turn(new_direct, bmp.loc.Orient[transform["direct"]])
                    if transnum is not None:
                        new_transnum = space.calc_leave_transnum(transnum, space_obj.pos, direct, transform)
                    else:
                        new_transnum = space.get_leave_transnum_from_pos(obj.pos, direct, transform)
                    new_move_list = self.get_move_list(super_space, obj, new_direct, space_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is not None:
                        leave_space = True
                        leave_list.extend(new_move_list)
            else:
                leave_space = True
                leave_list.append((obj, []))
        push_objects = [o for o in space.get_objs_from_pos(new_pos) if o.properties.enabled(bmp.obj.TextPush)]
        unpushable_objects: list[bmp.obj.Object] = []
        push = False
        push_list: list[MoveInfo] = []
        if len(push_objects) != 0 and not space.out_of_range(new_pos):
            push = True
            for push_object in push_objects:
                new_move_list = self.get_move_list(space, push_object, direct, pushed=pushed + [obj], depth=depth)
                if new_move_list is None:
                    unpushable_objects.append(push_object)
                    push = False
                else:
                    push_list.extend(new_move_list)
            if push:
                push_list.append((obj, [(space.space_id, new_pos, direct)]))
        simple = False
        stop_objects: list[bmp.obj.Object] = []
        if not space.out_of_range(new_pos):
            stop_objects = [o for o in space.get_objs_from_pos(new_pos) if o.properties.enabled(bmp.obj.TextStop) and not o.properties.enabled(bmp.obj.TextPush)]
            if len(stop_objects + unpushable_objects) != 0:
                push = False
                if obj.properties.enabled(bmp.obj.TextOpen):
                    simple = True
                    for stop_object in stop_objects + unpushable_objects:
                        if not stop_object.properties.enabled(bmp.obj.TextShut):
                            simple = False
                elif obj.properties.enabled(bmp.obj.TextShut):
                    simple = True
                    for stop_object in stop_objects + unpushable_objects:
                        if not stop_object.properties.enabled(bmp.obj.TextOpen):
                            simple = False
            else:
                simple = True
        squeeze = False
        squeeze_list: list[MoveInfo] = []
        if isinstance(obj, bmp.obj.SpaceObject) and (not space.out_of_range(new_pos)) and (not simple) and len(stop_objects) == 0:
            squeeze_space = self.get_space(obj.space_id)
            if squeeze_space is not None:
                if not squeeze_space.properties[type(obj)].disabled(bmp.obj.TextEnter):
                    squeeze = True
                    for new_push_object in push_objects:
                        if new_push_object.properties.disabled(bmp.obj.TextEnter):
                            squeeze = False
                            break
                        transform = bmp.loc.inverse_transform(squeeze_space.get_stacked_transform(obj.space_extra["static_transform"], obj.space_extra["dynamic_transform"]))
                        new_direct = bmp.loc.swap_direction(direct) if transform["flip"] and direct in (bmp.loc.Orient.A, bmp.loc.Orient.D) else direct
                        new_direct = bmp.loc.turn(new_direct, bmp.loc.Orient[transform["direct"]])
                        input_pos = squeeze_space.get_enter_pos_by_default(new_direct, transform)
                        squeeze_move_list = self.get_move_list(squeeze_space, new_push_object, bmp.loc.swap_direction(new_direct), input_pos, pushed=pushed + [obj], depth=depth)
                        if squeeze_move_list is None:
                            squeeze = False
                            break
                        squeeze_list.extend(squeeze_move_list)
            else:
                squeeze = True
                for new_push_object in push_objects:
                    if new_push_object.properties.disabled(bmp.obj.TextEnter):
                        squeeze = False
                        break
                    squeeze_list.append((new_push_object, []))
            if squeeze:
                squeeze_list.append((obj, [(space.space_id, new_pos, direct)]))
        enter_space = False
        enter_list: list[MoveInfo] = []
        if not space.out_of_range(new_pos) and not obj.properties.disabled(bmp.obj.TextEnter):
            sub_space_obj_list = [o for o in space.get_spaces_from_pos(new_pos) if not o.properties.disabled(bmp.obj.TextEnter)]
            for sub_space_obj in sub_space_obj_list:
                sub_space = self.get_space(sub_space_obj.space_id)
                if sub_space is None:
                    enter_space = True
                    continue
                if sub_space.properties[type(sub_space_obj)].disabled(bmp.obj.TextEnter):
                    continue
                if passed.count(sub_space.space_id) > infinite_move_number:
                    epsilon_space_id = sub_space.space_id - 1
                    epsilon_space = self.get_space(epsilon_space_id)
                    if epsilon_space is None:
                        enter_space = True
                        continue
                    if epsilon_space.properties[type(sub_space_obj)].disabled(bmp.obj.TextEnter):
                        continue
                    epsilon_space_list = self.find_super_spaces(epsilon_space.space_id)
                    for _, epsilon_space_obj in epsilon_space_list:
                        if epsilon_space_obj.properties.disabled(bmp.obj.TextEnter):
                            continue
                        transform = bmp.loc.inverse_transform(epsilon_space.get_stacked_transform(epsilon_space_obj.space_extra["static_transform"], epsilon_space_obj.space_extra["dynamic_transform"]))
                        inversed_transform = bmp.loc.inverse_transform(transform)
                        new_direct = bmp.loc.swap_direction(direct) if inversed_transform["flip"] and direct in (bmp.loc.Orient.A, bmp.loc.Orient.D) else direct
                        new_direct = bmp.loc.turn(new_direct, bmp.loc.Orient[transform["direct"]])
                        input_pos = epsilon_space.get_enter_pos_by_default(bmp.loc.swap_direction(new_direct), inversed_transform)
                        new_transnum = 0.5
                        passed.append(space.space_id)
                        new_move_list = self.get_move_list(epsilon_space, obj, new_direct, input_pos, pushed, passed, new_transnum, depth)
                        if new_move_list is not None:
                            enter_list.extend(new_move_list)
                            enter_space = True
                    continue
                transform = sub_space.get_stacked_transform(sub_space_obj.space_extra["static_transform"], sub_space_obj.space_extra["dynamic_transform"])
                inversed_transform = bmp.loc.inverse_transform(transform)
                new_direct = bmp.loc.swap_direction(direct) if inversed_transform["flip"] and direct in (bmp.loc.Orient.A, bmp.loc.Orient.D) else direct
                new_direct = bmp.loc.turn(new_direct, bmp.loc.Orient[transform["direct"]])
                if transnum is not None:
                    input_pos = sub_space.get_enter_pos(transnum, bmp.loc.swap_direction(direct), inversed_transform)
                    new_transnum = space.calc_enter_transnum(transnum, sub_space_obj.pos, bmp.loc.swap_direction(direct), inversed_transform)
                else:
                    input_pos = sub_space.get_enter_pos_by_default(bmp.loc.swap_direction(direct), inversed_transform)
                    new_transnum = 0.5
                passed.append(space.space_id)
                new_move_list = self.get_move_list(sub_space, obj, new_direct, input_pos, pushed, passed, new_transnum, depth)
                if new_move_list is not None:
                    enter_list.extend(new_move_list)
                    enter_space = True
        if enter_space and len(enter_list) == 0:
            enter_list.append((obj, []))
        if leave_space:
            return self.merge_move_list(leave_list)
        elif push:
            return self.merge_move_list(push_list)
        elif enter_space:
            return self.merge_move_list(enter_list)
        elif squeeze:
            return self.merge_move_list(squeeze_list)
        elif simple:
            return [(obj, [(space.space_id, new_pos, direct)])]
        else:
            return None
    def you(self, direct: Optional[bmp.loc.Orient]) -> bool:
        self.reset_move_numbers()
        if direct is None:
            return False
        pushing_game = False
        finished = False
        for _ in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for space in self.space_list:
                you_objs = [o for o in space.object_list if o.move_number < o.properties.count(bmp.obj.TextYou)]
                if len(you_objs) != 0:
                    finished = False
                for obj in you_objs:
                    obj.orient = direct
                    new_move_list = self.get_move_list(space, obj, obj.orient)
                    if new_move_list is not None:
                        move_list.extend(new_move_list)
                        obj.move_number += 1
                    else:
                        pushing_game = True
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def select(self, direct: Optional[bmp.loc.Orient]) -> Optional[list[bmp.ref.LevelID]]:
        if direct is None:
            level_list: list[bmp.ref.LevelID] = []
            for space in self.space_list:
                select_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextSelect)]
                for select_obj in select_objs:
                    level_list.extend([o.level_id for o in space.object_list if o.pos == select_obj.pos and o.level_id is not None and o != select_obj])
            return level_list
        else:
            for space in self.space_list:
                select_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextSelect)]
                for select_obj in select_objs:
                    new_pos = bmp.loc.front_position(select_obj.pos, direct)
                    if not space.out_of_range(new_pos):
                        level_objs = space.get_levels_from_pos(new_pos)
                        path_objs = space.get_objs_from_pos_and_type(new_pos, bmp.obj.Path)
                        if any(map(lambda p: p.unlocked, path_objs)) or len(level_objs) != 0:
                            space.set_obj_pos(select_obj, new_pos)
        return None
    def direction(self) -> None:
        for prop in bmp.obj.direct_fix_properties:
            for space in self.space_list:
                for obj in space.object_list:
                    if obj.properties.enabled(prop):
                        if isinstance(obj, bmp.obj.SpaceObject):
                            obj.space_extra["static_transform"] = prop.ref_transform.copy()
                        obj.orient = prop.ref_direct
                if space.properties[bmp.obj.default_space_object_type].enabled(prop):
                    space.static_transform = prop.ref_transform.copy()
            if self.properties[bmp.obj.default_level_object_type].enabled(prop):
                pass # NotImplemented
    def flip(self) -> None:
        for space in self.space_list:
            space.dynamic_transform = bmp.loc.default_space_transform.copy()
            for obj in space.get_spaces():
                obj.space_extra["dynamic_transform"] = bmp.loc.default_space_transform.copy()
        for prop in bmp.obj.direct_mapping_properties:
            for space in self.space_list:
                for obj in space.object_list:
                    if obj.properties.count(prop) % 2 == 1:
                        if isinstance(obj, bmp.obj.SpaceObject):
                            obj.space_extra["dynamic_transform"] = bmp.loc.get_stacked_transform(obj.space_extra["dynamic_transform"], prop.ref_transform)
                        obj.set_direct_mapping(prop.ref_mapping)
                if space.properties[bmp.obj.default_space_object_type].count(prop) % 2 == 1:
                    space.dynamic_transform = bmp.loc.get_stacked_transform(space.dynamic_transform, prop.ref_transform)
            if self.properties[bmp.obj.default_level_object_type].count(prop) % 2 == 1:
                pass # NotImplemented
    def turn(self) -> None:
        for space in self.space_list:
            for obj in space.object_list:
                turn_count = (obj.properties.count(bmp.obj.TextTurn) - obj.properties.count(bmp.obj.TextDeturn)) % 4
                for _ in range(turn_count):
                    obj.orient = bmp.loc.turn_right(obj.orient)
                    if isinstance(obj, bmp.obj.SpaceObject):
                        obj.space_extra["static_transform"] = bmp.loc.get_stacked_transform(obj.space_extra["static_transform"], {"direct": "A", "flip": False})
            turn_count = (space.properties[bmp.obj.default_space_object_type].count(bmp.obj.TextTurn) - space.properties[bmp.obj.default_space_object_type].count(bmp.obj.TextDeturn)) % 4
            for _ in range(turn_count):
                space.static_transform = bmp.loc.get_stacked_transform(space.static_transform, {"direct": "A", "flip": False})
        if self.properties[bmp.obj.default_level_object_type].count(bmp.obj.TextFlip) % 2 == 1:
            pass # NotImplemented
    def move(self) -> bool:
        self.reset_move_numbers()
        pushing_game = False
        for space in self.space_list:
            global_move_count = space.properties[bmp.obj.default_space_object_type].count(bmp.obj.TextMove) + self.properties[bmp.obj.default_level_object_type].count(bmp.obj.TextMove)
            for _ in range(global_move_count):
                move_list = []
                for obj in [o for o in space.object_list if o.move_number < global_move_count]:
                    if not obj.properties.enabled(bmp.obj.TextFloat):
                        new_move_list = self.get_move_list(space, obj, bmp.loc.Orient.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                            obj.move_number += 1
                        else:
                            pushing_game = True
                self.move_objs_from_move_list(move_list)
        self.reset_move_numbers()
        finished = False
        for _ in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for space in self.space_list:
                move_objs = [o for o in space.object_list if o.move_number < o.properties.count(bmp.obj.TextMove)]
                if len(move_objs) != 0:
                    finished = False
                for obj in move_objs:
                    new_move_list = self.get_move_list(space, obj, obj.orient)
                    if new_move_list is not None:
                        move_list = new_move_list
                        obj.move_number += 1
                    else:
                        obj.orient = bmp.loc.swap_direction(obj.orient)
                        new_move_list = self.get_move_list(space, obj, obj.orient)
                        if new_move_list is not None:
                            move_list = new_move_list
                            obj.move_number += 1
                        else:
                            pushing_game = True
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def shift(self) -> bool:
        self.reset_move_numbers()
        pushing_game = False
        for space in self.space_list:
            global_shift_count = space.properties[bmp.obj.default_space_object_type].count(bmp.obj.TextShift) + self.properties[bmp.obj.default_level_object_type].count(bmp.obj.TextShift)
            for _ in range(global_shift_count):
                move_list = []
                for obj in [o for o in space.object_list if o.move_number < global_shift_count]:
                    if not obj.properties.enabled(bmp.obj.TextFloat):
                        new_move_list = self.get_move_list(space, obj, bmp.loc.Orient.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                            obj.move_number += 1
                        else:
                            pushing_game = True
                self.move_objs_from_move_list(move_list)
        self.reset_move_numbers()
        finished = False
        for _ in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for space in self.space_list:
                shifter_objs = [o for o in space.object_list if o.move_number < o.properties.count(bmp.obj.TextShift)]
                for shifter_obj in shifter_objs:
                    shifted_objs = [o for o in space.get_objs_from_pos(shifter_obj.pos) if o != shifter_obj and bmp.obj.same_float_prop(o, shifter_obj)]
                    for obj in shifted_objs:
                        new_move_list = self.get_move_list(space, obj, shifter_obj.orient)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                            obj.move_number += 1
                            finished = False
                        else:
                            pushing_game = True
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def tele(self) -> None:
        if self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextTele):
            pass
        for space in self.space_list:
            if space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextTele):
                pass
        tele_list: list[tuple[bmp.space.Space, bmp.obj.Object, bmp.space.Space, bmp.loc.Coord[int]]] = []
        object_list: list[tuple[bmp.space.Space, bmp.obj.Object]] = []
        for space in self.space_list:
            object_list.extend([(space, o) for o in space.object_list])
        tele_objs = [t for t in object_list if t[1].properties.enabled(bmp.obj.TextTele)]
        tele_object_types: dict[type[bmp.obj.Object], list[tuple[bmp.space.Space, bmp.obj.Object]]] = {}
        for object_type in [n.ref_type for n in bmp.obj.noun_class_list]:
            for tele_obj in tele_objs:
                if isinstance(tele_obj[1], object_type):
                    tele_object_types[object_type] = tele_object_types.get(object_type, []) + [tele_obj]
        for new_tele_objs in tele_object_types.values():
            if len(new_tele_objs) <= 1:
                continue
            for tele_space, tele_obj in new_tele_objs:
                other_tele_objs = new_tele_objs[:]
                other_tele_objs.remove((tele_space, tele_obj))
                for obj in tele_space.get_objs_from_pos(tele_obj.pos):
                    if obj == tele_obj:
                        continue
                    if bmp.obj.same_float_prop(obj, tele_obj):
                        other_tele_space, other_tele_obj = random.choice(other_tele_objs)
                        tele_list.append((tele_space, obj, other_tele_space, other_tele_obj.pos))
        for old_space, obj, new_space, pos in tele_list:
            old_space.del_obj(obj)
            obj.pos = pos
            new_space.new_obj(obj)
        if len(tele_list) != 0:
            self.sound_events.append("tele")
    def sink(self) -> None:
        success = False
        for space in self.space_list:
            delete_list = []
            if space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextSink) or self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextSink):
                for obj in space.object_list:
                    if not obj.properties.enabled(bmp.obj.TextFloat):
                        delete_list.append(obj)
            sink_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextSink)]
            for sink_obj in sink_objs:
                for obj in space.get_objs_from_pos(sink_obj.pos):
                    if obj == sink_obj:
                        continue
                    if obj.pos == sink_obj.pos:
                        if bmp.obj.same_float_prop(obj, sink_obj):
                            if obj not in delete_list and sink_obj not in delete_list:
                                delete_list.append(obj)
                                delete_list.append(sink_obj)
                                break
            for obj in delete_list:
                self.destroy_obj(space, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("sink")
    def hot_and_melt(self) -> None:
        success = False
        for space in self.space_list:
            delete_list = []
            melt_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextMelt)]
            hot_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextHot)]
            if len(hot_objs) != 0 and (space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextMelt) or self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextMelt)):
                for melt_obj in melt_objs:
                    if not melt_obj.properties.enabled(bmp.obj.TextFloat):
                        delete_list.extend(space.object_list)
                continue
            if len(melt_objs) != 0 and (space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextHot) or self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextHot)):
                for melt_obj in melt_objs:
                    if not melt_obj.properties.enabled(bmp.obj.TextFloat):
                        delete_list.append(melt_obj)
                continue
            for hot_obj in hot_objs:
                for melt_obj in melt_objs:
                    if hot_obj.pos == melt_obj.pos:
                        if bmp.obj.same_float_prop(hot_obj, melt_obj):
                            if melt_obj not in delete_list:
                                delete_list.append(melt_obj)
            for obj in delete_list:
                self.destroy_obj(space, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("melt")
    def defeat(self) -> None:
        success = False
        for space in self.space_list:
            delete_list = []
            you_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextYou)]
            defeat_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextDefeat)]
            if len(defeat_objs) != 0 and (space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextYou) or self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextYou)):
                delete_list.extend(space.object_list)
                continue
            for you_obj in you_objs:
                if space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextDefeat) or self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextDefeat):
                    if you_obj not in delete_list:
                        delete_list.append(you_obj)
                        continue
                for defeat_obj in defeat_objs:
                    if you_obj.pos == defeat_obj.pos:
                        if bmp.obj.same_float_prop(defeat_obj, you_obj):
                            if you_obj not in delete_list:
                                delete_list.append(you_obj)
            for obj in delete_list:
                self.destroy_obj(space, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("defeat")
    def bonus(self) -> dict[type[bmp.obj.Object], bool]:
        collected: dict[type[bmp.obj.Object], bool] = {}
        for space in self.space_list:
            delete_list = []
            bonus_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextBonus)]
            you_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextYou)]
            if len(you_objs) != 0 and (space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextBonus) or self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextBonus)):
                delete_list.extend(space.object_list)
                continue
            for bonus_obj in bonus_objs:
                if space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextYou) or self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextYou):
                    if bonus_obj not in delete_list:
                        delete_list.append(bonus_obj)
                        continue
                for you_obj in you_objs:
                    if bonus_obj.pos == you_obj.pos:
                        if bmp.obj.same_float_prop(you_obj, bonus_obj):
                            if bonus_obj not in delete_list:
                                delete_list.append(bonus_obj)
                                collected[type(bonus_obj)] = True
            for obj in delete_list:
                self.destroy_obj(space, obj)
        if len(collected):
            self.sound_events.append("bonus")
        return collected
    def open_and_shut(self) -> None:
        success = False
        for space in self.space_list:
            delete_list = []
            shut_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextShut)]
            open_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextOpen)]
            if len(open_objs) != 0 and (space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextShut) or self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextShut)):
                delete_list.extend(space.object_list)
                continue
            if len(shut_objs) != 0 and (space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextOpen) or self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextOpen)):
                delete_list.extend(space.object_list)
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
                self.destroy_obj(space, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("open")
    def make(self) -> None:
        for space in self.space_list:
            for obj in space.object_list:
                for make_noun_type, make_noun_count in obj.operator_properties[bmp.obj.TextMake].enabled_count().items(): # type: ignore
                    make_noun_type: type[bmp.obj.Noun]
                    if issubclass(make_noun_type, bmp.obj.RangedNoun):
                        continue
                    make_object_type: type[bmp.obj.Object] = make_noun_type.ref_type
                    if issubclass(make_noun_type, bmp.obj.TextText):
                        make_object_type = bmp.obj.get_noun_from_type(type(obj))
                    if len(space.get_objs_from_pos_and_type(obj.pos, make_object_type)) != 0:
                        continue
                    for _ in range(make_noun_count):
                        if issubclass(make_object_type, bmp.obj.Game):
                            if isinstance(obj, (bmp.obj.LevelObject, bmp.obj.SpaceObject)):
                                space.new_obj(bmp.obj.Game(obj.pos, obj.orient, ref_type=bmp.obj.get_noun_from_type(type(obj))))
                            else:
                                space.new_obj(bmp.obj.Game(obj.pos, obj.orient, ref_type=type(obj)))
                        elif issubclass(make_object_type, bmp.obj.LevelObject):
                            if len(space.get_objs_from_pos_and_type(obj.pos, make_object_type)) == 0:
                                level_extra: bmp.obj.LevelObjectExtra = {"icon": {"name": obj.sprite_name, "color": obj.get_color()}}
                                if obj.level_id is not None:
                                    space.new_obj(make_object_type(obj.pos, obj.orient, level_id=obj.level_id, level_extra=level_extra))
                                else:
                                    space.new_obj(make_object_type(obj.pos, obj.orient, level_id=self.level_id, level_extra=level_extra))
                        elif issubclass(make_object_type, bmp.obj.SpaceObject):
                            if len(space.get_objs_from_pos_and_type(obj.pos, make_object_type)) == 0:
                                if obj.space_id is not None:
                                    space.new_obj(make_object_type(obj.pos, obj.orient, space_id=obj.space_id))
                                else:
                                    space.new_obj(make_object_type(obj.pos, obj.orient, space_id=space.space_id))
                        else:
                            space.new_obj(make_object_type(obj.pos, obj.orient, space_id=obj.space_id, level_id=obj.level_id))
    def text_plus_and_text_minus(self) -> None:
        for space in self.space_list:
            delete_list = []
            text_plus_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextTextPlus)]
            text_minus_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextTextMinus)]
            for text_plus_obj in text_plus_objs:
                if text_plus_obj in text_minus_objs:
                    continue
                new_type = bmp.obj.get_noun_from_type(type(text_plus_obj))
                if not issubclass(new_type, bmp.obj.TextText):
                    delete_list.append(text_plus_obj)
                    space.new_obj(new_type(text_plus_obj.pos, text_plus_obj.orient, space_id=text_plus_obj.space_id, level_id=text_plus_obj.level_id))
            for text_minus_obj in text_minus_objs:
                if text_minus_obj in text_plus_objs:
                    continue
                if not isinstance(text_minus_obj, bmp.obj.Noun):
                    continue
                new_type = text_minus_obj.ref_type
                if new_type == bmp.obj.Text:
                    continue
                delete_list.append(text_minus_obj)
                if issubclass(new_type, bmp.obj.Game):
                    space.new_obj(bmp.obj.Game(text_minus_obj.pos, text_minus_obj.orient, ref_type=bmp.obj.TextGame))
                elif issubclass(new_type, bmp.obj.LevelObject):
                    level_extra: bmp.obj.LevelObjectExtra = {"icon": {"name": text_minus_obj.json_name, "color": bmp.color.current_palette[text_minus_obj.sprite_palette]}}
                    if text_minus_obj.level_id is not None:
                        space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, level_id=self.level_id, level_extra=level_extra))
                    else:
                        space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, level_id=self.level_id, level_extra=level_extra))
                elif issubclass(new_type, bmp.obj.SpaceObject):
                    if text_minus_obj.space_id is not None:
                        space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, space_id=text_minus_obj.space_id))
                    else:
                        space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, space_id=space.space_id))
                else:
                    space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.orient, space_id=text_minus_obj.space_id, level_id=text_minus_obj.level_id))
            for obj in delete_list:
                self.destroy_obj(space, obj)
    def game(self) -> None:
        for space in self.space_list:
            for game_obj in space.get_objs_from_type(bmp.obj.Game):
                if bmp.base.current_os == bmp.base.windows:
                    if os.path.exists("submp.exe"):
                        os.system(f"start submp.exe {game_obj.ref_type.json_name}")
                    elif os.path.exists("submp.py"):
                        os.system(f"start /b python submp.py {game_obj.ref_type.json_name}")
                elif bmp.base.current_os == bmp.base.linux:
                    os.system(f"python ./submp.py {game_obj.ref_type.json_name} &")
    def win(self) -> bool:
        if self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextWin):
            return True
        for space in self.space_list:
            you_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextYou)]
            win_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextWin)]
            for you_obj in you_objs:
                if you_obj in win_objs:
                    return True
                if space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextWin):
                    if not you_obj.properties.enabled(bmp.obj.TextFloat):
                        return True
                for win_obj in win_objs:
                    if you_obj.pos == win_obj.pos:
                        if bmp.obj.same_float_prop(you_obj, win_obj):
                            return True
        return False
    def end(self) -> bool:
        if self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextEnd):
            return True
        for space in self.space_list:
            you_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextYou)]
            end_objs = [o for o in space.object_list if o.properties.enabled(bmp.obj.TextEnd)]
            for you_obj in you_objs:
                if you_obj in end_objs:
                    return True
                if space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextEnd):
                    if not you_obj.properties.enabled(bmp.obj.TextFloat):
                        return True
                for end_obj in end_objs:
                    if you_obj.pos == end_obj.pos:
                        if bmp.obj.same_float_prop(you_obj, end_obj):
                            return True
        return False
    def done(self) -> bool:
        for space in self.space_list:
            delete_list = []
            if self.properties[bmp.obj.default_level_object_type].enabled(bmp.obj.TextDone):
                delete_list.extend(space.object_list)
            if space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextDone):
                delete_list.extend(space.object_list)
            for obj in space.object_list:
                if obj.properties.enabled(bmp.obj.TextDone):
                    delete_list.append(obj)
            for obj in delete_list:
                space.del_obj(obj)
            if len(delete_list) != 0 and "done" not in self.sound_events:
                self.sound_events.append("done")
        for space in self.space_list:
            for obj in [o for o in space.object_list if bmp.obj.TextAll().isreferenceof(o, all_list = self.all_list)]:
                if not obj.properties.enabled(bmp.obj.TextDone):
                    return False
        return len(delete_list) > 0
    def have_you(self) -> bool:
        for space in self.space_list:
            for obj in space.object_list:
                if obj.properties.enabled(bmp.obj.TextYou):
                    return True
        return False
    def recursion_get_object_surface_info(
        self,
        old_pos: bmp.loc.Coord[int],
        old_space_id: bmp.ref.SpaceID,
        current_space_id: bmp.ref.SpaceID,
        depth: int = 0,
        passed: Optional[list[bmp.ref.SpaceID]] = None
    ) -> list[tuple[int, tuple[float, float], tuple[float, float]]]:
        return_list: list[tuple[int, tuple[float, float], tuple[float, float]]] = []
        current_space = self.get_space(current_space_id)
        if current_space is None:
            return []
        if current_space_id == old_space_id:
            return [(
                depth + 1,
                (old_pos[0] / current_space.width, old_pos[1] / current_space.height),
                (1 / current_space.width, 1 / current_space.height)
            )]
        passed = copy.deepcopy(passed) if passed is not None else []
        new_passed = copy.deepcopy(passed)
        if current_space_id in passed:
            inf_sub_space = self.get_space(current_space_id - 1)
            if inf_sub_space is None:
                return []
            for space_obj in current_space.get_spaces():
                if current_space_id - 1 != space_obj.space_id:
                    continue
                for new_depth, new_pos, new_size in self.recursion_get_object_surface_info(old_pos, old_space_id, current_space_id - 1, passed=new_passed):
                    return_list.append((
                        new_depth + 1,
                        bmp.loc.transform_relative_pos(
                            bmp.loc.default_space_transform, # NotImplemented
                            ((new_pos[0] + space_obj.x) / current_space.width, (new_pos[1] + space_obj.y) / current_space.height)
                        ),
                        bmp.loc.transform_relative_pos(
                            bmp.loc.default_space_transform, # NotImplemented
                            (new_size[0] / current_space.width, new_size[1] / current_space.height)
                        )
                    ))
            return return_list
        new_passed.append(copy.deepcopy(current_space_id))
        for space_obj in current_space.get_spaces():
            if space_obj.space_id is None:
                continue
            if space_obj.space_id in passed:
                continue
            sub_space = self.get_space(space_obj.space_id)
            if sub_space is None:
                continue
            transform = sub_space.get_stacked_transform(space_obj.space_extra["static_transform"], space_obj.space_extra["dynamic_transform"])
            for new_depth, new_pos, new_size in self.recursion_get_object_surface_info(old_pos, old_space_id, space_obj.space_id, passed=new_passed):
                return_list.append((
                    new_depth + 1,
                    bmp.loc.transform_relative_pos(
                        transform,
                        ((new_pos[0] + space_obj.x) / current_space.width, (new_pos[1] + space_obj.y) / current_space.height)
                    ),
                    bmp.loc.transform_relative_pos(
                        transform,
                        (new_size[0] / current_space.width, new_size[1] / current_space.height)
                    )
                ))
        return return_list
    def space_to_surface(self, space: bmp.space.Space, wiggle: int, size: bmp.loc.Coord[int], depth: int = 0, smooth: Optional[float] = None, cursor: Optional[bmp.loc.Coord[int]] = None, debug: bool = False) -> pygame.Surface:
        pixel_size = math.ceil(max(size[0] / space.width, size[1] / space.height) / bmp.render.sprite_size)
        scaled_sprite_size = pixel_size * bmp.render.sprite_size
        if depth > bmp.opt.options["render"]["space_depth"] or space.properties[bmp.obj.default_space_object_type].enabled(bmp.obj.TextHide):
            space_surface = pygame.Surface((scaled_sprite_size, scaled_sprite_size), pygame.SRCALPHA)
            space_surface.fill(space.color if space.color is not None else bmp.color.current_palette[0, 4])
            space_surface = bmp.render.simple_object_to_surface(bmp.obj.SpaceObject((0, 0), space_id=space.space_id), default_surface=space_surface)
            return space_surface
        space_surface_size = (space.width * scaled_sprite_size, space.height * scaled_sprite_size)
        space_surface = pygame.Surface(space_surface_size, pygame.SRCALPHA)
        # get objects
        object_list: list[bmp.obj.Object] = []
        obj_surface_list: list[tuple[bmp.loc.Coord[float], bmp.loc.Coord[float], pygame.Surface, bmp.obj.Object]] = []
        object_list.extend([o for o in space.object_list if bmp.render.valid(o) and (space.space_id, o) not in object_list])
        for obj in object_list:
            if not bmp.render.valid(obj):
                continue
            if obj.properties.enabled(bmp.obj.TextHide):
                continue
            obj_surface: pygame.Surface = bmp.render.simple_object_to_surface(obj, wiggle=wiggle, debug=debug)
            if self.game_properties.enabled(bmp.obj.TextWord):
                object_type = type(obj)
                for _ in range(self.game_properties.count(bmp.obj.TextWord)):
                    object_type = bmp.obj.get_noun_from_type(object_type)
                obj_surface = bmp.render.simple_type_to_surface(object_type, wiggle=wiggle, debug=debug)
            obj_surface_pos: bmp.loc.Coord[float] = (float(obj.x), float(obj.y))
            obj_surface_size: bmp.loc.Coord[float] = (1.0, 1.0)
            if isinstance(obj, bmp.obj.SpaceObject):
                sub_space = self.get_space(obj.space_id)
                if sub_space is not None:
                    default_surface = self.space_to_surface(sub_space, wiggle, (scaled_sprite_size, scaled_sprite_size), depth + 1, smooth)
                else:
                    default_surface = None
                obj_surface = bmp.render.simple_object_to_surface(obj, wiggle=wiggle, default_surface=default_surface, debug=debug)
                transform = bmp.loc.get_stacked_transform(obj.space_extra["static_transform"], obj.space_extra["dynamic_transform"])
                if transform["flip"]:
                    obj_surface = pygame.transform.flip(obj_surface, flip_x=True, flip_y=False)
                match transform["direct"]:
                    case "W": obj_surface = pygame.transform.rotate(obj_surface, 180)
                    case "S": pass
                    case "A": obj_surface = pygame.transform.rotate(obj_surface, 270)
                    case "D": obj_surface = pygame.transform.rotate(obj_surface, 90)
            obj_surface_list.append((obj_surface_pos, obj_surface_size, obj_surface, obj))
        # blit objects
        obj_surface_list.sort(key=lambda o: [f(o[-1]) for f in bmp.render.order].index(True), reverse=True)
        for obj_surface_pos, obj_surface_size, obj_surface, obj in obj_surface_list:
            if obj.old_state.new_surface_pos is None:
                obj.old_state.new_surface_pos = obj_surface_pos
            if obj.old_state.new_surface_size is None:
                obj.old_state.new_surface_size = obj_surface_size
            if smooth is not None and obj.old_state.level == self.level_id and obj.old_state.space == space.space_id:
                if obj.old_state.old_surface_pos is not None:
                    obj_surface_pos = bmp.render.calc_smooth_coord(obj.old_state.old_surface_pos, smooth, obj_surface_pos)
                if obj.old_state.old_surface_size is not None:
                    obj_surface_size = bmp.render.calc_smooth_coord(obj.old_state.old_surface_size, smooth, obj_surface_size)
            space_surface.blit(
                pygame.transform.scale(
                    obj_surface, (int(obj_surface_size[0] * scaled_sprite_size), int(obj_surface_size[1] * scaled_sprite_size))
                ),
                (int(obj_surface_pos[0] * scaled_sprite_size), int(obj_surface_pos[1] * scaled_sprite_size))
            )
        # cursor
        if cursor is not None:
            surface = bmp.render.current_sprites.get("cursor", 0, wiggle, raw=True).copy()
            pos = (cursor[0] * scaled_sprite_size - (surface.get_width() - bmp.render.sprite_size) * pixel_size // 2,
                   cursor[1] * scaled_sprite_size - (surface.get_height() - bmp.render.sprite_size) * pixel_size // 2)
            space_surface.blit(pygame.transform.scale(surface, (pixel_size * surface.get_width(), pixel_size * surface.get_height())), pos)
        # background
        space_background = pygame.Surface(space_surface.get_size(), pygame.SRCALPHA)
        space_background.fill(pygame.Color(*bmp.color.hex_to_rgb(space.color if space.color is not None else bmp.color.current_palette[0, 4])))
        space_background.blit(space_surface, (0, 0))
        space_surface = space_background
        if space.space_id.infinite_tier != 0 and depth == 0:
            infinite_text_surface = bmp.render.current_sprites.get("text_infinity" if space.space_id.infinite_tier > 0 else "text_epsilon", 0, wiggle, raw=True)
            infinite_tier_surface = pygame.Surface((infinite_text_surface.get_width(), infinite_text_surface.get_height() * abs(space.space_id.infinite_tier)), pygame.SRCALPHA)
            infinite_tier_surface.fill("#00000000")
            for i in range(abs(space.space_id.infinite_tier)):
                infinite_tier_surface.blit(infinite_text_surface, (0, i * infinite_text_surface.get_height()))
            infinite_tier_surface = bmp.render.set_alpha(infinite_tier_surface, 0x80 if depth > 0 else 0x40)
            infinite_tier_surface = pygame.transform.scale_by(infinite_tier_surface, space.height * pixel_size / abs(space.space_id.infinite_tier))
            space_surface.blit(infinite_tier_surface, ((space_surface.get_width() - infinite_tier_surface.get_width()) // 2, 0))
        # transform
        transform = bmp.loc.get_stacked_transform(space.static_transform, space.dynamic_transform)
        if transform["flip"]:
            space_surface = pygame.transform.flip(space_surface, flip_x=True, flip_y=False)
        match transform["direct"]:
            case "W": space_surface = pygame.transform.rotate(space_surface, 180)
            case "S": pass
            case "A": space_surface = pygame.transform.rotate(space_surface, 270)
            case "D": space_surface = pygame.transform.rotate(space_surface, 90)
        return space_surface
    def to_json(self) -> LevelJson:
        json_object: LevelJson = {
            "id": self.level_id.to_json(),
            "spaces": [s.to_json() for s in self.space_included],
            "current_space": self.current_space_id.to_json(),
        }
        if self.super_level_id is not None:
            json_object["super_level"] = self.super_level_id.to_json()
        if self.map_info is not None:
            json_object["map_info"] = self.map_info
        return json_object

type AnyLevelJson = LevelJson41 | LevelJson

def formatted_currently(json_object: AnyLevelJson, ver: str) -> TypeGuard[LevelJson]:
    return bmp.base.compare_versions(ver, bmp.base.version) == 0

def formatted_from_future(json_object: AnyLevelJson, ver: str) -> TypeGuard[AnyLevelJson]:
    return bmp.base.compare_versions(ver, bmp.base.version) > 0

def update_json_format(json_object: AnyLevelJson, ver: str) -> LevelJson:
    return json_object # old levelpacks aren't able to update in 4.1

def json_to_level(json_object: LevelJson) -> Level:
    level_id: bmp.ref.LevelID = bmp.ref.LevelID(**json_object["id"])
    space_id_list: list[bmp.ref.SpaceID] = [bmp.ref.SpaceID(**s) for s in json_object["spaces"]]
    current_space_id: bmp.ref.SpaceID = bmp.ref.SpaceID(**json_object["current_space"])
    super_level_id: Optional[bmp.ref.LevelID] = None
    super_level_json = json_object.get("super_level")
    if super_level_json is not None:
        super_level_id = bmp.ref.LevelID(**super_level_json)
    map_info: Optional[MapLevelExtraJson] = json_object.get("map_info")
    return Level(
        level_id = level_id,
        space_included = space_id_list,
        current_space_id = current_space_id,
        super_level_id = super_level_id,
        map_info = map_info,
    )