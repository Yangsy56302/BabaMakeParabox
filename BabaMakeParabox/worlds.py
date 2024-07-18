from typing import Any, Optional
import uuid
import random

from BabaMakeParabox import colors
from BabaMakeParabox import spaces
from BabaMakeParabox import objects
from BabaMakeParabox import rules
from BabaMakeParabox import displays

import pygame

def match_pos(obj: objects.Object, pos: spaces.Coord) -> bool:
    return obj.pos == pos

class world(object):
    class_name: str = "world"
    def __init__(self, name: str, size: tuple[int, int], inf_tier: int = 0, color: Optional[colors.ColorHex] = None) -> None:
        self.name: str = name
        self.inf_tier: int = inf_tier
        self.width: int = size[0]
        self.height: int = size[1]
        self.color: colors.ColorHex = color if color is not None else colors.random_world_color()
        self.object_list: list[objects.Object] = []
        self.rule_list: list[rules.Rule] = []
        self.strict_rule_list: list[rules.Rule] = []
    def __eq__(self, world: "world") -> bool:
        return self.name == world.name and self.inf_tier == world.inf_tier
    def __str__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def __repr__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def out_of_range(self, coord: spaces.Coord) -> bool:
        return coord[0] < 0 or coord[1] < 0 or coord[0] >= self.width or coord[1] >= self.height
    def new_obj(self, obj: objects.Object) -> bool:
        self.object_list.append(obj)
        return True
    def get_obj(self, uid: uuid.UUID) -> Optional[objects.Object]:
        res = [o for o in self.object_list if uid == o.uuid]
        return res[0] if len(res) != 0 else None
    def get_objs_from_pos_and_type[T: objects.Object](self, pos: spaces.Coord, obj_type: type[T]) -> list[T]:
        return [o for o in self.object_list if isinstance(o, obj_type) and match_pos(o, pos)]
    def get_objs_from_pos(self, pos: spaces.Coord) -> list[objects.Object]:
        return [o for o in self.object_list if match_pos(o, pos)]
    def get_objs_from_type[T: objects.Object](self, obj_type: type[T]) -> list[T]:
        return [o for o in self.object_list if isinstance(o, obj_type)]
    def del_obj(self, uid: uuid.UUID) -> bool:
        for i in range(len(self.object_list)):
            if uid == self.object_list[i].uuid:
                self.object_list.pop(i)
                return True
        return False
    def del_obj_from_pos_and_type(self, pos: spaces.Coord, obj_type: type) -> bool:
        for i in range(len(self.object_list)):
            if match_pos(self.object_list[i], pos) and isinstance(self.object_list[i], obj_type):
                self.object_list.pop(i)
                return True
        return False
    def del_objs_from_pos_and_type(self, pos: spaces.Coord, obj_type: type) -> bool:
        old_length = len(self.object_list)
        new_objects = filter(lambda o: not match_pos(o, pos) and isinstance(o, obj_type), self.object_list)
        self.object_list = list(new_objects)
        new_length = len(self.object_list)
        return old_length - new_length > 0
    def del_objs_from_pos(self, pos: spaces.Coord) -> bool:
        old_length = len(self.object_list)
        new_objects = filter(lambda o: not match_pos(o, pos), self.object_list)
        self.object_list = list(new_objects)
        new_length = len(self.object_list)
        return old_length - new_length > 0
    def del_objs_from_type(self, obj_type: type[objects.Object]) -> bool:
        old_length = len(self.object_list)
        new_objects = filter(lambda o: not isinstance(o, obj_type), self.object_list)
        self.object_list = list(new_objects)
        new_length = len(self.object_list)
        return old_length - new_length > 0
    def get_worlds(self) -> list[objects.World]:
        return [o for o in self.object_list if isinstance(o, objects.World)]
    def get_worlds_from_pos(self, pos: spaces.Coord) -> list[objects.World]:
        return [o for o in self.object_list if isinstance(o, objects.World) and match_pos(o, pos)]
    def get_clones(self) -> list[objects.Clone]:
        return [o for o in self.object_list if isinstance(o, objects.Clone)]
    def get_clones_from_pos(self, pos: spaces.Coord) -> list[objects.Clone]:
        return [o for o in self.object_list if isinstance(o, objects.Clone) and match_pos(o, pos)]
    def get_levels(self) -> list[objects.Level]:
        return [o for o in self.object_list if isinstance(o, objects.Level)]
    def get_levels_from_pos(self, pos: spaces.Coord) -> list[objects.Level]:
        return [o for o in self.object_list if isinstance(o, objects.Level) and match_pos(o, pos)]
    def repeated_world_to_clone(self) -> None:
        world_objs = self.get_worlds()
        to_clone_objs: list[objects.World] = []
        for i in range(len(world_objs)):
            for j in range(len(world_objs)):
                if i == j:
                    continue
                if world_objs[i].name == world_objs[j].name and world_objs[i].inf_tier == world_objs[j].inf_tier:
                    if world_objs[j] not in to_clone_objs:
                        to_clone_objs.append(world_objs[j])
        random.shuffle(to_clone_objs)
        to_clone_objs = to_clone_objs[1:]
        for to_clone in to_clone_objs:
            self.new_obj(objects.Clone(to_clone.pos, to_clone.name, to_clone.inf_tier, to_clone.facing))
            self.del_obj(to_clone.uuid)
    def get_rules_from_pos_and_orient(self, stage: Optional[type[objects.Text]], pos: spaces.Coord, orient: spaces.Orient) -> list[rules.Rule]:
        if stage == objects.Noun:
            matches = (objects.Noun, )
            next_stage = objects.Operator
        elif stage == objects.Operator:
            matches = (objects.Operator, )
            next_stage = objects.Property
        elif stage == objects.Property:
            matches = (objects.Noun, objects.Property)
            next_stage = None
        elif stage is None:
            matches = ()
            next_stage = None
        text_objs = self.get_objs_from_pos_and_type(pos, objects.Text)
        word_objs = filter(lambda o: o.has_prop(objects.WORD) and match_pos(o, pos), self.object_list)
        text_objs.extend(map(lambda o: objects.nouns_objs_dicts.get_exist_noun(type(o))(o.pos), word_objs))
        if len(text_objs) == 0:
            if stage is None:
                return [[]]
            return []
        obj_types: list[type[objects.Text]] = []
        if stage is not None:
            for obj in text_objs:
                if isinstance(obj, matches):
                    obj_types.append(type(obj))
        remain_rules = self.get_rules_from_pos_and_orient(next_stage, spaces.pos_facing(pos, orient), orient)
        remain_not_rules = []
        not_objs = self.get_objs_from_pos_and_type(pos, objects.NOT)
        if len(not_objs) != 0 and stage in (objects.Noun, objects.Property):
            remain_not_rules = self.get_rules_from_pos_and_orient(stage, spaces.pos_facing(pos, orient), orient)
        and_objs = self.get_objs_from_pos_and_type(pos, objects.AND)
        remain_and_rules = []
        if len(and_objs) != 0 and stage in (objects.Operator, None):
            if stage == objects.Operator:
                remain_and_rules = self.get_rules_from_pos_and_orient(objects.Noun, spaces.pos_facing(pos, orient), orient)
            else:
                remain_and_rules = self.get_rules_from_pos_and_orient(objects.Property, spaces.pos_facing(pos, orient), orient)
        return_rules: list[rules.Rule] = []
        if remain_rules != []:
            for remain_rule in remain_rules:
                for obj_type in obj_types:
                    return_rules.append([obj_type] + remain_rule)
        if remain_not_rules != []:
            for remain_not_rule in remain_not_rules:
                return_rules.append([objects.NOT] + remain_not_rule)
                if remain_not_rule in return_rules:
                    return_rules.remove(remain_not_rule)
        if remain_and_rules != []:
            for remain_and_rule in remain_and_rules:
                return_rules.append([objects.AND] + remain_and_rule)
                if remain_and_rule in return_rules:
                    return_rules.remove(remain_and_rule)
        if len(return_rules) == 0:
            if stage is None:
                return [[]]
            return []
        return return_rules
    def get_rules(self) -> list[rules.Rule]:
        rule_list: list[rules.Rule] = []
        x_rule_dict: dict[int, list[rules.Rule]] = {}
        y_rule_dict: dict[int, list[rules.Rule]] = {}
        for rule_type in rules.basic_rule_types:
            for x in range(self.width):
                for y in range(self.height - len(rule_type) + 1):
                    y_rule_dict.setdefault(y, [])
                    new_rule_list = self.get_rules_from_pos_and_orient(objects.Noun, (x, y), spaces.S)
                    if new_rule_list is not None:
                        for rule_index in range(len(new_rule_list)):
                            part_of_old_rule = False
                            for old_y, old_rule_list in y_rule_dict.items():
                                old_rule_list_test = list(map(lambda r: list(r[y - old_y:]), old_rule_list))
                                if list(new_rule_list[rule_index]) in old_rule_list_test:
                                    part_of_old_rule = True
                            if not part_of_old_rule:
                                y_rule_dict[y].append(new_rule_list[rule_index])
            for y in range(self.height):
                for x in range(self.width - len(rule_type) + 1):
                    x_rule_dict.setdefault(x, [])
                    new_rule_list = self.get_rules_from_pos_and_orient(objects.Noun, (x, y), spaces.D)
                    if new_rule_list is not None:
                        for rule_index in range(len(new_rule_list)):
                            part_of_old_rule = False
                            for old_x, old_rule_list in x_rule_dict.items():
                                old_rule_list_test = list(map(lambda r: list(r[x - old_x:]), old_rule_list))
                                if list(new_rule_list[rule_index]) in old_rule_list_test:
                                    part_of_old_rule = True
                            if not part_of_old_rule:
                                x_rule_dict[x].append(new_rule_list[rule_index])
        for x_rule_list in x_rule_dict.values():
            rule_list.extend(x_rule_list)
        for y_rule_list in y_rule_dict.values():
            rule_list.extend(y_rule_list)
        return rule_list
    def set_sprite_states(self, round_num: int = 0) -> None:
        for obj in self.object_list:
            if isinstance(obj, objects.Tiled):
                w_pos = spaces.pos_facing(obj.pos, spaces.W)
                w = len(self.get_objs_from_pos_and_type(w_pos, type(obj))) != 0
                s_pos = spaces.pos_facing(obj.pos, spaces.S)
                s = len(self.get_objs_from_pos_and_type(s_pos, type(obj))) != 0
                a_pos = spaces.pos_facing(obj.pos, spaces.A)
                a = len(self.get_objs_from_pos_and_type(a_pos, type(obj))) != 0
                d_pos = spaces.pos_facing(obj.pos, spaces.D)
                d = len(self.get_objs_from_pos_and_type(d_pos, type(obj))) != 0
                wsad = {spaces.W: w, spaces.S: s, spaces.A: a, spaces.D: d}
            else:
                wsad = {spaces.W: False, spaces.S: False, spaces.A: False, spaces.D: False}
            displays.set_sprite_state(obj, round_num, wsad) # type: ignore
    def default_input_position(self, side: spaces.Orient) -> spaces.Coord:
        match side:
            case spaces.W:
                return (self.width // 2, -1)
            case spaces.A:
                return (-1, self.height // 2)
            case spaces.S:
                return (self.width // 2, self.height)
            case spaces.D:
                return (self.width, self.height // 2)
            case _:
                raise ValueError()
    def pos_to_transnum(self, pos: spaces.Coord, side: spaces.Orient) -> float:
        if side in (spaces.W, spaces.S):
            return (pos[0] + 0.5) / self.width
        else:
            return (pos[1] + 0.5) / self.height
    def transnum_to_pos(self, num: float, side: spaces.Orient) -> spaces.Coord:
        match side:
            case spaces.W:
                return (int((num * self.width)), -1)
            case spaces.S:
                return (int((num * self.width)), self.height)
            case spaces.A:
                return (-1, int((num * self.height)))
            case spaces.D:
                return (self.width, int((num * self.height)))
            case _:
                raise ValueError()
    def transnum_to_smaller_transnum(self, num: float, pos: spaces.Coord, side: spaces.Orient) -> float:
        if side in (spaces.W, spaces.S):
            return (num * self.width) - pos[0]
        else:
            return (num * self.height) - pos[1]
    def transnum_to_bigger_transnum(self, num: float, pos: spaces.Coord, side: spaces.Orient) -> float:
        if side in (spaces.W, spaces.S):
            return (num + pos[0]) / self.width
        else:
            return (num + pos[1]) / self.height
    def to_json(self) -> dict[str, Any]:
        json_object = {"name": self.name, "infinite_tier": self.inf_tier, "size": [self.width, self.height], "color": self.color, "object_list": []}
        for obj in self.object_list:
            json_object["object_list"].append(obj.to_json())
        return json_object

def json_to_world(json_object: dict[str, Any]) -> world: # oh hell no * 2
    new_world = world(name=json_object["name"], # type: ignore
                      inf_tier=json_object["infinite_tier"], # type: ignore
                      size=tuple(json_object["size"]), # type: ignore
                      color=json_object["color"]) # type: ignore
    for obj in json_object["object_list"]: # type: ignore
        new_world.new_obj(objects.json_to_object(obj)) # type: ignore
    return new_world