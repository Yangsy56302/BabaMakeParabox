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
        self.world_properties: list[tuple[type[objects.BmpObject], int]] = []
        self.clone_properties: list[tuple[type[objects.BmpObject], int]] = []
        self.world_write_text: list[type[objects.Noun] | type[objects.Property]] = []
        self.clone_write_text: list[type[objects.Noun] | type[objects.Property]] = []
        self.rule_list: list[rules.Rule] = []
        self.refresh_index()
    def __eq__(self, world: "World") -> bool:
        return self.name == world.name and self.infinite_tier == world.infinite_tier
    def new_world_prop(self, prop: type[objects.Text], negated_count: int = 0) -> None:
        del_props = []
        for old_prop, old_negated_count in self.world_properties:
            if prop == old_prop:
                if old_negated_count > negated_count:
                    return
                del_props.append((old_prop, old_negated_count))
        for old_prop, old_negated_count in del_props:
            self.world_properties.remove((old_prop, old_negated_count))
        self.world_properties.append((prop, negated_count))
    def del_world_prop(self, prop: type[objects.Text], negated_count: int = 0) -> None:
        if (prop, negated_count) in self.world_properties:
            self.world_properties.remove((prop, negated_count))
    def has_world_prop(self, prop: type[objects.Text], negate: bool = False) -> bool:
        for get_prop, get_negated_count in self.world_properties:
            if get_prop == prop and get_negated_count % 2 == int(negate):
                return True
        return False
    def new_clone_prop(self, prop: type[objects.Text], negated_count: int = 0) -> None:
        del_props = []
        for old_prop, old_negated_count in self.clone_properties:
            if prop == old_prop:
                if old_negated_count > negated_count:
                    return
                del_props.append((old_prop, old_negated_count))
        for old_prop, old_negated_count in del_props:
            self.clone_properties.remove((old_prop, old_negated_count))
        self.clone_properties.append((prop, negated_count))
    def del_clone_prop(self, prop: type[objects.Text], negated_count: int = 0) -> None:
        if (prop, negated_count) in self.clone_properties:
            self.clone_properties.remove((prop, negated_count))
    def has_clone_prop(self, prop: type[objects.Text], negate: bool = False) -> bool:
        for get_prop, get_negated_count in self.clone_properties:
            if get_prop == prop and get_negated_count % 2 == int(negate):
                return True
        return False
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
    def get_rules_from_pos_and_orient(self, stage: str, pos: spaces.Coord, orient: spaces.Orient) -> list[rules.Rule]:
        if stage == "Prefix":
            first_matches = ()
            then_matches = (objects.Prefix, )
            next_stages = ("AndPrefix", "Noun")
            rule_can_be_done = False
        elif stage == "AndPrefix":
            first_matches = (objects.TextAnd, )
            then_matches = (objects.Prefix, )
            next_stages = ("AndPrefix", "Noun")
            rule_can_be_done = False
        elif stage == "Noun":
            first_matches = ()
            then_matches = (objects.Noun, )
            next_stages = ("AndPrefix", "AndNoun", "InfixText", "Operator")
            rule_can_be_done = False
        elif stage == "AndNoun":
            first_matches = (objects.TextAnd, )
            then_matches = (objects.Noun, )
            next_stages = ("AndPrefix", "AndNoun", "InfixText", "Operator")
            rule_can_be_done = False
        elif stage == "InfixText":
            first_matches = (objects.Infix, )
            then_matches = (objects.Noun, objects.Property)
            next_stages = ("AndPrefix", "AndNoun", "AndInfixText", "Operator")
            rule_can_be_done = False
        elif stage == "AndInfixText":
            first_matches = (objects.TextAnd, objects.Infix)
            then_matches = (objects.Noun, objects.Property)
            next_stages = ("AndPrefix", "AndNoun", "AndInfixText", "Operator")
            rule_can_be_done = False
        elif stage == "Operator":
            first_matches = ()
            then_matches = (objects.Operator, )
            next_stages = ("Property", )
            rule_can_be_done = False
        elif stage == "AndOperator":
            first_matches = (objects.TextAnd, )
            then_matches = (objects.Operator, )
            next_stages = ("Property", )
            rule_can_be_done = False
        elif stage == "Property":
            first_matches = ()
            then_matches = (objects.Noun, objects.Property)
            next_stages = ("AndOperator", "AndProperty")
            rule_can_be_done = False
        elif stage == "AndProperty":
            first_matches = (objects.TextAnd, )
            then_matches = (objects.Noun, objects.Property)
            next_stages = ("AndOperator", "AndProperty")
            rule_can_be_done = True
        else:
            raise ValueError(stage)
        not_rules: list[rules.Rule] = []
        if stage in ("Prefix", "Noun", "InfixText", "Property"):
            text__objs = self.get_objs_from_pos_and_type(pos, objects.TextNot)
            if len(text__objs) != 0:
                not_rules = self.get_rules_from_pos_and_orient(stage, spaces.pos_facing(pos, orient), orient)
                not_rules = [[objects.TextNot] + r for r in not_rules if len(r) != 0]
        new_pos = pos
        first_matched_list: list[list[type[objects.Text]]] = []
        for first_match in first_matches:
            text_objs = list(map(type, self.get_objs_from_pos_and_type(new_pos, objects.Text)))
            word_objs = filter(lambda o: o.has_prop(objects.TextWord), self.get_objs_from_pos(new_pos))
            text_objs.extend(map(lambda o: objects.get_noun_from_obj(type(o)), word_objs))
            first_matched = [o for o in text_objs if issubclass(o, first_match)]
            if len(first_matched) == 0 and len(not_rules) == 0:
                return [[]] if rule_can_be_done else []
            first_matched_list.append(first_matched) # type: ignore
            new_pos = spaces.pos_facing(new_pos, orient)
        prefix_rules: list[rules.Rule] = []
        if stage in ("Prefix", "AndPrefix"):
            prefix_objs = self.get_objs_from_pos_and_type(new_pos, objects.Prefix)
            for next_stage in next_stages:
                for prefix_obj in prefix_objs:
                    temp_prefix_rules = self.get_rules_from_pos_and_orient(next_stage, spaces.pos_facing(new_pos, orient), orient)
                    prefix_rules.extend([[type(prefix_obj)] + r for r in temp_prefix_rules if len(r) != 0])
        text_objs = list(map(type, self.get_objs_from_pos_and_type(new_pos, objects.Text)))
        word_objs = filter(lambda o: o.has_prop(objects.TextWord), self.get_objs_from_pos(new_pos))
        text_objs.extend(map(lambda o: objects.get_noun_from_obj(type(o)), word_objs))
        if len(text_objs) == 0 and len(not_rules) == 0:
            return [[]] if rule_can_be_done else []
        then_matched: list[type[objects.Text]] = [o for o in text_objs if issubclass(o, then_matches)]
        remain_rules: list[rules.Rule] = []
        for next_stage in next_stages:
            remain_rules.extend(self.get_rules_from_pos_and_orient(next_stage, spaces.pos_facing(new_pos, orient), orient))
        temp_pos = new_pos
        text__then_matched: list[type[objects.Text]] = []
        text__remain_rules: list[rules.Rule] = []
        text__after_first_len = 0
        if stage in ("Noun", "AndNoun", "InfixText", "AndInfixText", "Property", "AndProperty"):
            while True:
                text__objs = self.get_objs_from_pos_and_type(temp_pos, objects.TextText_)
                if len(text__objs) == 0:
                    break
                text__after_first_len += 1
                temp_pos = spaces.pos_facing(temp_pos, orient)
            if text__after_first_len > 0:
                text_objs = list(map(type, self.get_objs_from_pos_and_type(temp_pos, objects.Text)))
                word_objs = filter(lambda o: o.has_prop(objects.TextWord), self.get_objs_from_pos(temp_pos))
                text_objs.extend(map(lambda o: objects.get_noun_from_obj(type(o)), word_objs))
                text__then_matched = [o for o in text_objs]
                for next_stage in next_stages:
                    text__remain_rules.extend(self.get_rules_from_pos_and_orient(next_stage, spaces.pos_facing(temp_pos, orient), orient))
        not_then_matched: list[type[objects.Text]] = []
        not_remain_rules: list[rules.Rule] = []
        not_after_first_len = 0
        not_text__then_matched: list[type[objects.Text]] = []
        not_text__remain_rules: list[rules.Rule] = []
        not_text__after_first_len = 0
        if stage in ("Prefix", "AndPrefix", "Noun", "AndNoun", "InfixText", "AndInfixText", "Property", "AndProperty"):
            while True:
                text__objs = self.get_objs_from_pos_and_type(new_pos, objects.TextNot)
                if len(text__objs) == 0:
                    break
                not_after_first_len += 1
                new_pos = spaces.pos_facing(new_pos, orient)
            text_objs = list(map(type, self.get_objs_from_pos_and_type(new_pos, objects.Text)))
            word_objs = filter(lambda o: o.has_prop(objects.TextWord), self.get_objs_from_pos(new_pos))
            text_objs.extend(map(lambda o: objects.get_noun_from_obj(type(o)), word_objs))
            not_then_matched = [o for o in text_objs if issubclass(o, then_matches)]
            for next_stage in next_stages:
                not_remain_rules.extend(self.get_rules_from_pos_and_orient(next_stage, spaces.pos_facing(new_pos, orient), orient))
            if stage in ("Noun", "AndNoun", "InfixText", "AndInfixText", "Property", "AndProperty"):
                while True:
                    text__objs = self.get_objs_from_pos_and_type(new_pos, objects.TextText_)
                    if len(text__objs) == 0:
                        break
                    not_text__after_first_len += 1
                    new_pos = spaces.pos_facing(new_pos, orient)
                if not_text__after_first_len > 0:
                    text_objs = list(map(type, self.get_objs_from_pos_and_type(new_pos, objects.Text)))
                    word_objs = filter(lambda o: o.has_prop(objects.TextWord), self.get_objs_from_pos(new_pos))
                    text_objs.extend(map(lambda o: objects.get_noun_from_obj(type(o)), word_objs))
                    not_text__then_matched = [o for o in text_objs]
                    for next_stage in next_stages:
                        not_text__remain_rules.extend(self.get_rules_from_pos_and_orient(next_stage, spaces.pos_facing(new_pos, orient), orient))
        if len(then_matched) == 0 and len(text__then_matched) == 0 and len(not_then_matched) == 0 and len(not_text__then_matched) == 0 and len(not_rules) == 0 and len(prefix_rules) == 0:
            return [[]] if rule_can_be_done else []
        return_rules: list[rules.Rule] = [[]]
        new_return_rules: list[rules.Rule] = []
        if len(first_matched_list) != 0:
            for matches in first_matched_list:
                new_return_rules = []
                for match in matches:
                    for rule in return_rules:
                        new_return_rules.append(rule + [match])
                return_rules = new_return_rules[:]
        then_return_rules = []
        new_then_return_rules = []
        for match in then_matched:
            for rule in return_rules:
                if stage in ("InfixText", "AndInfixText"):
                    if rule[-1] == objects.TextFeeling: # prop infix
                        if issubclass(match, objects.Property):
                            new_then_return_rules.append(rule + [match])
                    elif issubclass(match, objects.Noun): # noun infix
                        new_then_return_rules.append(rule + [match])
                else:
                    new_then_return_rules.append(rule + [match])
        then_return_rules = new_then_return_rules[:]
        text__then_return_rules = []
        if text__after_first_len != 0:
            text__then_new_return_rules = []
            for match in text__then_matched:
                for rule in return_rules:
                    if stage in ("InfixText", "AndInfixText"):
                        if rule[-1] == objects.TextFeeling: # prop infix
                            if issubclass(match, objects.Property):
                                text__then_new_return_rules.append(rule + [objects.TextText_ for _ in range(text__after_first_len)] + [match])
                        elif issubclass(match, objects.Noun): # noun infix
                            text__then_new_return_rules.append(rule + [objects.TextText_ for _ in range(text__after_first_len)] + [match])
                    else:
                        text__then_new_return_rules.append(rule + [objects.TextText_ for _ in range(text__after_first_len)] + [match])
            text__then_return_rules = text__then_new_return_rules[:]
        not_then_return_rules = []
        if not_after_first_len != 0:
            not_then_new_return_rules = []
            for match in not_then_matched:
                for rule in return_rules:
                    if stage in ("InfixText", "AndInfixText"):
                        if rule[-1] == objects.TextFeeling: # prop infix
                            if issubclass(match, objects.Property):
                                not_then_new_return_rules.append(rule + [objects.TextNot for _ in range(not_after_first_len)] + [match])
                        elif issubclass(match, objects.Noun): # noun infix
                            not_then_new_return_rules.append(rule + [objects.TextNot for _ in range(not_after_first_len)] + [match])
                    else:
                        not_then_new_return_rules.append(rule + [objects.TextNot for _ in range(not_after_first_len)] + [match])
            not_then_return_rules = not_then_new_return_rules[:]
        not_text__then_return_rules = []
        if not_text__after_first_len != 0:
            not_text__then_new_return_rules = []
            for match in not_text__then_matched:
                for rule in return_rules:
                    if stage in ("InfixText", "AndInfixText"):
                        if rule[-1] == objects.TextFeeling: # prop infix
                            if issubclass(match, objects.Property):
                                not_text__then_new_return_rules.append(rule + [objects.TextNot for _ in range(not_after_first_len)] + [objects.TextText_ for _ in range(not_text__after_first_len)] + [match])
                        elif issubclass(match, objects.Noun): # noun infix
                            not_text__then_new_return_rules.append(rule + [objects.TextNot for _ in range(not_after_first_len)] + [objects.TextText_ for _ in range(not_text__after_first_len)] + [match])
                    else:
                        not_text__then_new_return_rules.append(rule + [objects.TextNot for _ in range(not_after_first_len)] + [objects.TextText_ for _ in range(not_text__after_first_len)] + [match])
            not_text__then_return_rules = not_text__then_new_return_rules[:]
        new_return_rules = []
        for remain_rule in remain_rules:
            for then_return_rule in then_return_rules:
                if stage in ("Operator", "AndOperator"):
                    if then_return_rule[-1] in (objects.TextHas, objects.TextMake): # noun infix
                        if not issubclass(remain_rule[0], objects.Noun):
                            continue
                    if then_return_rule[-1] == objects.TextWrite: # noun / prop infix
                        if not issubclass(remain_rule[0], (objects.Noun, objects.Property)):
                            continue
                new_return_rules.append(then_return_rule + remain_rule)
        for not_remain_rule in not_remain_rules:
            for not_then_return_rule in not_then_return_rules:
                new_return_rules.append(not_then_return_rule + not_remain_rule)
        for text__remain_rule in text__remain_rules:
            for text__then_return_rule in text__then_return_rules:
                new_return_rules.append(text__then_return_rule + text__remain_rule)
        for not_text__remain_rule in not_text__remain_rules:
            for not_text__then_return_rule in not_text__then_return_rules:
                new_return_rules.append(not_text__then_return_rule + not_text__remain_rule)
        if len(not_rules) != 0:
            new_return_rules.extend(not_rules)
        if len(prefix_rules) != 0:
            new_return_rules.extend(prefix_rules)
        return new_return_rules
    def get_rules(self) -> list[rules.Rule]:
        rule_list: list[rules.Rule] = []
        x_rule_dict: dict[int, list[rules.Rule]] = {}
        y_rule_dict: dict[int, list[rules.Rule]] = {}
        for x in range(self.width):
            for y in range(self.height):
                x_rule_dict.setdefault(x, [])
                new_rule_list = self.get_rules_from_pos_and_orient("Prefix", (x, y), spaces.Orient.D)
                new_rule_list.extend(self.get_rules_from_pos_and_orient("Noun", (x, y), spaces.Orient.D))
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
                new_rule_list = self.get_rules_from_pos_and_orient("Prefix", (x, y), spaces.Orient.S)
                new_rule_list.extend(self.get_rules_from_pos_and_orient("Noun", (x, y), spaces.Orient.S))
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
                wsad = {spaces.Orient.W: w, spaces.Orient.S: s, spaces.Orient.A: a, spaces.Orient.D: d}
            else:
                wsad = {spaces.Orient.W: False, spaces.Orient.S: False, spaces.Orient.A: False, spaces.Orient.D: False}
            displays.set_sprite_state(obj, round_num, wsad) # type: ignore
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
            case _:
                raise ValueError()
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
            case _:
                raise ValueError()
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