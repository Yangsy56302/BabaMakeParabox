from typing import Any, Optional
import pygame
import uuid

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.displays as displays

def match_pos(obj: objects.Object, pos: spaces.Coord) -> bool:
    return obj.pos == pos

class world(object):
    class_name: str = "world"
    def __init__(self, name: str, size: tuple[int, int], inf_tier: int = 0, color: Optional[pygame.Color] = None) -> None:
        self.uuid: uuid.UUID = uuid.uuid4()
        self.name: str = name
        self.inf_tier: int = inf_tier
        self.width: int = size[0]
        self.height: int = size[1]
        self.color: pygame.Color = color if color is not None else displays.random_hue()
        self.object_list: list[objects.Object] = []
        self.rule_list: list[rules.Rule] = []
    def __eq__(self, world: "world") -> bool:
        return self.uuid == world.uuid
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
    def get_rules_from_pos_and_orient(self, rule: rules.Rule, pos: spaces.Coord, orient: spaces.Orient) -> list[rules.Rule]:
        return_rules: list[rules.Rule] = []
        text_objs = self.get_objs_from_pos_and_type(pos, objects.Text)
        word_objs = filter(lambda o: o.has_prop(objects.WORD) and match_pos(o, pos), self.object_list)
        text_objs.extend(map(lambda o: objects.nouns_objs_dicts.get_noun(type(o))(o.pos), word_objs))
        if len(text_objs) == 0:
            return []
        if len(rule) == 1:
            for obj in text_objs:
                if isinstance(obj, rule[0]):
                    return_rules.append([type(obj)])
            return return_rules
        else:
            remain_rules = self.get_rules_from_pos_and_orient(rule[1:], spaces.pos_facing(pos, orient), orient)
            if len(remain_rules) == 0:
                return []
            getted_rules: list[rules.Rule] = []
            for obj in text_objs:
                if isinstance(obj, rule[0]):
                    getted_rules.append([type(obj)])
            if len(getted_rules) == 0:
                return []
            return_rules = []
            for remain_rule in remain_rules:
                for getted_rule in getted_rules:
                    return_rules.append(getted_rule + remain_rule)
            return return_rules
    def update_rules(self) -> None:
        self.rule_list = []
        for rule_type in rules.rule_types:
            for x in range(self.width):
                for y in range(self.height):
                    if x + len(rule_type) <= self.width:
                        self.rule_list.extend(self.get_rules_from_pos_and_orient(rule_type, (x, y), spaces.D))
                    if y + len(rule_type) <= self.height:
                        self.rule_list.extend(self.get_rules_from_pos_and_orient(rule_type, (x, y), spaces.S))
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
    def set_sprite_states(self, round_num: int = 0) -> None:
        for obj in self.object_list:
            if isinstance(obj, objects.Tiled):
                w_pos = spaces.pos_facing(obj.pos, spaces.W)
                w = self.out_of_range(w_pos) or len(self.get_objs_from_pos_and_type(w_pos, type(obj))) != 0
                s_pos = spaces.pos_facing(obj.pos, spaces.S)
                s = self.out_of_range(s_pos) or len(self.get_objs_from_pos_and_type(s_pos, type(obj))) != 0
                a_pos = spaces.pos_facing(obj.pos, spaces.A)
                a = self.out_of_range(a_pos) or len(self.get_objs_from_pos_and_type(a_pos, type(obj))) != 0
                d_pos = spaces.pos_facing(obj.pos, spaces.D)
                d = self.out_of_range(d_pos) or len(self.get_objs_from_pos_and_type(d_pos, type(obj))) != 0
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
    def to_json(self) -> basics.JsonObject:
        json_object = {"name": self.name, "infinite_tier": self.inf_tier, "size": [self.width, self.height],
                       "color": [self.color.r, self.color.g, self.color.b], "object_list": []}
        for obj in self.object_list:
            json_object["object_list"].append(obj.to_json())
        return json_object

def json_to_world(json_object: basics.JsonObject) -> world: # oh hell no * 2
    new_world = world(name=json_object["name"], # type: ignore
                      inf_tier=int(json_object["infinite_tier"]), # type: ignore
                      size=tuple(json_object["size"]), # type: ignore
                      color=pygame.Color(json_object["color"])) # type: ignore
    for obj in json_object["object_list"]: # type: ignore
        new_world.new_obj(objects.json_to_object(obj)) # type: ignore
    return new_world