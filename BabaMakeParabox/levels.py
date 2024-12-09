from typing import Any, NotRequired, Optional, TypedDict
import random
import copy
import uuid
import math
import os

from BabaMakeParabox import basics, colors, positions, refs, objects, collects, rules, spaces, displays

import pygame

class MapLevelExtraJson(TypedDict):
    minimum_clear_for_blossom: int

class LevelJson(TypedDict):
    id: refs.LevelIDJson
    super_level: NotRequired[refs.LevelIDJson]
    map_info: NotRequired[MapLevelExtraJson]
    main_space: refs.SpaceIDJson
    space_list: list[spaces.SpaceJson]

max_move_count: int = 16
infinite_move_number: int = 16
MoveInfo = tuple[objects.Object, Optional[tuple[spaces.Space, positions.Coordinate, positions.Direction]]]

class Level(object):
    def __init__(self, level_id: refs.LevelID, space_list: list[spaces.Space], *, super_level_id: Optional[refs.LevelID] = None, main_space_id: Optional[refs.SpaceID] = None, map_info: Optional[MapLevelExtraJson] = None, collected: Optional[dict[type[collects.Collectible], bool]] = None, ) -> None:
        self.level_id: refs.LevelID = level_id
        self.space_list: list[spaces.Space] = list(space_list)
        self.super_level_id: Optional[refs.LevelID] = super_level_id
        self.main_space_id: refs.SpaceID = main_space_id if main_space_id is not None else space_list[0].space_id
        self.collected: dict[type[collects.Collectible], bool] = collected if collected is not None else {k: False for k in collects.collectible_dict.keys()}
        self.map_info: Optional[MapLevelExtraJson] = map_info
        self.properties: dict[type[objects.LevelObject], objects.Properties] = {p: objects.Properties() for p in objects.level_object_types}
        self.special_operator_properties: dict[type[objects.LevelObject], dict[type[objects.Operator], objects.Properties]] = {p: {o: objects.Properties() for o in objects.special_operators} for p in objects.level_object_types}
        self.game_properties: objects.Properties = objects.Properties()
        self.created_levels: list["Level"] = []
        self.all_list: list[type[objects.Noun]] = []
        self.group_references: dict[type[objects.GroupNoun], objects.Properties] = {p: objects.Properties() for p in objects.group_noun_types}
        self.sound_events: list[str] = []
    def __eq__(self, level: "Level") -> bool:
        return self.level_id == level.level_id
    @property
    def main_space(self) -> spaces.Space:
        return self.get_exact_space(self.main_space_id)
    def get_space(self, space_object_info: refs.SpaceID) -> Optional[spaces.Space]:
        for space in self.space_list:
            if space.space_id == space_object_info:
                return space
        return None
    def get_space_or_default(self, space_object_info: refs.SpaceID, *, default: spaces.Space) -> spaces.Space:
        space = self.get_space(space_object_info)
        if space is None:
            return default
        return space
    def get_exact_space(self, space_object_info: refs.SpaceID) -> spaces.Space:
        space = self.get_space(space_object_info)
        if space is None:
            raise KeyError(space_object_info)
        return space
    def set_space(self, space: spaces.Space) -> None:
        for i in range(len(self.space_list)):
            if space.space_id == self.space_list[i].space_id:
                self.space_list[i] = space
                return
        self.space_list.append(space)
    def find_super_spaces(self, space_object_info: refs.SpaceID) -> list[tuple[spaces.Space, objects.SpaceObject]]:
        return_value: list[tuple[spaces.Space, objects.SpaceObject]] = []
        for super_space in self.space_list:
            for obj in super_space.get_spaces():
                if space_object_info == obj.space_id:
                    return_value.append((super_space, obj))
        return return_value
    def refresh_all_list(self) -> None:
        for space in self.space_list:
            for obj in space.object_list:
                if all(map(lambda t: isinstance(obj, t), objects.types_not_in_all)):
                    noun_type = objects.get_noun_from_type(type(obj))
                    if noun_type not in self.all_list:
                        self.all_list.append(noun_type)
    def reset_move_numbers(self) -> None:
        for space in self.space_list:
            for obj in space.object_list:
                obj.move_number = 0
    def move_obj_between_spaces(self, old_space: spaces.Space, obj: objects.Object, new_space: spaces.Space, pos: positions.Coordinate) -> None:
        if obj in old_space.object_list:
            old_space.del_obj(obj)
        obj = copy.deepcopy(obj)
        obj.reset_uuid()
        obj.old_state.space = old_space.space_id
        obj.old_state.pos = obj.pos
        obj.pos = pos
        new_space.new_obj(obj)
    def move_obj_in_space(self, space: spaces.Space, obj: objects.Object, pos: positions.Coordinate) -> None:
        if obj in space.object_list:
            space.del_obj(obj)
        obj = copy.deepcopy(obj)
        obj.reset_uuid()
        obj.old_state.pos = obj.pos
        obj.pos = pos
        space.new_obj(obj)
    def move_objs_from_move_list(self, move_list: list[MoveInfo]) -> None:
        delete_list: list[objects.Object] = []
        move_list = basics.remove_same_elements(move_list)
        for move_obj, new_info in move_list:
            for space in self.space_list:
                if move_obj in space.object_list:
                    old_space = space
            if new_info is None:
                if move_obj not in delete_list:
                    delete_list.append(move_obj)
                continue
            new_space, new_pos, new_direct = new_info
            move_obj.move_number += 1
            if old_space == new_space:
                self.move_obj_in_space(old_space, move_obj, new_pos)
            else:
                self.move_obj_between_spaces(old_space, move_obj, new_space, new_pos)
            move_obj.direct = new_direct
        for del_obj in delete_list:
            for space in self.space_list:
                if del_obj in space.object_list:
                    space.del_obj(del_obj)
        if len(move_list) != 0 and "move" not in self.sound_events:
            self.sound_events.append("move")
    def meet_prefix_conditions(self, space: spaces.Space, obj: objects.Object, prefix_info_list: list[rules.PrefixInfo], is_meta: bool = False) -> bool:
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
    def meet_infix_conditions(self, space: spaces.Space, obj: objects.Object, infix_info_list: list[rules.InfixInfo], old_feeling: Optional[objects.Properties] = None) -> bool:
        for infix_info in infix_info_list:
            meet_infix_condition = True
            if infix_info.infix_type in (objects.TextOn, objects.TextNear, objects.TextNextto):
                matched_objs: list[objects.Object] = [obj]
                find_range: list[positions.Coordinate]
                if infix_info.infix_type == objects.TextOn:
                    find_range = [positions.Coordinate(obj.pos.x, obj.pos.y)]
                elif infix_info.infix_type == objects.TextNear:
                    find_range = [positions.Coordinate(obj.pos.x - 1, obj.pos.y - 1), positions.Coordinate(obj.pos.x, obj.pos.y - 1), positions.Coordinate(obj.pos.x + 1, obj.pos.y - 1),
                                  positions.Coordinate(obj.pos.x - 1, obj.pos.y), positions.Coordinate(obj.pos.x, obj.pos.y), positions.Coordinate(obj.pos.x + 1, obj.pos.y),
                                  positions.Coordinate(obj.pos.x - 1, obj.pos.y + 1), positions.Coordinate(obj.pos.x, obj.pos.y + 1), positions.Coordinate(obj.pos.x + 1, obj.pos.y + 1)]
                elif infix_info.infix_type == objects.TextNextto:
                    find_range = [positions.Coordinate(obj.pos.x, obj.pos.y - 1), positions.Coordinate(obj.pos.x - 1, obj.pos.y), positions.Coordinate(obj.pos.x + 1, obj.pos.y), positions.Coordinate(obj.pos.x, obj.pos.y + 1)]
                for match_negated, match_noun in infix_info[2]: # type: ignore
                    match_objs: list[objects.Object] = []
                    match_noun: type[objects.Noun]
                    match_noun_list: list[type[objects.Noun]] = []
                    if match_noun == objects.TextAll:
                        if match_negated:
                            match_noun_list = [o for o in self.all_list if issubclass(o, objects.nouns_in_not_all)]
                        else:
                            match_noun_list = [o for o in self.all_list if not issubclass(o, objects.nouns_not_in_all)]
                    else:
                        if match_negated:
                            match_noun_list = [o for o in self.all_list if (not issubclass(o, objects.nouns_not_in_all)) and not issubclass(o, match_noun)]
                        else:
                            match_noun_list = [match_noun]
                    for new_match_noun in match_noun_list:
                        if issubclass(new_match_noun, objects.SupportsIsReferenceOf):
                            for pos in find_range:
                                match_objs.extend([o for o in space.get_objs_from_pos_and_special_noun(pos, new_match_noun) if o not in matched_objs])
                        else:
                            new_match_type = new_match_noun.ref_type
                            for pos in find_range:
                                match_objs.extend([o for o in space.get_objs_from_pos_and_type(pos, new_match_type) if o not in matched_objs])
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
                        if old_feeling.enabled(infix_noun_info.infix_noun_type) == infix_noun_info.negated:
                            meet_infix_condition = False
            elif infix_info.infix_type == objects.TextWithout:
                meet_infix_condition = True
                matched_objs: list[objects.Object] = [obj]
                match_type_count: dict[tuple[bool, type[objects.Noun]], int] = {}
                for match_negated, match_noun in infix_info[2]: # type: ignore
                    match_noun: type[objects.Noun]
                    match_type_count.setdefault((match_negated, match_noun), 0)
                    match_type_count[(match_negated, match_noun)] += 1
                for (match_negated, match_noun), match_count in match_type_count.items():
                    match_objs: list[objects.Object] = []
                    match_noun: type[objects.Noun]
                    match_noun_list: list[type[objects.Noun]] = []
                    if match_noun == objects.TextAll:
                        if match_negated:
                            match_noun_list = [o for o in self.all_list if issubclass(o, objects.nouns_in_not_all)]
                        else:
                            match_noun_list = [o for o in self.all_list if not issubclass(o, objects.nouns_not_in_all)]
                    else:
                        if match_negated:
                            match_noun_list = [o for o in self.all_list if (not issubclass(o, objects.nouns_not_in_all)) and not issubclass(o, match_noun)]
                        else:
                            match_noun_list = [match_noun]
                    for new_match_noun in match_noun_list:
                        if issubclass(new_match_noun, objects.SupportsIsReferenceOf):
                            for pos in find_range:
                                match_objs.extend([o for o in space.get_objs_from_special_noun(new_match_noun) if o not in matched_objs])
                        else:
                            new_match_type = new_match_noun.ref_type
                            for pos in find_range:
                                match_objs.extend([o for o in space.get_objs_from_type(new_match_type) if o not in matched_objs])
                        if len(match_objs) >= match_count:
                            meet_infix_condition = False
                        else:
                            matched_objs.append(match_objs[0])
                    if not meet_infix_condition:
                        break
            if meet_infix_condition == infix_info.negated:
                return False
        return True
    def recursion_rules(self, space: spaces.Space, passed: Optional[list[refs.SpaceID]] = None) -> tuple[list[rules.Rule], list[rules.RuleInfo]]:
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
    def destroy_obj(self, space: spaces.Space, obj: objects.Object) -> None:
        space.del_obj(obj)
        for new_noun_type, new_noun_count in obj.special_operator_properties[objects.TextHas].enabled_dict().items(): # type: ignore
            new_noun_type: type[objects.Noun]
            if issubclass(new_noun_type, objects.RangedNoun):
                continue
            new_object_type: type[objects.Object] = new_noun_type.ref_type
            if issubclass(new_noun_type, objects.TextText):
                new_object_type = objects.get_noun_from_type(type(obj))
            for _ in range(new_noun_count):
                if issubclass(new_object_type, objects.Game):
                    if isinstance(obj, (objects.LevelObject, objects.SpaceObject)):
                        space.new_obj(objects.Game(obj.pos, obj.direct, ref_type=objects.get_noun_from_type(type(obj))))
                    else:
                        space.new_obj(objects.Game(obj.pos, obj.direct, ref_type=type(obj)))
                elif issubclass(new_object_type, objects.LevelObject):
                    level_object_extra: objects.LevelObjectExtra = {"icon": {"name": obj.json_name, "color": colors.current_palette[obj.sprite_color]}}
                    if obj.level_id is not None:
                        space.new_obj(new_object_type(obj.pos, obj.direct, level_id=obj.level_id, level_object_extra=level_object_extra))
                    else:
                        space.new_obj(new_object_type(obj.pos, obj.direct, level_id=self.level_id, level_object_extra=level_object_extra))
                elif issubclass(new_object_type, objects.SpaceObject):
                    if obj.space_id is not None:
                        space.new_obj(new_object_type(obj.pos, obj.direct, space_id=obj.space_id))
                    else:
                        space.new_obj(new_object_type(obj.pos, obj.direct, space_id=space.space_id))
                else:
                    space.new_obj(new_object_type(obj.pos, obj.direct, space_id=obj.space_id, level_id=obj.level_id))
    def get_move_list(self, space: spaces.Space, obj: objects.Object, \
        direct: positions.Direction, pos: Optional[positions.Coordinate] = None, \
            pushed: Optional[list[objects.Object]] = None, passed: Optional[list[refs.SpaceID]] = None, \
                transnum: Optional[float] = None, depth: int = 0) -> Optional[list[MoveInfo]]:
        if depth > 100:
            return None
        depth += 1
        pushed = pushed[:] if pushed is not None else []
        if obj in pushed:
            return None
        passed = passed[:] if passed is not None else []
        pos = pos if pos is not None else obj.pos
        new_pos = positions.front_position(pos, direct)
        exit_space = False
        exit_list: list[MoveInfo] = []
        if space.out_of_range(new_pos) and not obj.properties.disabled(objects.TextLeave):
            super_space_id = space.space_id
            if passed.count(space.space_id) > infinite_move_number:
                super_space_id = space.space_id + 1
            passed.append(space.space_id)
            if self.get_space(super_space_id) is None:
                exit_list.append((obj, None))
                exit_space = True
            else:
                super_space_list = self.find_super_spaces(super_space_id)
                for super_space, space_obj in super_space_list:
                    if super_space.properties[type(space_obj)].disabled(objects.TextLeave):
                        continue
                    new_transnum = super_space.transnum_to_bigger_transnum(transnum, space_obj.pos, direct) if transnum is not None else space.pos_to_transnum(obj.pos, direct)
                    new_move_list = self.get_move_list(super_space, obj, direct, space_obj.pos, pushed, passed, new_transnum, depth)
                    if new_move_list is not None:
                        exit_space = True
                        exit_list.extend(new_move_list)
        push_objects = [o for o in space.get_objs_from_pos(new_pos) if o.properties.enabled(objects.TextPush)]
        unpushable_objects: list[objects.Object] = []
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
                push_list.append((obj, (space, new_pos, direct)))
        simple = False
        if not space.out_of_range(new_pos):
            stop_objects = [o for o in space.get_objs_from_pos(new_pos) if o.properties.enabled(objects.TextStop) and not o.properties.enabled(objects.TextPush)]
            if len(stop_objects + unpushable_objects) != 0:
                if obj.properties.enabled(objects.TextOpen):
                    simple = True
                    for stop_object in stop_objects + unpushable_objects:
                        if not stop_object.properties.enabled(objects.TextShut):
                            simple = False
                elif obj.properties.enabled(objects.TextShut):
                    simple = True
                    for stop_object in stop_objects + unpushable_objects:
                        if not stop_object.properties.enabled(objects.TextOpen):
                            simple = False
            else:
                simple = True
        squeeze = False
        squeeze_list: list[MoveInfo] = []
        if isinstance(obj, objects.SpaceObject) and (not space.out_of_range(new_pos)) and (not simple) and len(stop_objects) == 0:
            sub_space = self.get_space(obj.space_id)
            if sub_space is not None:
                if not sub_space.properties[type(obj)].disabled(objects.TextEnter):
                    squeeze = True
                    for new_push_object in push_objects:
                        if new_push_object.properties.disabled(objects.TextEnter):
                            squeeze = False
                            break
                        input_pos = sub_space.default_input_position(direct)
                        squeeze_move_list = self.get_move_list(sub_space, new_push_object, positions.swap_direction(direct), input_pos, pushed=pushed + [obj], depth=depth)
                        if squeeze_move_list is None:
                            squeeze = False
                            break
                        squeeze_list.extend(squeeze_move_list)
            else:
                squeeze = True
                for new_push_object in push_objects:
                    if new_push_object.properties.disabled(objects.TextEnter):
                        squeeze = False
                        break
                    squeeze_list.append((new_push_object, None))
            if squeeze:
                squeeze_list.append((obj, (space, new_pos, direct)))
        enter_space = False
        enter_list: list[MoveInfo] = []
        if not space.out_of_range(new_pos) and not obj.properties.disabled(objects.TextEnter):
            sub_space_obj_list = [o for o in space.get_spaces_from_pos(new_pos) if not o.properties.disabled(objects.TextEnter)]
            for space_obj in sub_space_obj_list:
                sub_space = self.get_space(space_obj.space_id)
                if sub_space is None:
                    enter_space = True
                    continue
                input_pos = sub_space.transnum_to_pos(transnum, positions.swap_direction(direct)) if transnum is not None else sub_space.default_input_position(positions.swap_direction(direct))
                new_transnum = space.transnum_to_smaller_transnum(transnum, space_obj.pos, positions.swap_direction(direct)) if transnum is not None else 0.5
                if passed.count(sub_space.space_id) > infinite_move_number:
                    sub_space = self.get_space(sub_space.space_id - 1)
                    if sub_space is None:
                        enter_space = True
                        continue
                    input_pos = sub_space.default_input_position(positions.swap_direction(direct))
                    new_transnum = 0.5
                if sub_space.properties[type(space_obj)].disabled(objects.TextEnter):
                    continue
                passed.append(space.space_id)
                new_move_list = self.get_move_list(sub_space, obj, direct, input_pos, pushed, passed, new_transnum, depth)
                if new_move_list is not None:
                    enter_list.extend(new_move_list)
                    enter_space = True
        if enter_space and len(enter_list) == 0:
            enter_list.append((obj, None))
        if exit_space:
            return basics.remove_same_elements(exit_list)
        elif push:
            return basics.remove_same_elements(push_list)
        elif enter_space:
            return basics.remove_same_elements(enter_list)
        elif squeeze:
            return basics.remove_same_elements(squeeze_list)
        elif simple:
            return [(obj, (space, new_pos, direct))]
        else:
            return None
    def you(self, direct: positions.PlayerOperation) -> bool:
        self.reset_move_numbers()
        if direct == positions.NoDirect.O:
            return False
        pushing_game = False
        finished = False
        for _ in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for space in self.space_list:
                you_objs = [o for o in space.object_list if o.move_number < o.properties.get(objects.TextYou)]
                if len(you_objs) != 0:
                    finished = False
                for obj in you_objs:
                    obj.direct = direct
                    new_move_list = self.get_move_list(space, obj, obj.direct)
                    if new_move_list is not None:
                        move_list.extend(new_move_list)
                        obj.move_number += 1
                    else:
                        pushing_game = True
            move_list = basics.remove_same_elements(move_list)
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def select(self, direct: positions.PlayerOperation) -> Optional[refs.LevelID]:
        if direct == positions.NoDirect.O:
            level_objs: list[objects.LevelObject] = []
            for space in self.space_list:
                select_objs = [o for o in space.object_list if o.properties.enabled(objects.TextSelect)]
                for obj in select_objs:
                    level_objs.extend(space.get_levels_from_pos(obj.pos))
            if len(level_objs) != 0:
                return random.choice(level_objs).level_id
        else:
            for space in self.space_list:
                select_objs = [o for o in space.object_list if o.properties.enabled(objects.TextSelect)]
                for obj in select_objs:
                    new_pos = positions.front_position(obj.pos, direct)
                    if not space.out_of_range(new_pos):
                        level_objs = space.get_levels_from_pos(new_pos)
                        path_objs = space.get_objs_from_pos_and_type(new_pos, objects.Path)
                        if any(map(lambda p: p.unlocked, path_objs)) or len(level_objs) != 0:
                            self.move_obj_in_space(space, obj, new_pos)
            return None
    def move(self) -> bool:
        self.reset_move_numbers()
        pushing_game = False
        for space in self.space_list:
            global_move_count = space.properties[objects.default_space_object_type].get(objects.TextMove) + self.properties[objects.default_level_object_type].get(objects.TextMove)
            for _ in range(global_move_count):
                move_list = []
                for obj in [o for o in space.object_list if o.move_number < global_move_count]:
                    if not obj.properties.enabled(objects.TextFloat):
                        new_move_list = self.get_move_list(space, obj, positions.Direction.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                            obj.move_number += 1
                        else:
                            pushing_game = True
                move_list = basics.remove_same_elements(move_list)
                self.move_objs_from_move_list(move_list)
        self.reset_move_numbers()
        finished = False
        for _ in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for space in self.space_list:
                move_objs = [o for o in space.object_list if o.move_number < o.properties.get(objects.TextMove)]
                if len(move_objs) != 0:
                    finished = False
                for obj in move_objs:
                    new_move_list = self.get_move_list(space, obj, obj.direct)
                    if new_move_list is not None:
                        move_list = new_move_list
                        obj.move_number += 1
                    else:
                        obj.direct = positions.swap_direction(obj.direct)
                        new_move_list = self.get_move_list(space, obj, obj.direct)
                        if new_move_list is not None:
                            move_list = new_move_list
                            obj.move_number += 1
                        else:
                            pushing_game = True
            move_list = basics.remove_same_elements(move_list)
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def shift(self) -> bool:
        self.reset_move_numbers()
        pushing_game = False
        for space in self.space_list:
            global_shift_count = space.properties[objects.default_space_object_type].get(objects.TextShift) + self.properties[objects.default_level_object_type].get(objects.TextShift)
            for _ in range(global_shift_count):
                move_list = []
                for obj in [o for o in space.object_list if o.move_number < global_shift_count]:
                    if not obj.properties.enabled(objects.TextFloat):
                        new_move_list = self.get_move_list(space, obj, positions.Direction.S)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                            obj.move_number += 1
                        else:
                            pushing_game = True
                move_list = basics.remove_same_elements(move_list)
                self.move_objs_from_move_list(move_list)
        self.reset_move_numbers()
        finished = False
        for _ in range(max_move_count):
            if finished:
                return pushing_game
            move_list = []
            finished = True
            for space in self.space_list:
                shifter_objs = [o for o in space.object_list if o.move_number < o.properties.get(objects.TextShift)]
                for shifter_obj in shifter_objs:
                    shifted_objs = [o for o in space.get_objs_from_pos(shifter_obj.pos) if obj != shifter_obj and objects.same_float_prop(obj, shifter_obj)]
                    for obj in shifted_objs:
                        new_move_list = self.get_move_list(space, obj, shifter_obj.direct)
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                            obj.move_number += 1
                            finished = False
                        else:
                            pushing_game = True
            move_list = basics.remove_same_elements(move_list)
            self.move_objs_from_move_list(move_list)
        return pushing_game
    def tele(self) -> None:
        if self.properties[objects.default_level_object_type].enabled(objects.TextTele):
            pass
        for space in self.space_list:
            if space.properties[objects.default_space_object_type].enabled(objects.TextTele):
                pass
        tele_list: list[tuple[spaces.Space, objects.Object, spaces.Space, positions.Coordinate]] = []
        object_list: list[tuple[spaces.Space, objects.Object]] = []
        for space in self.space_list:
            object_list.extend([(space, o) for o in space.object_list])
        tele_objs = [t for t in object_list if t[1].properties.enabled(objects.TextTele)]
        tele_object_types: dict[type[objects.Object], list[tuple[spaces.Space, objects.Object]]] = {}
        for object_type in [n.ref_type for n in objects.noun_class_list]:
            for tele_obj in tele_objs:
                if isinstance(tele_obj[1], object_type):
                    tele_object_types[object_type] = tele_object_types.get(object_type, []) + [tele_obj]
        for new_tele_objs in tele_object_types.values():
            if len(new_tele_objs) <= 1:
                continue
            for tele_space, tele_obj in new_tele_objs:
                other_tele_objs = new_tele_objs[:]
                other_tele_objs.remove((tele_space, tele_obj))
                for obj in space.get_objs_from_pos(tele_obj.pos):
                    if obj == tele_obj:
                        continue
                    if objects.same_float_prop(obj, tele_obj):
                        other_tele_space, other_tele_obj = random.choice(other_tele_objs)
                        tele_list.append((space, obj, other_tele_space, other_tele_obj.pos))
        for old_space, obj, new_space, pos in tele_list:
            self.move_obj_between_spaces(old_space, obj, new_space, pos)
        if len(tele_list) != 0:
            self.sound_events.append("tele")
    def sink(self) -> None:
        success = False
        for space in self.space_list:
            delete_list = []
            if space.properties[objects.default_space_object_type].enabled(objects.TextSink) or self.properties[objects.default_level_object_type].enabled(objects.TextSink):
                for obj in space.object_list:
                    if not obj.properties.enabled(objects.TextFloat):
                        delete_list.append(obj)
            sink_objs = [o for o in space.object_list if o.properties.enabled(objects.TextSink)]
            for sink_obj in sink_objs:
                for obj in space.get_objs_from_pos(sink_obj.pos):
                    if obj == sink_obj:
                        continue
                    if obj.pos == sink_obj.pos:
                        if objects.same_float_prop(obj, sink_obj):
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
            melt_objs = [o for o in space.object_list if o.properties.enabled(objects.TextMelt)]
            hot_objs = [o for o in space.object_list if o.properties.enabled(objects.TextHot)]
            if len(hot_objs) != 0 and (space.properties[objects.default_space_object_type].enabled(objects.TextMelt) or self.properties[objects.default_level_object_type].enabled(objects.TextMelt)):
                for melt_obj in melt_objs:
                    if not melt_obj.properties.enabled(objects.TextFloat):
                        delete_list.extend(space.object_list)
                continue
            if len(melt_objs) != 0 and (space.properties[objects.default_space_object_type].enabled(objects.TextHot) or self.properties[objects.default_level_object_type].enabled(objects.TextHot)):
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
                self.destroy_obj(space, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("melt")
    def defeat(self) -> None:
        success = False
        for space in self.space_list:
            delete_list = []
            you_objs = [o for o in space.object_list if o.properties.enabled(objects.TextYou)]
            defeat_objs = [o for o in space.object_list if o.properties.enabled(objects.TextDefeat)]
            if len(defeat_objs) != 0 and (space.properties[objects.default_space_object_type].enabled(objects.TextYou) or self.properties[objects.default_level_object_type].enabled(objects.TextYou)):
                delete_list.extend(space.object_list)
                continue
            for you_obj in you_objs:
                if space.properties[objects.default_space_object_type].enabled(objects.TextDefeat) or self.properties[objects.default_level_object_type].enabled(objects.TextDefeat):
                    if you_obj not in delete_list:
                        delete_list.append(you_obj)
                        continue
                for defeat_obj in defeat_objs:
                    if you_obj.pos == defeat_obj.pos:
                        if objects.same_float_prop(defeat_obj, you_obj):
                            if you_obj not in delete_list:
                                delete_list.append(you_obj)
            for obj in delete_list:
                self.destroy_obj(space, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.sound_events.append("defeat")
    def bonus(self) -> None:
        success = False
        for space in self.space_list:
            delete_list = []
            bonus_objs = [o for o in space.object_list if o.properties.enabled(objects.TextBonus)]
            you_objs = [o for o in space.object_list if o.properties.enabled(objects.TextYou)]
            if len(you_objs) != 0 and (space.properties[objects.default_space_object_type].enabled(objects.TextBonus) or self.properties[objects.default_level_object_type].enabled(objects.TextBonus)):
                delete_list.extend(space.object_list)
                continue
            for bonus_obj in bonus_objs:
                if space.properties[objects.default_space_object_type].enabled(objects.TextYou) or self.properties[objects.default_level_object_type].enabled(objects.TextYou):
                    if bonus_obj not in delete_list:
                        delete_list.append(bonus_obj)
                        continue
                for you_obj in you_objs:
                    if bonus_obj.pos == you_obj.pos:
                        if objects.same_float_prop(you_obj, bonus_obj):
                            if bonus_obj not in delete_list:
                                delete_list.append(bonus_obj)
            for obj in delete_list:
                self.destroy_obj(space, obj)
            if len(delete_list) != 0:
                success = True
        if success:
            self.collected[collects.Bonus] = True
            self.sound_events.append("bonus")
    def open_and_shut(self) -> None:
        success = False
        for space in self.space_list:
            delete_list = []
            shut_objs = [o for o in space.object_list if o.properties.enabled(objects.TextShut)]
            open_objs = [o for o in space.object_list if o.properties.enabled(objects.TextOpen)]
            if len(open_objs) != 0 and (space.properties[objects.default_space_object_type].enabled(objects.TextShut) or self.properties[objects.default_level_object_type].enabled(objects.TextShut)):
                delete_list.extend(space.object_list)
                continue
            if len(shut_objs) != 0 and (space.properties[objects.default_space_object_type].enabled(objects.TextOpen) or self.properties[objects.default_level_object_type].enabled(objects.TextOpen)):
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
                for make_noun_type, make_noun_count in obj.special_operator_properties[objects.TextMake].enabled_dict().items(): # type: ignore
                    make_noun_type: type[objects.Noun]
                    if issubclass(make_noun_type, objects.RangedNoun):
                        continue
                    make_object_type: type[objects.Object] = make_noun_type.ref_type
                    if issubclass(make_noun_type, objects.TextText):
                        make_object_type = objects.get_noun_from_type(type(obj))
                    if len(space.get_objs_from_pos_and_type(obj.pos, make_object_type)) != 0:
                        continue
                    for _ in range(make_noun_count):
                        if issubclass(make_object_type, objects.Game):
                            if isinstance(obj, (objects.LevelObject, objects.SpaceObject)):
                                space.new_obj(objects.Game(obj.pos, obj.direct, ref_type=objects.get_noun_from_type(type(obj))))
                            else:
                                space.new_obj(objects.Game(obj.pos, obj.direct, ref_type=type(obj)))
                        elif issubclass(make_object_type, objects.LevelObject):
                            if len(space.get_objs_from_pos_and_type(obj.pos, make_object_type)) == 0:
                                level_object_extra: objects.LevelObjectExtra = {"icon": {"name": obj.json_name, "color": colors.current_palette[obj.sprite_color]}}
                                if obj.level_id is not None:
                                    space.new_obj(make_object_type(obj.pos, obj.direct, level_id=obj.level_id, level_object_extra=level_object_extra))
                                else:
                                    space.new_obj(make_object_type(obj.pos, obj.direct, level_id=self.level_id, level_object_extra=level_object_extra))
                        elif issubclass(make_object_type, objects.SpaceObject):
                            if len(space.get_objs_from_pos_and_type(obj.pos, make_object_type)) == 0:
                                if obj.space_id is not None:
                                    space.new_obj(make_object_type(obj.pos, obj.direct, space_id=obj.space_id))
                                else:
                                    space.new_obj(make_object_type(obj.pos, obj.direct, space_id=space.space_id))
                        else:
                            space.new_obj(make_object_type(obj.pos, obj.direct, space_id=obj.space_id, level_id=obj.level_id))
    def text_plus_and_text_minus(self) -> None:
        for space in self.space_list:
            delete_list = []
            text_plus_objs = [o for o in space.object_list if o.properties.enabled(objects.TextTextPlus)]
            text_minus_objs = [o for o in space.object_list if o.properties.enabled(objects.TextTextMinus)]
            for text_plus_obj in text_plus_objs:
                if text_plus_obj in text_minus_objs:
                    continue
                new_type = objects.get_noun_from_type(type(text_plus_obj))
                if not issubclass(new_type, objects.TextText):
                    delete_list.append(text_plus_obj)
                    space.new_obj(new_type(text_plus_obj.pos, text_plus_obj.direct, space_id=text_plus_obj.space_id, level_id=text_plus_obj.level_id))
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
                    space.new_obj(objects.Game(text_minus_obj.pos, text_minus_obj.direct, ref_type=objects.TextGame))
                elif issubclass(new_type, objects.LevelObject):
                    level_object_extra: objects.LevelObjectExtra = {"icon": {"name": text_minus_obj.json_name, "color": colors.current_palette[text_minus_obj.sprite_color]}}
                    if text_minus_obj.level_id is not None:
                        space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.direct, level_id=self.level_id, level_object_extra=level_object_extra))
                    else:
                        space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.direct, level_id=self.level_id, level_object_extra=level_object_extra))
                elif issubclass(new_type, objects.SpaceObject):
                    if text_minus_obj.space_id is not None:
                        space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.direct, space_id=text_minus_obj.space_id))
                    else:
                        space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.direct, space_id=space.space_id))
                else:
                    space.new_obj(new_type(text_minus_obj.pos, text_minus_obj.direct, space_id=text_minus_obj.space_id, level_id=text_minus_obj.level_id))
            for obj in delete_list:
                self.destroy_obj(space, obj)
    def game(self) -> None:
        for space in self.space_list:
            for game_obj in space.get_objs_from_type(objects.Game):
                if basics.current_os == basics.windows:
                    if os.path.exists("submp.exe"):
                        os.system(f"start submp.exe {game_obj.ref_type.json_name}")
                    elif os.path.exists("submp.py"):
                        os.system(f"start /b python submp.py {game_obj.ref_type.json_name}")
                elif basics.current_os == basics.linux:
                    os.system(f"python ./submp.py {game_obj.ref_type.json_name} &")
    def win(self) -> bool:
        for space in self.space_list:
            you_objs = [o for o in space.object_list if o.properties.enabled(objects.TextYou)]
            win_objs = [o for o in space.object_list if o.properties.enabled(objects.TextWin)]
            for you_obj in you_objs:
                if you_obj in win_objs:
                    self.collected[collects.Spore] = True
                    return True
                if space.properties[objects.default_space_object_type].enabled(objects.TextWin) or self.properties[objects.default_level_object_type].enabled(objects.TextWin):
                    if not you_obj.properties.enabled(objects.TextFloat):
                        self.collected[collects.Spore] = True
                        return True
                for win_obj in win_objs:
                    if you_obj.pos == win_obj.pos:
                        if objects.same_float_prop(you_obj, win_obj):
                            self.collected[collects.Spore] = True
                            return True
        return False
    def end(self) -> bool:
        for space in self.space_list:
            you_objs = [o for o in space.object_list if o.properties.enabled(objects.TextYou)]
            end_objs = [o for o in space.object_list if o.properties.enabled(objects.TextEnd)]
            for you_obj in you_objs:
                if you_obj in end_objs:
                    return True
                if space.properties[objects.default_space_object_type].enabled(objects.TextEnd) or self.properties[objects.default_level_object_type].enabled(objects.TextEnd):
                    if not you_obj.properties.enabled(objects.TextFloat):
                        return True
                for end_obj in end_objs:
                    if you_obj.pos == end_obj.pos:
                        if objects.same_float_prop(you_obj, end_obj):
                            return True
        return False
    def done(self) -> bool:
        for space in self.space_list:
            delete_list = []
            if space.properties[objects.default_space_object_type].enabled(objects.TextDone) or self.properties[objects.default_level_object_type].enabled(objects.TextDone):
                delete_list.extend(space.object_list)
            for obj in space.object_list:
                if obj.properties.enabled(objects.TextDone):
                    delete_list.append(obj)
            for obj in delete_list:
                space.del_obj(obj)
            if len(delete_list) != 0 and "done" not in self.sound_events:
                self.sound_events.append("done")
        for space in self.space_list:
            if [objects.TextAll, objects.TextIs, objects.TextDone] in space.rule_list:
                return True
        return False
    def have_you(self) -> bool:
        for space in self.space_list:
            for obj in space.object_list:
                if obj.properties.enabled(objects.TextYou):
                    return True
        return False
    def recursion_get_object_surface_info(self, old_pos: positions.Coordinate, old_space_id: refs.SpaceID, current_space_id: refs.SpaceID, depth: int = 0, passed: Optional[list[refs.SpaceID]] = None) -> list[tuple[int, tuple[float, float], tuple[float, float]]]:
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
        return_list: list[tuple[int, tuple[float, float], tuple[float, float]]] = []
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
                        ((new_pos[0] + space_obj.pos.x) / current_space.width, (new_pos[1] + space_obj.pos.y) / current_space.height),
                        (new_size[0] / current_space.width, new_size[1] / current_space.height)
                    ))
            return return_list
        new_passed.append(copy.deepcopy(current_space_id))
        for space_obj in current_space.get_spaces():
            if space_obj.space_id in passed:
                continue
            sub_space = self.get_space(space_obj.space_id)
            if sub_space is None:
                continue
            for new_depth, new_pos, new_size in self.recursion_get_object_surface_info(old_pos, old_space_id, space_obj.space_id, passed=new_passed):
                return_list.append((
                    new_depth + 1,
                    ((new_pos[0] + space_obj.pos.x) / current_space.width, (new_pos[1] + space_obj.pos.y) / current_space.height),
                    (new_size[0] / current_space.width, new_size[1] / current_space.height)
                ))
        return return_list
    def space_to_surface(self, space: spaces.Space, wiggle: int, size: positions.CoordTuple, depth: int = 0, smooth: Optional[float] = None, cursor: Optional[positions.Coordinate] = None, debug: bool = False) -> pygame.Surface:
        pixel_size = math.ceil(max(size[0] / space.width, size[1] / space.height) / displays.sprite_size)
        scaled_sprite_size = pixel_size * displays.sprite_size
        if depth > basics.options["space_display_recursion_depth"] or space.properties[objects.default_space_object_type].enabled(objects.TextHide):
            space_surface = pygame.Surface((scaled_sprite_size, scaled_sprite_size), pygame.SRCALPHA)
            space_surface.fill(space.color)
            space_surface = displays.simple_object_to_surface(objects.SpaceObject(positions.Coordinate(0, 0), space_id=space.space_id), default_surface=space_surface)
            return space_surface
        space_surface_size = (space.width * scaled_sprite_size, space.height * scaled_sprite_size)
        space_surface = pygame.Surface(space_surface_size, pygame.SRCALPHA)
        object_list: list[tuple[Optional[refs.SpaceID], objects.Object]] = []
        obj_surface_list: list[tuple[positions.Coordinate, positions.Coordinate, pygame.Surface, objects.Object]] = []
        for other_space in self.space_list:
            for other_object in other_space.object_list:
                if (smooth is not None) and other_object.old_state.space == space.space_id and isinstance(other_object, displays.order):
                    object_list.append((other_space.space_id, other_object))
        object_list.extend([(None, o) for o in space.object_list if isinstance(o, displays.order) and (space.space_id, o) not in object_list])
        for super_space_id, obj in object_list:
            if not isinstance(obj, displays.order):
                continue
            if obj.properties.enabled(objects.TextHide):
                continue
            obj_surface: pygame.Surface = displays.simple_object_to_surface(obj, wiggle=wiggle, debug=debug)
            obj_surface_pos: positions.Coordinate = positions.Coordinate(obj.pos.x * scaled_sprite_size, obj.pos.y * scaled_sprite_size)
            obj_surface_size: positions.Coordinate = positions.Coordinate(scaled_sprite_size, scaled_sprite_size)
            if isinstance(obj, objects.SpaceObject):
                space_of_object = self.get_space(obj.space_id)
                if space_of_object is not None:
                    default_surface = self.space_to_surface(space_of_object, wiggle, (scaled_sprite_size, scaled_sprite_size), depth + 1, smooth)
                    obj_surface = displays.simple_object_to_surface(obj, wiggle=wiggle, default_surface=default_surface, debug=debug)
            if (smooth is not None) and (obj.old_state.pos is not None):
                if smooth >= 0.0 and smooth <= 1.0:
                    old_surface_pos = positions.Coordinate(obj.old_state.pos[0] * scaled_sprite_size, obj.old_state.pos[1] * scaled_sprite_size)
                    if obj.old_state.space is not None:
                        new_surface_info = self.recursion_get_object_surface_info(obj.old_state.pos, obj.old_state.space, space.space_id)
                        if len(new_surface_info) != 0:
                            new_surface_info = sorted(new_surface_info, key=lambda t: t[0])
                            min_space_depth = new_surface_info[0][0]
                            for space_depth, old_surface_pos, old_surface_size in new_surface_info:
                                if space_depth > min_space_depth:
                                    break
                                if super_space_id is not None:
                                    old_super_space = self.get_exact_space(super_space_id)
                                    for old_super_space_object in [o for o in space.get_spaces() if o.space_id == super_space_id]:
                                        old_surface_pos = (obj.old_state.pos[0] * scaled_sprite_size, obj.old_state.pos[1] * scaled_sprite_size)
                                        old_surface_size = (scaled_sprite_size, scaled_sprite_size)
                                        new_surface_pos = ((obj.pos.x / old_super_space.width + old_super_space_object.pos.x) * scaled_sprite_size, (obj.pos.y / old_super_space.height + old_super_space_object.pos.y) * scaled_sprite_size)
                                        new_surface_size = (obj_surface_size[0] / old_super_space.width, obj_surface_size[1] / old_super_space.height)
                                        obj_surface_pos = positions.Coordinate(int(new_surface_pos[0] + (old_surface_pos[0] - new_surface_pos[0]) * smooth), int(new_surface_pos[1] + (old_surface_pos[1] - new_surface_pos[1]) * smooth))
                                        obj_surface_size = positions.Coordinate(int(new_surface_size[0] + (old_surface_size[0] - new_surface_size[0]) * smooth), int(new_surface_size[1] + (old_surface_size[1] - new_surface_size[1]) * smooth))
                                        obj_surface_list.append((obj_surface_pos, obj_surface_size, obj_surface, obj))
                                else:
                                    old_surface_pos = (old_surface_pos[0] * space_surface_size[0], old_surface_pos[1] * space_surface_size[1])
                                    old_surface_size = (old_surface_size[0] * space_surface_size[0], old_surface_size[1] * space_surface_size[1])
                                    obj_surface_pos = positions.Coordinate(int(obj_surface_pos[0] + (old_surface_pos[0] - obj_surface_pos[0]) * smooth), int(obj_surface_pos[1] + (old_surface_pos[1] - obj_surface_pos[1]) * smooth))
                                    obj_surface_size = positions.Coordinate(int(obj_surface_size[0] + (old_surface_size[0] - obj_surface_size[0]) * smooth), int(obj_surface_size[1] + (old_surface_size[1] - obj_surface_size[1]) * smooth))
                                    obj_surface_list.append((obj_surface_pos, obj_surface_size, obj_surface, obj))
                    else:
                        obj_surface_pos = positions.Coordinate(
                            int((obj_surface_pos[0] + (old_surface_pos[0] - obj_surface_pos[0]) * smooth)),
                            int((obj_surface_pos[1] + (old_surface_pos[1] - obj_surface_pos[1]) * smooth))
                        )
                        obj_surface_list.append((obj_surface_pos, obj_surface_size, obj_surface, obj))
                else:
                    raise ValueError(smooth)
            else:
                obj_surface_list.append((obj_surface_pos, obj_surface_size, obj_surface, obj))
        obj_surface_list.sort(key=lambda o: [isinstance(o[-1], t) for t in displays.order].index(True), reverse=True)
        for pos, size, surface, obj in obj_surface_list:
            space_surface.blit(pygame.transform.scale(surface, size), pos)
        if cursor is not None:
            surface = displays.current_sprites.get("cursor", 0, wiggle, raw=True).copy()
            pos = (cursor[0] * scaled_sprite_size - (surface.get_width() - displays.sprite_size) * pixel_size // 2,
                   cursor[1] * scaled_sprite_size - (surface.get_height() - displays.sprite_size) * pixel_size // 2)
            space_surface.blit(pygame.transform.scale(surface, (pixel_size * surface.get_width(), pixel_size * surface.get_height())), pos)
        space_background = pygame.Surface(space_surface.get_size(), pygame.SRCALPHA)
        space_background.fill(pygame.Color(*colors.hex_to_rgb(space.color)))
        space_background.blit(space_surface, (0, 0))
        space_surface = space_background
        if space.space_id.infinite_tier != 0 and depth == 0:
            infinite_text_surface = displays.current_sprites.get("text_infinity" if space.space_id.infinite_tier > 0 else "text_epsilon", 0, wiggle, raw=True)
            infinite_tier_surface = pygame.Surface((infinite_text_surface.get_width(), infinite_text_surface.get_height() * abs(space.space_id.infinite_tier)), pygame.SRCALPHA)
            infinite_tier_surface.fill("#00000000")
            for i in range(abs(space.space_id.infinite_tier)):
                infinite_tier_surface.blit(infinite_text_surface, (0, i * infinite_text_surface.get_height()))
            infinite_tier_surface = displays.set_alpha(infinite_tier_surface, 0x80 if depth > 0 else 0x40)
            infinite_tier_surface = pygame.transform.scale_by(infinite_tier_surface, space.height * pixel_size / abs(space.space_id.infinite_tier))
            space_surface.blit(infinite_tier_surface, ((space_surface.get_width() - infinite_tier_surface.get_width()) // 2, 0))
        return space_surface
    def to_json(self) -> LevelJson:
        json_object: LevelJson = {"id": self.level_id.to_json(), "space_list": [], "main_space": self.main_space_id.to_json()}
        if self.super_level_id is not None:
            json_object["super_level"] = self.super_level_id.to_json()
        if self.map_info is not None:
            json_object["map_info"] = self.map_info
        for space in self.space_list:
            json_object["space_list"].append(space.to_json())
        return json_object

def json_to_level(json_object: LevelJson, ver: Optional[str] = None) -> Level:
    space_list = []
    super_level_id: Optional[refs.LevelID] = None
    if basics.compare_versions(ver if ver is not None else "0.0", "3.8") == -1:
        level_id: refs.LevelID = refs.LevelID(json_object["name"]) # type: ignore
        super_level_id = refs.LevelID(json_object["super_level"]) # type: ignore
        main_space_id: refs.SpaceID = refs.SpaceID(json_object["main_world"]) # type: ignore
        for space in json_object["world_list"]: # type: ignore
            space_list.append(spaces.json_to_space(space, ver))
    elif basics.compare_versions(ver if ver is not None else "0.0", "3.91") == -1:
        level_id: refs.LevelID = refs.LevelID(**json_object["id"])
        super_level_json = json_object.get("super_level")
        if super_level_json is not None:
            super_level_id = refs.LevelID(**super_level_json)
        main_space_id: refs.SpaceID = refs.SpaceID(**json_object["main_world"]) # type: ignore
        for space in json_object["world_list"]: # type: ignore
            space_list.append(spaces.json_to_space(space, ver))
    else:
        level_id: refs.LevelID = refs.LevelID(**json_object["id"])
        super_level_json = json_object.get("super_level")
        if super_level_json is not None:
            super_level_id = refs.LevelID(**super_level_json)
        main_space_id: refs.SpaceID = refs.SpaceID(**json_object["main_space"])
        for space in json_object["space_list"]:
            space_list.append(spaces.json_to_space(space, ver))
    return Level(level_id=level_id,
                 space_list=space_list,
                 super_level_id=super_level_id,
                 main_space_id=main_space_id,
                 map_info=json_object.get("map_info"))