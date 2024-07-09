from typing import Any, Optional
import pygame

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.levels as levels
import baba_make_parabox.displays as displays

class world(object):
    class_name: str = "World"
    def __init__(self, name: str, level_list: list[levels.level], rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name
        self.level_list: list[levels.level] = list(level_list)
        self.rule_list: list[rules.Rule] = rule_list if rule_list is not None else rules.default_rule_list
    def __str__(self) -> str:
        return self.class_name
    def __repr__(self) -> str:
        return self.class_name
    def find_rules(self, *match_rule: Optional[type[objects.Text]]) -> list[rules.Rule]:
        found_rules = []
        for rule in self.rule_list:
            if len(rule) != len(match_rule):
                continue
            not_match = False
            for i in range(len(rule)):
                text_type = match_rule[i]
                if text_type is not None:
                    if not issubclass(rule[i], text_type):
                        not_match = True
                        break
            if not_match:
                continue
            found_rules.append(rule)
        return found_rules
    def get_level(self, name: str, inf_tier: int) -> Optional[levels.level]:
        level = list(filter(lambda l: l.name == name and l.inf_tier == inf_tier, self.level_list))
        return level[0] if len(level) != 0 else None
    def get_exist_level(self, name: str, inf_tier: int) -> levels.level:
        level = list(filter(lambda l: l.name == name and l.inf_tier == inf_tier, self.level_list))
        return level[0]
    def find_super_level(self, name: str, inf_tier: int) -> Optional[tuple[levels.level, objects.Object]]:
        for super_level in self.level_list:
            for obj in super_level.get_levels():
                if name == obj.name and inf_tier == obj.inf_tier:
                    return (super_level, obj)
        return None
    def update_rules(self) -> None:
        for level in self.level_list:
            level.update_rules()
            for obj in level.object_list:
                obj.clear_prop()
        for level in self.level_list:
            for prop in objects.object_name.values():
                if issubclass(prop, objects.Property):
                    prop_rules = level.find_rules(objects.Noun, objects.IS, prop) + self.find_rules(objects.Noun, objects.IS, prop)
                    for obj_type in [t[0] for t in prop_rules]:
                        for obj in level.get_objs_from_type(objects.nouns_objs_dicts.get_obj(obj_type)): # type: ignore
                            obj: objects.Object
                            obj.new_prop(prop)
    def get_move_list(self, level: levels.level, obj: objects.Object, pos: spaces.Coord, facing: spaces.Orient, passed: Optional[list[levels.level]] = None, depth: int = 1) -> Optional[list[tuple[objects.Object, levels.level, spaces.Coord, spaces.Orient]]]:
        if depth > 127:
            return None
        depth += 1
        passed = passed[:] if passed is not None else []
        new_pos = spaces.pos_facing(pos, facing)
        simple_push = True
        # push out
        move_list = []
        if level.out_of_range(new_pos):
            # inf out
            if level in passed:
                ret = self.find_super_level(level.name, level.inf_tier + 1)
                if ret is None:
                    return None
                super_level, level_obj = ret
                get_move_list = self.get_move_list(super_level, obj, (level_obj.x, level_obj.y), facing, passed, depth)
                if get_move_list is None:
                    return None
                move_list.extend(get_move_list)
            else:
                ret = self.find_super_level(level.name, level.inf_tier)
                if ret is None:
                    return None
                super_level, level_obj = ret
                passed.append(level)
                get_move_list = self.get_move_list(super_level, obj, (level_obj.x, level_obj.y), facing, passed, depth)
                if get_move_list is None:
                    return None
                move_list.extend(get_move_list)
            simple_push = False
        # stop wall & shut door
        stop_objects = list(filter(lambda o: objects.Object.has_prop(o, objects.STOP), level.get_objs_from_pos(new_pos)))
        shut_objects = list(filter(lambda o: objects.Object.has_prop(o, objects.SHUT), level.get_objs_from_pos(new_pos)))
        if len(stop_objects) != 0:
            if not obj.has_prop(objects.OPEN):
                return None
            for stop_object in stop_objects:
                if stop_object not in shut_objects:
                    return None
            return [(obj, level, new_pos, facing)]
        # push box
        push_objects = list(filter(lambda o: objects.Object.has_prop(o, objects.PUSH), level.get_objs_from_pos(new_pos)))
        if len(push_objects) != 0:
            for push_object in push_objects:
                new_move_list = self.get_move_list(level, push_object, (push_object.x, push_object.y), facing, depth=depth)
                if new_move_list is None:
                    if not isinstance(push_object, (objects.Level, objects.Clone)):
                        return None
                else:
                    move_list.extend(new_move_list)
            move_list.append((obj, level, new_pos, facing))
            simple_push = False
        # level
        level_objects = level.get_levels_from_pos(new_pos)
        clone_objects = level.get_clones_from_pos(new_pos)
        level_like_objects = level_objects + clone_objects
        if len(level_like_objects) != 0:
            for level_like_object in level_like_objects:
                if level_like_object in [t[0] for t in move_list]:
                    continue
                sub_level = self.get_level(level_like_object.name, level_like_object.inf_tier)
                if sub_level is None:
                    return None
                # inf in
                elif sub_level in passed:
                    sub_sub_level = self.get_level(sub_level.name, sub_level.inf_tier - 1)
                    if sub_sub_level is None:
                        return None
                    input_pos = sub_sub_level.default_input_position(spaces.swap_orientation(facing))
                    passed.append(level)
                    new_move_list = self.get_move_list(sub_sub_level, obj, input_pos, facing, passed, depth)
                # push in
                else:
                    input_pos = sub_level.default_input_position(spaces.swap_orientation(facing))
                    passed.append(level)
                    new_move_list = self.get_move_list(sub_level, obj, input_pos, facing, passed, depth)
                if new_move_list is None:
                    return None
                move_list.extend(new_move_list)
            simple_push = False
        move_list = basics.remove_same_elements(move_list)
        return [(obj, level, new_pos, facing)] if simple_push else move_list
    def move_objs_from_move_list(self, move_list: list[tuple[objects.Object, levels.level, spaces.Coord, spaces.Orient]]) -> None:
        move_list = basics.remove_same_elements(move_list)
        for move_obj, new_level, new_pos, new_facing in move_list:
            for level in self.level_list:
                if level.get_obj(move_obj.uuid) is not None:
                    old_level = level
            if old_level == new_level:
                move_obj.x, move_obj.y = new_pos
                move_obj.facing = new_facing
            else:
                old_level.del_obj(move_obj.uuid)
                move_obj.x, move_obj.y = new_pos
                move_obj.facing = new_facing
                new_level.new_obj(move_obj)
    def you(self, facing: spaces.PlayerOperation) -> None:
        if facing == " ":
            return
        move_list = []
        for level in self.level_list:
            for obj in level.object_list:
                if obj.has_prop(objects.YOU):
                    new_move_list = self.get_move_list(level, obj, (obj.x, obj.y), facing)
                    if new_move_list is not None:
                        move_list.extend(new_move_list)
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
    def move(self) -> None:
        move_list = []
        for level in self.level_list:
            for obj in level.object_list:
                if obj.has_prop(objects.MOVE):
                    new_move_list = self.get_move_list(level, obj, (obj.x, obj.y), obj.facing)
                    if new_move_list is not None:
                        move_list.extend(new_move_list)
                    else:
                        new_move_list = self.get_move_list(level, obj, (obj.x, obj.y), spaces.swap_orientation(obj.facing))
                        if new_move_list is not None:
                            move_list.extend(new_move_list)
                        else:
                            move_list.append((obj, level, (obj.x, obj.y), spaces.swap_orientation(obj.facing)))
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
    def sink(self) -> None:
        for level in self.level_list:
            sink_objs = filter(lambda o: objects.Object.has_prop(o, objects.SINK), level.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), level.object_list)
            delete_list = []
            for sink_obj in sink_objs:
                for obj in level.object_list:
                    if obj == sink_obj:
                        continue
                    if obj.x == sink_obj.x and obj.y == sink_obj.y:
                        if not ((obj in float_objs) ^ (sink_obj in float_objs)):
                            if obj.uuid not in delete_list and sink_obj.uuid not in delete_list:
                                delete_list.append(obj.uuid)
                                delete_list.append(sink_obj.uuid)
                                break
            for uuid in delete_list:
                level.del_obj(uuid)
    def hot_and_melt(self) -> None:
        for level in self.level_list:
            hot_objs = filter(lambda o: objects.Object.has_prop(o, objects.HOT), level.object_list)
            melt_objs = filter(lambda o: objects.Object.has_prop(o, objects.MELT), level.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), level.object_list)
            for hot_obj in hot_objs:
                for melt_obj in melt_objs:
                    if melt_obj.x == hot_obj.x and melt_obj.y == hot_obj.y:
                        if not ((melt_obj in float_objs) ^ (hot_obj in float_objs)):
                            level.del_obj(melt_obj.uuid)
    def defeat(self) -> None:
        for level in self.level_list:
            you_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), level.object_list)
            defeat_objs = filter(lambda o: objects.Object.has_prop(o, objects.DEFEAT), level.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), level.object_list)
            for defeat_obj in defeat_objs:
                for you_obj in you_objs:
                    if you_obj.x == defeat_obj.x and you_obj.y == defeat_obj.y:
                        if not ((you_obj in float_objs) ^ (defeat_obj in float_objs)):
                            level.del_obj(you_obj.uuid)
    def open_and_shut(self) -> None:
        for level in self.level_list:
            open_objs = filter(lambda o: objects.Object.has_prop(o, objects.OPEN), level.object_list)
            shut_objs = filter(lambda o: objects.Object.has_prop(o, objects.SHUT), level.object_list)
            delete_list = []
            for shut_obj in shut_objs:
                for open_obj in open_objs:
                    if shut_obj.x == open_obj.x and shut_obj.y == open_obj.y:
                        if shut_obj.uuid not in delete_list and open_obj.uuid not in delete_list:
                            delete_list.append(shut_obj.uuid)
                            delete_list.append(open_obj.uuid)
                            break
            for uuid in delete_list:
                level.del_obj(uuid)
    def transform(self) -> None:
        global_transform_rules = self.find_rules(objects.Noun, objects.IS, objects.Noun)
        for level in self.level_list:
            transform_rules = level.find_rules(objects.Noun, objects.IS, objects.Noun)
            transform_rules.extend(global_transform_rules)
            for rule in transform_rules:
                for old_obj in level.get_objs_from_type(objects.nouns_objs_dicts.get_obj(rule[0])): # type: ignore
                    old_obj: objects.Object
                    new_type = objects.nouns_objs_dicts.get_obj(rule[2]) # type: ignore
                    if new_type in (objects.Level, objects.Clone):
                        new_level = levels.level(old_obj.uuid.hex, (1, 1), 0, pygame.Color("#000000"))
                        self.level_list.append(new_level)
                        new_level.new_obj(type(old_obj)((0, 0)))
                        new_obj = new_type((old_obj.x, old_obj.y), old_obj.uuid.hex, 0, old_obj.facing)
                        level.del_obj(old_obj.uuid)
                        level.new_obj(new_obj)
                    else:
                        new_obj = new_type((old_obj.x, old_obj.y), old_obj.facing)
                        level.del_obj(old_obj.uuid)
                        level.new_obj(new_obj)
    def winned(self) -> bool:
        for level in self.level_list:
            you_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), level.object_list)
            win_objs = filter(lambda o: objects.Object.has_prop(o, objects.WIN), level.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), level.object_list)
            for you_obj in you_objs:
                for win_obj in win_objs:
                    if you_obj.x == win_obj.x and you_obj.y == win_obj.y:
                        if not ((you_obj in float_objs) ^ (win_obj in float_objs)):
                            return True
        return False
    def round(self, op: spaces.PlayerOperation) -> bool:
        self.update_rules()
        self.you(op)
        self.move()
        self.update_rules()
        self.transform()
        self.update_rules()
        self.sink()
        self.hot_and_melt()
        self.defeat()
        self.open_and_shut()
        self.update_rules()
        return self.winned()
    def show_level(self, level: levels.level, layer: int, cursor: Optional[spaces.Coord] = None) -> pygame.Surface:
        if layer <= 0:
            return displays.sprites.get("text_level").copy()
        pixel_sprite_size = displays.sprite_size * displays.pixel_size
        level_surface_size = (level.width * pixel_sprite_size, level.height * pixel_sprite_size)
        level_surface = pygame.Surface(level_surface_size, pygame.SRCALPHA)
        for i in range(len(level.object_list)):
            obj = level.object_list[i]
            if isinstance(obj, objects.Level):
                obj_level = self.get_level(obj.name, obj.inf_tier)
                if obj_level is not None:
                    obj_surface = self.show_level(obj_level, layer - 1)
                    obj_surface = displays.set_color_dark(obj_surface, pygame.Color("#CCCCCC"))
                else:
                    obj_surface = displays.sprites.get("level").copy()
            elif isinstance(obj, objects.Clone):
                obj_level = self.get_level(obj.name, obj.inf_tier)
                if obj_level is not None:
                    obj_surface = self.show_level(obj_level, layer - 1)
                    obj_surface = displays.set_color_light(obj_surface, pygame.Color("#444444"))
                else:
                    obj_surface = displays.sprites.get("clone").copy()
            else:
                obj_surface = displays.sprites.get(obj.sprite_name).copy()
            pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
            level_surface.blit(pygame.transform.scale(obj_surface, (pixel_sprite_size, pixel_sprite_size)), pos)
        if cursor is not None:
            obj_surface = displays.sprites.get("cursor").copy()
            pos = (cursor[0] * pixel_sprite_size, cursor[1] * pixel_sprite_size)
            level_surface.blit(pygame.transform.scale(obj_surface, (pixel_sprite_size, pixel_sprite_size)), pos)
        level_background = pygame.Surface(level_surface.get_size(), pygame.SRCALPHA)
        level_background.fill(pygame.Color(level.color))
        level_background.blit(level_surface, (0, 0))
        level_surface = level_background
        return level_surface
    def to_json(self) -> basics.JsonObject:
        json_object = {"name": self.name, "level_list": [], "rule_list": []}
        for level in self.level_list:
            json_object["level_list"].append(level.to_json())
        for rule in self.rule_list:
            json_object["rule_list"].append([])
            for obj in rule:
                json_object["rule_list"][-1].append({v: k for k, v in objects.object_name.items()}[obj])
        return json_object

def json_to_world(json_object: basics.JsonObject) -> world: # oh hell no * 3
    level_list = []
    for level in json_object["level_list"]: # type: ignore
        level_list.append(levels.json_to_level(level))
    rule_list = []
    for rule in json_object["rule_list"]: # type: ignore
        rule_list.append([])
        for obj_type in rule:
            rule_list[-1].append(objects.object_name[obj_type])
    return world(name=json_object["name"], # type: ignore
                 level_list=level_list, # type: ignore
                 rule_list=rule_list) # type: ignore