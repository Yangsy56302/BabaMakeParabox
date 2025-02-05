from typing import Optional, TypeGuard, TypedDict, NotRequired
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
    select: Optional[list[bmp.ref.LevelID]]

default_levelpack_info: ReturnInfo = {
    "win": False,
    "end": False,
    "done": False,
    "transform": False,
    "game_push": False,
    "select": None
}

class LevelpackJson41(TypedDict):
    ver: str
    name: NotRequired[str]
    author: NotRequired[str]
    current_level: bmp.ref.LevelIDJson
    collectibles: list[bmp.obj.CollectibleJson]
    levels: list[bmp.level.LevelJson41]
    spaces: list[bmp.space.SpaceJson41]
    level_init_states: NotRequired[list[bmp.level.LevelJson41]]
    space_init_states: NotRequired[list[bmp.space.SpaceJson41]]
    rules: list[list[str]]

class LevelpackJson4102(TypedDict):
    ver: str
    name: NotRequired[str]
    author: NotRequired[str]
    current_level: bmp.ref.LevelIDJson
    collectibles: list[bmp.obj.CollectibleJson]
    levels: list[bmp.level.LevelJson41]
    spaces: list[bmp.space.SpaceJson4102]
    level_init_states: NotRequired[list[bmp.level.LevelJson41]]
    space_init_states: NotRequired[list[bmp.space.SpaceJson4102]]
    rules: list[list[str]]

type LevelpackJson = LevelpackJson4102

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
        self.level_init_state_dict: dict[bmp.ref.LevelID, bmp.level.Level] = copy.deepcopy(self.level_dict)
        if level_init_state_dict is not None:
            self.level_init_state_dict.update(level_init_state_dict)
        self.space_init_state_dict: dict[bmp.ref.SpaceID, bmp.space.Space] = copy.deepcopy(self.space_dict)
        if space_init_state_dict is not None:
            self.space_init_state_dict.update(space_init_state_dict)
        for level in self.level_dict.values():
            level.space_dict = space_dict
        for level in self.level_init_state_dict.values():
            level.space_dict = space_dict
        self.current_level_id: bmp.ref.LevelID = current_level_id
        self.collectibles: set[bmp.obj.Collectible] = collectibles if collectibles is not None else set()
        self.rule_list: list[bmp.rule.Rule] = rule_list if (rule_list is not None and len(rule_list) != 0) else bmp.rule.default_rule_list
    def get_exact_level(self, level_id: bmp.ref.LevelID) -> bmp.level.Level:
        return self.level_dict[level_id]
    def get_level(self, level_id: Optional[bmp.ref.LevelID]) -> Optional[bmp.level.Level]:
        return None if level_id is None else self.level_dict.get(level_id)
    def set_level(self, level_id: bmp.ref.LevelID, level: bmp.level.Level) -> None:
        level.space_dict = self.space_dict
        self.level_dict[level_id] = level
    def set_level_init_state(self, level_id: bmp.ref.LevelID, level: bmp.level.Level) -> None:
        self.level_init_state_dict[level_id] = level
    def reset_level(self, level_id: bmp.ref.LevelID) -> None:
        old_level = self.level_dict.get(level_id)
        if old_level is not None:
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
        self.current_level.game_properties.clear()
        for level_object_type in bmp.obj.level_object_types:
            self.current_level.properties[level_object_type].clear()
            self.current_level.special_operator_properties[level_object_type] = {o: bmp.obj.PropertyStorage() for o in bmp.obj.special_operators}
        active_space_objs: list[bmp.obj.SpaceObject] = []
        for space in self.current_level.space_list:
            for object_type in bmp.obj.space_object_types:
                space.properties[object_type].clear()
                space.special_operator_properties[object_type] = {o: bmp.obj.PropertyStorage() for o in bmp.obj.special_operators}
            for obj in space.object_list:
                obj.properties.clear()
                obj.operator_properties = {o: bmp.obj.PropertyStorage() for o in bmp.obj.special_operators}
            if space != self.current_level.current_space:
                active_space_objs.extend(o for o in space.get_spaces())
        for space_obj in active_space_objs:
            space_obj.properties.clear()
        current_level_objs: list[bmp.obj.LevelObject] = []
        for level in self.level_list:
            for space in level.space_list:
                if level != self.current_level:
                    current_level_objs.extend([
                        o for o in space.get_levels()
                        if o.level_id == self.current_level.level_id
                    ])
        for level_obj in current_level_objs:
            level_obj.properties.clear()
        for space in self.current_level.space_list:
            space.set_rule()
        new_prop_list: list[tuple[bmp.obj.Object, tuple[bmp.obj.Text, bool]]] = []
        global_rule_info_list = [bmp.rule.get_info_from_rule(r) for r in self.rule_list]
        for space in self.current_level.space_list:
            # space & levelpack
            for rule_info in space.rule_info + global_rule_info_list:
                prefix_info_list = rule_info.prefix_info_list
                noun_negated = rule_info.noun_negated
                noun_obj = rule_info.noun
                infix_info_list = rule_info.infix_info_list
                new_match_obj_list: list[bmp.obj.Object] = []
                if isinstance(noun_obj, bmp.obj.Noun):
                    if type(noun_obj) == bmp.obj.TextAll:
                        if noun_negated:
                            new_match_obj_list = [o for o in space.object_list if isinstance(o, bmp.obj.types_in_not_all)]
                        else:
                            new_match_obj_list = [o for o in space.object_list if noun_obj.isreferenceof(o, all_list = self.current_level.all_list)]
                    elif noun_negated:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll().isreferenceof(o, all_list = self.current_level.all_list) and not noun_obj.isreferenceof(o)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_noun(noun_obj)]
                        # meta object
                        for oper_info in rule_info.oper_list:
                            oper_obj = oper_info.oper
                            for prop_info in oper_info.prop_list:
                                prop_obj = prop_info.prop
                                prop_negated = prop_info.prop_negated
                                # meta game
                                if issubclass(noun_obj.ref_type, bmp.obj.Game) and isinstance(oper_obj, bmp.obj.TextIs):
                                    if len(infix_info_list) == 0 and len(prefix_info_list) == 0:
                                        self.current_level.game_properties.update(prop_obj, prop_negated)
                                # meta level
                                elif issubclass(noun_obj.ref_type, bmp.obj.LevelObject):
                                    print("meta level")
                                    level_prop_update: bool = False
                                    for level_obj in current_level_objs:
                                        if not isinstance(level_obj, noun_obj.ref_type):
                                            continue
                                        meet_prefix_conditions = self.current_level.meet_prefix_conditions(space, level_obj, prefix_info_list, True)
                                        meet_infix_conditions = self.current_level.meet_infix_conditions(space, level_obj, infix_info_list)
                                        if len(prefix_info_list) != 0 and not meet_prefix_conditions:
                                            continue
                                        if len(infix_info_list) != 0 and not meet_infix_conditions:
                                            continue
                                        level_prop_update |= True
                                        if type(oper_obj) == bmp.obj.TextIs:
                                            level_obj.properties.update(prop_obj, prop_negated)
                                        else:
                                            level_obj.operator_properties[type(oper_obj)].update(prop_obj, prop_negated)
                                    if len(current_level_objs) == 0:
                                        level_prop_update |= True
                                    if level_prop_update:
                                        if type(oper_obj) == bmp.obj.TextIs:
                                            self.current_level.properties[noun_obj.ref_type].update(prop_obj, prop_negated)
                                        else:
                                            self.current_level.special_operator_properties[noun_obj.ref_type][type(oper_obj)].update(prop_obj, prop_negated)
                                    del level_prop_update
                                # meta space
                                elif issubclass(noun_obj.ref_type, bmp.obj.SpaceObject):
                                    space_prop_update: bool = False
                                    for space_obj in active_space_objs:
                                        if not isinstance(space_obj, noun_obj.ref_type):
                                            continue
                                        meet_prefix_conditions = self.current_level.meet_prefix_conditions(space, space_obj, prefix_info_list, True)
                                        meet_infix_conditions = self.current_level.meet_infix_conditions(space, space_obj, infix_info_list)
                                        if len(prefix_info_list) != 0 and not meet_prefix_conditions:
                                            continue
                                        if len(infix_info_list) != 0 and not meet_infix_conditions:
                                            continue
                                        space_prop_update |= True
                                        if type(oper_obj) == bmp.obj.TextIs:
                                            space_obj.properties.update(prop_obj, prop_negated)
                                        else:
                                            space_obj.operator_properties[type(oper_obj)].update(prop_obj, prop_negated)
                                    if len(active_space_objs) == 0:
                                        space_prop_update |= True
                                    if space_prop_update:
                                        if type(oper_obj) == bmp.obj.TextIs:
                                            space.properties[noun_obj.ref_type].update(prop_obj, prop_negated)
                                        else:
                                            space.special_operator_properties[noun_obj.ref_type][type(oper_obj)].update(prop_obj, prop_negated)
                                    del space_prop_update
                else:
                    if noun_negated:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll().isreferenceof(o, all_list = self.current_level.all_list) and not noun_obj.isreferenceof(o)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_noun(noun_obj)]
                for oper_info in rule_info.oper_list:
                    oper_obj = oper_info.oper
                    for prop_info in oper_info.prop_list:
                        prop_obj = prop_info.prop
                        prop_negated = prop_info.prop_negated
                        for obj in new_match_obj_list:
                            if self.current_level.meet_infix_conditions(space, obj, infix_info_list) and self.current_level.meet_prefix_conditions(space, obj, prefix_info_list):
                                if type(oper_obj) == bmp.obj.TextIs:
                                    new_prop_list.append((obj, (prop_obj, prop_negated)))
                                else:
                                    obj.operator_properties[type(oper_obj)].update(prop_obj, prop_negated)
            # outer space
            outer_space_rule_info = self.current_level.recursion_rules(space)[1]
            for rule_info in outer_space_rule_info:
                prefix_info_list = rule_info.prefix_info_list
                noun_negated = rule_info.noun_negated
                noun_obj = rule_info.noun
                infix_info_list = rule_info.infix_info_list
                new_match_obj_list: list[bmp.obj.Object] = []
                if isinstance(noun_obj, bmp.obj.GeneralNoun):
                    object_type = noun_obj.ref_type
                    if noun_negated:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll().isreferenceof(o, all_list = self.current_level.all_list) and not isinstance(o, object_type)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_type(object_type)]
                elif type(noun_obj) is bmp.obj.TextAll:
                    if noun_negated:
                        new_match_obj_list = [o for o in space.object_list if isinstance(o, bmp.obj.types_in_not_all)]
                    else:
                        new_match_obj_list = [o for o in space.object_list if noun_obj.isreferenceof(o, all_list = self.current_level.all_list)]
                else:
                    if noun_negated:
                        new_match_obj_list = [o for o in space.object_list if bmp.obj.TextAll().isreferenceof(o, all_list = self.current_level.all_list) and not noun_obj.isreferenceof(o)]
                    else:
                        new_match_obj_list = [o for o in space.get_objs_from_noun(noun_obj)]
                for oper_info in rule_info.oper_list:
                    oper_obj = oper_info.oper
                    for prop_info in oper_info.prop_list:
                        prop_obj = prop_info.prop
                        prop_negated = prop_info.prop_negated
                        if issubclass(object_type, bmp.obj.Game) and isinstance(oper_obj, bmp.obj.TextIs):
                            if not noun_negated and len(infix_info_list) == 0 and self.current_level.meet_prefix_conditions(space, bmp.obj.Object((0, 0)), prefix_info_list, True):
                                self.current_level.game_properties.update(prop_obj, prop_negated)
                        for obj in new_match_obj_list:
                            if self.current_level.meet_infix_conditions(space, obj, infix_info_list) and self.current_level.meet_prefix_conditions(space, obj, prefix_info_list):
                                if type(oper_obj) == bmp.obj.TextIs:
                                    new_prop_list.append((obj, (prop_obj, prop_negated)))
                                else:
                                    obj.operator_properties[type(oper_obj)].update(prop_obj, prop_negated)
        for obj, (prop_obj, prop_negated) in new_prop_list:
            obj.properties.update(prop_obj, prop_negated)
    def get_transform_noun(self, old_obj: bmp.obj.Object, negated: bool = False) -> list[bmp.obj.Noun]:
        new_noun_list: list[bmp.obj.Noun] = []
        get_prop_dict_func = bmp.obj.PropertyStorage.disabled_dict if negated else bmp.obj.PropertyStorage.enabled_dict
        for noun_type, noun_info_list in get_prop_dict_func(old_obj.properties).items():
            if not issubclass(noun_type, bmp.obj.Noun):
                continue
            for noun_info in noun_info_list:
                if isinstance(noun_info.obj, bmp.obj.Noun):
                    new_noun_list.append(noun_info.obj)
        for text_type, text_info_list in get_prop_dict_func(old_obj.operator_properties[bmp.obj.TextWrite]).items():
            for text_info in text_info_list:
                new_noun_list.append(bmp.obj.get_noun_from_type(type(text_info.obj))())
        while any(map(lambda n: isinstance(n, bmp.obj.RangedNoun), new_noun_list)):
            delete_noun_list: list[bmp.obj.Noun] = []
            for noun_obj in new_noun_list:
                if not isinstance(noun_obj, bmp.obj.RangedNoun):
                    continue
                if type(noun_obj) == bmp.obj.TextAll:
                    new_noun_list.extend([bmp.obj.get_noun_from_type(o)() for o in self.current_level.all_list])
                if isinstance(noun_obj, bmp.obj.GroupNoun):
                    for group_noun_type, group_noun_info_list in self.current_level.group_references[type(noun_obj)].enabled_dict().items():
                        if not issubclass(group_noun_type, bmp.obj.Noun):
                            continue
                        for group_noun_info in group_noun_info_list:
                            if isinstance(group_noun_info.obj, bmp.obj.Noun):
                                new_noun_list.append(group_noun_info.obj)
                delete_noun_list.append(noun_obj)
            for delete_noun in delete_noun_list:
                new_noun_list.remove(delete_noun)
        return new_noun_list
    def transform_object(self, old_obj: bmp.obj.Object, space: bmp.space.Space, level: bmp.level.Level) -> bool:
        new_noun_list: list[bmp.obj.Noun] = self.get_transform_noun(old_obj)
        not_new_noun_list: list[bmp.obj.Noun] = self.get_transform_noun(old_obj, negated=True)
        transform_success: bool = False
        noun_is_noun: bool = False
        noun_is_not_noun: bool = False
        for new_noun in new_noun_list:
            if new_noun.isreferenceof(old_obj):
                noun_is_noun = True
        for not_new_noun in not_new_noun_list:
            if not_new_noun.isreferenceof(old_obj):
                noun_is_not_noun = True
        if noun_is_not_noun:
            transform_success = True
        if noun_is_noun:
            return False
        for new_noun in new_noun_list:
            if isinstance(new_noun, bmp.obj.FixedNoun):
                if isinstance(new_noun, bmp.obj.TextEmpty):
                    transform_success = True
                if isinstance(new_noun, bmp.obj.SpecificSpaceNoun):
                    if new_noun.isreferenceof(old_obj) and old_obj.space_id is not None:
                        old_obj.space_id += new_noun.delta_infinite_tier
                continue
            new_obj = old_obj.transform(new_noun.ref_type)
            new_obj.reset_uuid()
            if isinstance(old_obj, bmp.obj.SpaceObject) and isinstance(new_obj, bmp.obj.LevelObject):
                if old_obj.space_id is not None and new_obj.level_id is not None:
                    if new_obj.level_id not in self.level_dict.keys():
                        new_obj_level = bmp.level.Level(
                            new_obj.level_id, [old_obj.space_id], old_obj.space_id,
                            super_level_id = level.level_id,
                        )
                        self.set_level(new_obj.level_id, new_obj_level)
                        self.set_level_init_state(new_obj.level_id, new_obj_level)
                space.new_obj(new_obj)
                transform_success = True
            elif isinstance(old_obj, bmp.obj.LevelObject) and isinstance(new_obj, bmp.obj.SpaceObject):
                old_obj_level = self.get_level(old_obj.level_id)
                if old_obj_level is not None:
                    for old_obj_space in old_obj_level.space_list:
                        new_obj_copy = copy.deepcopy(new_obj)
                        new_obj_copy.reset_uuid()
                        new_obj_copy.space_id = old_obj_space.space_id
                        level.space_included.append(old_obj_space.space_id)
                        space.new_obj(new_obj_copy)
                transform_success = True
            else:
                space.new_obj(new_obj)
                transform_success = True
        if transform_success:
            space.del_obj(old_obj)
        return transform_success
    def transform(self) -> bool:
        level_transform_success: bool = False
        for space in self.current_level.space_list:
            for old_obj in space.object_list:
                self.transform_object(old_obj, space, self.current_level)
        for outer_level in self.level_dict.values():
            for space in outer_level.space_list:
                for old_level_obj in [l for l in space.get_levels() if l.level_id == self.current_level_id]:
                    level_transform_success |= self.transform_object(old_level_obj, space, outer_level)
        return level_transform_success
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
        transform = self.transform()
        self.current_level.game()
        self.current_level.text_plus_and_text_minus()
        self.update_rules()
        self.current_level.tele()
        select = self.current_level.select(op)
        if select is not None:
            select = [l for l in select if l in self.level_dict.keys()]
            if len(select) == 0:
                select = None
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
            self.set_level(new_level.level_id, new_level)
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
            "win": win,
            "end": end,
            "done": done,
            "transform": transform,
            "game_push": game_push,
            "select": select,
        }
    def to_json(self) -> LevelpackJson:
        json_object: LevelpackJson = {
            "ver": bmp.base.version,
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
            desc = bmp.lang.fformat("saving.levelpack.levels"),
            unit = bmp.lang.fformat("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["levels"].append(level.to_json())
        for space in tqdm(
            self.space_dict.values(),
            desc = bmp.lang.fformat("saving.level.spaces"),
            unit = bmp.lang.fformat("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["spaces"].append(space.to_json())
        for level in tqdm(
            self.level_init_state_dict.values(),
            desc = bmp.lang.fformat("saving.levelpack.levels"),
            unit = bmp.lang.fformat("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["level_init_states"].append(level.to_json())
        for space in tqdm(
            self.space_init_state_dict.values(),
            desc = bmp.lang.fformat("saving.level.spaces"),
            unit = bmp.lang.fformat("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["space_init_states"].append(space.to_json())
        for collectible in tqdm(
            self.collectibles,
            desc = bmp.lang.fformat("saving.levelpack.collectibles"),
            unit = bmp.lang.fformat("collectible.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["collectibles"].append(collectible.to_json())
        for rule in tqdm(
            self.rule_list,
            desc = bmp.lang.fformat("saving.levelpack.rules"),
            unit = bmp.lang.fformat("rule.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            json_object["rules"].append([])
            for obj in rule:
                json_object["rules"][-1].append(obj.json_name)
        return json_object

type AnyLevelpackJson = LevelpackJson41 | LevelpackJson4102 | LevelpackJson

def formatted_after_41(json_object: AnyLevelpackJson, ver: str) -> TypeGuard[LevelpackJson41]:
    return bmp.base.compare_versions(ver, "4.1") >= 0

def formatted_after_4102(json_object: AnyLevelpackJson, ver: str) -> TypeGuard[LevelpackJson4102]:
    return bmp.base.compare_versions(ver, "4.102") >= 0

def formatted_currently(json_object: AnyLevelpackJson, ver: str) -> TypeGuard[LevelpackJson]:
    return bmp.base.compare_versions(ver, bmp.base.version) == 0

def formatted_from_future(json_object: AnyLevelpackJson, ver: str) -> TypeGuard[AnyLevelpackJson]:
    return bmp.base.compare_versions(ver, bmp.base.version) > 0

def update_json_format(json_object: AnyLevelpackJson, ver: str) -> LevelpackJson:
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
        new_json_object: LevelpackJson = {
            "ver": bmp.base.version,
            "collectibles": json_object["collectibles"],
            "current_level": json_object["current_level"],
            "levels": [bmp.level.update_json_format(l, ver) for l in json_object["levels"]],
            "spaces": [bmp.space.update_json_format(s, ver) for s in json_object["spaces"]],
            "rules": json_object["rules"],
        }
        if "name" in json_object:
            new_json_object["name"] = json_object["name"]
        if "author" in json_object:
            new_json_object["author"] = json_object["author"]
        if "level_init_states" in json_object:
            new_json_object["level_init_states"] = [bmp.level.update_json_format(l, ver) for l in json_object["level_init_states"]]
        if "space_init_states" in json_object:
            new_json_object["space_init_states"] = [bmp.space.update_json_format(s, ver) for s in json_object["space_init_states"]]
        return new_json_object
    else:
        raise bmp.base.UpgradeError(json_object)

def json_to_levelpack(json_object: LevelpackJson) -> Levelpack:
    collectibles: set[bmp.obj.Collectible] = set()
    space_dict: dict[bmp.ref.SpaceID, bmp.space.Space] = {}
    for space_json in tqdm(
        json_object["spaces"],
        desc = bmp.lang.fformat("loading.level.spaces"),
        unit = bmp.lang.fformat("space.name"),
        position = 0,
        **bmp.lang.default_tqdm_args,
    ):
        space = bmp.space.json_to_space(space_json)
        space_dict[space.space_id] = space
    level_dict: dict[bmp.ref.LevelID, bmp.level.Level] = {}
    for level_json in tqdm(
        json_object["levels"],
        desc = bmp.lang.fformat("loading.levelpack.levels"),
        unit = bmp.lang.fformat("level.name"),
        position = 0,
        **bmp.lang.default_tqdm_args,
    ):
        level = bmp.level.json_to_level(level_json)
        level_dict[level.level_id] = level
    space_init_state_dict_json = json_object.get("space_init_states")
    space_init_state_dict: dict[bmp.ref.SpaceID, bmp.space.Space]
    if space_init_state_dict_json is not None:
        space_init_state_dict = {}
        for space_json in tqdm(
            space_init_state_dict_json,
            desc = bmp.lang.fformat("loading.level.spaces"),
            unit = bmp.lang.fformat("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            space = bmp.space.json_to_space(space_json)
            space_init_state_dict[space.space_id] = space
    else:
        space_init_state_dict = copy.deepcopy(space_dict)
    level_init_state_dict_json = json_object.get("level_init_states")
    level_init_state_dict: dict[bmp.ref.LevelID, bmp.level.Level]
    if level_init_state_dict_json is not None:
        level_init_state_dict = {}
        for level_json in tqdm(
            level_init_state_dict_json,
            desc = bmp.lang.fformat("loading.levelpack.levels"),
            unit = bmp.lang.fformat("level.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            level = bmp.level.json_to_level(level_json)
            level_init_state_dict[level.level_id] = level
    else:
        level_init_state_dict = copy.deepcopy(level_dict)
    rule_list: list[bmp.rule.Rule] = []
    for rule in tqdm(
        json_object["rules"],
        desc = bmp.lang.fformat("loading.levelpack.rules"),
        unit = bmp.lang.fformat("rule.name"),
        position = 0,
        **bmp.lang.default_tqdm_args,
    ):
        rule_list.append([])
        for object_type in rule:
            rule_list[-1].append(bmp.obj.name_to_class[object_type]()) # type: ignore
    current_level_id: bmp.ref.LevelID = bmp.ref.LevelID(**json_object["current_level"])
    for collectible in tqdm(
        json_object["collectibles"],
        desc = bmp.lang.fformat("loading.levelpack.collectibles"),
        unit = bmp.lang.fformat("collectible.name"),
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