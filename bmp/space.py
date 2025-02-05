from typing import Never, NotRequired, Optional, TypeGuard, TypedDict
from tqdm import tqdm

import bmp.base
import bmp.color
import bmp.loc
import bmp.obj
import bmp.ref
import bmp.rule

class SpaceJson4102(TypedDict):
    id: bmp.ref.SpaceIDJson
    size: bmp.loc.Coord[int]
    color: NotRequired[bmp.color.ColorHex]
    objects: list[bmp.obj.ObjectJson41]

class SpaceJson41(SpaceJson4102):
    objects: Never
    object_list: list[bmp.obj.ObjectJson41]

type SpaceJson = SpaceJson4102

class Space(object):
    def __init__(
        self,
        space_id: bmp.ref.SpaceID,
        size: bmp.loc.Coord[int],
        color: Optional[bmp.color.ColorHex] = None,
        object_list: Optional[list[bmp.obj.Object]] = None,
    ) -> None:
        self.space_id: bmp.ref.SpaceID = space_id
        self.size: bmp.loc.Coord[int] = size
        self.color: Optional[bmp.color.ColorHex] = color
        self.object_list: list[bmp.obj.Object] = object_list if object_list is not None else []
        self.object_pos_index: list[list[bmp.obj.Object]]
        self.refresh_index()
        self.properties: dict[type[bmp.obj.SpaceObject], bmp.obj.PropertyStorage] = {p: bmp.obj.PropertyStorage() for p in bmp.obj.space_object_types}
        self.special_operator_properties: dict[type[bmp.obj.SpaceObject], dict[type[bmp.obj.Operator], bmp.obj.PropertyStorage]] = {p: {o: bmp.obj.PropertyStorage() for o in bmp.obj.special_operators} for p in bmp.obj.space_object_types}
        self.rule_list: list[bmp.rule.Rule] = []
        self.rule_info: list[bmp.rule.RuleInfo] = []
        self.static_transform: bmp.loc.SpaceTransform = bmp.loc.default_space_transform.copy()
        self.dynamic_transform: bmp.loc.SpaceTransform = bmp.loc.default_space_transform.copy()
    def __eq__(self, space: "Space") -> bool:
        return self.space_id == space.space_id
    @property
    def width(self) -> int:
        return self.size[0]
    @width.setter
    def width(self, value: int) -> None:
        self.size = (value, self.size[1])
    @property
    def height(self) -> int:
        return self.size[1]
    @height.setter
    def height(self, value: int) -> None:
        self.size = (self.size[0], value)
    def out_of_range(self, coord: bmp.loc.Coord[int]) -> bool:
        return coord[0] < 0 or coord[1] < 0 or coord[0] >= self.width or coord[1] >= self.height
    def pos_to_index(self, pos) -> int:
        return pos[1] * self.width + pos[0]
    def pos_to_objs(self, pos) -> list[bmp.obj.Object]:
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
    # @auto_refresh
    def new_obj(self, obj: bmp.obj.Object) -> None:
        self.object_list.append(obj)
        if not self.out_of_range(obj.pos):
            self.pos_to_objs(obj.pos).append(obj)
    # @auto_refresh
    def get_objs_from_pos(self, pos: bmp.loc.Coord[int]) -> list[bmp.obj.Object]:
        if self.out_of_range(pos):
            return []
        return self.pos_to_objs(pos)
    # @auto_refresh
    def get_objs_from_pos_and_type[T: bmp.obj.Object](self, pos: bmp.loc.Coord[int], object_type: type[T]) -> list[T]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, object_type)]
    # @auto_refresh
    def get_objs_from_pos_and_noun(self, pos: bmp.loc.Coord[int], noun: bmp.obj.Noun) -> list[bmp.obj.Object]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if noun.isreferenceof(o)]
    # @auto_refresh
    def get_objs_from_type[T: bmp.obj.Object](self, object_type: type[T]) -> list[T]:
        return [o for o in self.object_list if isinstance(o, object_type)]
    # @auto_refresh
    def get_objs_from_noun(self, noun: bmp.obj.Noun) -> list[bmp.obj.Object]:
        return [o for o in self.object_list if noun.isreferenceof(o)]
    # @auto_refresh
    def del_obj(self, obj: bmp.obj.Object) -> None:
        self.object_list.remove(obj)
        if not self.out_of_range(obj.pos):
            self.pos_to_objs(obj.pos).remove(obj)
    # @auto_refresh
    def del_objs_from_pos(self, pos: bmp.loc.Coord[int]) -> bool:
        if self.out_of_range(pos):
            return False
        deleted = len(self.pos_to_objs(pos)) != 0
        for obj in self.pos_to_objs(pos):
            self.object_list.remove(obj)
        self.object_pos_index[self.pos_to_index(pos)].clear()
        return deleted
    # @auto_refresh
    def del_objs_from_pos_and_type(self, pos: bmp.loc.Coord[int], object_type: type) -> bool:
        del_objects = filter(lambda o: isinstance(o, object_type), self.pos_to_objs(pos))
        deleted = False
        for obj in del_objects:
            deleted = True
            self.object_list.remove(obj)
            if not self.out_of_range(obj.pos):
                self.pos_to_objs(pos).remove(obj)
        return deleted
    # @auto_refresh
    def del_objs_from_pos_and_noun(self, pos: bmp.loc.Coord[int], noun: bmp.obj.Noun) -> bool:
        del_objects = filter(lambda o: noun.isreferenceof(o), self.pos_to_objs(pos))
        deleted = False
        for obj in del_objects:
            deleted = True
            self.object_list.remove(obj)
            if not self.out_of_range(obj.pos):
                self.pos_to_objs(pos).remove(obj)
        return deleted
    # @auto_refresh
    def set_obj_pos(self, obj: bmp.obj.Object, pos: bmp.loc.Coord[int]) -> None:
        self.pos_to_objs(obj.pos).remove(obj)
        obj.pos = pos
        self.pos_to_objs(pos).append(obj)
    # @auto_refresh
    def get_spaces(self) -> list[bmp.obj.SpaceObject]:
        return [o for o in self.object_list if isinstance(o, bmp.obj.SpaceObject)]
    # @auto_refresh
    def get_spaces_from_pos(self, pos: bmp.loc.Coord[int]) -> list[bmp.obj.SpaceObject]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, bmp.obj.SpaceObject)]
    # @auto_refresh
    def get_levels(self) -> list[bmp.obj.LevelObject]:
        return [o for o in self.object_list if isinstance(o, bmp.obj.LevelObject)]
    # @auto_refresh
    def get_levels_from_pos(self, pos: bmp.loc.Coord[int]) -> list[bmp.obj.LevelObject]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, bmp.obj.LevelObject)]
    def get_rule_from_pos_and_direct(self, pos: bmp.loc.Coord[int], direct: bmp.loc.Orient, stage: str = "before prefix") -> tuple[list[bmp.rule.Rule], list[bmp.rule.RuleInfo]]:
        new_rule_list: list[bmp.rule.Rule] = []
        new_info_list: list[bmp.rule.RuleInfo] = []
        for match_type, unmatch_type, next_stage, func in bmp.rule.how_to_match_rule[stage]:
            text_list: list[bmp.obj.Text] = self.get_objs_from_pos_and_type(pos, bmp.obj.Text)
            text_list += [
                o.transform(bmp.obj.get_noun_from_type(type(o)))
                for o in self.get_objs_from_pos(pos)
                if o.old_state.prop is not None and o.old_state.prop.enabled(bmp.obj.TextWord)
            ] # type: ignore
            matched_list = [o for o in text_list if isinstance(o, tuple(match_type))]
            if len(unmatch_type) != 0:
                matched_list = [o for o in matched_list if not isinstance(o, tuple(unmatch_type))]
            if len(matched_list) != 0:
                rule_list, info_list = self.get_rule_from_pos_and_direct(bmp.loc.front_position(pos, direct), direct, next_stage)
                for matched_text in matched_list:
                    new_rule_list.extend([matched_text] + r for r in rule_list)
                    new_info_list.extend(func(i, matched_text) for i in info_list)
            if stage == "after property":
                new_rule_list.append([])
                new_info_list.append(bmp.rule.RuleInfo([], False, bmp.obj.Noun(), [], [bmp.rule.OperInfo(bmp.obj.Operator(), [])]))
        return new_rule_list, new_info_list
    def set_rule(self) -> None:
        for text_obj in self.get_objs_from_type(bmp.obj.Text):
            text_obj.render_state = bmp.obj.TextRenderState.UNUSED
        self.rule_list = []
        self.rule_info = []
        x_rule_dict: dict[int, list[bmp.rule.Rule]] = {}
        y_rule_dict: dict[int, list[bmp.rule.Rule]] = {}
        for x in range(self.width):
            for y in range(self.height):
                x_rule_dict.setdefault(x, [])
                new_rule_list, new_rule_info = self.get_rule_from_pos_and_direct((x, y), bmp.loc.Orient.D)
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
                new_rule_list, new_rule_info = self.get_rule_from_pos_and_direct((x, y), bmp.loc.Orient.S)
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
        for rule in self.rule_list:
            for text_obj in rule:
                text_obj.render_state = bmp.obj.TextRenderState.USED
    def set_sprite_states(self, round_num: int = 0) -> None:
        for obj in self.object_list:
            if obj.sprite_category == "tiled":
                connected = {
                    o: len(self.get_objs_from_pos_and_type(
                        bmp.loc.front_position(obj.pos, o), type(obj)
                    )) != 0
                    for o in bmp.loc.Orient
                }
            else:
                connected = {o: False for o in bmp.loc.Orient}
            obj.set_sprite(round_num=round_num, connected=connected)
    def get_stacked_transform(self, static: bmp.loc.SpaceTransform, dynamic: bmp.loc.SpaceTransform) -> bmp.loc.SpaceTransform:
        transform = bmp.loc.get_stacked_transform(
            bmp.loc.get_stacked_transform(self.static_transform, self.dynamic_transform),
            bmp.loc.get_stacked_transform(static, dynamic)
        )
        return transform
    def calc_enter_transnum(self, transnum: float, pos: bmp.loc.Coord[int], side: bmp.loc.Orient, transform: bmp.loc.SpaceTransform) -> float:
        new_side = bmp.loc.turn(side, bmp.loc.Orient[transform["direct"]])
        if new_side in (bmp.loc.Orient.W, bmp.loc.Orient.S):
            new_transnum = (transnum * self.width) - pos[0]
        else:
            new_transnum = (transnum * self.height) - pos[1]
        if transform["flip"]:
            new_transnum = 1.0 - new_transnum
        return new_transnum
    def calc_leave_transnum(self, transnum: float, pos: bmp.loc.Coord[int], side: bmp.loc.Orient, transform: bmp.loc.SpaceTransform) -> float:
        new_side = bmp.loc.turn(side, bmp.loc.Orient[transform["direct"]])
        if new_side in (bmp.loc.Orient.W, bmp.loc.Orient.S):
            new_transnum = (transnum + pos[0]) / self.width
        else:
            new_transnum = (transnum + pos[1]) / self.height
        return new_transnum
    def get_leave_transnum_from_pos(self, pos: bmp.loc.Coord[int], side: bmp.loc.Orient, transform: bmp.loc.SpaceTransform) -> float:
        new_side = bmp.loc.turn(side, bmp.loc.Orient[transform["direct"]])
        if new_side in (bmp.loc.Orient.W, bmp.loc.Orient.S):
            new_transnum = (pos[0] + 0.5) / self.width
        else:
            new_transnum = (pos[1] + 0.5) / self.height
        if transform["flip"]:
            new_transnum = 1.0 - new_transnum
        return new_transnum
    def get_enter_pos_by_default(self, side: bmp.loc.Orient, transform: bmp.loc.SpaceTransform) -> bmp.loc.Coord[int]:
        new_side = bmp.loc.swap_direction(side) if transform["flip"] and side in (bmp.loc.Orient.A, bmp.loc.Orient.D) else side
        new_side = bmp.loc.turn(new_side, bmp.loc.Orient[transform["direct"]])
        match new_side:
            case bmp.loc.Orient.W:
                return (self.width // 2, -1)
            case bmp.loc.Orient.A:
                return (-1, self.height // 2)
            case bmp.loc.Orient.S:
                return (self.width // 2, self.height)
            case bmp.loc.Orient.D:
                return (self.width, self.height // 2)
    def get_enter_pos(self, transnum: float, side: bmp.loc.Orient, transform: bmp.loc.SpaceTransform) -> bmp.loc.Coord[int]:
        new_side = bmp.loc.swap_direction(side) if transform["flip"] and side in (bmp.loc.Orient.A, bmp.loc.Orient.D) else side
        new_side = bmp.loc.turn(new_side, bmp.loc.Orient[transform["direct"]])
        new_transnum = (1.0 - transnum) if transform["flip"] and side in (bmp.loc.Orient.A, bmp.loc.Orient.D) else transnum
        match new_side:
            case bmp.loc.Orient.W:
                return (int((new_transnum * self.width)), -1)
            case bmp.loc.Orient.S:
                return (int((new_transnum * self.width)), self.height)
            case bmp.loc.Orient.A:
                return (-1, int((new_transnum * self.height)))
            case bmp.loc.Orient.D:
                return (self.width, int((new_transnum * self.height)))
    def to_json(self) -> SpaceJson:
        json_object: SpaceJson = {
            "id": self.space_id.to_json(),
            "size": (self.width, self.height),
            "objects": []
        }
        if self.color is not None:
            json_object["color"] = self.color
        for obj in tqdm(
            self.object_list,
            desc = bmp.lang.fformat("saving.space.objects"),
            unit = bmp.lang.fformat("object.name"),
            position = 2,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["objects"].append(obj.to_json())
        return json_object

type AnySpaceJson = SpaceJson41 | SpaceJson4102 | SpaceJson

def formatted_after_41(json_object: AnySpaceJson, ver: str) -> TypeGuard[SpaceJson41]:
    return bmp.base.compare_versions(ver, "4.1") >= 0

def formatted_after_4102(json_object: AnySpaceJson, ver: str) -> TypeGuard[SpaceJson4102]:
    return bmp.base.compare_versions(ver, "4.102") >= 0

def formatted_currently(json_object: AnySpaceJson, ver: str) -> TypeGuard[SpaceJson]:
    return bmp.base.compare_versions(ver, bmp.base.version) == 0

def formatted_from_future(json_object: AnySpaceJson, ver: str) -> TypeGuard[AnySpaceJson]:
    return bmp.base.compare_versions(ver, bmp.base.version) > 0

def update_json_format(json_object: AnySpaceJson, ver: str) -> SpaceJson:
    # old levelpacks aren't able to update in 4.1
    if not isinstance(json_object, dict):
        raise TypeError(type(json_object))
    elif formatted_from_future(json_object, ver):
        raise bmp.base.DowngradeError(ver)
    elif formatted_currently(json_object, ver):
        return json_object
    elif formatted_after_4102(json_object, ver):
        return json_object
    elif formatted_after_41(json_object, ver):
        return {
            "objects": json_object["object_list"],
            "color": json_object.get("color", 0x000000),
            "id": json_object["id"],
            "size": json_object["size"],
        }
    else:
        raise bmp.base.UpgradeError(json_object)

def json_to_space(json_object: SpaceJson) -> Space:
    space_id: bmp.ref.SpaceID = bmp.ref.SpaceID(**json_object["id"])
    new_space = Space(
        space_id = space_id,
        size = (json_object["size"][0], json_object["size"][1]),
        color=json_object.get("color")
    )
    for obj in tqdm(
        json_object["objects"],
        desc = bmp.lang.fformat("loading.space.objects"),
        unit = bmp.lang.fformat("object.name"),
        position = 2,
        **bmp.lang.default_tqdm_args,
    ):
        new_space.object_list.append(bmp.obj.json_to_object(obj))
    new_space.refresh_index()
    return new_space