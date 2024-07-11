from typing import Any, Optional
import random
import pygame

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces
import baba_make_parabox.objects as objects
import baba_make_parabox.rules as rules
import baba_make_parabox.worlds as worlds
import baba_make_parabox.displays as displays

class level(object):
    class_name: str = "level"
    def __init__(self, name: str, world_list: list[worlds.world], super_level: Optional[str] = None, main_world_name: Optional[str] = None, main_world_tier: Optional[int] = None, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name
        self.world_list: list[worlds.world] = list(world_list)
        self.super_level: Optional[str] = super_level
        self.main_world_name: str = main_world_name if main_world_name is not None else world_list[0].name
        self.main_world_tier: int = main_world_tier if main_world_tier is not None else world_list[0].inf_tier
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
    def get_world(self, name: str, inf_tier: int) -> Optional[worlds.world]:
        world = list(filter(lambda l: l.name == name and l.inf_tier == inf_tier, self.world_list))
        return world[0] if len(world) != 0 else None
    def get_exist_world(self, name: str, inf_tier: int) -> worlds.world:
        world = list(filter(lambda l: l.name == name and l.inf_tier == inf_tier, self.world_list))
        return world[0]
    def find_super_world(self, name: str, inf_tier: int) -> Optional[tuple[worlds.world, objects.Object]]:
        for super_world in self.world_list:
            for obj in super_world.get_worlds():
                if name == obj.name and inf_tier == obj.inf_tier:
                    return (super_world, obj)
        return None
    def update_rules_with_word(self) -> None:
        for world in self.world_list:
            world.update_rules_with_word()
        for world in self.world_list:
            for prop in objects.object_name.values():
                if issubclass(prop, objects.Property):
                    prop_rules = world.find_rules(objects.Noun, objects.IS, prop) + self.find_rules(objects.Noun, objects.IS, prop)
                    for obj_type in [t[0] for t in prop_rules]:
                        for obj in world.get_objs_from_type(objects.nouns_objs_dicts.get_obj(obj_type)): # type: ignore
                            obj: objects.Object
                            obj.new_prop(prop)
    def update_rules(self) -> None:
        for world in self.world_list:
            for obj in world.object_list:
                obj.clear_prop()
            world.update_rules()
        for world in self.world_list:
            for prop in objects.object_name.values():
                if issubclass(prop, objects.Property):
                    prop_rules = world.find_rules(objects.Noun, objects.IS, prop) + self.find_rules(objects.Noun, objects.IS, prop)
                    for obj_type in [t[0] for t in prop_rules]:
                        for obj in world.get_objs_from_type(objects.nouns_objs_dicts.get_obj(obj_type)): # type: ignore
                            obj: objects.Object
                            obj.new_prop(prop)
        self.update_rules_with_word()
    def get_move_list(self, world: worlds.world, obj: objects.Object, pos: spaces.Coord, facing: spaces.Orient, passed: Optional[list[worlds.world]] = None, depth: int = 1) -> Optional[list[tuple[objects.Object, worlds.world, spaces.Coord, spaces.Orient]]]:
        if depth > 127:
            return None
        depth += 1
        passed = passed[:] if passed is not None else []
        new_pos = spaces.pos_facing(pos, facing)
        simple_push = True
        # push out
        move_list = []
        if world.out_of_range(new_pos):
            # inf out
            if world in passed:
                ret = self.find_super_world(world.name, world.inf_tier + 1)
                if ret is None:
                    return None
                super_world, world_obj = ret
                get_move_list = self.get_move_list(super_world, obj, world_obj.pos, facing, passed, depth)
                if get_move_list is None:
                    return None
                move_list.extend(get_move_list)
            else:
                ret = self.find_super_world(world.name, world.inf_tier)
                if ret is None:
                    return None
                super_world, world_obj = ret
                passed.append(world)
                get_move_list = self.get_move_list(super_world, obj, world_obj.pos, facing, passed, depth)
                if get_move_list is None:
                    return None
                move_list.extend(get_move_list)
            simple_push = False
        # stop wall & shut door
        stop_objects = list(filter(lambda o: objects.Object.has_prop(o, objects.STOP), world.get_objs_from_pos(new_pos)))
        if len(stop_objects) != 0:
            if obj.has_prop(objects.OPEN):
                for stop_object in stop_objects:
                    if stop_object.has_prop(objects.SHUT):
                        return None
                return [(obj, world, new_pos, facing)]
            for stop_object in stop_objects:
                if not stop_object.has_prop(objects.PUSH):
                    return None
        # push box
        push_objects = list(filter(lambda o: objects.Object.has_prop(o, objects.PUSH), world.get_objs_from_pos(new_pos)))
        if len(push_objects) != 0:
            for push_object in push_objects:
                new_move_list = self.get_move_list(world, push_object, push_object.pos, facing, depth=depth)
                if new_move_list is None:
                    if not isinstance(push_object, objects.WorldPointer):
                        return None
                else:
                    move_list.extend(new_move_list)
            move_list.append((obj, world, new_pos, facing))
            simple_push = False
        # level
        world_objects = world.get_worlds_from_pos(new_pos)
        clone_objects = world.get_clones_from_pos(new_pos)
        world_like_objects = world_objects + clone_objects
        if len(world_like_objects) != 0:
            for world_like_object in world_like_objects:
                if world_like_object in [t[0] for t in move_list]:
                    continue
                sub_world = self.get_world(world_like_object.name, world_like_object.inf_tier)
                if sub_world is None:
                    return None
                # inf in
                elif sub_world in passed:
                    sub_sub_world = self.get_world(sub_world.name, sub_world.inf_tier - 1)
                    if sub_sub_world is None:
                        return None
                    input_pos = sub_sub_world.default_input_position(spaces.swap_orientation(facing))
                    passed.append(world)
                    new_move_list = self.get_move_list(sub_sub_world, obj, input_pos, facing, passed, depth)
                # push in
                else:
                    input_pos = sub_world.default_input_position(spaces.swap_orientation(facing))
                    passed.append(world)
                    new_move_list = self.get_move_list(sub_world, obj, input_pos, facing, passed, depth)
                if new_move_list is None:
                    return None
                move_list.extend(new_move_list)
            simple_push = False
        move_list = basics.remove_same_elements(move_list)
        return [(obj, world, new_pos, facing)] if simple_push else move_list
    def move_objs_from_move_list(self, move_list: list[tuple[objects.Object, worlds.world, spaces.Coord, spaces.Orient]]) -> None:
        move_list = basics.remove_same_elements(move_list)
        for move_obj, new_world, new_pos, new_facing in move_list:
            move_obj.moved = True
            for world in self.world_list:
                if world.get_obj(move_obj.uuid) is not None:
                    old_world = world
            if old_world == new_world:
                move_obj.pos = new_pos
                move_obj.facing = new_facing
            else:
                old_world.del_obj(move_obj.uuid)
                move_obj.pos = new_pos
                move_obj.facing = new_facing
                new_world.new_obj(move_obj)
    def you(self, facing: spaces.PlayerOperation) -> None:
        if facing == spaces.O:
            return
        move_list = []
        for world in self.world_list:
            you_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), world.object_list)
            for obj in you_objs:
                new_move_list = self.get_move_list(world, obj, obj.pos, facing) # type: ignore
                if new_move_list is not None:
                    move_list.extend(new_move_list)
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
    def select(self, facing: spaces.PlayerOperation) -> Optional[str]:
        if facing == spaces.O:
            for world in self.world_list:
                select_objs = filter(lambda o: objects.Object.has_prop(o, objects.SELECT), world.object_list)
                levels: list[objects.Level] = []
                for obj in select_objs:
                    levels.extend(world.get_levels_from_pos(obj.pos))
                    if len(levels) != 0:
                        return levels[0].name
        else:
            for world in self.world_list:
                select_objs = filter(lambda o: objects.Object.has_prop(o, objects.SELECT), world.object_list)
                for obj in select_objs:
                    new_pos = spaces.pos_facing(obj.pos, facing) # type: ignore
                    if not world.out_of_range(new_pos):
                        obj.pos = new_pos
            return None
    def move(self) -> None:
        move_list = []
        for world in self.world_list:
            move_objs = filter(lambda o: objects.Object.has_prop(o, objects.MOVE), world.object_list)
            for obj in move_objs:
                new_move_list = self.get_move_list(world, obj, obj.pos, obj.facing)
                if new_move_list is not None:
                    move_list.extend(new_move_list)
                else:
                    new_move_list = self.get_move_list(world, obj, obj.pos, spaces.swap_orientation(obj.facing))
                    if new_move_list is not None:
                        move_list.extend(new_move_list)
                    else:
                        move_list.append((obj, world, obj.pos, spaces.swap_orientation(obj.facing)))
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
    def shift(self) -> None:
        move_list = []
        for world in self.world_list:
            shift_objs = filter(lambda o: objects.Object.has_prop(o, objects.SHIFT), world.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), world.object_list)
            for shift_obj in shift_objs:
                for obj in world.get_objs_from_pos(shift_obj.pos):
                    if shift_obj != obj:
                        if not ((shift_obj in float_objs) ^ (obj in float_objs)):
                            new_move_list = self.get_move_list(world, obj, obj.pos, shift_obj.facing)
                            if new_move_list is not None:
                                move_list.extend(new_move_list)
        move_list = basics.remove_same_elements(move_list)
        self.move_objs_from_move_list(move_list)
    def tele(self) -> None:
        tele_list: list[tuple[objects.Object, spaces.Coord]] = []
        object_list = []
        for world in self.world_list:
            object_list.extend(world.object_list)
        tele_objs = filter(lambda o: objects.Object.has_prop(o, objects.TELE), object_list)
        float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), object_list)
        for tele_obj in tele_objs:
            other_tele_objs = list(filter(lambda o: objects.Object.has_prop(o, objects.TELE) and isinstance(o, type(tele_obj)) and o != tele_obj, object_list))
            if len(other_tele_objs) <= 1:
                continue
            for obj in world.get_objs_from_pos(tele_obj.pos):
                if tele_obj != obj:
                    if not ((tele_obj in float_objs) ^ (obj in float_objs)):
                        other_tele_obj = random.choice(other_tele_objs)
                        tele_list.append((obj, other_tele_obj.pos))
        for obj, pos in tele_list:
            obj.pos = pos
    def sink(self) -> None:
        for world in self.world_list:
            sink_objs = filter(lambda o: objects.Object.has_prop(o, objects.SINK), world.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), world.object_list)
            delete_list = []
            for sink_obj in sink_objs:
                for obj in world.object_list:
                    if obj == sink_obj:
                        continue
                    if obj.pos == sink_obj.pos:
                        if not ((obj in float_objs) ^ (sink_obj in float_objs)):
                            if obj.uuid not in delete_list and sink_obj.uuid not in delete_list:
                                delete_list.append(obj.uuid)
                                delete_list.append(sink_obj.uuid)
                                break
            for uuid in delete_list:
                world.del_obj(uuid)
    def hot_and_melt(self) -> None:
        for world in self.world_list:
            hot_objs = filter(lambda o: objects.Object.has_prop(o, objects.HOT), world.object_list)
            melt_objs = filter(lambda o: objects.Object.has_prop(o, objects.MELT), world.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), world.object_list)
            for hot_obj in hot_objs:
                for melt_obj in melt_objs:
                    if melt_obj.pos == hot_obj.pos:
                        if not ((melt_obj in float_objs) ^ (hot_obj in float_objs)):
                            world.del_obj(melt_obj.uuid)
    def defeat(self) -> None:
        for world in self.world_list:
            you_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), world.object_list)
            defeat_objs = filter(lambda o: objects.Object.has_prop(o, objects.DEFEAT), world.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), world.object_list)
            for defeat_obj in defeat_objs:
                for you_obj in you_objs:
                    if you_obj.pos == defeat_obj.pos:
                        if not ((you_obj in float_objs) ^ (defeat_obj in float_objs)):
                            world.del_obj(you_obj.uuid)
    def open_and_shut(self) -> None:
        for world in self.world_list:
            open_objs = filter(lambda o: objects.Object.has_prop(o, objects.OPEN), world.object_list)
            shut_objs = filter(lambda o: objects.Object.has_prop(o, objects.SHUT), world.object_list)
            delete_list = []
            for shut_obj in shut_objs:
                for open_obj in open_objs:
                    if shut_obj.pos == open_obj.pos:
                        if shut_obj.uuid not in delete_list and open_obj.uuid not in delete_list:
                            delete_list.append(shut_obj.uuid)
                            delete_list.append(open_obj.uuid)
                            break
            for uuid in delete_list:
                world.del_obj(uuid)
    def transform(self) -> tuple[list["level"], list[objects.Object]]:
        global_transform_rules = self.find_rules(objects.Noun, objects.IS, objects.Noun)
        new_levels: list[level] = []
        transform_to: list[objects.Object] = []
        for world in self.world_list:
            transform_rules = world.find_rules(objects.Noun, objects.IS, objects.Noun)
            transform_rules.extend(global_transform_rules)
            world_transform_to: list[objects.Object] = []
            clone_transform_to: list[objects.Object] = []
            for rule in transform_rules:
                old_type = objects.nouns_objs_dicts.get_obj(rule[0]) # type: ignore
                new_type = objects.nouns_objs_dicts.get_obj(rule[2]) # type: ignore
                if issubclass(old_type, objects.Level):
                    if issubclass(new_type, objects.Level):
                        continue
                    elif issubclass(new_type, objects.WorldPointer):
                        info = {"from": {"type": objects.Level, "name": self.name},
                                "to": {"type": new_type}}
                        transform_to.append(objects.Transform((0, 0), info))
                    elif issubclass(new_type, objects.Text):
                        transform_to.append(objects.nouns_objs_dicts.get_noun(old_type)((0, 0)))
                    else:
                        transform_to.append(new_type((0, 0)))
                elif issubclass(old_type, objects.World):
                    if issubclass(new_type, objects.World):
                        continue
                    elif issubclass(new_type, objects.Level):
                        new_levels.append(level(world.name, self.world_list, self.name, world.name, world.inf_tier, self.rule_list))
                        world_transform_to.append(objects.Level((0, 0), world.name))
                    elif issubclass(new_type, objects.Clone):
                        world_transform_to.append(objects.Clone((0, 0), world.name, world.inf_tier))
                    elif issubclass(new_type, objects.Text):
                        world_transform_to.append(objects.nouns_objs_dicts.get_noun(old_type)((0, 0)))
                    else:
                        world_transform_to.append(new_type((0, 0)))
                elif issubclass(old_type, objects.Clone):
                    if issubclass(new_type, objects.Clone):
                        continue
                    elif issubclass(new_type, objects.Level):
                        new_levels.append(level(world.name, self.world_list, self.name, world.name, world.inf_tier, self.rule_list))
                        clone_transform_to.append(objects.Level((0, 0), world.name))
                    elif issubclass(new_type, objects.World):
                        clone_transform_to.append(objects.World((0, 0), world.name, world.inf_tier))
                    elif issubclass(new_type, objects.Text):
                        clone_transform_to.append(objects.nouns_objs_dicts.get_noun(old_type)((0, 0)))
                    else:
                        clone_transform_to.append(new_type((0, 0)))
                for old_obj in world.get_objs_from_type(old_type): # type: ignore
                    old_obj: objects.Object # type: ignore
                    if issubclass(old_type, objects.Level):
                        old_obj: objects.Level # type: ignore
                        if issubclass(new_type, objects.Level):
                            continue
                        elif issubclass(new_type, objects.WorldPointer):
                            info = {"from": {"type": objects.Level, "name": old_obj.name},
                                    "to": {"type": new_type}}
                            new_obj = objects.Transform(old_obj.pos, info, old_obj.facing)
                            world.new_obj(new_obj)
                        elif issubclass(new_type, objects.Text):
                            new_obj = objects.nouns_objs_dicts.get_noun(old_type)(old_obj.pos, old_obj.facing)
                            world.new_obj(new_obj)
                        else:
                            new_obj = new_type(old_obj.pos, old_obj.facing)
                            world.new_obj(new_obj)
                    if isinstance(old_obj, objects.WorldPointer):
                        if old_type == new_type:
                            continue
                        elif issubclass(new_type, objects.Level):
                            info = {"from": {"type": old_type, "name": old_obj.name, "inf_tier": old_obj.inf_tier},
                                    "to": {"type": objects.Level}}
                            new_obj = objects.Transform(old_obj.pos, info, old_obj.facing)
                            world.new_obj(new_obj)
                        elif issubclass(new_type, objects.WorldPointer):
                            new_obj = new_type(old_obj.pos, old_obj.name, old_obj.inf_tier, old_obj.facing)
                            world.new_obj(new_obj)
                        elif issubclass(new_type, objects.Text):
                            new_obj = objects.nouns_objs_dicts.get_noun(old_type)(old_obj.pos, old_obj.facing)
                            world.new_obj(new_obj)
                        else:
                            new_obj = new_type(old_obj.pos, old_obj.facing)
                            world.new_obj(new_obj)
                    else:
                        if old_type == new_type:
                            continue
                        elif issubclass(new_type, objects.Level):
                            new_world = worlds.world(old_obj.uuid.hex, (1, 1), 0, pygame.Color("#000000"))
                            new_levels.append(level(old_obj.uuid.hex, [new_world], self.name, rule_list = self.rule_list))
                            new_world.new_obj(old_type((0, 0))) # type: ignore
                            new_obj = objects.Level(old_obj.pos, old_obj.uuid.hex, old_obj.facing)
                            world.new_obj(new_obj)
                        elif issubclass(new_type, objects.WorldPointer):
                            new_world = worlds.world(old_obj.uuid.hex, (1, 1), 0, pygame.Color("#000000"))
                            self.world_list.append(new_world)
                            new_world.new_obj(old_type((0, 0))) # type: ignore
                            new_obj = new_type(old_obj.pos, old_obj.uuid.hex, 0, old_obj.facing)
                            world.new_obj(new_obj)
                        elif issubclass(new_type, objects.Text) and not issubclass(old_type, objects.Text):
                            new_obj = objects.nouns_objs_dicts.get_noun(old_type)(old_obj.pos, old_obj.facing)
                            world.new_obj(new_obj)
                        else:
                            new_obj = new_type(old_obj.pos, old_obj.facing)
                            world.new_obj(new_obj)
                    world.del_obj(old_obj.uuid)
            for super_world in self.world_list:
                for world_obj in filter(lambda o: o.name == world.name and o.inf_tier == world.inf_tier, super_world.get_worlds()):
                    for transform_obj in world_transform_to:
                        transform_obj.pos = world_obj.pos
                        transform_obj.facing = world_obj.facing
                        super_world.new_obj(transform_obj)
                    if len(world_transform_to) != 0:
                        super_world.del_obj(world_obj.uuid)
                for clone_obj in filter(lambda o: o.name == world.name and o.inf_tier == world.inf_tier, super_world.get_worlds()):
                    for transform_obj in clone_transform_to:
                        transform_obj.pos = clone_obj.pos
                        transform_obj.facing = clone_obj.facing
                        super_world.new_obj(transform_obj)
                    if len(clone_transform_to) != 0:
                        super_world.del_obj(clone_obj.uuid)
        return (new_levels, transform_to)
    def winned(self) -> bool:
        for world in self.world_list:
            you_objs = filter(lambda o: objects.Object.has_prop(o, objects.YOU), world.object_list)
            win_objs = filter(lambda o: objects.Object.has_prop(o, objects.WIN), world.object_list)
            float_objs = filter(lambda o: objects.Object.has_prop(o, objects.FLOAT), world.object_list)
            for you_obj in you_objs:
                for win_obj in win_objs:
                    if you_obj.pos == win_obj.pos:
                        if not ((you_obj in float_objs) ^ (win_obj in float_objs)):
                            return True
        return False
    def round(self, op: spaces.PlayerOperation) -> dict[str, Any]:
        for world in self.world_list:
            for obj in world.object_list:
                obj.moved = False
        self.update_rules()
        self.you(op)
        self.move()
        self.update_rules()
        self.shift()
        self.update_rules()
        new_levels, transform_to = self.transform()
        self.update_rules()
        self.tele()
        selected_level = self.select(op)
        self.update_rules()
        self.sink()
        self.hot_and_melt()
        self.defeat()
        self.open_and_shut()
        self.update_rules()
        win = self.winned()
        return {"win": win, "selected_level": selected_level, "new_levels": new_levels, "transform_to": transform_to}
    def show_world(self, world: worlds.world, layer: int, frame: int, cursor: Optional[spaces.Coord] = None) -> pygame.Surface:
        if layer <= 0:
            return displays.sprites.get("text_world", 0, frame).copy()
        pixel_sprite_size = displays.sprite_size * displays.pixel_size
        world_surface_size = (world.width * pixel_sprite_size, world.height * pixel_sprite_size)
        world_surface = pygame.Surface(world_surface_size, pygame.SRCALPHA)
        obj_surface_list: list[tuple[spaces.Coord, pygame.Surface, objects.Object]] = []
        for i in range(len(world.object_list)):
            obj = world.object_list[i]
            if isinstance(obj, objects.World):
                obj_world = self.get_world(obj.name, obj.inf_tier)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, layer - 1, frame)
                    obj_surface = displays.set_color_dark(obj_surface, pygame.Color("#CCCCCC"))
                else:
                    obj_surface = displays.sprites.get("level", 0, frame).copy()
            elif isinstance(obj, objects.Clone):
                obj_world = self.get_world(obj.name, obj.inf_tier)
                if obj_world is not None:
                    obj_surface = self.show_world(obj_world, layer - 1, frame)
                    obj_surface = displays.set_color_light(obj_surface, pygame.Color("#444444"))
                else:
                    obj_surface = displays.sprites.get("clone", 0, frame).copy()
            else:
                obj_surface = displays.sprites.get(obj.sprite_name, obj.sprite_state, frame).copy()
            surface_pos = (obj.x * pixel_sprite_size, obj.y * pixel_sprite_size)
            obj_surface_list.append((surface_pos, obj_surface, obj))
        sorted_obj_surface_list = map(lambda o: list(map(lambda t: isinstance(o[2], t), displays.order)).index(True), obj_surface_list)
        sorted_obj_surface_list = map(lambda t: t[1], sorted(zip(sorted_obj_surface_list, obj_surface_list), key=lambda t: t[0]))
        for pos, surface, _ in sorted_obj_surface_list:
            world_surface.blit(pygame.transform.scale(surface, (pixel_sprite_size, pixel_sprite_size)), pos)
        if cursor is not None:
            obj_surface = displays.sprites.get("cursor", 0, frame).copy()
            pos = (cursor[0] * pixel_sprite_size, cursor[1] * pixel_sprite_size)
            world_surface.blit(pygame.transform.scale(obj_surface, (pixel_sprite_size, pixel_sprite_size)), pos)
        world_background = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA)
        world_background.fill(pygame.Color(world.color))
        world_background.blit(world_surface, (0, 0))
        world_surface = world_background
        return world_surface
    def to_json(self) -> basics.JsonObject:
        json_object = {"name": self.name, "world_list": [], "super_level": self.super_level, "main_world": {"name": self.main_world_name, "infinite_tier": self.main_world_tier}}
        for world in self.world_list:
            json_object["world_list"].append(world.to_json())
        return json_object

def json_to_level(json_object: basics.JsonObject) -> level: # oh hell no * 3
    world_list = []
    for world in json_object["world_list"]: # type: ignore
        world_list.append(worlds.json_to_world(world)) # type: ignore
    return level(name=json_object["name"], # type: ignore
                 world_list=world_list,
                 super_level=json_object["super_level"], # type: ignore
                 main_world_name=json_object["main_world"]["name"], # type: ignore
                 main_world_tier=json_object["main_world"]["infinite_tier"]) # type: ignore