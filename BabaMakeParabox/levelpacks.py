from typing import Any, Optional, TypedDict, NotRequired
import uuid

from BabaMakeParabox import basics, colors, displays, objects, collects, positions, refs, rules, levels, spaces

class ReturnInfo(TypedDict):
    win: bool
    end: bool
    done: bool
    transform: bool
    game_push: bool
    selected_level: Optional[refs.LevelID]
default_levelpack_info: ReturnInfo = {"win": False, "end": False, "done": False, "transform": False, "game_push": False, "selected_level": None}

class LevelpackJson(TypedDict):
    ver: str
    name: NotRequired[str]
    author: NotRequired[str]
    main_level: refs.LevelIDJson
    collectibles: list[collects.CollectibleJson]
    level_list: list[levels.LevelJson]
    rule_list: list[list[str]]

class Levelpack(object):
    def __init__(self, level_list: list[levels.Level], name: Optional[str] = None, author: Optional[str] = None, main_level_id: Optional[refs.LevelID] = None, collectibles: Optional[set[collects.Collectible]] = None, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name if name is not None else "Unnamed"
        self.author: str = author if author is not None else "Unknown"
        self.level_list: list[levels.Level] = list(level_list)
        self.main_level_id: refs.LevelID = main_level_id if main_level_id is not None else self.level_list[0].level_id
        self.collectibles: set[collects.Collectible] = collectibles if collectibles is not None else set()
        self.rule_list: list[rules.Rule] = rule_list if (rule_list is not None and len(rule_list) != 0) else rules.default_rule_list
    def get_level(self, level_id: refs.LevelID) -> Optional[levels.Level]:
        level = list(filter(lambda l: level_id == l.level_id, self.level_list))
        return level[0] if len(level) != 0 else None
    def get_exact_level(self, level_id: refs.LevelID) -> levels.Level:
        level = list(filter(lambda l: level_id == l.level_id, self.level_list))
        return level[0]
    def set_level(self, level: levels.Level) -> None:
        for i in range(len(self.level_list)):
            if level == self.level_list[i]:
                self.level_list[i] = level
                return
        self.level_list.append(level)
    def update_rules(self, active_level: levels.Level, old_prop_dict: dict[uuid.UUID, objects.Properties]) -> None:
        active_level.game_properties = objects.Properties()
        active_level_objs: list[objects.LevelObject] = []
        for level in self.level_list:
            for space in level.space_list:
                active_level_objs.extend([o for o in space.get_levels() if o.level_id == active_level.level_id])
        active_space_objs: list[objects.SpaceObject] = []
        for space in active_level.space_list:
            active_space_objs.extend(space.get_spaces())
        for level_object_type in objects.level_object_types:
            active_level.properties[level_object_type] = objects.Properties()
            active_level.special_operator_properties[level_object_type] = {o: objects.Properties() for o in objects.special_operators}
        for space in active_level.space_list:
            for object_type in objects.space_object_types:
                space.properties[object_type] = objects.Properties()
                space.special_operator_properties[object_type] = {o: objects.Properties() for o in objects.special_operators}
            for obj in space.object_list:
                obj.properties = objects.Properties()
                obj.special_operator_properties = {o: objects.Properties() for o in objects.special_operators}
        for space in active_level.space_list:
            space.set_rule()
        new_prop_list: list[tuple[objects.Object, tuple[type[objects.Text], int]]] = []
        global_rule_info_list = [rules.get_info_from_rule(r) for r in self.rule_list]
        global_rule_info_list = [r for r in global_rule_info_list if r is not None]
        for space in active_level.space_list:
            outer_space_rule_list, outer_space_rule_info = active_level.recursion_rules(space)
            for rule_info in space.rule_info + global_rule_info_list + outer_space_rule_info:
                prefix_info_list = rule_info.prefix_info_list
                noun_negated_tier = rule_info.noun_negated_tier
                noun_type = rule_info.noun_type
                infix_info_list = rule_info.infix_info_list
                new_match_obj_list: list[objects.Object] = []
                if issubclass(noun_type, objects.GeneralNoun):
                    object_type = noun_type.ref_type
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if objects.TextAll.isreferenceof(o, all_list = active_level.all_list) and not isinstance(o, object_type)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_type(object_type)]
                elif issubclass(noun_type, objects.SupportsIsReferenceOf):
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if objects.TextAll.isreferenceof(o, all_list = active_level.all_list) and not noun_type.isreferenceof(o, all_list = active_level.all_list)]
                    else:
                        new_match_obj_list = [o for o in space.object_list if noun_type.isreferenceof(o, all_list = active_level.all_list)]
                for oper_info in rule_info.oper_list:
                    oper_type = oper_info.oper_type
                    if oper_type != objects.TextIs:
                        continue
                    for prop_info in oper_info.prop_list:
                        prop_type = prop_info.prop_type
                        prop_negated_tier = prop_info.prop_negated_tier
                        if prop_type != (objects.TextWord):
                            continue
                        for obj in new_match_obj_list:
                            if active_level.meet_infix_conditions(space, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and active_level.meet_prefix_conditions(space, obj, prefix_info_list):
                                new_prop_list.append((obj, (prop_type, prop_negated_tier)))
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.properties.update(prop_type, prop_negated_count)
        for space in active_level.space_list:
            for object_type in objects.space_object_types:
                space.properties[object_type] = objects.Properties()
                space.special_operator_properties[object_type] = {o: objects.Properties() for o in objects.special_operators}
            for obj in space.object_list:
                obj.properties = objects.Properties()
                obj.special_operator_properties = {o: objects.Properties() for o in objects.special_operators}
        for space in active_level.space_list:
            space.set_rule()
        new_prop_list = []
        for space in active_level.space_list:
            for rule_info in space.rule_info + global_rule_info_list:
                prefix_info_list = rule_info.prefix_info_list
                noun_negated_tier = rule_info.noun_negated_tier
                noun_type = rule_info.noun_type
                infix_info_list = rule_info.infix_info_list
                new_match_obj_list: list[objects.Object] = []
                if issubclass(noun_type, objects.GeneralNoun):
                    object_type = noun_type.ref_type
                    if issubclass(object_type, objects.Game) and issubclass(oper_type, objects.TextIs):
                        if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and len(prefix_info_list) == 0:
                            active_level.game_properties.update(prop_type, prop_negated_tier)
                    elif noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if objects.TextAll.isreferenceof(o, all_list = active_level.all_list) and not isinstance(o, object_type)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_type(object_type)]
                elif issubclass(noun_type, objects.SupportsIsReferenceOf):
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if objects.TextAll.isreferenceof(o, all_list = active_level.all_list) and not noun_type.isreferenceof(o, all_list = active_level.all_list)]
                    else:
                        new_match_obj_list = [o for o in space.object_list if noun_type.isreferenceof(o, all_list = active_level.all_list)]
                for oper_info in rule_info.oper_list:
                    oper_type = oper_info.oper_type
                    for prop_info in oper_info.prop_list:
                        prop_type = prop_info.prop_type
                        prop_negated_tier = prop_info.prop_negated_tier
                        if issubclass(object_type, objects.LevelObject) and noun_negated_tier % 2 == 0:
                            meet_prefix_conditions = any(active_level.meet_prefix_conditions(space, o, prefix_info_list, True) for o in active_level_objs)
                            meet_infix_conditions = any(active_level.meet_infix_conditions(space, o, infix_info_list, old_prop_dict.get(o.uuid)) for o in active_level_objs)
                            if (meet_prefix_conditions and meet_infix_conditions) or (len(prefix_info_list) == 0 and len(infix_info_list) == 0 and len(active_level_objs) == 0):
                                if oper_type == objects.TextIs:
                                    active_level.properties[object_type].update(prop_type, prop_negated_tier)
                                else:
                                    active_level.special_operator_properties[object_type][oper_type].update(prop_type, prop_negated_tier)
                        elif issubclass(object_type, objects.SpaceObject) and noun_negated_tier % 2 == 0:
                            meet_prefix_conditions = any(active_level.meet_prefix_conditions(space, o, prefix_info_list, True) for o in active_space_objs)
                            meet_infix_conditions = any(active_level.meet_infix_conditions(space, o, infix_info_list, old_prop_dict.get(o.uuid)) for o in active_space_objs)
                            if (meet_prefix_conditions and meet_infix_conditions) or (len(prefix_info_list) == 0 and len(infix_info_list) == 0 and len(active_space_objs) == 0):
                                if oper_type == objects.TextIs:
                                    space.properties[object_type].update(prop_type, prop_negated_tier)
                                else:
                                    space.special_operator_properties[object_type][oper_type].update(prop_type, prop_negated_tier)
                        for obj in new_match_obj_list:
                            if active_level.meet_infix_conditions(space, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and active_level.meet_prefix_conditions(space, obj, prefix_info_list):
                                if oper_type == objects.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                else:
                                    obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
            outer_space_rule_list, outer_space_rule_info = active_level.recursion_rules(space)
            for rule_info in outer_space_rule_info:
                prefix_info_list = rule_info.prefix_info_list
                noun_negated_tier = rule_info.noun_negated_tier
                noun_type = rule_info.noun_type
                infix_info_list = rule_info.infix_info_list
                new_match_obj_list: list[objects.Object] = []
                if issubclass(noun_type, objects.GeneralNoun):
                    object_type = noun_type.ref_type
                    if issubclass(object_type, objects.Game) and issubclass(oper_type, objects.TextIs):
                        if noun_negated_tier % 2 == 0 and len(infix_info_list) == 0 and active_level.meet_prefix_conditions(space, objects.Object(positions.Coordinate(0, 0)), prefix_info_list, True):
                            active_level.game_properties.update(prop_type, prop_negated_tier)
                    elif noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if objects.TextAll.isreferenceof(o, all_list = active_level.all_list) and not isinstance(o, object_type)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_type(object_type)]
                elif issubclass(noun_type, objects.SupportsIsReferenceOf):
                    if noun_negated_tier % 2 == 1:
                        new_match_obj_list = [o for o in space.object_list if objects.TextAll.isreferenceof(o, all_list = active_level.all_list) and not noun_type.isreferenceof(o, all_list = active_level.all_list)]
                    else:
                        new_match_obj_list = [o for o in space.object_list if noun_type.isreferenceof(o, all_list = active_level.all_list)]
                for oper_info in rule_info.oper_list:
                    oper_type = oper_info.oper_type
                    for prop_info in oper_info.prop_list:
                        prop_type = prop_info.prop_type
                        prop_negated_tier = prop_info.prop_negated_tier
                        for obj in new_match_obj_list:
                            if active_level.meet_infix_conditions(space, obj, infix_info_list, old_prop_dict.get(obj.uuid)) and active_level.meet_prefix_conditions(space, obj, prefix_info_list):
                                if oper_type == objects.TextIs:
                                    new_prop_list.append((obj, (prop_type, prop_negated_tier)))
                                else:
                                    obj.special_operator_properties[oper_type].update(prop_type, prop_negated_tier)
        for obj, prop in new_prop_list:
            prop_type, prop_negated_count = prop
            obj.properties.update(prop_type, prop_negated_count)
    def transform(self, active_level: levels.Level) -> None:
        for space in active_level.space_list:
            delete_object_list = []
            for old_obj in space.object_list:
                old_type = type(old_obj)
                new_noun_list: list[type["objects.Noun"]] = []
                for noun_type, prop_count in old_obj.properties.enabled_dict().items():
                    if issubclass(noun_type, objects.Noun):
                        new_noun_list.extend([noun_type] * prop_count)
                while any(map(lambda p: issubclass(p, objects.RangedNoun), new_noun_list)):
                    delete_noun_list: list[type[objects.Noun]] = []
                    for noun_type in new_noun_list:
                        if not issubclass(noun_type, objects.RangedNoun):
                            continue
                        if issubclass(noun_type, objects.TextAll):
                            new_noun_list.extend(active_level.all_list * prop_count)
                        if issubclass(noun_type, objects.GroupNoun):
                            for group_prop_type, group_prop_count in active_level.group_references[noun_type].enabled_dict().items():
                                if issubclass(group_prop_type, objects.Noun):
                                    new_noun_list.extend([group_prop_type] * group_prop_count)
                        delete_noun_list.append(noun_type)
                    for delete_noun in delete_noun_list:
                        new_noun_list.remove(delete_noun)
                not_new_noun_list: list[type["objects.Noun"]] = []
                for noun_type, prop_count in old_obj.properties.disabled_dict().items():
                    if issubclass(noun_type, objects.Noun):
                        not_new_noun_list.extend([noun_type] * prop_count)
                while any(map(lambda p: issubclass(p, objects.RangedNoun), not_new_noun_list)):
                    delete_noun_list: list[type[objects.Noun]] = []
                    for noun_type in not_new_noun_list:
                        if not issubclass(noun_type, objects.RangedNoun):
                            continue
                        if issubclass(noun_type, objects.TextAll):
                            not_new_noun_list.extend(active_level.all_list * prop_count)
                        if issubclass(noun_type, objects.GroupNoun):
                            for group_prop_type, group_prop_count in active_level.group_references[noun_type].disabled_dict().items():
                                if issubclass(group_prop_type, objects.Noun):
                                    not_new_noun_list.extend([group_prop_type] * group_prop_count)
                        delete_noun_list.append(noun_type)
                    for delete_noun in delete_noun_list:
                        not_new_noun_list.remove(delete_noun)
                transform_success = False
                noun_is_noun = False
                noun_is_not_noun = False
                for new_noun in new_noun_list:
                    if issubclass(new_noun, objects.SupportsReferenceType):
                        if isinstance(old_obj, new_noun.ref_type):
                            noun_is_noun = True
                    elif issubclass(new_noun, objects.SupportsIsReferenceOf):
                        if new_noun.isreferenceof(old_obj):
                            noun_is_noun = True
                for not_new_noun in not_new_noun_list:
                    if issubclass(new_noun, objects.SupportsReferenceType):
                        if isinstance(old_obj, not_new_noun.ref_type):
                            noun_is_not_noun = True
                    elif issubclass(new_noun, objects.SupportsIsReferenceOf):
                        if new_noun.isreferenceof(old_obj):
                            noun_is_not_noun = True
                if noun_is_noun:
                    continue
                if noun_is_not_noun:
                    transform_success = True
                for new_text_type, new_text_count in old_obj.special_operator_properties[objects.TextWrite].enabled_dict().items():
                    for _ in range(new_text_count):
                        new_obj = new_text_type(old_obj.pos, old_obj.direct, space_id=old_obj.space_id, level_id=old_obj.level_id)
                        space.new_obj(new_obj)
                    transform_success = True
                for new_noun in new_noun_list:
                    if issubclass(new_noun, objects.FixedNoun):
                        if issubclass(new_noun, objects.TextEmpty):
                            transform_success = True
                        if issubclass(new_noun, objects.SpecificSpaceNoun):
                            if new_noun.isreferenceof(old_obj):
                                old_obj.space_id += new_noun.delta_infinite_tier
                        continue
                    new_type = new_noun.ref_type
                    if issubclass(new_type, objects.Game):
                        if isinstance(old_obj, (objects.LevelObject, objects.SpaceObject)):
                            space.new_obj(objects.Game(old_obj.pos, old_obj.direct, ref_type=objects.get_noun_from_type(old_type)))
                        else:
                            space.new_obj(objects.Game(old_obj.pos, old_obj.direct, ref_type=old_type))
                        transform_success = True
                    elif issubclass(new_type, objects.LevelObject):
                        if isinstance(old_obj, new_type):
                            pass
                        elif isinstance(old_obj, objects.LevelObject):
                            space.new_obj(new_type(old_obj.pos, old_obj.direct, level_id=old_obj.level_id, level_object_extra=old_obj.level_object_extra))
                            transform_success = True
                        elif isinstance(old_obj, objects.SpaceObject):
                            level_id: refs.LevelID = refs.LevelID(old_obj.space_id.name)
                            self.set_level(levels.Level(level_id, active_level.space_list, super_level_id=active_level.level_id,
                                                        main_space_id=old_obj.space_id))
                            level_object_extra: objects.LevelObjectExtra = {"icon": {"name": objects.get_noun_from_type(objects.default_space_object_type).json_name, "color": space.color}}
                            new_obj = new_type(old_obj.pos, old_obj.direct, level_id=level_id, level_object_extra=level_object_extra)
                            space.new_obj(new_obj)
                            transform_success = True
                        elif old_obj.level_id is not None:
                            space.new_obj(new_type(old_obj.pos, old_obj.direct, level_id=old_obj.level_id))
                            transform_success = True
                        else:
                            space_id: refs.SpaceID = refs.SpaceID(old_obj.uuid.hex)
                            space_color = colors.to_background_color(colors.current_palette[old_obj.sprite_color])
                            new_space = spaces.Space(space_id, positions.Coordinate(3, 3), space_color)
                            level_id: refs.LevelID = refs.LevelID(old_obj.uuid.hex)
                            self.set_level(levels.Level(level_id, [new_space], super_level_id=active_level.level_id))
                            new_space.new_obj(old_type(positions.Coordinate(1, 1)))
                            level_object_extra: objects.LevelObjectExtra = {"icon": {"name": old_obj.json_name, "color": colors.current_palette[old_obj.sprite_color]}}
                            new_obj = new_type(old_obj.pos, old_obj.direct, level_id=level_id)
                            space.new_obj(new_obj)
                            transform_success = True
                    elif issubclass(new_type, objects.SpaceObject):
                        if isinstance(old_obj, new_type):
                            pass
                        elif isinstance(old_obj, objects.SpaceObject):
                            space.new_obj(new_type(old_obj.pos, old_obj.direct, space_id=old_obj.space_id, space_object_extra=old_obj.space_object_extra))
                            transform_success = True
                        elif isinstance(old_obj, objects.LevelObject):
                            new_level = self.get_exact_level(old_obj.level_id)
                            for temp_space in new_level.space_list:
                                active_level.set_space(temp_space)
                            space.new_obj(new_type(old_obj.pos, old_obj.direct, space_id=new_level.main_space_id))
                            transform_success = True
                        elif old_obj.space_id is not None:
                            space.new_obj(new_type(old_obj.pos, old_obj.direct, space_id=old_obj.space_id))
                            transform_success = True
                        else:
                            space_id: refs.SpaceID = refs.SpaceID(old_obj.uuid.hex)
                            space_color = colors.to_background_color(colors.current_palette[old_obj.sprite_color])
                            new_space = spaces.Space(space_id, positions.Coordinate(3, 3), space_color)
                            new_space.new_obj(old_type(positions.Coordinate(1, 1), old_obj.direct))
                            active_level.set_space(new_space)
                            space.new_obj(new_type(old_obj.pos, old_obj.direct, space_id=space_id))
                            transform_success = True
                    elif issubclass(new_noun, objects.TextText):
                        if not isinstance(old_obj, objects.Text):
                            new_obj = objects.get_noun_from_type(old_type)(old_obj.pos, old_obj.direct, space_id=old_obj.space_id, level_id=old_obj.level_id)
                            transform_success = True
                            space.new_obj(new_obj)
                    else:
                        transform_success = True
                        new_obj = new_type(old_obj.pos, old_obj.direct, space_id=old_obj.space_id, level_id=old_obj.level_id)
                        space.new_obj(new_obj)
                if transform_success:
                    delete_object_list.append(old_obj)
            for delete_obj in delete_object_list: 
                space.del_obj(delete_obj)
    def space_transform(self, active_level: levels.Level) -> None:
        old_obj_list: dict[type[objects.SpaceObject], list[tuple[refs.SpaceID, objects.SpaceObject]]]
        new_noun_list: dict[type[objects.SpaceObject], list[type[objects.Noun]]]
        for space_object_type in objects.space_object_types:
            for active_space in active_level.space_list:
                old_obj_list = {p: [] for p in objects.space_object_types}
                new_noun_list = {p: [] for p in objects.space_object_types}
                for other_space in active_level.space_list:
                    for old_obj in other_space.get_spaces():
                        if isinstance(old_obj, space_object_type) and active_space.space_id == old_obj.space_id:
                            old_obj_list[type(old_obj)].append((other_space.space_id, old_obj))
                for noun_type, prop_count in active_space.properties[space_object_type].enabled_dict().items():
                    if issubclass(noun_type, objects.Noun):
                        new_noun_list[space_object_type].extend([noun_type] * prop_count)
                while any(map(lambda p: issubclass(p, objects.RangedNoun), new_noun_list)):
                    delete_noun_list: list[type[objects.Noun]] = []
                    for noun_type in new_noun_list:
                        if not issubclass(noun_type, objects.RangedNoun):
                            continue
                        if issubclass(noun_type, objects.TextAll):
                            new_noun_list[space_object_type].extend(active_level.all_list * prop_count)
                        if issubclass(noun_type, objects.GroupNoun):
                            for group_prop_type, group_prop_count in active_level.group_references[noun_type].enabled_dict().items():
                                if issubclass(group_prop_type, objects.Noun):
                                    new_noun_list[space_object_type].extend([group_prop_type] * group_prop_count)
                        delete_noun_list.append(noun_type)
                    for delete_noun in delete_noun_list:
                        new_noun_list[space_object_type].remove(delete_noun)
                for new_text_type, new_text_count in active_space.special_operator_properties[space_object_type][objects.TextWrite].enabled_dict().items():
                    for _ in range(new_text_count):
                        new_obj = new_text_type(old_obj.pos, old_obj.direct, space_id=old_obj.space_id, level_id=old_obj.level_id)
                        active_space.new_obj(new_obj)
                for old_space_id, old_obj in old_obj_list[space_object_type]:
                    transform_success = False
                    old_space = active_level.get_exact_space(old_space_id)
                    for new_noun in new_noun_list[space_object_type]:
                        if issubclass(new_noun, objects.FixedNoun):
                            if issubclass(new_noun, objects.TextEmpty):
                                transform_success = True
                            if issubclass(new_noun, objects.SpecificSpaceNoun):
                                if new_noun.isreferenceof(old_obj):
                                    old_obj.space_id += new_noun.delta_infinite_tier
                            continue
                        new_type = new_noun.ref_type
                        if issubclass(space_object_type, new_type):
                            transform_success = False
                            break
                        elif issubclass(new_type, objects.SpaceObject):
                            new_obj = new_type(old_obj.pos, old_obj.direct, space_id=old_obj.space_id, space_object_extra=old_obj.space_object_extra)
                        elif issubclass(new_type, objects.LevelObject):
                            new_level_id = refs.LevelID(old_obj.space_id.name)
                            new_level_object_extra = objects.LevelObjectExtra(icon=objects.LevelObjectIcon(
                                name=objects.get_noun_from_type(space_object_type).json_name, color=active_level.get_exact_space(old_obj.space_id).color
                            ))
                            self.set_level(levels.Level(new_level_id, active_level.space_list, super_level_id=active_level.level_id, main_space_id=old_obj.space_id))
                            new_obj = new_type(old_obj.pos, old_obj.direct, level_id=new_level_id, level_object_extra=new_level_object_extra)
                        elif issubclass(new_type, objects.Game):
                            new_obj = objects.Game(old_obj.pos, old_obj.direct, ref_type=objects.get_noun_from_type(space_object_type))
                        elif issubclass(new_noun, objects.TextText):
                            new_obj = objects.get_noun_from_type(space_object_type)(old_obj.pos, old_obj.direct, space_id=old_obj.space_id)
                        else:
                            new_obj = new_type(old_obj.pos, old_obj.direct, space_id=old_obj.space_id)
                        old_space.new_obj(new_obj)
                    if transform_success and len(new_noun_list[space_object_type]) != 0:
                        old_space.del_obj(old_obj)
    def level_transform(self, active_level: levels.Level) -> bool:
        old_obj_list: dict[type[objects.LevelObject], list[tuple[refs.LevelID, refs.SpaceID, objects.LevelObject]]]
        new_noun_list: dict[type[objects.LevelObject], list[type[objects.Noun]]]
        new_noun_list = {p: [] for p in objects.level_object_types}
        for level_object_type in objects.level_object_types:
            transform_success = False
            old_obj_list = {p: [] for p in objects.level_object_types}
            for level in self.level_list:
                for other_space in level.space_list:
                    for old_obj in other_space.get_levels():
                        if isinstance(old_obj, level_object_type) and active_level.level_id == old_obj.level_id:
                            old_obj_list[type(old_obj)].append((level.level_id, other_space.space_id, old_obj))
            for noun_type, prop_count in active_level.properties[level_object_type].enabled_dict().items():
                if issubclass(noun_type, objects.Noun):
                    new_noun_list[level_object_type].extend([noun_type] * prop_count)
            while any(map(lambda p: issubclass(p, objects.RangedNoun), new_noun_list)):
                delete_noun_list: list[type[objects.Noun]] = []
                for noun_type in new_noun_list:
                    if not issubclass(noun_type, objects.RangedNoun):
                        continue
                    if issubclass(noun_type, objects.TextAll):
                        new_noun_list[level_object_type].extend(active_level.all_list * prop_count)
                    if issubclass(noun_type, objects.GroupNoun):
                        for group_prop_type, group_prop_count in active_level.group_references[noun_type].enabled_dict().items():
                            if issubclass(group_prop_type, objects.Noun):
                                new_noun_list[level_object_type].extend([group_prop_type] * group_prop_count)
                    delete_noun_list.append(noun_type)
                for delete_noun in delete_noun_list:
                    new_noun_list[level_object_type].remove(delete_noun)
            for new_text_type, new_text_count in active_level.special_operator_properties[level_object_type][objects.TextWrite].enabled_dict().items():
                for _ in range(new_text_count):
                    new_obj = new_text_type(old_obj.pos, old_obj.direct, space_id=old_obj.space_id, level_id=old_obj.level_id)
                    old_space.new_obj(new_obj)
                transform_success = True
            for old_level_id, old_space_id, old_obj in old_obj_list[level_object_type]:
                old_level = self.get_exact_level(old_level_id)
                old_space = old_level.get_exact_space(old_space_id)
                object_transform_success = True
                for new_noun in new_noun_list[level_object_type]:
                    if issubclass(new_noun, objects.FixedNoun):
                        if issubclass(new_noun, objects.TextEmpty):
                            transform_success = True
                        continue
                    new_type = new_noun.ref_type
                    if issubclass(level_object_type, new_type):
                        object_transform_success = False
                        break
                    elif issubclass(new_type, objects.LevelObject):
                        new_obj = new_type(old_obj.pos, old_obj.direct, level_id=old_obj.level_id, level_object_extra=old_obj.level_object_extra)
                    elif issubclass(new_type, objects.SpaceObject):
                        for new_space in active_level.space_list:
                            if old_level.get_space(new_space.space_id) is None:
                                old_level.set_space(new_space)
                        new_obj = new_type(old_obj.pos, old_obj.direct, space_id=active_level.main_space_id)
                    elif issubclass(new_type, objects.Game):
                        new_obj = objects.Game(old_obj.pos, old_obj.direct, ref_type=objects.get_noun_from_type(level_object_type))
                    elif issubclass(new_noun, objects.TextText):
                        new_obj = objects.get_noun_from_type(level_object_type)(old_obj.pos, old_obj.direct, level_id=active_level.level_id)
                    else:
                        new_obj = new_type(old_obj.pos, old_obj.direct, level_id=active_level.level_id)
                    old_space.new_obj(new_obj)
                if object_transform_success and len(new_noun_list[level_object_type]) != 0:
                    old_space.del_obj(old_obj)
                    transform_success = True
        return transform_success
    def prepare(self, active_level: levels.Level) -> dict[uuid.UUID, objects.Properties]:
        clear_counts: int = 0
        for sub_level in self.level_list:
            if sub_level.super_level_id == active_level.level_id and sub_level.collected[collects.Spore]:
                clear_counts += 1
                self.collectibles.add(collects.Spore(sub_level.level_id))
        if active_level.map_info is not None and clear_counts >= active_level.map_info["minimum_clear_for_blossom"]:
            active_level.collected[collects.Blossom] = True
        old_prop_dict: dict[uuid.UUID, objects.Properties] = {}
        for space in active_level.space_list:
            for obj in space.object_list:
                old_prop_dict[obj.uuid] = obj.properties
            for path in space.get_objs_from_type(objects.Path):
                unlocked = True
                for bonus_type, bonus_counts in path.conditions.items():
                    if len({c for c in self.collectibles if isinstance(c, bonus_type)}) < bonus_counts:
                        unlocked = False
                path.unlocked = unlocked
        for level in self.level_list:
            for space in level.space_list:
                for level_obj in [o for o in space.get_levels() if o.level_id == active_level.level_id]:
                    old_prop_dict[level_obj.uuid] = level_obj.properties
        self.update_rules(active_level, old_prop_dict)
        for space in active_level.space_list:
            for obj in space.object_list:
                obj.old_state = objects.OldObjectState()
        return old_prop_dict
    def turn(self, active_level: levels.Level, op: positions.PlayerOperation) -> ReturnInfo:
        old_prop_dict: dict[uuid.UUID, objects.Properties] = self.prepare(active_level)
        active_level.sound_events = []
        active_level.created_levels = []
        game_push = False
        game_push |= active_level.you(op)
        game_push |= active_level.move()
        self.update_rules(active_level, old_prop_dict)
        game_push |= active_level.shift()
        self.update_rules(active_level, old_prop_dict)
        self.transform(active_level)
        self.space_transform(active_level)
        transform = self.level_transform(active_level)
        active_level.game()
        active_level.text_plus_and_text_minus()
        self.update_rules(active_level, old_prop_dict)
        active_level.tele()
        selected_level = active_level.select(op)
        self.update_rules(active_level, old_prop_dict)
        done = active_level.done()
        active_level.sink()
        active_level.hot_and_melt()
        active_level.defeat()
        active_level.open_and_shut()
        self.update_rules(active_level, old_prop_dict)
        active_level.make()
        self.update_rules(active_level, old_prop_dict)
        for new_level in active_level.created_levels:
            self.set_level(new_level)
        active_level.refresh_all_list()
        active_level.bonus()
        end = active_level.end()
        win = active_level.win()
        for space in active_level.space_list:
            for path in space.get_objs_from_type(objects.Path):
                unlocked = True
                for bonus_type, bonus_counts in path.conditions.items():
                    if len({c for c in self.collectibles if isinstance(c, bonus_type)}) < bonus_counts:
                        unlocked = False
                path.unlocked = unlocked
        if active_level.collected[collects.Bonus] and win:
            self.collectibles.add(collects.Bonus(active_level.level_id))
        return {"win": win, "end": end, "done": done, "transform": transform,
                "game_push": game_push, "selected_level": selected_level}
    def to_json(self) -> LevelpackJson:
        json_object: LevelpackJson = {
            "ver": basics.versions,
            "name": self.name,
            "main_level": self.main_level_id.to_json(),
            "collectibles": list(map(collects.Collectible.to_json, self.collectibles)),
            "level_list": list(map(levels.Level.to_json, self.level_list)),
            "rule_list": []
        }
        for rule in self.rule_list:
            json_object["rule_list"].append([])
            for obj in rule:
                json_object["rule_list"][-1].append({v: k for k, v in objects.object_name.items()}[obj])
        return json_object

def json_to_levelpack(json_object: LevelpackJson) -> Levelpack:
    ver = json_object.get("ver")
    reversed_collectible_dict = {v: k for k, v in collects.collectible_dict.items()}
    collectibles: set[collects.Collectible] = set()
    level_list = []
    for level in json_object["level_list"]:
        level_list.append(levels.json_to_level(level, ver))
    rule_list: list[rules.Rule] = []
    for rule in json_object["rule_list"]:
        rule_list.append([])
        for object_type in rule:
            rule_list[-1].append(objects.object_name[object_type]) # type: ignore
    if basics.compare_versions(ver if ver is not None else "0.0", "3.8") == -1:
        main_level_id: refs.LevelID = refs.LevelID(json_object["main_level"]) # type: ignore
    else:
        main_level_id: refs.LevelID = refs.LevelID(**json_object["main_level"])
        for collectible in json_object["collectibles"]:
            collectibles.add(reversed_collectible_dict[collectible["type"]](source=refs.LevelID(collectible["source"]["name"])))
    return Levelpack(name=json_object.get("name"),
                     author=json_object.get("author"),
                     main_level_id=main_level_id,
                     level_list=level_list,
                     collectibles=collectibles,
                     rule_list=rule_list)