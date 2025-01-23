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
    level_list: list[bmp.level.LevelJson]
    level_init_state_list: list[bmp.level.LevelJson]
    rule_list: list[list[str]]

class Levelpack(object):
    def __init__(
        self,
        level_list: list[bmp.level.Level],
        level_init_state_list: Optional[list[bmp.level.Level]] = None,
        name: Optional[str] = None,
        author: Optional[str] = None,
        current_level_id: Optional[bmp.ref.LevelID] = None,
        collectibles: Optional[set[bmp.obj.Collectible]] = None,
        rule_list: Optional[list[bmp.rule.Rule]] = None,
    ) -> None:
        self.name: Optional[str] = name
        self.author: Optional[str] = author
        self.level_list: list[bmp.level.Level] = list(level_list)
        self.level_init_state_list: list[bmp.level.Level] = list(level_init_state_list) if level_init_state_list is not None else copy.deepcopy(list(level_list))
        self.current_level_id: bmp.ref.LevelID = current_level_id if current_level_id is not None else self.level_list[0].level_id
        self.collectibles: set[bmp.obj.Collectible] = collectibles if collectibles is not None else set()
        self.rule_list: list[bmp.rule.Rule] = rule_list if (rule_list is not None and len(rule_list) != 0) else bmp.rule.default_rule_list
    def get_exact_level(self, level_id: bmp.ref.LevelID) -> bmp.level.Level:
        return next(filter(lambda l: level_id == l.level_id, self.level_list))
    def get_level(self, level_id: bmp.ref.LevelID) -> Optional[bmp.level.Level]:
        try:
            return self.get_exact_level(level_id)
        except StopIteration:
            return None
    @property
    def current_level(self) -> bmp.level.Level:
        return self.get_exact_level(self.current_level_id)
    @current_level.setter
    def current_level(self, level: bmp.level.Level) -> None:
        self.current_level_id = level.level_id
    def set_level(self, level: bmp.level.Level) -> None:
        for index, old_level in enumerate(self.level_list):
            if old_level == level:
                self.level_list[index] = level
                return
        self.level_list.append(level)
    def reset_level(self, level_id: bmp.ref.LevelID) -> None:
        self.set_level(copy.deepcopy(next(filter(lambda l: level_id == l.level_id, self.level_init_state_list))))
    def set_level_init_state(self, level_id: bmp.ref.LevelID, level: bmp.level.Level) -> None:
        for index, old_level in enumerate(self.level_init_state_list):
            if old_level.level_id == level_id:
                self.level_init_state_list[index] = level
                return
        self.level_init_state_list.append(level)
    def update_rules(self, active_level: bmp.level.Level) -> None:
        active_level.game_properties = bmp.obj.Properties()
        active_level_objs: list[bmp.obj.LevelObject] = []
        for level in self.level_list:
            for space in level.space_list:
                active_level_objs.extend([o for o in space.get_levels() if o.level_id == active_level.level_id])
        active_space_objs: list[bmp.obj.SpaceObject] = []
        for space in active_level.space_list:
            active_space_objs.extend(space.get_spaces())
        for level_object_type in bmp.obj.level_object_types:
            active_level.properties[level_object_type] = bmp.obj.Properties()
            active_level.special_operator_properties[level_object_type] = {o: bmp.obj.Properties() for o in bmp.obj.special_operators}
        for space in active_level.space_list:
            for object_type in bmp.obj.space_object_types:
                space.properties[object_type] = bmp.obj.Properties()
                space.special_operator_properties[object_type] = {o: bmp.obj.Properties() for o in bmp.obj.special_operators}
            for obj in space.object_list:
                obj.properties = bmp.obj.Properties()
                obj.special_operator_properties = {o: bmp.obj.Properties() for o in bmp.obj.special_operators}
        for space in active_level.space_list:
            space.set_rule()
        new_prop_list: list[tuple[bmp.obj.Object, tuple[type[bmp.obj.Text], int]]] = []
        global_rule_info_list = [bmp.rule.get_info_from_rule(r) for r in self.rule_list]
        global_rule_info_list = [r for r in global_rule_info_list if r is not None]
        for space in active_level.space_list:
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
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = active_level.all_list) and not isinstance(o, object_type)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_type(object_type)]
                elif noun_type is bmp.obj.TextAll:
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if isinstance(o, bmp.obj.types_in_not_all)]
                    else:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = active_level.all_list)]
                elif issubclass(noun_type, bmp.obj.SupportsIsReferenceOf):
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = active_level.all_list) and not noun_type.isreferenceof(o)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_special_noun(noun_type)]
                for oper_info in rule_info.oper_list:
                    oper_type = oper_info.oper_type
                    for prop_info in oper_info.prop_list:
                        prop_type = prop_info.prop_type
                        prop_negated_tier = prop_info.prop_negated_tier
                        if issubclass(object_type, bmp.obj.Game) and issubclass(oper_type, bmp.obj.TextIs):
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and len(prefix_info_list) == 0:
                                active_level.game_properties.update(prop_type, prop_negated_tier)
                        elif issubclass(object_type, bmp.obj.LevelObject) and noun_negated_tier % 2 == 0:
                            meet_prefix_conditions = any(active_level.meet_prefix_conditions(space, o, prefix_info_list, True) for o in active_level_objs)
                            meet_infix_conditions = any(active_level.meet_infix_conditions(space, o, infix_info_list) for o in active_level_objs)
                            if (meet_prefix_conditions and meet_infix_conditions) or (len(prefix_info_list) == 0 and len(infix_info_list) == 0 and len(active_level_objs) == 0):
                                if oper_type == bmp.obj.TextIs:
                                    active_level.properties[object_type].update(prop_type, prop_negated_tier)
                                else:
                                    active_level.special_operator_properties[object_type][oper_type].update(prop_type, prop_negated_tier)
                        elif issubclass(object_type, bmp.obj.SpaceObject) and noun_negated_tier % 2 == 0:
                            meet_prefix_conditions = any(active_level.meet_prefix_conditions(space, o, prefix_info_list, True) for o in active_space_objs)
                            meet_infix_conditions = any(active_level.meet_infix_conditions(space, o, infix_info_list) for o in active_space_objs)
                            if (meet_prefix_conditions and meet_infix_conditions) or (len(prefix_info_list) == 0 and len(infix_info_list) == 0 and len(active_space_objs) == 0):
                                if oper_type == bmp.obj.TextIs:
                                    space.properties[object_type].update(prop_type, prop_negated_tier)
                                else:
                                    space.special_operator_properties[object_type][oper_type].update(prop_type, prop_negated_tier)
                        for obj in new_match_obj_list:
                            if active_level.meet_infix_conditions(space, obj, infix_info_list) and active_level.meet_prefix_conditions(space, obj, prefix_info_list):
                                if oper_type == bmp.obj.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                else:
                                    obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
            # outer space
            outer_space_rule_info = active_level.recursion_rules(space)[1]
            for rule_info in outer_space_rule_info:
                prefix_info_list = rule_info.prefix_info_list
                noun_negated_tier = rule_info.noun_negated_tier
                noun_type = rule_info.noun_type
                infix_info_list = rule_info.infix_info_list
                new_match_obj_list: list[bmp.obj.Object] = []
                if issubclass(noun_type, bmp.obj.GeneralNoun):
                    object_type = noun_type.ref_type
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = active_level.all_list) and not isinstance(o, object_type)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_type(object_type)]
                elif noun_type is bmp.obj.TextAll:
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if isinstance(o, bmp.obj.types_in_not_all)]
                    else:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = active_level.all_list)]
                elif issubclass(noun_type, bmp.obj.SupportsIsReferenceOf):
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll.isreferenceof(o, all_list = active_level.all_list) and not noun_type.isreferenceof(o)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_special_noun(noun_type)]
                for oper_info in rule_info.oper_list:
                    oper_type = oper_info.oper_type
                    for prop_info in oper_info.prop_list:
                        prop_type = prop_info.prop_type
                        prop_negated_tier = prop_info.prop_negated_tier
                        if issubclass(object_type, bmp.obj.Game) and issubclass(oper_type, bmp.obj.TextIs):
                            if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and active_level.meet_prefix_conditions(space, bmp.obj.Object((0, 0)), prefix_info_list, True):
                                active_level.game_properties.update(prop_type, prop_negated_tier)
                        for obj in new_match_obj_list:
                            if active_level.meet_infix_conditions(space, obj, infix_info_list) and active_level.meet_prefix_conditions(space, obj, prefix_info_list):
                                if oper_type == bmp.obj.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                else:
                                    obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.properties.update(prop_type, prop_negated_count)
    def transform(self, active_level: bmp.level.Level) -> None:
        for space in active_level.space_list:
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
                            new_noun_list.extend([bmp.obj.get_noun_from_type(o) for o in active_level.all_list] * prop_count)
                        if issubclass(noun_type, bmp.obj.GroupNoun):
                            for group_prop_type, group_prop_count in active_level.group_references[noun_type].enabled_dict().items():
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
                            not_new_noun_list.extend([bmp.obj.get_noun_from_type(o) for o in active_level.all_list] * prop_count)
                        if issubclass(noun_type, bmp.obj.GroupNoun):
                            for group_prop_type, group_prop_count in active_level.group_references[noun_type].disabled_dict().items():
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
                                level_id, active_level.space_list,
                                super_level_id=active_level.level_id,
                                current_space_id=old_obj.space_id
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
                            new_obj = new_type(old_obj.pos, old_obj.orient, level_id=active_level.level_id, level_extra=level_extra)
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
                                    active_level.set_space(temp_space)
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
    def space_transform(self, active_level: bmp.level.Level) -> None:
        old_obj_list: dict[type[bmp.obj.SpaceObject], list[tuple[bmp.ref.SpaceID, bmp.obj.SpaceObject]]]
        new_noun_list: dict[type[bmp.obj.SpaceObject], list[type[bmp.obj.Noun]]]
        for space_object_type in bmp.obj.space_object_types:
            for active_space in active_level.space_list:
                old_obj_list = {p: [] for p in bmp.obj.space_object_types}
                new_noun_list = {p: [] for p in bmp.obj.space_object_types}
                for other_space in active_level.space_list:
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
                            new_noun_list[space_object_type].extend([bmp.obj.get_noun_from_type(o) for o in active_level.all_list] * prop_count)
                        if issubclass(noun_type, bmp.obj.GroupNoun):
                            for group_prop_type, group_prop_count in active_level.group_references[noun_type].enabled_dict().items():
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
                    old_space = active_level.get_exact_space(old_space_id)
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
                            new_level_icon_color: Optional[bmp.color.ColorHex] = active_level.get_exact_space(old_obj.space_id).color
                            if new_level_icon_color is None:
                                new_level_icon_color = bmp.obj.default_space_object_type.get_color()
                            new_level_extra = bmp.obj.LevelObjectExtra(icon=bmp.obj.LevelObjectIcon(
                                name=bmp.obj.get_noun_from_type(space_object_type).sprite_name,
                                color=new_level_icon_color
                            ))
                            self.set_level(bmp.level.Level(
                                new_level_id, active_level.space_list,
                                super_level_id=active_level.level_id,
                                current_space_id=old_obj.space_id
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
    def level_transform(self, active_level: bmp.level.Level) -> bool:
        old_obj_list: dict[type[bmp.obj.LevelObject], list[tuple[bmp.ref.LevelID, bmp.ref.SpaceID, bmp.obj.LevelObject]]]
        new_noun_list: dict[type[bmp.obj.LevelObject], list[type[bmp.obj.Noun]]]
        new_noun_list = {p: [] for p in bmp.obj.level_object_types}
        transform_success = False
        for level_object_type in bmp.obj.level_object_types:
            old_obj_list = {p: [] for p in bmp.obj.level_object_types}
            for level in self.level_list:
                for other_space in level.space_list:
                    for old_obj in other_space.get_levels():
                        if isinstance(old_obj, level_object_type) and active_level.level_id == old_obj.level_id:
                            old_obj_list[type(old_obj)].append((level.level_id, other_space.space_id, old_obj))
            for noun_type, prop_count in active_level.properties[level_object_type].enabled_dict().items():
                if issubclass(noun_type, bmp.obj.Noun):
                    new_noun_list[level_object_type].extend([noun_type] * prop_count)
            while any(map(lambda p: issubclass(p, bmp.obj.RangedNoun), new_noun_list)):
                delete_noun_list: list[type[bmp.obj.Noun]] = []
                for noun_type in new_noun_list:
                    if not issubclass(noun_type, bmp.obj.RangedNoun):
                        continue
                    if issubclass(noun_type, bmp.obj.TextAll):
                        new_noun_list[level_object_type].extend([bmp.obj.get_noun_from_type(o) for o in active_level.all_list] * prop_count)
                    if issubclass(noun_type, bmp.obj.GroupNoun):
                        for group_prop_type, group_prop_count in active_level.group_references[noun_type].enabled_dict().items():
                            if issubclass(group_prop_type, bmp.obj.Noun):
                                new_noun_list[level_object_type].extend([group_prop_type] * group_prop_count)
                    delete_noun_list.append(noun_type)
                for delete_noun in delete_noun_list:
                    new_noun_list[level_object_type].remove(delete_noun)
            for new_text_type, new_text_count in active_level.special_operator_properties[level_object_type][bmp.obj.TextWrite].enabled_dict().items():
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
                        for new_space in active_level.space_list:
                            if old_level.get_space(new_space.space_id) is None:
                                old_level.set_space(new_space)
                        new_obj = new_type(old_obj.pos, old_obj.orient, space_id=active_level.current_space_id)
                    elif issubclass(new_type, bmp.obj.Game):
                        new_obj = bmp.obj.Game(old_obj.pos, old_obj.orient, ref_type=bmp.obj.get_noun_from_type(level_object_type))
                    elif issubclass(new_noun, bmp.obj.TextText):
                        new_obj = bmp.obj.get_noun_from_type(level_object_type)(old_obj.pos, old_obj.orient, level_id=active_level.level_id)
                    else:
                        new_obj = new_type(old_obj.pos, old_obj.orient, level_id=active_level.level_id)
                    old_space.new_obj(new_obj)
                if len(new_noun_list[level_object_type]) != 0 and not unchangeable:
                    old_space.del_obj(old_obj)
                    transform_success |= True
        return transform_success
    def prepare(self, active_level: bmp.level.Level) -> None:
        clear_counts: int = 0
        for sub_level in self.level_list:
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
            if sub_level.super_level_id == active_level.level_id and sub_level.collected.get(bmp.obj.Spore):
                clear_counts += 1
                self.collectibles.add(bmp.obj.Collectible(bmp.obj.Spore, sub_level.level_id))
            if sub_level.map_info is not None and clear_counts >= sub_level.map_info["minimum_clear_for_blossom"]:
                sub_level.collected[bmp.obj.Blossom] = True
    def tick(self, active_level: bmp.level.Level, op: Optional[bmp.loc.Orient]) -> ReturnInfo:
        self.prepare(active_level)
        active_level.sound_events = []
        active_level.created_levels = []
        self.update_rules(active_level)
        game_push = False
        game_push |= active_level.you(op)
        game_push |= active_level.move()
        # BIY had this parsing step
        # self.update_rules(active_level)
        game_push |= active_level.shift()
        self.update_rules(active_level)
        self.transform(active_level)
        self.space_transform(active_level)
        transform = self.level_transform(active_level)
        active_level.game()
        active_level.text_plus_and_text_minus()
        self.update_rules(active_level)
        active_level.tele()
        selected_level = active_level.select(op)
        self.update_rules(active_level)
        active_level.direction()
        active_level.flip()
        active_level.turn()
        self.update_rules(active_level)
        done = active_level.done()
        active_level.sink()
        active_level.hot_and_melt()
        active_level.defeat()
        active_level.open_and_shut()
        self.update_rules(active_level)
        active_level.make()
        self.update_rules(active_level)
        for new_level in active_level.created_levels:
            self.set_level(new_level)
        active_level.refresh_all_list()
        active_level.bonus()
        end = active_level.end()
        win = active_level.win()
        if win:
            for object_type in [t for t, b in active_level.collected.items() if b]:
                self.collectibles.add(bmp.obj.Collectible(object_type, active_level.level_id))
        for space in active_level.space_list:
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
            "level_list": [],
            "level_init_state_list": [],
            "collectibles": [],
            "rule_list": []
        }
        if self.name is not None: json_object["name"] = self.name
        if self.author is not None: json_object["author"] = self.author
        for level in tqdm(
            self.level_list,
            desc=bmp.lang.lang_format("saving.levelpack.level_list"),
            unit=bmp.lang.lang_format("level.name"),
            position=0,
            **bmp.lang.default_tqdm_args
        ):
            json_object["level_list"].append(level.to_json())
        for level in tqdm(
            self.level_init_state_list,
            desc=bmp.lang.lang_format("saving.levelpack.level_list"),
            unit=bmp.lang.lang_format("level.name"),
            position=0,
            **bmp.lang.default_tqdm_args
        ):
            json_object["level_init_state_list"].append(level.to_json())
        for collectible in tqdm(
            self.collectibles,
            desc=bmp.lang.lang_format("saving.levelpack.collect_list"),
            unit=bmp.lang.lang_format("collectible.name"),
            position=0,
            **bmp.lang.default_tqdm_args
        ):
            json_object["collectibles"].append(collectible.to_json())
        for rule in tqdm(
            self.rule_list,
            desc=bmp.lang.lang_format("saving.levelpack.rule_list"),
            unit=bmp.lang.lang_format("rule.name"),
            position=0,
            **bmp.lang.default_tqdm_args
        ):
            json_object["rule_list"].append([])
            for obj in rule:
                json_object["rule_list"][-1].append(obj.json_name)
        return json_object

def json_to_levelpack(json_object: LevelpackJson) -> Levelpack:
    ver = json_object.get("ver")
    collectibles: set[bmp.obj.Collectible] = set()
    level_list = []
    for level in tqdm(
        json_object["level_list"],
        desc=bmp.lang.lang_format("loading.levelpack.level_list"),
        unit=bmp.lang.lang_format("level.name"),
        position=0,
        **bmp.lang.default_tqdm_args
    ):
        level_list.append(bmp.level.json_to_level(level, ver))
    if "level_init_state_list" in json_object.keys():
        level_init_state_list = []
        for level in tqdm(
            json_object["level_init_state_list"],
            desc=bmp.lang.lang_format("loading.levelpack.level_init_state_list"),
            unit=bmp.lang.lang_format("level.name"),
            position=0,
            **bmp.lang.default_tqdm_args
        ):
            level_init_state_list.append(bmp.level.json_to_level(level, ver))
    else:
        level_init_state_list = copy.deepcopy(level_list)
    rule_list: list[bmp.rule.Rule] = []
    for rule in tqdm(
        json_object["rule_list"],
        desc=bmp.lang.lang_format("loading.levelpack.rule_list"),
        unit=bmp.lang.lang_format("rule.name"),
        position=0,
        **bmp.lang.default_tqdm_args
    ):
        rule_list.append([])
        for object_type in rule:
            rule_list[-1].append(bmp.obj.name_to_class[object_type]) # type: ignore
    if bmp.base.compare_versions(ver if ver is not None else "0.0", "3.8") == -1:
        current_level_id: bmp.ref.LevelID = bmp.ref.LevelID(json_object["main_level"]) # type: ignore
    elif bmp.base.compare_versions(ver if ver is not None else "0.0", "4.03") == -1:
        current_level_id: bmp.ref.LevelID = bmp.ref.LevelID(**json_object["main_level"]) # type: ignore
    else:
        current_level_id: bmp.ref.LevelID = bmp.ref.LevelID(**json_object["current_level"])
        for collectible in tqdm(
            json_object["collectibles"],
            desc=bmp.lang.lang_format("loading.levelpack.collect_list"),
            unit=bmp.lang.lang_format("collectible.name"),
            position=0,
            **bmp.lang.default_tqdm_args
        ):
            collectibles.add(bmp.obj.Collectible(
                bmp.obj.name_to_class[collectible["type"]],
                source=bmp.ref.LevelID(collectible["source"]["name"])
            ))
    return Levelpack(
        level_list=level_list,
        level_init_state_list=level_init_state_list,
        name=json_object.get("name"),
        author=json_object.get("author"),
        current_level_id=current_level_id,
        collectibles=collectibles,
        rule_list=rule_list
    )