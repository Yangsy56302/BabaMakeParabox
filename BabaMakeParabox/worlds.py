from typing import Any, Optional, TypedDict
import random

from BabaMakeParabox import basics, colors, spaces, objects, rules, displays

def match_pos(obj: objects.BmpObject, pos: spaces.Coord) -> bool:
    return obj.pos == pos

class WorldJson(TypedDict):
    name: str
    infinite_tier: int
    size: spaces.Coord
    color: colors.ColorHex
    object_list: list[objects.BmpObjectJson]

class World(object):
    def __init__(self, name: str, size: tuple[int, int], infinite_tier: int = 0, color: Optional[colors.ColorHex] = None) -> None:
        self.name: str = name
        self.infinite_tier: int = infinite_tier
        self.width: int = size[0]
        self.height: int = size[1]
        self.color: colors.ColorHex = color if color is not None else colors.random_world_color()
        self.object_list: list[objects.BmpObject] = []
        self.object_pos_index: list[list[objects.BmpObject]]
        self.properties: dict[type[objects.WorldPointer], objects.Properties] = {objects.World: objects.Properties(), objects.Clone: objects.Properties()}
        self.special_operator_properties: dict[type[objects.WorldPointer], dict[type[objects.Operator], objects.Properties]] = {objects.World: {}, objects.Clone: {}}
        self.rule_list: list[rules.Rule] = []
        self.refresh_index()
    def __eq__(self, world: "World") -> bool:
        return self.name == world.name and self.infinite_tier == world.infinite_tier
    def out_of_range(self, coord: spaces.Coord) -> bool:
        return coord[0] < 0 or coord[1] < 0 or coord[0] >= self.width or coord[1] >= self.height
    def pos_to_index(self, pos) -> int:
        return pos[1] * self.width + pos[0]
    def pos_to_objs(self, pos) -> list[objects.BmpObject]:
        return self.object_pos_index[self.pos_to_index(pos)]
    def refresh_index(self) -> None:
        self.object_pos_index = [[] for _ in range(self.width * self.height)]
        for obj in self.object_list:
            self.pos_to_objs(obj.pos).append(obj)
    def new_obj(self, obj: objects.BmpObject) -> None:
        self.object_list.append(obj)
        self.pos_to_objs(obj.pos).append(obj)
    def get_objs_from_pos(self, pos: spaces.Coord) -> list[objects.BmpObject]:
        if self.out_of_range(pos):
            return []
        return self.pos_to_objs(pos)
    def get_objs_from_pos_and_type[T: objects.BmpObject](self, pos: spaces.Coord, obj_type: type[T]) -> list[T]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, obj_type)]
    def get_objs_from_type[T: objects.BmpObject](self, obj_type: type[T]) -> list[T]:
        return [o for o in self.object_list if isinstance(o, obj_type)]
    def del_obj(self, obj: objects.BmpObject) -> None:
        self.pos_to_objs(obj.pos).remove(obj)
        self.object_list.remove(obj)
    def del_obj_from_pos_and_type(self, pos: spaces.Coord, obj_type: type) -> bool:
        for obj in self.pos_to_objs(pos):
            if isinstance(obj, obj_type):
                self.object_list.remove(obj)
                self.pos_to_objs(pos).remove(obj)
                return True
        return False
    def del_objs_from_pos_and_type(self, pos: spaces.Coord, obj_type: type) -> bool:
        del_objects = filter(lambda o: isinstance(o, obj_type), self.pos_to_objs(pos))
        deleted = False
        for obj in del_objects:
            deleted = True
            self.object_list.remove(obj)
            self.pos_to_objs(pos).remove(obj)
        return deleted
    def del_objs_from_pos(self, pos: spaces.Coord) -> bool:
        deleted = len(self.pos_to_objs(pos)) != 0
        for obj in self.pos_to_objs(pos):
            self.object_list.remove(obj)
        self.object_pos_index[self.pos_to_index(pos)].clear()
        return deleted
    def get_worlds(self) -> list[objects.World]:
        return [o for o in self.object_list if isinstance(o, objects.World)]
    def get_worlds_from_pos(self, pos: spaces.Coord) -> list[objects.World]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, objects.World)]
    def get_clones(self) -> list[objects.Clone]:
        return [o for o in self.object_list if isinstance(o, objects.Clone)]
    def get_clones_from_pos(self, pos: spaces.Coord) -> list[objects.Clone]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, objects.Clone)]
    def get_levels(self) -> list[objects.LevelPointer]:
        return [o for o in self.object_list if isinstance(o, objects.LevelPointer)]
    def get_levels_from_pos(self, pos: spaces.Coord) -> list[objects.LevelPointer]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, objects.LevelPointer)]
    def get_rules_from_pos_and_orient(self, pos: spaces.Coord, orient: spaces.Orient, stage: str = "before prefix") -> list[rules.Rule]:
        match_list: list[tuple[list[type[objects.Text]], list[type[objects.Text]], str]] = []
        rule_list: list[rules.Rule] = []
        discard_parse: bool = False
        if stage == "before prefix": # start, before prefix, or noun
            match_list = [
                ([objects.TextNot, objects.TextNeg], [], "before prefix"),
                ([objects.Prefix], [], "after prefix"),
                ([objects.TextText_], [], "text_ noun"),
                ([objects.Noun], [], "before infix"),
            ]
        elif stage == "after prefix": # after prefix, before new prefix, or noun
            match_list = [
                ([objects.TextNot, objects.TextNeg], [], "after prefix"),
                ([objects.TextAnd], [], "before prefix"),
                ([objects.TextText_], [], "text_ noun"),
                ([objects.Noun], [], "before infix"),
            ]
        elif stage == "before infix": # after noun, before infix type, new noun, and operator
            match_list = [
                ([objects.TextNot, objects.TextNeg], [], "before infix"),
                ([objects.Infix], [], "in infix"),
                ([objects.TextAnd], [], "before prefix"),
                ([objects.Operator], [], "before property"),
            ]
        elif stage == "in infix": # after infix type, before infix noun
            match_list = [
                ([objects.TextNot, objects.TextNeg], [], "in infix"),
                ([objects.TextText_], [], "text_ infix"),
                ([objects.Noun, objects.Property], [], "after infix"),
            ]
        elif stage == "after infix": # after infix noun, before operator, or new infix
            match_list = [
                ([objects.TextAnd], [], "new infix"),
                ([objects.Operator], [], "before property"),
            ]
        elif stage == "new infix": # before new infix type, or new infix noun
            match_list = [
                ([objects.Infix], [], "in infix"),
                ([objects.TextText_], [], "text_ infix"),
                ([objects.Noun, objects.Property], [], "after infix"),
            ]
        elif stage == "before property": # after operator, before property
            match_list = [
                ([objects.TextNot, objects.TextNeg], [], "before property"),
                ([objects.TextText_], [], "text_ property"),
                ([objects.Noun, objects.Property], [], "after property"),
            ]
        elif stage == "after property": # after property, may before new property
            match_list = [
                ([objects.TextAnd], [], "before property"),
            ]
        elif stage == "text_ noun": # metatext
            match_list = [
                ([objects.TextText_], [], "text_ noun"),
                ([objects.Text], [objects.TextText_], "before infix"),
            ]
        elif stage == "text_ infix": # metatext
            match_list = [
                ([objects.TextText_], [], "text_ infix"),
                ([objects.Text], [objects.TextText_], "after infix"),
            ]
        elif stage == "text_ property": # metatext
            match_list = [
                ([objects.TextText_], [], "text_ property"),
                ([objects.Text], [objects.TextText_], "after property"),
            ]
        else:
            raise ValueError(stage)
        for match_type, unmatch_type, next_stage in match_list:
            text_type_list: list[type[objects.Text]] = [type(o) for o in self.get_objs_from_pos_and_type(pos, objects.Text)]
            text_type_list += [objects.get_noun_from_type(type(o)) for o in self.get_objs_from_pos(pos) if o.properties.has(objects.TextWord)]
            matched_list = [o for o in text_type_list if issubclass(o, tuple(match_type))]
            if len(unmatch_type) != 0:
                matched_list = [o for o in matched_list if not issubclass(o, tuple(unmatch_type))]
            if len(matched_list) != 0:
                rule_list_after_this = self.get_rules_from_pos_and_orient(spaces.pos_facing(pos, orient), orient, next_stage)
                for rule_after_this in rule_list_after_this:
                    for matched_text in matched_list:
                        rule_list.append([matched_text] + rule_after_this)
            elif stage == "after property":
                rule_list = [[]]
        return rule_list # rest in piece, more-than-200-lines-long-and-extremely-fucking-confusing function(BabaMakeParabox.worlds.World.get_rules_from_pos_and_orient)
    def get_rules(self) -> list[rules.Rule]:
        rule_list: list[rules.Rule] = []
        x_rule_dict: dict[int, list[rules.Rule]] = {}
        y_rule_dict: dict[int, list[rules.Rule]] = {}
        for x in range(self.width):
            for y in range(self.height):
                x_rule_dict.setdefault(x, [])
                new_rule_list = self.get_rules_from_pos_and_orient((x, y), spaces.Orient.D)
                if new_rule_list is not None:
                    for rule_index in range(len(new_rule_list)):
                        part_of_old_rule = False
                        for old_x, old_rule_list in x_rule_dict.items():
                            old_rule_list_test = list(map(lambda r: list(r[x - old_x:]), old_rule_list))
                            if list(new_rule_list[rule_index]) in old_rule_list_test:
                                part_of_old_rule = True
                        if not part_of_old_rule:
                            x_rule_dict[x].append(new_rule_list[rule_index])
                y_rule_dict.setdefault(y, [])
                new_rule_list = self.get_rules_from_pos_and_orient((x, y), spaces.Orient.S)
                if new_rule_list is not None:
                    for rule_index in range(len(new_rule_list)):
                        part_of_old_rule = False
                        for old_y, old_rule_list in y_rule_dict.items():
                            old_rule_list_test = list(map(lambda r: list(r[y - old_y:]), old_rule_list))
                            if list(new_rule_list[rule_index]) in old_rule_list_test:
                                part_of_old_rule = True
                        if not part_of_old_rule:
                            y_rule_dict[y].append(new_rule_list[rule_index])
        for x_rule_list in x_rule_dict.values():
            rule_list.extend(x_rule_list)
        for y_rule_list in y_rule_dict.values():
            rule_list.extend(y_rule_list)
        return rule_list
    def set_sprite_states(self, round_num: int = 0) -> None:
        for obj in self.object_list:
            if isinstance(obj, objects.Tiled):
                w_pos = spaces.pos_facing(obj.pos, spaces.Orient.W)
                w = len(self.get_objs_from_pos_and_type(w_pos, type(obj))) != 0
                s_pos = spaces.pos_facing(obj.pos, spaces.Orient.S)
                s = len(self.get_objs_from_pos_and_type(s_pos, type(obj))) != 0
                a_pos = spaces.pos_facing(obj.pos, spaces.Orient.A)
                a = len(self.get_objs_from_pos_and_type(a_pos, type(obj))) != 0
                d_pos = spaces.pos_facing(obj.pos, spaces.Orient.D)
                d = len(self.get_objs_from_pos_and_type(d_pos, type(obj))) != 0
                connected = {spaces.Orient.W: w, spaces.Orient.S: s, spaces.Orient.A: a, spaces.Orient.D: d}
            else:
                connected = {spaces.Orient.W: False, spaces.Orient.S: False, spaces.Orient.A: False, spaces.Orient.D: False}
            obj.set_sprite(round_num=round_num, connected=connected)
    def default_input_position(self, side: spaces.Orient) -> spaces.Coord:
        match side:
            case spaces.Orient.W:
                return (self.width // 2, -1)
            case spaces.Orient.A:
                return (-1, self.height // 2)
            case spaces.Orient.S:
                return (self.width // 2, self.height)
            case spaces.Orient.D:
                return (self.width, self.height // 2)
    def pos_to_transnum(self, pos: spaces.Coord, side: spaces.Orient) -> float:
        if side in (spaces.Orient.W, spaces.Orient.S):
            return (pos[0] + 0.5) / self.width
        else:
            return (pos[1] + 0.5) / self.height
    def transnum_to_pos(self, num: float, side: spaces.Orient) -> spaces.Coord:
        match side:
            case spaces.Orient.W:
                return (int((num * self.width)), -1)
            case spaces.Orient.S:
                return (int((num * self.width)), self.height)
            case spaces.Orient.A:
                return (-1, int((num * self.height)))
            case spaces.Orient.D:
                return (self.width, int((num * self.height)))
    def transnum_to_smaller_transnum(self, num: float, pos: spaces.Coord, side: spaces.Orient) -> float:
        if side in (spaces.Orient.W, spaces.Orient.S):
            return (num * self.width) - pos[0]
        else:
            return (num * self.height) - pos[1]
    def transnum_to_bigger_transnum(self, num: float, pos: spaces.Coord, side: spaces.Orient) -> float:
        if side in (spaces.Orient.W, spaces.Orient.S):
            return (num + pos[0]) / self.width
        else:
            return (num + pos[1]) / self.height
    def to_json(self) -> WorldJson:
        json_object: WorldJson = {"name": self.name, "infinite_tier": self.infinite_tier, "size": (self.width, self.height), "color": self.color, "object_list": []}
        for obj in self.object_list:
            json_object["object_list"].append(obj.to_json())
        return json_object

def json_to_world(json_object: WorldJson, ver: Optional[str] = None) -> World:
    new_world = World(name=json_object["name"],
                      infinite_tier=json_object["infinite_tier"],
                      size=json_object["size"],
                      color=json_object["color"])
    for obj in json_object["object_list"]:
        new_world.new_obj(objects.json_to_object(obj, ver))
    new_world.refresh_index()
    return new_world