from typing import Any, Optional, TypedDict, Callable
import random

from BabaMakeParabox import Base, Color, Locate, Object, Ref, Rule

class SpaceJson(TypedDict):
    id: Ref.SpaceIDJson
    size: Locate.CoordTuple
    color: Color.ColorHex
    object_list: list[Object.ObjectJson]

class Space(object):
    def __init__(self, space_id: Ref.SpaceID, size: Locate.Coordinate, color: Optional[Color.ColorHex] = None) -> None:
        self.space_id: Ref.SpaceID = space_id
        self.size: Locate.Coordinate = size
        self.color: Color.ColorHex = color if color is not None else Color.random_space_color()
        self.static_transform: Locate.SpaceTransform = Locate.default_space_transform.copy()
        self.dynamic_transform: Locate.SpaceTransform = Locate.default_space_transform.copy()
        self.object_list: list[Object.Object] = []
        self.object_pos_index: list[list[Object.Object]]
        self.properties: dict[type[Object.SpaceObject], Object.Properties] = {p: Object.Properties() for p in Object.space_object_types}
        self.special_operator_properties: dict[type[Object.SpaceObject], dict[type[Object.Operator], Object.Properties]] = {p: {o: Object.Properties() for o in Object.special_operators} for p in Object.space_object_types}
        self.rule_list: list[Rule.Rule] = []
        self.rule_info: list[Rule.RuleInfo] = []
        self.refresh_index()
    def __eq__(self, space: "Space") -> bool:
        return self.space_id == space.space_id
    @property
    def width(self) -> int:
        return self.size.x
    @width.setter
    def width(self, value: int) -> None:
        self.size = Locate.Coordinate(value, self.size.y)
    @property
    def height(self) -> int:
        return self.size.y
    @height.setter
    def height(self, value: int) -> None:
        self.size = Locate.Coordinate(self.size.x, value)
    def out_of_range(self, coord: Locate.Coordinate) -> bool:
        return coord[0] < 0 or coord[1] < 0 or coord[0] >= self.width or coord[1] >= self.height
    def pos_to_index(self, pos) -> int:
        return pos[1] * self.width + pos[0]
    def pos_to_objs(self, pos) -> list[Object.Object]:
        return self.object_pos_index[self.pos_to_index(pos)]
    def refresh_index(self) -> None:
        self.object_pos_index = [[] for _ in range(self.width * self.height)]
        for obj in self.object_list:
            if not self.out_of_range(obj.pos):
                self.pos_to_objs(obj.pos).append(obj)
    @staticmethod
    def auto_refresh(func):
        def wrapper(self: "Space", *args, **kwds):
            try:
                r = func(self, *args, **kwds)
                return r
            except Exception:
                self.refresh_index()
                r = func(self, *args, **kwds)
                return r
        return wrapper
    @auto_refresh
    def new_obj(self, obj: Object.Object) -> None:
        self.object_list.append(obj)
        if not self.out_of_range(obj.pos):
            self.pos_to_objs(obj.pos).append(obj)
    @auto_refresh
    def get_objs_from_pos(self, pos: Locate.Coordinate) -> list[Object.Object]:
        if self.out_of_range(pos):
            return []
        return self.pos_to_objs(pos)
    @auto_refresh
    def get_objs_from_pos_and_type[T: Object.Object](self, pos: Locate.Coordinate, object_type: type[T]) -> list[T]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, object_type)]
    @auto_refresh
    def get_objs_from_pos_and_special_noun(self, pos: Locate.Coordinate, noun_type: type[Object.SupportsIsReferenceOf]) -> list[Object.Object]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if noun_type.isreferenceof(o)]
    @auto_refresh
    def get_objs_from_type[T: Object.Object](self, object_type: type[T]) -> list[T]:
        return [o for o in self.object_list if isinstance(o, object_type)]
    @auto_refresh
    def get_objs_from_special_noun(self, object_type: type[Object.SupportsIsReferenceOf]) -> list[Object.Object]:
        return [o for o in self.object_list if object_type.isreferenceof(o)]
    @auto_refresh
    def del_obj(self, obj: Object.Object) -> None:
        if not self.out_of_range(obj.pos):
            self.pos_to_objs(obj.pos).remove(obj)
        self.object_list.remove(obj)
    @auto_refresh
    def del_objs_from_pos(self, pos: Locate.Coordinate) -> bool:
        if self.out_of_range(pos):
            return False
        deleted = len(self.pos_to_objs(pos)) != 0
        for obj in self.pos_to_objs(pos):
            self.object_list.remove(obj)
        self.object_pos_index[self.pos_to_index(pos)].clear()
        return deleted
    @auto_refresh
    def del_objs_from_pos_and_type(self, pos: Locate.Coordinate, object_type: type) -> bool:
        del_objects = filter(lambda o: isinstance(o, object_type), self.pos_to_objs(pos))
        deleted = False
        for obj in del_objects:
            deleted = True
            self.object_list.remove(obj)
            if not self.out_of_range(obj.pos):
                self.pos_to_objs(pos).remove(obj)
        return deleted
    @auto_refresh
    def del_objs_from_pos_and_special_noun(self, pos: Locate.Coordinate, noun_type: type[Object.SupportsIsReferenceOf]) -> bool:
        del_objects = filter(lambda o: noun_type.isreferenceof(o), self.pos_to_objs(pos))
        deleted = False
        for obj in del_objects:
            deleted = True
            self.object_list.remove(obj)
            if not self.out_of_range(obj.pos):
                self.pos_to_objs(pos).remove(obj)
        return deleted
    @auto_refresh
    def get_spaces(self) -> list[Object.SpaceObject]:
        return [o for o in self.object_list if isinstance(o, Object.SpaceObject)]
    @auto_refresh
    def get_spaces_from_pos(self, pos: Locate.Coordinate) -> list[Object.SpaceObject]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, Object.SpaceObject)]
    @auto_refresh
    def get_levels(self) -> list[Object.LevelObject]:
        return [o for o in self.object_list if isinstance(o, Object.LevelObject)]
    @auto_refresh
    def get_levels_from_pos(self, pos: Locate.Coordinate) -> list[Object.LevelObject]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, Object.LevelObject)]
    def get_rule_from_pos_and_direct(self, pos: Locate.Coordinate, direct: Locate.Direction, stage: str = "before prefix") -> tuple[list[Rule.Rule], list[Rule.RuleInfo]]:
        new_rule_list: list[Rule.Rule] = []
        new_info_list: list[Rule.RuleInfo] = []
        for match_type, unmatch_type, next_stage, func in Rule.how_to_match_rule[stage]:
            text_type_list: list[type[Object.Text]] = [type(o) for o in self.get_objs_from_pos_and_type(pos, Object.Text)]
            text_type_list += [Object.get_noun_from_type(type(o)) for o in self.get_objs_from_pos(pos) if o.properties.has(Object.TextWord)]
            matched_list = [o for o in text_type_list if issubclass(o, tuple(match_type))]
            if len(unmatch_type) != 0:
                matched_list = [o for o in matched_list if not issubclass(o, tuple(unmatch_type))]
            if len(matched_list) != 0:
                rule_list, info_list = self.get_rule_from_pos_and_direct(Locate.front_position(pos, direct), direct, next_stage)
                for matched_text in matched_list:
                    new_rule_list.extend([matched_text] + r for r in rule_list)
                    new_info_list.extend(func(i, matched_text) for i in info_list)
            if stage == "after property":
                new_rule_list.append([])
                new_info_list.append(Rule.RuleInfo([], 0, Object.Noun, [], [Rule.OperInfo(Object.Operator, [])]))
        return new_rule_list, new_info_list
    def set_rule(self) -> None:
        self.rule_list = []
        self.rule_info = []
        x_rule_dict: dict[int, list[Rule.Rule]] = {}
        y_rule_dict: dict[int, list[Rule.Rule]] = {}
        for x in range(self.width):
            for y in range(self.height):
                x_rule_dict.setdefault(x, [])
                new_rule_list, new_rule_info = self.get_rule_from_pos_and_direct(Locate.Coordinate(x, y), Locate.Direction.D)
                for rule_index in range(len(new_rule_list)):
                    part_of_old_rule = False
                    for old_x, old_rule_list in x_rule_dict.items():
                        old_rule_list_test = list(map(lambda r: list(r[x - old_x:]), old_rule_list))
                        if list(new_rule_list[rule_index]) in old_rule_list_test:
                            part_of_old_rule = True
                    if not part_of_old_rule:
                        x_rule_dict[x].append(new_rule_list[rule_index])
                        self.rule_list.append(new_rule_list[rule_index])
                        self.rule_info.append(new_rule_info[rule_index])
                y_rule_dict.setdefault(y, [])
                new_rule_list, new_rule_info = self.get_rule_from_pos_and_direct(Locate.Coordinate(x, y), Locate.Direction.S)
                for rule_index in range(len(new_rule_list)):
                    part_of_old_rule = False
                    for old_y, old_rule_list in y_rule_dict.items():
                        old_rule_list_test = list(map(lambda r: list(r[y - old_y:]), old_rule_list))
                        if list(new_rule_list[rule_index]) in old_rule_list_test:
                            part_of_old_rule = True
                    if not part_of_old_rule:
                        y_rule_dict[y].append(new_rule_list[rule_index])
                        self.rule_list.append(new_rule_list[rule_index])
                        self.rule_info.append(new_rule_info[rule_index])
    def set_sprite_states(self, round_num: int = 0) -> None:
        for obj in self.object_list:
            if isinstance(obj, Object.Tiled):
                w_pos = Locate.front_position(obj.pos, Locate.Direction.W)
                w = len(self.get_objs_from_pos_and_type(w_pos, type(obj))) != 0
                s_pos = Locate.front_position(obj.pos, Locate.Direction.S)
                s = len(self.get_objs_from_pos_and_type(s_pos, type(obj))) != 0
                a_pos = Locate.front_position(obj.pos, Locate.Direction.A)
                a = len(self.get_objs_from_pos_and_type(a_pos, type(obj))) != 0
                d_pos = Locate.front_position(obj.pos, Locate.Direction.D)
                d = len(self.get_objs_from_pos_and_type(d_pos, type(obj))) != 0
                connected = {Locate.Direction.W: w, Locate.Direction.S: s, Locate.Direction.A: a, Locate.Direction.D: d}
            else:
                connected = {Locate.Direction.W: False, Locate.Direction.S: False, Locate.Direction.A: False, Locate.Direction.D: False}
            obj.set_sprite(round_num=round_num, connected=connected)
    def get_stacked_transform(self, static: Locate.SpaceTransform, dynamic: Locate.SpaceTransform) -> Locate.SpaceTransform:
        transform = Locate.get_stacked_transform(
            Locate.get_stacked_transform(self.static_transform, self.dynamic_transform),
            Locate.get_stacked_transform(static, dynamic)
        )
        return transform
    def calc_enter_transnum(self, transnum: float, pos: Locate.Coordinate, side: Locate.Direction, transform: Locate.SpaceTransform) -> float:
        new_side = Locate.turn(side, Locate.str_to_direct(transform["direct"]))
        if new_side in (Locate.Direction.W, Locate.Direction.S):
            new_transnum = (transnum * self.width) - pos[0]
        else:
            new_transnum = (transnum * self.height) - pos[1]
        if transform["flip"]:
            new_transnum = 1.0 - new_transnum
        return new_transnum
    def calc_leave_transnum(self, transnum: float, pos: Locate.Coordinate, side: Locate.Direction, transform: Locate.SpaceTransform) -> float:
        new_side = Locate.turn(side, Locate.str_to_direct(transform["direct"]))
        if new_side in (Locate.Direction.W, Locate.Direction.S):
            new_transnum = (transnum + pos[0]) / self.width
        else:
            new_transnum = (transnum + pos[1]) / self.height
        return new_transnum
    def get_leave_transnum_from_pos(self, pos: Locate.Coordinate, side: Locate.Direction, transform: Locate.SpaceTransform) -> float:
        new_side = Locate.turn(side, Locate.str_to_direct(transform["direct"]))
        if new_side in (Locate.Direction.W, Locate.Direction.S):
            new_transnum = (pos[0] + 0.5) / self.width
        else:
            new_transnum = (pos[1] + 0.5) / self.height
        if transform["flip"]:
            new_transnum = 1.0 - new_transnum
        return new_transnum
    def get_enter_pos_by_default(self, side: Locate.Direction, transform: Locate.SpaceTransform) -> Locate.Coordinate:
        new_side = Locate.swap_direction(side) if transform["flip"] and side in (Locate.Direction.A, Locate.Direction.D) else side
        new_side = Locate.turn(new_side, Locate.str_to_direct(transform["direct"]))
        match new_side:
            case Locate.Direction.W:
                return Locate.Coordinate(self.width // 2, -1)
            case Locate.Direction.A:
                return Locate.Coordinate(-1, self.height // 2)
            case Locate.Direction.S:
                return Locate.Coordinate(self.width // 2, self.height)
            case Locate.Direction.D:
                return Locate.Coordinate(self.width, self.height // 2)
    def get_enter_pos(self, transnum: float, side: Locate.Direction, transform: Locate.SpaceTransform) -> Locate.Coordinate:
        new_side = Locate.swap_direction(side) if transform["flip"] and side in (Locate.Direction.A, Locate.Direction.D) else side
        new_side = Locate.turn(new_side, Locate.str_to_direct(transform["direct"]))
        new_transnum = (1.0 - transnum) if transform["flip"] and side in (Locate.Direction.A, Locate.Direction.D) else transnum
        match new_side:
            case Locate.Direction.W:
                return Locate.Coordinate(int((new_transnum * self.width)), -1)
            case Locate.Direction.S:
                return Locate.Coordinate(int((new_transnum * self.width)), self.height)
            case Locate.Direction.A:
                return Locate.Coordinate(-1, int((new_transnum * self.height)))
            case Locate.Direction.D:
                return Locate.Coordinate(self.width, int((new_transnum * self.height)))
    def to_json(self) -> SpaceJson:
        json_object: SpaceJson = {"id": self.space_id.to_json(), "size": (self.width, self.height), "color": self.color, "object_list": []}
        for obj in self.object_list:
            json_object["object_list"].append(obj.to_json())
        return json_object

def json_to_space(json_object: SpaceJson, ver: Optional[str] = None) -> Space:
    if Base.compare_versions(ver if ver is not None else "0.0", "3.8") == -1:
        space_id: Ref.SpaceID = Ref.SpaceID(json_object["name"], json_object["infinite_tier"]) # type: ignore
    else:
        space_id: Ref.SpaceID = Ref.SpaceID(**json_object["id"])
    new_space = Space(space_id=space_id,
                      size=Locate.Coordinate(*json_object["size"]),
                      color=json_object["color"])
    for obj in json_object["object_list"]:
        new_space.new_obj(Object.json_to_object(obj, ver))
    new_space.refresh_index()
    return new_space