from typing import Any, Optional
import pygame
import uuid

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.displays as displays

def match_pos(obj: objects.Object, pos: spaces.Coord) -> bool:
    return (obj.x, obj.y) == tuple(pos)

class level(object):
    class_name: str = "level"
    def __init__(self, name: str, size: tuple[int, int], inf_tier: int = 0, color: Optional[pygame.Color] = None) -> None:
        self.uuid: uuid.UUID = uuid.uuid4()
        self.name: str = name
        self.inf_tier: int = inf_tier
        self.width: int = size[0]
        self.height: int = size[1]
        self.color: pygame.Color = color if color is not None else displays.random_hue()
        self.object_list: list[objects.Object] = []
        self.rule_list: list[rules.Rule] = []
    def __eq__(self, level: "level") -> bool:
        return self.uuid == level.uuid
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
    def get_levels(self) -> list[objects.Level]:
        return [o for o in self.object_list if isinstance(o, objects.Level)]
    def get_levels_from_pos(self, pos: spaces.Coord) -> list[objects.Level]:
        return [o for o in self.object_list if isinstance(o, objects.Level) and match_pos(o, pos)]
    def get_clones(self) -> list[objects.Clone]:
        return [o for o in self.object_list if isinstance(o, objects.Clone)]
    def get_clones_from_pos(self, pos: spaces.Coord) -> list[objects.Clone]:
        return [o for o in self.object_list if isinstance(o, objects.Clone) and match_pos(o, pos)]
    def update_rules(self) -> None:
        self.rule_list = []
        text_objs = self.get_objs_from_type(objects.Text)
        noun_objs = [o for o in text_objs if isinstance(o, objects.Noun)]
        oper_objs = [o for o in text_objs if isinstance(o, objects.Operator)]
        prop_objs = [o for o in text_objs if isinstance(o, objects.Property)]
        for noun_obj in noun_objs:
            for oper_obj in oper_objs:
                if not spaces.on_line((noun_obj.x, noun_obj.y), (oper_obj.x, oper_obj.y)):
                    continue
                if not isinstance(oper_obj, objects.IS):
                    continue
                for prop_obj in prop_objs:
                    if not spaces.on_line((noun_obj.x, noun_obj.y), (oper_obj.x, oper_obj.y), (prop_obj.x, prop_obj.y)):
                        continue
                    self.rule_list.append((type(noun_obj), type(oper_obj), type(prop_obj)))
                for noun_obj_2 in noun_objs:
                    if not spaces.on_line((noun_obj.x, noun_obj.y), (oper_obj.x, oper_obj.y), (noun_obj_2.x, noun_obj_2.y)):
                        continue
                    self.rule_list.append((type(noun_obj), type(oper_obj), type(noun_obj_2)))
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
    def default_input_position(self, side: spaces.Orient) -> spaces.Coord:
        match side:
            case "W":
                return (self.width // 2, -1)
            case "A":
                return (-1, self.height // 2)
            case "S":
                return (self.width // 2, self.height)
            case "D":
                return (self.width, self.height // 2)
    def to_json(self) -> basics.JsonObject:
        json_object = {"name": self.name, "infinite_tier": self.inf_tier, "size": [self.width, self.height],
                       "color": [self.color.r, self.color.g, self.color.b], "object_list": []}
        for obj in self.object_list:
            json_object["object_list"].append(obj.to_json())
        return json_object

def json_to_level(json_object: basics.JsonObject) -> level: # oh hell no * 2
    new_level = level(name=json_object["name"], # type: ignore
                      inf_tier=int(json_object["infinite_tier"]), # type: ignore
                      size=tuple(json_object["size"]), # type: ignore
                      color=pygame.Color(json_object["color"])) # type: ignore
    for obj in json_object["object_list"]: # type: ignore
        new_level.new_obj(objects.json_to_object(obj))
    return new_level