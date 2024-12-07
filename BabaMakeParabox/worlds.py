from typing import Any, Optional, TypedDict
import random

from BabaMakeParabox import basics, positions, refs, colors, objects, rules

def match_pos(obj: objects.Object, pos: positions.Coordinate) -> bool:
    return obj.pos == pos

class WorldJson(TypedDict):
    id: refs.WorldIDJson
    size: positions.CoordTuple
    color: colors.ColorHex
    object_list: list[objects.ObjectJson]

class World(object):
    def __init__(self, world_id: refs.WorldID, size: positions.Coordinate, color: Optional[colors.ColorHex] = None) -> None:
        self.world_id: refs.WorldID = world_id
        self.size: positions.Coordinate = size
        self.color: colors.ColorHex = color if color is not None else colors.random_world_color()
        self.object_list: list[objects.Object] = []
        self.object_pos_index: list[list[objects.Object]]
        self.properties: dict[type[objects.WorldObject], objects.Properties] = {p: objects.Properties() for p in objects.world_object_types}
        self.special_operator_properties: dict[type[objects.WorldObject], dict[type[objects.Operator], objects.Properties]] = {p: {o: objects.Properties() for o in objects.special_operators} for p in objects.world_object_types}
        self.rule_list: list[rules.Rule] = []
        self.refresh_index()
    def __eq__(self, world: "World") -> bool:
        return self.world_id == world.world_id
    @property
    def width(self) -> int:
        return self.size.x
    @width.setter
    def width(self, value: int) -> None:
        self.size = positions.Coordinate(value, self.size.y)
    @property
    def height(self) -> int:
        return self.size.y
    @height.setter
    def height(self, value: int) -> None:
        self.size = positions.Coordinate(self.size.x, value)
    def out_of_range(self, coord: positions.Coordinate) -> bool:
        return coord[0] < 0 or coord[1] < 0 or coord[0] >= self.width or coord[1] >= self.height
    def pos_to_index(self, pos) -> int:
        return pos[1] * self.width + pos[0]
    def pos_to_objs(self, pos) -> list[objects.Object]:
        return self.object_pos_index[self.pos_to_index(pos)]
    def refresh_index(self) -> None:
        self.object_pos_index = [[] for _ in range(self.width * self.height)]
        for obj in self.object_list:
            if not self.out_of_range(obj.pos):
                self.pos_to_objs(obj.pos).append(obj)
    def new_obj(self, obj: objects.Object) -> None:
        self.object_list.append(obj)
        if not self.out_of_range(obj.pos):
            self.pos_to_objs(obj.pos).append(obj)
    def get_objs_from_pos(self, pos: positions.Coordinate) -> list[objects.Object]:
        if self.out_of_range(pos):
            return []
        return self.pos_to_objs(pos)
    def get_objs_from_pos_and_type[T: objects.Object](self, pos: positions.Coordinate, object_type: type[T]) -> list[T]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, object_type)]
    def get_objs_from_pos_and_special_noun(self, pos: positions.Coordinate, noun_type: type[objects.SupportsIsReferenceOf]) -> list[objects.Object]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if noun_type.isreferenceof(o)]
    def get_objs_from_type[T: objects.Object](self, object_type: type[T]) -> list[T]:
        return [o for o in self.object_list if isinstance(o, object_type)]
    def get_objs_from_special_noun(self, object_type: type[objects.SupportsIsReferenceOf]) -> list[objects.Object]:
        return [o for o in self.object_list if object_type.isreferenceof(o)]
    def del_obj(self, obj: objects.Object) -> None:
        if not self.out_of_range(obj.pos):
            self.pos_to_objs(obj.pos).remove(obj)
        self.object_list.remove(obj)
    def del_objs_from_pos(self, pos: positions.Coordinate) -> bool:
        if self.out_of_range(pos):
            return False
        deleted = len(self.pos_to_objs(pos)) != 0
        for obj in self.pos_to_objs(pos):
            self.object_list.remove(obj)
        self.object_pos_index[self.pos_to_index(pos)].clear()
        return deleted
    def del_objs_from_pos_and_type(self, pos: positions.Coordinate, object_type: type) -> bool:
        del_objects = filter(lambda o: isinstance(o, object_type), self.pos_to_objs(pos))
        deleted = False
        for obj in del_objects:
            deleted = True
            self.object_list.remove(obj)
            if not self.out_of_range(obj.pos):
                self.pos_to_objs(pos).remove(obj)
        return deleted
    def del_objs_from_pos_and_special_noun(self, pos: positions.Coordinate, noun_type: type[objects.SupportsIsReferenceOf]) -> bool:
        del_objects = filter(lambda o: noun_type.isreferenceof(o), self.pos_to_objs(pos))
        deleted = False
        for obj in del_objects:
            deleted = True
            self.object_list.remove(obj)
            if not self.out_of_range(obj.pos):
                self.pos_to_objs(pos).remove(obj)
        return deleted
    def get_worlds(self) -> list[objects.WorldObject]:
        return [o for o in self.object_list if isinstance(o, objects.WorldObject)]
    def get_worlds_from_pos(self, pos: positions.Coordinate) -> list[objects.WorldObject]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, objects.WorldObject)]
    def get_levels(self) -> list[objects.LevelObject]:
        return [o for o in self.object_list if isinstance(o, objects.LevelObject)]
    def get_levels_from_pos(self, pos: positions.Coordinate) -> list[objects.LevelObject]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, objects.LevelObject)]
    def get_rules_from_pos_and_direct(self, pos: positions.Coordinate, direct: positions.Direction, stage: str = "before prefix") -> list[rules.Rule]:
        match_list: list[tuple[list[type[objects.Text]], list[type[objects.Text]], str]] = []
        rule_list: list[rules.Rule] = []
        if stage == "before prefix": # start, before prefix, or noun
            match_list = [
                ([objects.TextNot], [], "before prefix"),
                ([objects.Prefix], [], "after prefix"),
                ([objects.TextText_], [], "text_ noun"),
                ([objects.Noun], [], "before infix"),
            ]
        elif stage == "after prefix": # after prefix, before new prefix, or noun
            match_list = [
                ([objects.TextNot], [], "after prefix"),
                ([objects.TextAnd], [], "before prefix"),
                ([objects.TextText_], [], "text_ noun"),
                ([objects.Noun], [], "before infix"),
            ]
        elif stage == "before infix": # after noun, before infix type, new noun, and operator
            match_list = [
                ([objects.TextNot], [], "before infix"),
                ([objects.Infix], [], "in infix"),
                ([objects.TextAnd], [], "before prefix"),
                ([objects.Operator], [], "before property"),
            ]
        elif stage == "in infix": # after infix type, before infix noun
            match_list = [
                ([objects.TextNot], [], "in infix"),
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
                ([objects.TextNot], [], "before property"),
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
                rule_list_after_this = self.get_rules_from_pos_and_direct(positions.front_position(pos, direct), direct, next_stage)
                for rule_after_this in rule_list_after_this:
                    for matched_text in matched_list:
                        rule_list.append([matched_text] + rule_after_this)
            elif stage == "after property":
                rule_list = [[]]
        return rule_list
    # rest in piece, more-than-200-lines-long-and-extremely-fucking-confusing function(BabaMakeParabox.worlds.World.get_rules_from_pos_and_orient)
    def get_rules(self) -> list[rules.Rule]:
        rule_list: list[rules.Rule] = []
        x_rule_dict: dict[int, list[rules.Rule]] = {}
        y_rule_dict: dict[int, list[rules.Rule]] = {}
        for x in range(self.width):
            for y in range(self.height):
                x_rule_dict.setdefault(x, [])
                new_rule_list = self.get_rules_from_pos_and_direct(positions.Coordinate(x, y), positions.Direction.D)
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
                new_rule_list = self.get_rules_from_pos_and_direct(positions.Coordinate(x, y), positions.Direction.S)
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
                w_pos = positions.front_position(obj.pos, positions.Direction.W)
                w = len(self.get_objs_from_pos_and_type(w_pos, type(obj))) != 0
                s_pos = positions.front_position(obj.pos, positions.Direction.S)
                s = len(self.get_objs_from_pos_and_type(s_pos, type(obj))) != 0
                a_pos = positions.front_position(obj.pos, positions.Direction.A)
                a = len(self.get_objs_from_pos_and_type(a_pos, type(obj))) != 0
                d_pos = positions.front_position(obj.pos, positions.Direction.D)
                d = len(self.get_objs_from_pos_and_type(d_pos, type(obj))) != 0
                connected = {positions.Direction.W: w, positions.Direction.S: s, positions.Direction.A: a, positions.Direction.D: d}
            else:
                connected = {positions.Direction.W: False, positions.Direction.S: False, positions.Direction.A: False, positions.Direction.D: False}
            obj.set_sprite(round_num=round_num, connected=connected)
    def default_input_position(self, side: positions.Direction) -> positions.Coordinate:
        match side:
            case positions.Direction.W:
                return positions.Coordinate(self.width // 2, -1)
            case positions.Direction.A:
                return positions.Coordinate(-1, self.height // 2)
            case positions.Direction.S:
                return positions.Coordinate(self.width // 2, self.height)
            case positions.Direction.D:
                return positions.Coordinate(self.width, self.height // 2)
    def pos_to_transnum(self, pos: positions.Coordinate, side: positions.Direction) -> float:
        if side in (positions.Direction.W, positions.Direction.S):
            return (pos[0] + 0.5) / self.width
        else:
            return (pos[1] + 0.5) / self.height
    def transnum_to_pos(self, num: float, side: positions.Direction) -> positions.Coordinate:
        match side:
            case positions.Direction.W:
                return positions.Coordinate(int((num * self.width)), -1)
            case positions.Direction.S:
                return positions.Coordinate(int((num * self.width)), self.height)
            case positions.Direction.A:
                return positions.Coordinate(-1, int((num * self.height)))
            case positions.Direction.D:
                return positions.Coordinate(self.width, int((num * self.height)))
    def transnum_to_smaller_transnum(self, num: float, pos: positions.Coordinate, side: positions.Direction) -> float:
        if side in (positions.Direction.W, positions.Direction.S):
            return (num * self.width) - pos[0]
        else:
            return (num * self.height) - pos[1]
    def transnum_to_bigger_transnum(self, num: float, pos: positions.Coordinate, side: positions.Direction) -> float:
        if side in (positions.Direction.W, positions.Direction.S):
            return (num + pos[0]) / self.width
        else:
            return (num + pos[1]) / self.height
    def to_json(self) -> WorldJson:
        json_object: WorldJson = {"id": self.world_id.to_json(), "size": (self.width, self.height), "color": self.color, "object_list": []}
        for obj in self.object_list:
            json_object["object_list"].append(obj.to_json())
        return json_object

def json_to_world(json_object: WorldJson, ver: Optional[str] = None) -> World:
    if basics.compare_versions(ver if ver is not None else "0.0", "3.8") == -1:
        world_id: refs.WorldID = refs.WorldID(json_object["name"], json_object["infinite_tier"]) # type: ignore
    else:
        world_id: refs.WorldID = refs.WorldID(**json_object["id"])
    new_world = World(world_id=world_id,
                      size=positions.Coordinate(*json_object["size"]),
                      color=json_object["color"])
    for obj in json_object["object_list"]:
        new_world.new_obj(objects.json_to_object(obj, ver))
    new_world.refresh_index()
    return new_world