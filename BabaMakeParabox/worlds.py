from typing import Any, Optional
import random

from BabaMakeParabox import colors, spaces, objects, rules, displays

def match_pos(obj: objects.Object, pos: spaces.Coord) -> bool:
    return obj.pos == pos

class world(object):
    def __init__(self, name: str, size: tuple[int, int], inf_tier: int = 0, color: Optional[colors.ColorHex] = None) -> None:
        self.name: str = name
        self.inf_tier: int = inf_tier
        self.width: int = size[0]
        self.height: int = size[1]
        self.color: colors.ColorHex = color if color is not None else colors.random_world_color()
        self.object_list: list[objects.Object] = []
        self.object_pos_index: list[list[objects.Object]]
        self.properties: list[tuple[type[objects.Object], int]] = []
        self.rule_list: list[rules.Rule] = []
        self.strict_rule_list: list[rules.Rule] = []
        self.refresh_index()
    def __eq__(self, world: "world") -> bool:
        return self.name == world.name and self.inf_tier == world.inf_tier
    def new_prop(self, prop: type[objects.Text], negated_count: int = 0) -> None:
        del_props = []
        for old_prop, old_negated_count in self.properties:
            if prop == old_prop:
                if old_negated_count > negated_count:
                    return
                del_props.append((old_prop, old_negated_count))
        for old_prop, old_negated_count in del_props:
            self.properties.remove((old_prop, old_negated_count))
        self.properties.append((prop, negated_count))
    def del_prop(self, prop: type[objects.Text], negated_count: int = 0) -> None:
        if (prop, negated_count) in self.properties:
            self.properties.remove((prop, negated_count))
    def has_prop(self, prop: type[objects.Text], negate: bool = False) -> bool:
        for get_prop, get_negated_count in self.properties:
            if get_prop == prop and get_negated_count % 2 == int(negate):
                return True
        return False
    def out_of_range(self, coord: spaces.Coord) -> bool:
        return coord[0] < 0 or coord[1] < 0 or coord[0] >= self.width or coord[1] >= self.height
    def pos_to_index(self, pos) -> int:
        return pos[1] * self.width + pos[0]
    def pos_to_objs(self, pos) -> list[objects.Object]:
        return self.object_pos_index[self.pos_to_index(pos)]
    def refresh_index(self) -> None:
        self.object_pos_index = [[] for _ in range(self.width * self.height)]
        for obj in self.object_list:
            self.pos_to_objs(obj.pos).append(obj)
    def new_obj(self, obj: objects.Object) -> None:
        self.object_list.append(obj)
        self.pos_to_objs(obj.pos).append(obj)
    def get_objs_from_pos(self, pos: spaces.Coord) -> list[objects.Object]:
        if self.out_of_range(pos):
            return []
        return self.pos_to_objs(pos)
    def get_objs_from_pos_and_type[T: objects.Object](self, pos: spaces.Coord, obj_type: type[T]) -> list[T]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, obj_type)]
    def get_objs_from_type[T: objects.Object](self, obj_type: type[T]) -> list[T]:
        return [o for o in self.object_list if isinstance(o, obj_type)]
    def del_obj(self, obj: objects.Object) -> None:
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
    def get_levels(self) -> list[objects.Level]:
        return [o for o in self.object_list if isinstance(o, objects.Level)]
    def get_levels_from_pos(self, pos: spaces.Coord) -> list[objects.Level]:
        if self.out_of_range(pos):
            return []
        return [o for o in self.pos_to_objs(pos) if isinstance(o, objects.Level)]
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
            self.del_obj(to_clone)
    def get_rules_from_pos_and_orient(self, stage: Optional[str], pos: spaces.Coord, orient: spaces.Orient) -> list[rules.Rule]:
        if stage == "Noun":
            first_matches = ()
            then_matches = (objects.Noun, )
            next_stages = ("AndNoun", "InfixText", "Operator")
            rule_can_be_done = False
        elif stage == "AndNoun":
            first_matches = (objects.AND, )
            then_matches = (objects.Noun, )
            next_stages = ("AndNoun", "InfixText", "Operator")
            rule_can_be_done = False
        elif stage == "InfixText":
            first_matches = (objects.Infix, )
            then_matches = (objects.Noun, objects.Property)
            next_stages = ("AndNoun", "AndInfixText", "Operator")
            rule_can_be_done = False
        elif stage == "AndInfixText":
            first_matches = (objects.AND, objects.Infix)
            then_matches = (objects.Noun, objects.Property)
            next_stages = ("AndNoun", "AndInfixText", "Operator")
            rule_can_be_done = False
        elif stage == "Operator":
            first_matches = ()
            then_matches = (objects.Operator, )
            next_stages = ("Property", )
            rule_can_be_done = False
        elif stage == "Property":
            first_matches = ()
            then_matches = (objects.Noun, objects.Property)
            next_stages = ("AndProperty", )
            rule_can_be_done = False
        elif stage == "AndProperty":
            first_matches = (objects.AND, )
            then_matches = (objects.Noun, objects.Property)
            next_stages = ("AndProperty", )
            rule_can_be_done = True
        not_rules: list[rules.Rule] = []
        if stage in ("Noun", "AndNoun", "InfixText", "AndInfixText", "Property", "AndProperty"):
            not_objs = self.get_objs_from_pos_and_type(pos, objects.NOT)
            if len(not_objs) != 0:
                not_rules = self.get_rules_from_pos_and_orient(stage, spaces.pos_facing(pos, orient), orient)
                not_rules = [[objects.NOT] + r for r in not_rules if len(r) != 0]
        new_pos = pos
        first_matched_list: list[list[objects.Text]] = []
        for first_match in first_matches:
            text_objs = self.get_objs_from_pos_and_type(new_pos, objects.Text)
            word_objs = filter(lambda o: o.has_prop(objects.WORD), self.get_objs_from_pos(new_pos))
            text_objs.extend(map(lambda o: objects.nouns_objs_dicts.get_exist_noun(type(o))(new_pos), word_objs))
            first_matched = [o for o in text_objs if isinstance(o, first_match)]
            if len(first_matched) == 0 and len(not_rules) == 0:
                return [[]] if rule_can_be_done else []
            first_matched_list.append(first_matched) # type: ignore
            new_pos = spaces.pos_facing(new_pos, orient)
        text_objs = self.get_objs_from_pos_and_type(new_pos, objects.Text)
        word_objs = filter(lambda o: o.has_prop(objects.WORD), self.get_objs_from_pos(new_pos))
        text_objs.extend(map(lambda o: objects.nouns_objs_dicts.get_exist_noun(type(o))(new_pos), word_objs))
        then_matched: list[objects.Text] = []
        if len(text_objs) == 0 and len(not_rules) == 0:
            return [[]] if rule_can_be_done else []
        then_matched = [o for o in text_objs if isinstance(o, then_matches)]
        remain_rules: list[rules.Rule] = []
        for next_stage in next_stages:
            remain_rules.extend(self.get_rules_from_pos_and_orient(next_stage, spaces.pos_facing(new_pos, orient), orient))
        not_then_matched: list[objects.Text] = []
        not_remain_rules: list[rules.Rule] = []
        not_after_first_len = 0
        if stage in ("Noun", "AndNoun", "InfixText", "AndInfixText", "Property", "AndProperty"):
            while True:
                not_objs = self.get_objs_from_pos_and_type(new_pos, objects.NOT)
                if len(not_objs) == 0:
                    break
                not_after_first_len += 1
                new_pos = spaces.pos_facing(new_pos, orient)
            text_objs = self.get_objs_from_pos_and_type(new_pos, objects.Text)
            word_objs = filter(lambda o: o.has_prop(objects.WORD), self.get_objs_from_pos(new_pos))
            text_objs.extend(map(lambda o: objects.nouns_objs_dicts.get_exist_noun(type(o))(new_pos), word_objs))
            if len(text_objs) != 0:
                not_then_matched = [o for o in text_objs if isinstance(o, then_matches)]
            for next_stage in next_stages:
                not_remain_rules.extend(self.get_rules_from_pos_and_orient(next_stage, spaces.pos_facing(new_pos, orient), orient))
        if len(then_matched) == 0 and len(not_then_matched) == 0 and len(not_rules) == 0:
            return [[]] if rule_can_be_done else []
        return_rules: list[rules.Rule] = [[]]
        new_return_rules: list[rules.Rule] = []
        if len(first_matched_list) != 0:
            for matches in first_matched_list:
                for match in matches:
                    for rule in return_rules:
                        new_return_rules.append(rule + [type(match)])
            return_rules = new_return_rules[:]
        not_return_rules = []
        if not_after_first_len != 0:
            not_new_return_rules = []
            for match in not_then_matched:
                for rule in return_rules:
                    not_new_return_rules.append(rule + [objects.NOT for _ in range(not_after_first_len)] + [type(match)])
            not_return_rules = not_new_return_rules[:]
        new_return_rules = []
        for match in then_matched:
            for rule in return_rules:
                new_return_rules.append(rule + [type(match)])
        return_rules = new_return_rules[:]
        new_return_rules = []
        for remain_rule in remain_rules:
            for return_rule in return_rules:
                new_return_rules.append(return_rule + remain_rule)
        for not_remain_rule in not_remain_rules:
            for not_return_rule in not_return_rules:
                new_return_rules.append(not_return_rule + not_remain_rule)
        if len(not_rules) != 0:
            new_return_rules.extend(not_rules)
        return new_return_rules
    def get_rules(self) -> list[rules.Rule]:
        rule_list: list[rules.Rule] = []
        x_rule_dict: dict[int, list[rules.Rule]] = {}
        y_rule_dict: dict[int, list[rules.Rule]] = {}
        for x in range(self.width):
            for y in range(self.height):
                x_rule_dict.setdefault(x, [])
                new_rule_list = self.get_rules_from_pos_and_orient("Noun", (x, y), spaces.D)
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
                new_rule_list = self.get_rules_from_pos_and_orient("Noun", (x, y), spaces.S)
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
    new_world.refresh_index()
    return new_world