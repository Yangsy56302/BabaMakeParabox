from typing import Optional, TypedDict, NotRequired
import copy
from tqdm import tqdm

import bmp.base
import bmp.level
import bmp.loc
import bmp.obj
import bmp.ref
import bmp.rule
import bmp.space

class ReturnInfo(TypedDict):
    win: bool
    end: bool
    done: bool
    transform: bool
    game_push: bool
    selected_level: Optional[bmp.ref.LevelID]
default_levelpack_info: ReturnInfo = {"win": False, "end": False, "done": False, "transform": False, "game_push": False, "selected_level": None}

class LevelpackJson(TypedDict):
    ver: str
    name: NotRequired[str]
    author: NotRequired[str]
    current_level: bmp.ref.LevelIDJson
    collectibles: list[bmp.obj.CollectibleJson]
    levels: list[bmp.level.LevelJson]
    spaces: list[bmp.space.SpaceJson]
    level_init_states: NotRequired[list[bmp.level.LevelJson]]
    space_init_states: NotRequired[list[bmp.space.SpaceJson]]
    rules: list[list[str]]

class Levelpack(object):
    def __init__(
        self,
        level_dict: dict[bmp.ref.LevelID, bmp.level.Level],
        space_dict: dict[bmp.ref.SpaceID, bmp.space.Space],
        current_level_id: bmp.ref.LevelID,
        name: Optional[str] = None,
        author: Optional[str] = None,
        level_init_state_dict: Optional[dict[bmp.ref.LevelID, bmp.level.Level]] = None,
        space_init_state_dict: Optional[dict[bmp.ref.SpaceID, bmp.space.Space]] = None,
        collectibles: Optional[set[bmp.obj.Collectible]] = None,
        rule_list: Optional[list[bmp.rule.Rule]] = None,
    ) -> None:
        self.name: Optional[str] = name
        self.author: Optional[str] = author
        self.level_dict: dict[bmp.ref.LevelID, bmp.level.Level] = level_dict
        self.space_dict: dict[bmp.ref.SpaceID, bmp.space.Space] = space_dict
        for level in self.level_dict.values():
            level.space_dict = space_dict
        self.level_init_state_dict: dict[bmp.ref.LevelID, bmp.level.Level] = level_init_state_dict if level_init_state_dict is not None else copy.deepcopy(self.level_dict)
        self.space_init_state_dict: dict[bmp.ref.SpaceID, bmp.space.Space] = space_init_state_dict if space_init_state_dict is not None else copy.deepcopy(self.space_dict)
        for level in self.level_init_state_dict.values():
            level.space_dict = space_dict
        self.current_level_id: bmp.ref.LevelID = current_level_id
        self.collectibles: set[bmp.obj.Collectible] = collectibles if collectibles is not None else set()
        self.rule_list: list[bmp.rule.Rule] = rule_list if (rule_list is not None and len(rule_list) != 0) else bmp.rule.default_rule_list
    def get_exact_level(self, level_id: bmp.ref.LevelID) -> bmp.level.Level:
        return self.level_dict[level_id]
    def get_level(self, level_id: bmp.ref.LevelID) -> Optional[bmp.level.Level]:
        return self.level_dict.get(level_id)
    def set_level(self, level: bmp.level.Level, level_id: Optional[bmp.ref.LevelID] = None) -> None:
        _level_id: bmp.ref.LevelID = level_id if level_id is not None else level.level_id
        level.space_dict = self.space_dict
        self.level_dict[_level_id] = level
    def set_level_init_state(self, level_id: bmp.ref.LevelID, level: bmp.level.Level) -> None:
        self.level_init_state_dict[level_id] = level
    def reset_level(self, level_id: bmp.ref.LevelID) -> None:
        old_level = self.level_dict.get(level_id)
        if old_level is not None and old_level.map_info is None:
            for space_id in old_level.space_included:
                self.space_dict[space_id] = copy.deepcopy(self.space_init_state_dict[space_id])
            level = copy.deepcopy(self.level_init_state_dict[level_id])
            level.space_dict = self.space_dict
            self.level_dict[level_id] = level
    def del_level(self, level_id: bmp.ref.LevelID) -> None:
        self.level_dict.pop(level_id)
        self.level_init_state_dict.pop(level_id)
    @property
    def level_list(self) -> list[bmp.level.Level]:
        return list(self.level_dict.values())
    @level_list.setter
    def level_list(self, __level_list: list[bmp.level.Level]) -> None:
        self.level_dict.clear()
        self.level_dict.update({l.level_id: l for l in __level_list})
        for level in self.level_dict.values():
            level.space_dict = self.space_dict
    @property
    def current_level(self) -> bmp.level.Level:
        return self.level_dict[self.current_level_id]
    @current_level.setter
    def current_level(self, level: bmp.level.Level) -> None:
        self.current_level_id = level.level_id
    def update_rules(self) -> None:
        self.current_level.game_properties = bmp.obj.Properties()
        self.current_level_objs: list[bmp.obj.LevelObject] = []
        for level in self.level_list:
            for space in level.space_list:
                self.current_level_objs.extend([o for o in space.get_levels() if o.level_id == self.current_level.level_id])
        active_space_objs: list[bmp.obj.SpaceObject] = []
        for space in self.current_level.space_list:
            active_space_objs.extend(space.get_spaces())
        for level_object_type in bmp.obj.level_object_types:
            self.current_level.properties[level_object_type] = bmp.obj.Properties()
            self.current_level.special_operator_properties[level_object_type] = {o: bmp.obj.Properties() for o in bmp.obj.special_operators}
        for space in self.current_level.space_list:
            for object_type in bmp.obj.space_object_types:
                space.properties[object_type] = bmp.obj.Properties()
                space.special_operator_properties[object_type] = {o: bmp.obj.Properties() for o in bmp.obj.special_operators}
            for obj in space.object_list:
                obj.properties = bmp.obj.Properties()
                obj.special_operator_properties = {o: bmp.obj.Properties() for o in bmp.obj.special_operators}
        for space in self.current_level.space_list:
            space.set_rule()
        new_prop_list: list[tuple[bmp.obj.Object, tuple[type[bmp.obj.Text], int]]] = []
        global_rule_info_list = [bmp.rule.get_info_from_rule(r) for r in self.rule_list]
        global_rule_info_list = [r for r in global_rule_info_list if r is not None]
        for space in self.current_level.space_list:
            # space & levelpack
            for rule_info in space.rule_info + global_rule_info_list:
                prefix_info_list = rule_info.prefix_info_list
                noun_negated_tier = rule_info.noun_negated_tier
                noun_type = rule_info.noun_type
                infix_info_list = rule_info.infix_info_list
                new_match_obj_list: list[bmp.obj.Object] = []
                if issubclass(noun_type, bmp.obj.GeneralNoun):
                    object_type = noun_type.ref_type
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = self.current_level.all_list) and not isinstance(o, object_type)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_type(object_type)]
                elif noun_type is bmp.obj.TextAll:
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if isinstance(o, bmp.obj.types_in_not_all)]
                    else:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = self.current_level.all_list)]
                elif issubclass(noun_type, bmp.obj.SupportsIsReferenceOf):
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = self.current_level.all_list) and not noun_type.isreferenceof(o)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_special_noun(noun_type)]
                for oper_info in rule_info.oper_list:
                    oper_type = oper_info.oper_type
                    for prop_info in oper_info.prop_list:
                        prop_type = prop_info.prop_type
                        prop_negated_tier = prop_info.prop_negated_tier
                        if issubclass(object_type, bmp.obj.Game) and issubclass(oper_type, bmp.obj.TextIs):
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and len(prefix_info_list) == 0:
                                self.current_level.game_properties.update(prop_type, prop_negated_tier)
                        elif issubclass(object_type, bmp.obj.LevelObject) and noun_negated_tier % 2 == 0:
                            meet_prefix_conditions = any(self.current_level.meet_prefix_conditions(space, o, prefix_info_list, True) for o in self.current_level_objs)
                            meet_infix_conditions = any(self.current_level.meet_infix_conditions(space, o, infix_info_list) for o in self.current_level_objs)
                            if (meet_prefix_conditions and meet_infix_conditions) or (len(prefix_info_list) == 0 and len(infix_info_list) == 0 and len(self.current_level_objs) == 0):
                                if oper_type == bmp.obj.TextIs:
                                    self.current_level.properties[object_type].update(prop_type, prop_negated_tier)
                                else:
                                    self.current_level.special_operator_properties[object_type][oper_type].update(prop_type, prop_negated_tier)
                        elif issubclass(object_type, bmp.obj.SpaceObject) and noun_negated_tier % 2 == 0:
                            meet_prefix_conditions = any(self.current_level.meet_prefix_conditions(space, o, prefix_info_list, True) for o in active_space_objs)
                            meet_infix_conditions = any(self.current_level.meet_infix_conditions(space, o, infix_info_list) for o in active_space_objs)
                            if (meet_prefix_conditions and meet_infix_conditions) or (len(prefix_info_list) == 0 and len(infix_info_list) == 0 and len(active_space_objs) == 0):
                                if oper_type == bmp.obj.TextIs:
                                    space.properties[object_type].update(prop_type, prop_negated_tier)
                                else:
                                    space.special_operator_properties[object_type][oper_type].update(prop_type, prop_negated_tier)
                        for obj in new_match_obj_list:
                            if self.current_level.meet_infix_conditions(space, obj, infix_info_list) and self.current_level.meet_prefix_conditions(space, obj, prefix_info_list):
                                if oper_type == bmp.obj.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                else:
                                    obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
            # outer space
            outer_space_rule_info = self.current_level.recursion_rules(space)[1]
            for rule_info in outer_space_rule_info:
                prefix_info_list = rule_info.prefix_info_list
                noun_negated_tier = rule_info.noun_negated_tier
                noun_type = rule_info.noun_type
                infix_info_list = rule_info.infix_info_list
                new_match_obj_list: list[bmp.obj.Object] = []
                if issubclass(noun_type, bmp.obj.GeneralNoun):
                    object_type = noun_type.ref_type
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = self.current_level.all_list) and not isinstance(o, object_type)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_type(object_type)]
                elif noun_type is bmp.obj.TextAll:
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if isinstance(o, bmp.obj.types_in_not_all)]
                    else:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = self.current_level.all_list)]
                elif issubclass(noun_type, bmp.obj.SupportsIsReferenceOf):
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = self.current_level.all_list) and not noun_type.isreferenceof(o)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_special_noun(noun_type)]
                for oper_info in rule_info.oper_list:
                    oper_type = oper_info.oper_type
                    for prop_info in oper_info.prop_list:
                        prop_type = prop_info.prop_type
                        prop_negated_tier = prop_info.prop_negated_tier
                        if issubclass(object_type, bmp.obj.Game) and issubclass(oper_type, bmp.obj.TextIs):
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and self.current_level.meet_prefix_conditions(space, bmp.obj.Object((0, 0)), prefix_info_list, True):
                                self.current_level.game_properties.update(prop_type, prop_negated_tier)
                        for obj in new_match_obj_list:
                            if self.current_level.meet_infix_conditions(space, obj, infix_info_list) and self.current_level.meet_prefix_conditions(space, obj, prefix_info_list):
                                if oper_type == bmp.obj.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                else:
                                    obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.properties.update(prop_type, prop_negated_count)
    def transform(self) -> None:
        for space in self.current_level.space_list:
            delete_object_list = []
            for old_obj in space.object_list:
                old_type = type(old_obj)
                new_noun_list: list[type["bmp.obj.Noun"]] = []
                for noun_type, prop_count in old_obj.properties.enabled_dict().items():
                    if issubclass(noun_type, bmp.obj.Noun):
                        new_noun_list.extend([noun_type] * prop_count)
                while any(map(lambda p: issubclass(p, bmp.obj.RangedNoun), new_noun_list)):
                    delete_noun_list: list[type[bmp.obj.Noun]] = []
                    for noun_type in new_noun_list:
                        if not issubclass(noun_type, bmp.obj.RangedNoun):
                            continue
                        if issubclass(noun_type, bmp.obj.TextAll):
                            new_noun_list.extend([bmp.obj.get_noun_from_type(o) for o in self.current_level.all_list] * prop_count)
                        if issubclass(noun_type, bmp.obj.GroupNoun):
                            for group_prop_type, group_prop_count in self.current_level.group_references[noun_type].enabled_dict().items():
                                if issubclass(group_prop_type, bmp.obj.Noun):
                                    new_noun_list.extend([group_prop_type] * group_prop_count)
                        delete_noun_list.append(noun_type)
                    for delete_noun in delete_noun_list:
                        new_noun_list.remove(delete_noun)
                not_new_noun_list: list[type["bmp.obj.Noun"]] = []
                for noun_type, prop_count in old_obj.properties.disabled_dict().items():
                    if issubclass(noun_type, bmp.obj.Noun):
                        not_new_noun_list.extend([noun_type] * prop_count)
                while any(map(lambda p: issubclass(p, bmp.obj.RangedNoun), not_new_noun_list)):
                    delete_noun_list: list[type[bmp.obj.Noun]] = []
                    for noun_type in not_new_noun_list:
                        if not issubclass(noun_type, bmp.obj.RangedNoun):
                            continue
                        if issubclass(noun_type, bmp.obj.TextAll):
                            not_new_noun_list.extend([bmp.obj.get_noun_from_type(o) for o in self.current_level.all_list] * prop_count)
                        if issubclass(noun_type, bmp.obj.GroupNoun):
                            for group_prop_type, group_prop_count in self.current_level.group_references[noun_type].disabled_dict().items():
                                if issubclass(group_prop_type, bmp.obj.Noun):
                                    not_new_noun_list.extend([group_prop_type] * group_prop_count)
                        delete_noun_list.append(noun_type)
                    for delete_noun in delete_noun_list:
                        not_new_noun_list.remove(delete_noun)
                transform_success = False
                noun_is_noun = False
                noun_is_not_noun = False
                for new_noun in new_noun_list:
                    if issubclass(new_noun, bmp.obj.SupportsReferenceType):
                        if isinstance(old_obj, new_noun.ref_type):
                            noun_is_noun = True
                    elif issubclass(new_noun, bmp.obj.SupportsIsReferenceOf):
                        if new_noun.isreferenceof(old_obj):
                            noun_is_noun = True
                for not_new_noun in not_new_noun_list:
                    if issubclass(new_noun, bmp.obj.SupportsReferenceType):
                        if isinstance(old_obj, not_new_noun.ref_type):
                            noun_is_not_noun = True
                    elif issubclass(new_noun, bmp.obj.SupportsIsReferenceOf):
                        if new_noun.isreferenceof(old_obj):
                            noun_is_not_noun = True
                if noun_is_noun:
                    continue
                if noun_is_not_noun:
                    transform_success = True
                for new_text_type, new_text_count in old_obj.special_operator_properties[bmp.obj.TextWrite].enabled_dict().items():
                    for _ in range(new_text_count):
                        new_obj = new_text_type(old_obj.pos, old_obj.orient, space_id=old_obj.space_id, level_id=old_obj.level_id)
                        space.new_obj(new_obj)
                    transform_success = True
                for new_noun in new_noun_list:
                    if issubclass(new_noun, bmp.obj.FixedNoun):
                        if issubclass(new_noun, bmp.obj.TextEmpty):
                            transform_success = True
                        if issubclass(new_noun, bmp.obj.SpecificSpaceNoun):
                            if new_noun.isreferenceof(old_obj):
                                old_obj.space_id += new_noun.delta_infinite_tier
                        continue
                    new_type = new_noun.ref_type
                    if issubclass(new_type, bmp.obj.Game):
                        if isinstance(old_obj, (bmp.obj.LevelObject, bmp.obj.SpaceObject)):
                            space.new_obj(bmp.obj.Game(old_obj.pos, old_obj.orient, ref_type=bmp.obj.get_noun_from_type(old_type)))
                        else:
                            space.new_obj(bmp.obj.Game(old_obj.pos, old_obj.orient, ref_type=old_type))
                        transform_success = True
                    elif issubclass(new_type, bmp.obj.LevelObject):
                        if isinstance(old_obj, new_type):
                            pass
                        elif isinstance(old_obj, bmp.obj.LevelObject):
                            space.new_obj(new_type(old_obj.pos, old_obj.orient, level_id=old_obj.level_id, level_extra=old_obj.level_extra))
                            transform_success = True
                        elif isinstance(old_obj, bmp.obj.SpaceObject):
                            level_id: bmp.ref.LevelID = old_obj.space_id.to_level_id()
                            self.set_level(bmp.level.Level(
                                level_id, self.current_level.space_included, old_obj.space_id,
                                super_level_id = self.current_level.level_id,
                            ))
                            level_extra: bmp.obj.LevelObjectExtra = {
                                "icon": {
                                    "name": bmp.obj.get_noun_from_type(bmp.obj.default_space_object_type).sprite_name,
                                    "color": space.color if space.color is not None else bmp.obj.SpaceObject.get_color()
                                }
                            }
                            new_obj = new_type(old_obj.pos, old_obj.orient, level_id=level_id, level_extra=level_extra)
                            space.new_obj(new_obj)
                            transform_success = True
                        elif old_obj.level_id is not None:
                            level_extra: bmp.obj.LevelObjectExtra = {"icon": {"name": old_obj.sprite_name, "color": old_obj.get_color()}}
                            space.new_obj(new_type(old_obj.pos, old_obj.orient, level_id=old_obj.level_id, level_extra=level_extra))
                            transform_success = True
                        else:
                            level_extra: bmp.obj.LevelObjectExtra = {"icon": {"name": old_obj.sprite_name, "color": old_obj.get_color()}}
                            new_obj = new_type(old_obj.pos, old_obj.orient, level_id=self.current_level.level_id, level_extra=level_extra)
                            space.new_obj(new_obj)
                            transform_success = True
                    elif issubclass(new_type, bmp.obj.SpaceObject):
                        if isinstance(old_obj, new_type):
                            pass
                        elif isinstance(old_obj, bmp.obj.SpaceObject):
                            space.new_obj(new_type(old_obj.pos, old_obj.orient, space_id=old_obj.space_id, space_extra=old_obj.space_extra))
                            transform_success = True
                        elif isinstance(old_obj, bmp.obj.LevelObject):
                            new_level = self.get_level(old_obj.level_id)
                            if new_level is not None:
                                for temp_space in new_level.space_list:
                                    self.current_level.set_space(temp_space)
                                space.new_obj(new_type(old_obj.pos, old_obj.orient, space_id=new_level.current_space_id))
                            else:
                                space.new_obj(new_type(old_obj.pos, old_obj.orient, space_id=old_obj.level_id.to_space_id()))
                            transform_success = True
                        elif old_obj.space_id is not None:
                            space.new_obj(new_type(old_obj.pos, old_obj.orient, space_id=old_obj.space_id))
                            transform_success = True
                        else:
                            space.new_obj(new_type(old_obj.pos, old_obj.orient, space_id=space.space_id))
                            transform_success = True
                    elif issubclass(new_noun, bmp.obj.TextText):
                        if not isinstance(old_obj, bmp.obj.Text):
                            new_obj = bmp.obj.get_noun_from_type(old_type)(old_obj.pos, old_obj.orient, space_id=old_obj.space_id, level_id=old_obj.level_id)
                            transform_success = True
                            space.new_obj(new_obj)
                    else:
                        transform_success = True
                        new_obj = new_type(old_obj.pos, old_obj.orient, space_id=old_obj.space_id, level_id=old_obj.level_id)
                        space.new_obj(new_obj)
                if transform_success:
                    delete_object_list.append(old_obj)
            for delete_obj in delete_object_list:
                space.del_obj(delete_obj)
    def space_transform(self) -> None:
        old_obj_list: dict[type[bmp.obj.SpaceObject], list[tuple[bmp.ref.SpaceID, bmp.obj.SpaceObject]]]
        new_noun_list: dict[type[bmp.obj.SpaceObject], list[type[bmp.obj.Noun]]]
        for space_object_type in bmp.obj.space_object_types:
            for active_space in self.current_level.space_list:
                old_obj_list = {p: [] for p in bmp.obj.space_object_types}
                new_noun_list = {p: [] for p in bmp.obj.space_object_types}
                for other_space in self.current_level.space_list:
                    for old_obj in other_space.get_spaces():
                        if isinstance(old_obj, space_object_type) and active_space.space_id == old_obj.space_id:
                            old_obj_list[type(old_obj)].append((other_space.space_id, old_obj))
                for noun_type, prop_count in active_space.properties[space_object_type].enabled_dict().items():
                    if issubclass(noun_type, bmp.obj.Noun):
                        new_noun_list[space_object_type].extend([noun_type] * prop_count)
                while any(map(lambda p: issubclass(p, bmp.obj.RangedNoun), new_noun_list)):
                    delete_noun_list: list[type[bmp.obj.Noun]] = []
                    for noun_type in new_noun_list:
                        if not issubclass(noun_type, bmp.obj.RangedNoun):
                            continue
                        if issubclass(noun_type, bmp.obj.TextAll):
                            new_noun_list[space_object_type].extend([bmp.obj.get_noun_from_type(o) for o in self.current_level.all_list] * prop_count)
                        if issubclass(noun_type, bmp.obj.GroupNoun):
                            for group_prop_type, group_prop_count in self.current_level.group_references[noun_type].enabled_dict().items():
                                if issubclass(group_prop_type, bmp.obj.Noun):
                                    new_noun_list[space_object_type].extend([group_prop_type] * group_prop_count)
                        delete_noun_list.append(noun_type)
                    for delete_noun in delete_noun_list:
                        new_noun_list[space_object_type].remove(delete_noun)
                for new_text_type, new_text_count in active_space.special_operator_properties[space_object_type][bmp.obj.TextWrite].enabled_dict().items():
                    for _ in range(new_text_count):
                        new_obj = new_text_type(old_obj.pos, old_obj.orient, space_id=old_obj.space_id, level_id=old_obj.level_id)
                        active_space.new_obj(new_obj)
                for old_space_id, old_obj in old_obj_list[space_object_type]:
                    unchangeable = False
                    old_space = self.current_level.get_exact_space(old_space_id)
                    for new_noun in new_noun_list[space_object_type]:
                        if issubclass(new_noun, bmp.obj.FixedNoun):
                            if issubclass(new_noun, bmp.obj.TextEmpty):
                                continue
                            if issubclass(new_noun, bmp.obj.SpecificSpaceNoun):
                                if new_noun.isreferenceof(old_obj):
                                    old_obj.space_id += new_noun.delta_infinite_tier
                            continue
                        new_type = new_noun.ref_type
                        if issubclass(space_object_type, new_type):
                            unchangeable = True
                            break
                        elif issubclass(new_type, bmp.obj.SpaceObject):
                            new_obj = new_type(old_obj.pos, old_obj.orient, space_id=old_obj.space_id, space_extra=old_obj.space_extra)
                        elif issubclass(new_type, bmp.obj.LevelObject):
                            new_level_id: bmp.ref.LevelID = old_obj.space_id.to_level_id()
                            new_level_icon_color: Optional[bmp.color.ColorHex] = self.current_level.get_exact_space(old_obj.space_id).color
                            if new_level_icon_color is None:
                                new_level_icon_color = bmp.obj.default_space_object_type.get_color()
                            new_level_extra = bmp.obj.LevelObjectExtra(icon=bmp.obj.LevelObjectIcon(
                                name = bmp.obj.get_noun_from_type(space_object_type).sprite_name,
                                color = new_level_icon_color,
                            ))
                            self.set_level(bmp.level.Level(
                                new_level_id, self.current_level.space_included, old_obj.space_id,
                                super_level_id = self.current_level.level_id,
                            ))
                            new_obj = new_type(old_obj.pos, old_obj.orient, level_id=new_level_id, level_extra=new_level_extra)
                        elif issubclass(new_type, bmp.obj.Game):
                            new_obj = bmp.obj.Game(old_obj.pos, old_obj.orient, ref_type=bmp.obj.get_noun_from_type(space_object_type))
                        elif issubclass(new_noun, bmp.obj.TextText):
                            new_obj = bmp.obj.get_noun_from_type(space_object_type)(old_obj.pos, old_obj.orient, space_id=old_obj.space_id)
                        else:
                            new_obj = new_type(old_obj.pos, old_obj.orient, space_id=old_obj.space_id)
                        old_space.new_obj(new_obj)
                    if len(new_noun_list[space_object_type]) != 0 and not unchangeable:
                        old_space.del_obj(old_obj)
    def level_transform(self) -> bool:
        old_obj_list: dict[type[bmp.obj.LevelObject], list[tuple[bmp.ref.LevelID, bmp.ref.SpaceID, bmp.obj.LevelObject]]]
        new_noun_list: dict[type[bmp.obj.LevelObject], list[type[bmp.obj.Noun]]]
        new_noun_list = {p: [] for p in bmp.obj.level_object_types}
        transform_success = False
        for level_object_type in bmp.obj.level_object_types:
            old_obj_list = {p: [] for p in bmp.obj.level_object_types}
            for level in self.level_list:
                for other_space in level.space_list:
                    for old_obj in other_space.get_levels():
                        if isinstance(old_obj, level_object_type) and self.current_level.level_id == old_obj.level_id:
                            old_obj_list[type(old_obj)].append((level.level_id, other_space.space_id, old_obj))
            for noun_type, prop_count in self.current_level.properties[level_object_type].enabled_dict().items():
                if issubclass(noun_type, bmp.obj.Noun):
                    new_noun_list[level_object_type].extend([noun_type] * prop_count)
            while any(map(lambda p: issubclass(p, bmp.obj.RangedNoun), new_noun_list)):
                delete_noun_list: list[type[bmp.obj.Noun]] = []
                for noun_type in new_noun_list:
                    if not issubclass(noun_type, bmp.obj.RangedNoun):
                        continue
                    if issubclass(noun_type, bmp.obj.TextAll):
                        new_noun_list[level_object_type].extend([bmp.obj.get_noun_from_type(o) for o in self.current_level.all_list] * prop_count)
                    if issubclass(noun_type, bmp.obj.GroupNoun):
                        for group_prop_type, group_prop_count in self.current_level.group_references[noun_type].enabled_dict().items():
                            if issubclass(group_prop_type, bmp.obj.Noun):
                                new_noun_list[level_object_type].extend([group_prop_type] * group_prop_count)
                    delete_noun_list.append(noun_type)
                for delete_noun in delete_noun_list:
                    new_noun_list[level_object_type].remove(delete_noun)
            for new_text_type, new_text_count in self.current_level.special_operator_properties[level_object_type][bmp.obj.TextWrite].enabled_dict().items():
                for _ in range(new_text_count):
                    new_obj = new_text_type(old_obj.pos, old_obj.orient, space_id=old_obj.space_id, level_id=old_obj.level_id)
                    old_space.new_obj(new_obj)
                transform_success |= True
            for old_level_id, old_space_id, old_obj in old_obj_list[level_object_type]:
                old_level = self.get_exact_level(old_level_id)
                old_space = old_level.get_exact_space(old_space_id)
                unchangeable = False
                for new_noun in new_noun_list[level_object_type]:
                    if issubclass(new_noun, bmp.obj.FixedNoun):
                        if issubclass(new_noun, bmp.obj.TextEmpty):
                            continue
                        continue
                    new_type = new_noun.ref_type
                    if issubclass(level_object_type, new_type):
                        unchangeable = True
                        break
                    elif issubclass(new_type, bmp.obj.LevelObject):
                        new_obj = new_type(old_obj.pos, old_obj.orient, level_id=old_obj.level_id, level_extra=old_obj.level_extra)
                    elif issubclass(new_type, bmp.obj.SpaceObject):
                        for new_space in self.current_level.space_list:
                            if old_level.get_space(new_space.space_id) is None:
                                old_level.set_space(new_space)
                        new_obj = new_type(old_obj.pos, old_obj.orient, space_id=self.current_level.current_space_id)
                    elif issubclass(new_type, bmp.obj.Game):
                        new_obj = bmp.obj.Game(old_obj.pos, old_obj.orient, ref_type=bmp.obj.get_noun_from_type(level_object_type))
                    elif issubclass(new_noun, bmp.obj.TextText):
                        new_obj = bmp.obj.get_noun_from_type(level_object_type)(old_obj.pos, old_obj.orient, level_id=self.current_level.level_id)
                    else:
                        new_obj = new_type(old_obj.pos, old_obj.orient, level_id=self.current_level.level_id)
                    old_space.new_obj(new_obj)
                if len(new_noun_list[level_object_type]) != 0 and not unchangeable:
                    old_space.del_obj(old_obj)
                    transform_success |= True
        return transform_success
    def prepare(self) -> None:
        clear_counts: int = 0
        for sub_level in self.level_dict.values():
            for space in sub_level.space_list:
                for obj in space.object_list:
                    obj.old_state = bmp.obj.OldObjectState(
                        uid = obj.uid,
                        pos = obj.pos,
                        orient = obj.orient,
                        prop = obj.properties,
                        level = obj.level_id,
                        space = obj.space_id,
                    )
                    if isinstance(obj, bmp.obj.Path):
                        unlocked = True
                        for bonus_type, bonus_counts in obj.conditions.items():
                            if len({c for c in self.collectibles if isinstance(c.object_type, bonus_type)}) < bonus_counts:
                                unlocked = False
                        obj.unlocked = unlocked
            if sub_level.super_level_id == self.current_level.level_id and bmp.obj.Collectible(bmp.obj.Spore, sub_level.level_id) in self.collectibles:
                clear_counts += 1
                self.collectibles.add(bmp.obj.Collectible(bmp.obj.Spore, sub_level.level_id))
            if sub_level.map_info is not None:
                if clear_counts >= sub_level.map_info.get("spore_for_blossom", float("inf")):
                    self.collectibles.add(bmp.obj.Collectible(bmp.obj.Blossom, sub_level.level_id))
    def tick(self, op: Optional[bmp.loc.Orient]) -> ReturnInfo:
        self.prepare()
        self.current_level.sound_events = []
        self.current_level.created_levels = []
        self.update_rules()
        game_push = False
        game_push |= self.current_level.you(op)
        game_push |= self.current_level.move()
        # BIY had this parsing step
        # self.update_rules()
        game_push |= self.current_level.shift()
        self.update_rules()
        self.transform()
        self.space_transform()
        transform = self.level_transform()
        self.current_level.game()
        self.current_level.text_plus_and_text_minus()
        self.update_rules()
        self.current_level.tele()
        selected_level = self.current_level.select(op)
        self.update_rules()
        self.current_level.direction()
        self.current_level.flip()
        self.current_level.turn()
        self.update_rules()
        done = self.current_level.done()
        self.current_level.sink()
        self.current_level.hot_and_melt()
        self.current_level.defeat()
        self.current_level.open_and_shut()
        self.update_rules()
        self.current_level.make()
        self.update_rules()
        for new_level in self.current_level.created_levels:
            self.set_level(new_level)
        self.current_level.refresh_all_list()
        bonus = self.current_level.bonus()
        end = self.current_level.end()
        win = self.current_level.win()
        for object_type in [t for t, b in bonus.items() if b]:
            self.collectibles.add(bmp.obj.Collectible(object_type, self.current_level.level_id))
        for space in self.current_level.space_list:
            for path in space.get_objs_from_type(bmp.obj.Path):
                unlocked = True
                for bonus_type, bonus_counts in path.conditions.items():
                    if len({c for c in self.collectibles if isinstance(c, bonus_type)}) < bonus_counts:
                        unlocked = False
                path.unlocked = unlocked
        return {
            "win": win, "end": end, "done": done, "transform": transform,
            "game_push": game_push, "selected_level": selected_level
        }
    def to_json(self) -> LevelpackJson:
        json_object: LevelpackJson = {
            "ver": bmp.base.versions,
            "current_level": self.current_level_id.to_json(),
            "levels": [],
            "spaces": [],
            "level_init_states": [],
            "space_init_states": [],
            "collectibles": [],
            "rules": []
        }
        if self.name is not None: json_object["name"] = self.name
        if self.author is not None: json_object["author"] = self.author
        for level in tqdm(
            self.level_dict.values(),
            desc = bmp.lang.lang_format("saving.levelpack.level_list"),
            unit = bmp.lang.lang_format("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["levels"].append(level.to_json())
        for space in tqdm(
            self.space_dict.values(),
            desc = bmp.lang.lang_format("saving.level.space_list"),
            unit = bmp.lang.lang_format("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["spaces"].append(space.to_json())
        for level in tqdm(
            self.level_init_state_dict.values(),
            desc = bmp.lang.lang_format("saving.levelpack.level_list"),
            unit = bmp.lang.lang_format("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["level_init_states"].append(level.to_json())
        for space in tqdm(
            self.space_init_state_dict.values(),
            desc = bmp.lang.lang_format("saving.level.space_list"),
            unit = bmp.lang.lang_format("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["space_init_states"].append(space.to_json())
        for collectible in tqdm(
            self.collectibles,
            desc = bmp.lang.lang_format("saving.levelpack.collect_list"),
            unit = bmp.lang.lang_format("collectible.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["collectibles"].append(collectible.to_json())
        for rule in tqdm(
            self.rule_list,
            desc = bmp.lang.lang_format("saving.levelpack.rule_list"),
            unit = bmp.lang.lang_format("rule.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["rules"].append([])
            for obj in rule:
                json_object["rules"][-1].append(obj.json_name)
        return json_object

def update_json_format(json_object: LevelpackJson) -> LevelpackJson:
    return json_object # old levelpacks aren't able to update in 4.1

def json_to_levelpack(json_object: LevelpackJson) -> Levelpack:
    ver: str = json_object.get("ver", "0.0")
    collectibles: set[bmp.obj.Collectible] = set()
    space_dict: dict[bmp.ref.SpaceID, bmp.space.Space] = {}
    for space_json in tqdm(
        json_object["spaces"],
        desc = bmp.lang.lang_format("loading.level.space_list"),
        unit = bmp.lang.lang_format("space.name"),
        position = 0,
        **bmp.lang.default_tqdm_args,
    ):
        space = bmp.space.json_to_space(space_json, ver)
        space_dict[space.space_id] = space
    level_dict: dict[bmp.ref.LevelID, bmp.level.Level] = {}
    for level_json in tqdm(
        json_object["levels"],
        desc = bmp.lang.lang_format("loading.levelpack.level_list"),
        unit = bmp.lang.lang_format("level.name"),
        position = 0,
        **bmp.lang.default_tqdm_args,
    ):
        level = bmp.level.json_to_level(level_json, ver)
        level_dict[level.level_id] = level
    space_init_state_dict_json = json_object.get("space_init_states")
    space_init_state_dict: dict[bmp.ref.SpaceID, bmp.space.Space]
    if space_init_state_dict_json is not None:
        space_init_state_dict = {}
        for space_json in tqdm(
            space_init_state_dict_json,
            desc = bmp.lang.lang_format("loading.level.space_list"),
            unit = bmp.lang.lang_format("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            space = bmp.space.json_to_space(space_json, ver)
            space_init_state_dict[space.space_id] = space
    else:
        space_init_state_dict = copy.deepcopy(space_dict)
    level_init_state_dict_json = json_object.get("level_init_states")
    level_init_state_dict: dict[bmp.ref.LevelID, bmp.level.Level]
    if level_init_state_dict_json is not None:
        level_init_state_dict = {}
        for level_json in tqdm(
            level_init_state_dict_json,
            desc = bmp.lang.lang_format("loading.levelpack.level_list"),
            unit = bmp.lang.lang_format("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            level = bmp.level.json_to_level(level_json, ver)
            level_init_state_dict[level.level_id] = level
    else:
        level_init_state_dict = copy.deepcopy(level_dict)
    rule_list: list[bmp.rule.Rule] = []
    for rule in tqdm(
        json_object["rules"],
        desc = bmp.lang.lang_format("loading.levelpack.rule_list"),
        unit = bmp.lang.lang_format("rule.name"),
        position = 0,
        **bmp.lang.default_tqdm_args,
    ):
        rule_list.append([])
        for object_type in rule:
            rule_list[-1].append(bmp.obj.name_to_class[object_type]) # type: ignore
    current_level_id: bmp.ref.LevelID = bmp.ref.LevelID(**json_object["current_level"])
    for collectible in tqdm(
        json_object["collectibles"],
        desc = bmp.lang.lang_format("loading.levelpack.collect_list"),
        unit = bmp.lang.lang_format("collectible.name"),
        position = 0,
        **bmp.lang.default_tqdm_args,
    ):
        collectibles.add(bmp.obj.Collectible(
            bmp.obj.name_to_class[collectible["type"]],
            source=bmp.ref.LevelID(collectible["source"]["name"])
        ))
    return Levelpack(
        level_dict = level_dict,
        space_dict = space_dict,
        level_init_state_dict = level_init_state_dict,
        space_init_state_dict = space_init_state_dict,
        name = json_object.get("name"),
        author = json_object.get("author"),
        current_level_id = current_level_id,
        collectibles = collectibles,
        rule_list = rule_list,
    )