from typing import Any, Optional
import pygame
import uuid

import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules

def match_pos(obj: objects.Object, pos: spaces.Coord) -> bool:
    return (obj.x, obj.y) == tuple(pos)

class level(object):
    class_name: str = "level"
    def __init__(self, name: str, inf_tier: int, size: tuple[int, int], color: Optional[pygame.Color] = None, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)
        self.uuid: uuid.UUID = uuid.uuid4()
        self.name: str = name
        self.inf_tier: int = inf_tier
        self.width: int = size[0]
        self.height: int = size[1]
        self.objects: list[objects.Object] = []
        self.rules: list[rules.Rule] = []
    def __eq__(self, level: "level") -> bool:
        return self.uuid == level.uuid
    def __str__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def __repr__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def out_of_range(self, coord: spaces.Coord) -> bool:
        return coord[0] < 0 or coord[1] < 0 or coord[0] >= self.width or coord[1] >= self.height
    def new_obj(self, obj: objects.Object) -> bool:
        self.objects.append(obj)
        return True
    def get_obj(self, uid: uuid.UUID) -> Optional[objects.Object]:
        res = [o for o in self.objects if uid == o.uuid]
        return res[0] if len(res) != 0 else None
    def get_objs_from_pos_and_type[T: objects.Object](self, pos: spaces.Coord, obj_type: type[T]) -> list[T]:
        return [o for o in self.objects if isinstance(o, obj_type) and match_pos(o, pos)]
    def get_objs_from_pos(self, pos: spaces.Coord) -> list[objects.Object]:
        return [o for o in self.objects if match_pos(o, pos)]
    def get_objs_from_type[T: objects.Object](self, obj_type: type[T]) -> list[T]:
        return [o for o in self.objects if isinstance(o, obj_type)]
    def del_obj(self, uid: uuid.UUID) -> bool:
        for i in range(len(self.objects)):
            if uid == self.objects[i].uuid:
                self.objects.pop(i)
                return True
        return False
    def del_obj_from_pos_and_type(self, pos: spaces.Coord, obj_type: type) -> bool:
        for i in range(len(self.objects)):
            if match_pos(self.objects[i], pos) and isinstance(self.objects[i], obj_type):
                self.objects.pop(i)
                return True
        return False
    def del_objs_from_pos_and_type(self, pos: spaces.Coord, obj_type: type) -> bool:
        old_length = len(self.objects)
        new_objects = filter(lambda o: not match_pos(o, pos) and isinstance(o, obj_type), self.objects)
        self.objects = list(new_objects)
        new_length = len(self.objects)
        return old_length - new_length > 0
    def del_objs_from_type(self, obj_type: type) -> bool:
        old_length = len(self.objects)
        new_objects = filter(lambda o: isinstance(o, obj_type), self.objects)
        self.objects = list(new_objects)
        new_length = len(self.objects)
        return old_length - new_length > 0
    def get_levels(self) -> list[objects.Level]:
        return [o for o in self.objects if isinstance(o, objects.Level)]
    def get_levels_from_pos(self, pos: spaces.Coord) -> list[objects.Level]:
        return [o for o in self.objects if isinstance(o, objects.Level) and match_pos(o, pos)]
    def get_clones(self) -> list[objects.Clone]:
        return [o for o in self.objects if isinstance(o, objects.Clone)]
    def get_clones_from_pos(self, pos: spaces.Coord) -> list[objects.Clone]:
        return [o for o in self.objects if isinstance(o, objects.Clone) and match_pos(o, pos)]
    def update_rules(self) -> None:
        self.rules = []
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
                    self.rules.append((type(noun_obj), type(oper_obj), type(prop_obj)))
                for noun_obj_2 in noun_objs:
                    if not spaces.on_line((noun_obj.x, noun_obj.y), (oper_obj.x, oper_obj.y), (noun_obj_2.x, noun_obj_2.y)):
                        continue
                    self.rules.append((type(noun_obj), type(oper_obj), type(noun_obj_2)))
    def find_rules(self, *match_rule: Optional[type[objects.Text]]) -> list[rules.Rule]:
        found_rules = []
        for rule in self.rules:
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