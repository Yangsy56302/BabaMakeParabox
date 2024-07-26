from typing import Any, Optional
import math
import uuid

from BabaMakeParabox import colors, spaces

class Object(object):
    typename: str = "Object"
    sprite_name: str
    def __init__(self, pos: spaces.Coord, orient: spaces.Orient = spaces.Orient.S) -> None:
        self.uuid: uuid.UUID = uuid.uuid4()
        self.x: int = pos[0]
        self.y: int = pos[1]
        self.orient: spaces.Orient = orient
        self.properties: list[tuple[type["Text"], int]] = []
        self.has_object: list[type["Noun"]] = []
        self.make_object: list[type["Noun"]] = []
        self.write_text: list[type["Noun"] | type["Property"]] = []
        self.moved: bool = False
        self.sprite_state: int = 0
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    @property
    def pos(self) -> spaces.Coord:
        return (self.x, self.y)
    @pos.getter
    def pos(self) -> spaces.Coord:
        return (self.x, self.y)
    @pos.setter
    def pos(self, new_pos: spaces.Coord) -> None:
        self.x, self.y = new_pos
    @pos.deleter
    def pos(self) -> None:
        del self.x
        del self.y
    def reset_uuid(self) -> None:
        self.uuid = uuid.uuid4()
    def set_sprite(self) -> None:
        self.sprite_state = 0
    def new_prop(self, prop: type["Text"], negated_count: int = 0) -> None:
        del_props = []
        for old_prop, old_negated_count in self.properties:
            if prop == old_prop:
                if old_negated_count > negated_count:
                    return
                del_props.append((old_prop, old_negated_count))
        for old_prop, old_negated_count in del_props:
            self.properties.remove((old_prop, old_negated_count))
        self.properties.append((prop, negated_count))
    def del_prop(self, prop: type["Text"], negated_count: int = 0) -> None:
        if (prop, negated_count) in self.properties:
            self.properties.remove((prop, negated_count))
    def has_prop(self, prop: type["Text"], negate: bool = False) -> bool:
        for get_prop, get_negated_count in self.properties:
            if get_prop == prop and get_negated_count % 2 == int(negate):
                return True
        return False
    def clear_prop(self) -> None:
        self.properties = []
    def to_json(self) -> dict[str, Any]:
        return {"type": self.typename, "position": [self.x, self.y], "orientation": spaces.orient_to_str(self.orient)}

class Static(Object):
    typename: str = "Static"
    def set_sprite(self) -> None:
        self.sprite_state = 0
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Tiled(Object):
    typename: str = "Tiled"
    def set_sprite(self, connected: dict[spaces.Orient, bool]) -> None:
        self.sprite_state = (connected[spaces.Orient.D] * 0x1) | (connected[spaces.Orient.W] * 0x2) | (connected[spaces.Orient.A] * 0x4) | (connected[spaces.Orient.S] * 0x8)
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Animated(Object):
    typename: str = "Animated"
    def set_sprite(self, round_num: int) -> None:
        self.sprite_state = round_num % 4
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Directional(Object):
    typename: str = "Directional"
    def set_sprite(self) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class AnimatedDirectional(Object):
    typename: str = "AnimatedDirectional"
    def set_sprite(self, round_num: int) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | round_num % 4
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Character(Object):
    typename: str = "Character"
    def set_sprite(self) -> None:
        self.sleeping = False
        if not self.sleeping:
            if self.moved:
                temp_state = (self.sprite_state & 0x3) + 1 if (self.sprite_state & 0x3) != 0x3 else 0x0
                self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | temp_state
            else:
                self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | (self.sprite_state & 0x3)
        else:
            self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | 0x7
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Baba(Character):
    typename: str = "Baba"
    sprite_name: str = "baba"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Keke(Character):
    typename: str = "Keke"
    sprite_name: str = "keke"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Me(Character):
    typename: str = "Me"
    sprite_name: str = "me"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Patrick(Directional):
    typename: str = "Patrick"
    sprite_name: str = "patrick"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Skull(Directional):
    typename: str = "Skull"
    sprite_name: str = "skull"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Ghost(Directional):
    typename: str = "Ghost"
    sprite_name: str = "ghost"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Wall(Tiled):
    typename: str = "Wall"
    sprite_name: str = "wall"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Hedge(Tiled):
    typename: str = "Hedge"
    sprite_name: str = "hedge"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Ice(Tiled):
    typename: str = "Ice"
    sprite_name: str = "ice"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Tile(Static):
    typename: str = "Tile"
    sprite_name: str = "tile"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Grass(Tiled):
    typename: str = "Grass"
    sprite_name: str = "grass"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Water(Tiled):
    typename: str = "Water"
    sprite_name: str = "water"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Lava(Tiled):
    typename: str = "Lava"
    sprite_name: str = "lava"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Door(Static):
    typename: str = "Door"
    sprite_name: str = "door"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Key(Static):
    typename: str = "Key"
    sprite_name: str = "key"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Box(Static):
    typename: str = "Box"
    sprite_name: str = "box"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Rock(Static):
    typename: str = "Rock"
    sprite_name: str = "rock"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Fruit(Static):
    typename: str = "Fruit"
    sprite_name: str = "fruit"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Belt(AnimatedDirectional):
    typename: str = "Belt"
    sprite_name: str = "belt"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Sun(Static):
    typename: str = "Sun"
    sprite_name: str = "sun"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Moon(Static):
    typename: str = "Moon"
    sprite_name: str = "moon"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Star(Static):
    typename: str = "Star"
    sprite_name: str = "star"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class What(Static):
    typename: str = "What"
    sprite_name: str = "what"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Love(Static):
    typename: str = "Love"
    sprite_name: str = "love"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Flag(Static):
    typename: str = "Flag"
    sprite_name: str = "flag"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Cursor(Static):
    typename: str = "Cursor"
    sprite_name: str = "cursor"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Empty(Object):
    typename: str = "Empty"
    sprite_name: str = "empty"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Level(Object):
    typename: str = "Level"
    sprite_name: str = "level"
    def __init__(self, pos: spaces.Coord, name: str, icon_name: str = "empty", icon_color: colors.ColorHex = colors.WHITE, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.name: str = name
        self.icon_name: str = icon_name
        self.icon_color: colors.ColorHex = icon_color
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def to_json(self) -> dict[str, Any]:
        json_object = super().to_json()
        json_object.update({"level": {"name": self.name}})
        json_object.update({"icon": {"name": self.icon_name, "color": self.icon_color}})
        return json_object

class WorldPointer(Object):
    typename: str = "WorldContainer"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.name: str = name
        self.inf_tier: int = inf_tier
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def to_json(self) -> dict[str, Any]:
        json_object = super().to_json()
        json_object.update({"world": {"name": self.name, "infinite_tier": self.inf_tier}})
        return json_object

class World(WorldPointer):
    typename: str = "World"
    sprite_name: str = "world"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, name, inf_tier, orient)
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
        
class Clone(WorldPointer):
    typename: str = "Clone"
    sprite_name: str = "clone"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, name, inf_tier, orient)
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Transform(Object):
    typename: str = "Transform"
    def __init__(self, pos: spaces.Coord, info: dict[str, Any], orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.from_type: type[Object] = info["from"]["type"]
        self.from_name: str = info["from"]["name"]
        if issubclass(self.from_type, WorldPointer):
            self.from_inf_tier: int = info["from"]["inf_tier"]
        self.to_type: type[Object] = info["to"]["type"]
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Sprite(Object):
    typename: str = "Sprite"
    def __init__(self, pos: spaces.Coord, sprite_name: str, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.sprite_name: str = sprite_name
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def to_json(self) -> dict[str, Any]:
        json_object = super().to_json()
        json_object.update({"sprite": {"name": self.sprite_name}})
        return json_object

class Game(Object):
    typename: str = "Game"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Text(Object):
    typename: str = "Text"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Noun(Text):
    typename: str = "Noun"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Prefix(Text):
    typename: str = "Prefix"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Infix(Text):
    typename: str = "Infix"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Operator(Text):
    typename: str = "Operator"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class Property(Text):
    typename: str = "Property"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class BABA(Noun):
    typename: str = "BABA"
    sprite_name: str = "text_baba"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class KEKE(Noun):
    typename: str = "KEKE"
    sprite_name: str = "text_keke"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class ME(Noun):
    typename: str = "ME"
    sprite_name: str = "text_me"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class PATRICK(Noun):
    typename: str = "PATRICK"
    sprite_name: str = "text_patrick"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class SKULL(Noun):
    typename: str = "SKULL"
    sprite_name: str = "text_skull"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class GHOST(Noun):
    typename: str = "GHOST"
    sprite_name: str = "text_ghost"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class WALL(Noun):
    typename: str = "WALL"
    sprite_name: str = "text_wall"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class HEDGE(Noun):
    typename: str = "HEDGE"
    sprite_name: str = "text_hedge"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class ICE(Noun):
    typename: str = "ICE"
    sprite_name: str = "text_ice"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class TILE(Noun):
    typename: str = "TILE"
    sprite_name: str = "text_tile"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class GRASS(Noun):
    typename: str = "GRASS"
    sprite_name: str = "text_grass"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class WATER(Noun):
    typename: str = "WATER"
    sprite_name: str = "text_water"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class LAVA(Noun):
    typename: str = "LAVA"
    sprite_name: str = "text_lava"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class DOOR(Noun):
    typename: str = "DOOR"
    sprite_name: str = "text_door"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class KEY(Noun):
    typename: str = "KEY"
    sprite_name: str = "text_key"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class BOX(Noun):
    typename: str = "BOX"
    sprite_name: str = "text_box"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class ROCK(Noun):
    typename: str = "ROCK"
    sprite_name: str = "text_rock"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class FRUIT(Noun):
    typename: str = "FRUIT"
    sprite_name: str = "text_fruit"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class BELT(Noun):
    typename: str = "BELT"
    sprite_name: str = "text_belt"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class SUN(Noun):
    typename: str = "SUN"
    sprite_name: str = "text_sun"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class MOON(Noun):
    typename: str = "MOON"
    sprite_name: str = "text_moon"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class STAR(Noun):
    typename: str = "STAR"
    sprite_name: str = "text_star"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class WHAT(Noun):
    typename: str = "WHAT"
    sprite_name: str = "text_what"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class LOVE(Noun):
    typename: str = "LOVE"
    sprite_name: str = "text_love"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class FLAG(Noun):
    typename: str = "FLAG"
    sprite_name: str = "text_flag"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class CURSOR(Noun):
    typename: str = "CURSOR"
    sprite_name: str = "text_cursor"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class ALL(Noun):
    typename: str = "ALL"
    sprite_name: str = "text_all"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class EMPTY(Noun):
    typename: str = "EMPTY"
    sprite_name: str = "text_empty"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class TEXT(Noun):
    typename: str = "TEXT"
    sprite_name: str = "text_text"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class LEVEL(Noun):
    typename: str = "LEVEL"
    sprite_name: str = "text_level"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class WORLD(Noun):
    typename: str = "WORLD"
    sprite_name: str = "text_world"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class CLONE(Noun):
    typename: str = "CLONE"
    sprite_name: str = "text_clone"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class GAME(Noun):
    typename: str = "GAME"
    sprite_name: str = "text_game"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class META(Prefix):
    typename: str = "META"
    sprite_name: str = "text_meta"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class ON(Infix):
    typename: str = "ON"
    sprite_name: str = "text_on"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class NEAR(Infix):
    typename: str = "NEAR"
    sprite_name: str = "text_near"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class NEXTTO(Infix):
    typename: str = "NEXTTO"
    sprite_name: str = "text_nextto"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class FEELING(Infix):
    typename: str = "FEELING"
    sprite_name: str = "text_feeling"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class IS(Operator):
    typename: str = "IS"
    sprite_name: str = "text_is"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class HAS(Operator):
    typename: str = "HAS"
    sprite_name: str = "text_has"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class MAKE(Operator):
    typename: str = "MAKE"
    sprite_name: str = "text_make"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class WRITE(Operator):
    typename: str = "WRITE"
    sprite_name: str = "text_write"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class NOT(Text):
    typename: str = "NOT"
    sprite_name: str = "text_not"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class AND(Text):
    typename: str = "AND"
    sprite_name: str = "text_and"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class YOU(Property):
    typename: str = "YOU"
    sprite_name: str = "text_you"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class MOVE(Property):
    typename: str = "MOVE"
    sprite_name: str = "text_move"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class STOP(Property):
    typename: str = "STOP"
    sprite_name: str = "text_stop"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class PUSH(Property):
    typename: str = "PUSH"
    sprite_name: str = "text_push"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class SINK(Property):
    typename: str = "SINK"
    sprite_name: str = "text_sink"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class FLOAT(Property):
    typename: str = "FLOAT"
    sprite_name: str = "text_float"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class OPEN(Property):
    typename: str = "OPEN"
    sprite_name: str = "text_open"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class SHUT(Property):
    typename: str = "SHUT"
    sprite_name: str = "text_shut"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class HOT(Property):
    typename: str = "HOT"
    sprite_name: str = "text_hot"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class MELT(Property):
    typename: str = "MELT"
    sprite_name: str = "text_melt"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class WIN(Property):
    typename: str = "WIN"
    sprite_name: str = "text_win"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class DEFEAT(Property):
    typename: str = "DEFEAT"
    sprite_name: str = "text_defeat"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class SHIFT(Property):
    typename: str = "SHIFT"
    sprite_name: str = "text_shift"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class TELE(Property):
    typename: str = "TELE"
    sprite_name: str = "text_tele"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class WORD(Property):
    typename: str = "WORD"
    sprite_name: str = "text_word"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class SELECT(Property):
    typename: str = "SELECT"
    sprite_name: str = "text_select"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class END(Property):
    typename: str = "END"
    sprite_name: str = "text_end"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

class DONE(Property):
    typename: str = "DONE"
    sprite_name: str = "text_done"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid

def json_to_object(json_object: dict[str, Any]) -> Object: # oh hell no
    typename: str = json_object["type"] # type: ignore
    object_type: type[Object] = object_name[typename]
    if issubclass(object_type, WorldPointer):
        if json_object.get("world") is not None:
            return object_type(pos=tuple(json_object["position"]), # type: ignore
                            name=json_object["world"]["name"], # type: ignore
                            inf_tier=json_object["world"]["infinite_tier"], # type: ignore
                            orient=spaces.str_to_orient(json_object["orientation"])) # type: ignore
        else:
            return object_type(pos=tuple(json_object["position"]), # type: ignore
                            name=json_object["level"]["name"], # type: ignore
                            inf_tier=json_object["level"]["infinite_tier"], # type: ignore
                            orient=spaces.str_to_orient(json_object["orientation"])) # type: ignore
    elif object_type == Level:
        if json_object.get("icon") is not None:
            if isinstance(json_object["icon"]["color"], int):
                return object_type(pos=tuple(json_object["position"]), # type: ignore
                                   name=json_object["level"]["name"], # type: ignore
                                   icon_name=json_object["icon"]["name"], # type: ignore
                                   icon_color=json_object["icon"]["color"], # type: ignore
                                   orient=spaces.str_to_orient(json_object["orientation"])) # type: ignore
            else:
                return object_type(pos=tuple(json_object["position"]), # type: ignore
                                   name=json_object["level"]["name"], # type: ignore
                                   icon_name=json_object["icon"]["name"], # type: ignore
                                   icon_color=colors.rgb_to_hex(*json_object["icon"]["color"]), # type: ignore
                                   orient=spaces.str_to_orient(json_object["orientation"])) # type: ignore
        else:
            return object_type(pos=tuple(json_object["position"]), # type: ignore
                               name=json_object["level"]["name"], # type: ignore
                               orient=spaces.str_to_orient(json_object["orientation"])) # type: ignore
    elif issubclass(object_type, Sprite):
        return object_type(pos=tuple(json_object["position"]), # type: ignore
                           orient=spaces.str_to_orient(json_object["orientation"]),
                           sprite_name=json_object["sprite"]["name"]) # type: ignore
    else:
        return object_type(pos=tuple(json_object["position"]), # type: ignore
                           orient=spaces.str_to_orient(json_object["orientation"])) # type: ignore

object_name: dict[str, type[Object]] = {}
object_name["Baba"] = Baba
object_name["Keke"] = Keke
object_name["Me"] = Me
object_name["Patrick"] = Patrick
object_name["Skull"] = Skull
object_name["Ghost"] = Ghost
object_name["Wall"] = Wall
object_name["Hedge"] = Hedge
object_name["Ice"] = Ice
object_name["Tile"] = Tile
object_name["Grass"] = Grass
object_name["Water"] = Water
object_name["Lava"] = Lava
object_name["Box"] = Box
object_name["Rock"] = Rock
object_name["Fruit"] = Fruit
object_name["Belt"] = Belt
object_name["Sun"] = Sun
object_name["Moon"] = Moon
object_name["Star"] = Star
object_name["What"] = What
object_name["Love"] = Love
object_name["Flag"] = Flag
object_name["Cursor"] = Cursor
object_name["Empty"] = Empty
object_name["Level"] = Level
object_name["World"] = World
object_name["Clone"] = Clone
object_name["BABA"] = BABA
object_name["KEKE"] = KEKE
object_name["ME"] = ME
object_name["PATRICK"] = PATRICK
object_name["SKULL"] = SKULL
object_name["GHOST"] = GHOST
object_name["WALL"] = WALL
object_name["HEDGE"] = HEDGE
object_name["ICE"] = ICE
object_name["TILE"] = TILE
object_name["GRASS"] = GRASS
object_name["WATER"] = WATER
object_name["LAVA"] = LAVA
object_name["BOX"] = BOX
object_name["ROCK"] = ROCK
object_name["FRUIT"] = FRUIT
object_name["BELT"] = BELT
object_name["SUN"] = SUN
object_name["MOON"] = MOON
object_name["STAR"] = STAR
object_name["WHAT"] = WHAT
object_name["LOVE"] = LOVE
object_name["FLAG"] = FLAG
object_name["CURSOR"] = CURSOR
object_name["ALL"] = ALL
object_name["EMPTY"] = EMPTY
object_name["TEXT"] = TEXT
object_name["LEVEL"] = LEVEL
object_name["WORLD"] = WORLD
object_name["CLONE"] = CLONE
object_name["GAME"] = GAME
object_name["META"] = META
object_name["ON"] = ON
object_name["NEAR"] = NEAR
object_name["NEXTTO"] = NEXTTO
object_name["FEELING"] = FEELING
object_name["IS"] = IS
object_name["HAS"] = HAS
object_name["MAKE"] = MAKE
object_name["WRITE"] = WRITE
object_name["NOT"] = NOT
object_name["AND"] = AND
object_name["YOU"] = YOU
object_name["MOVE"] = MOVE
object_name["STOP"] = STOP
object_name["PUSH"] = PUSH
object_name["SINK"] = SINK
object_name["FLOAT"] = FLOAT
object_name["OPEN"] = OPEN
object_name["SHUT"] = SHUT
object_name["HOT"] = HOT
object_name["MELT"] = MELT
object_name["WIN"] = WIN
object_name["DEFEAT"] = DEFEAT
object_name["SHIFT"] = SHIFT
object_name["TELE"] = TELE
object_name["WORD"] = WORD
object_name["SELECT"] = SELECT
object_name["END"] = END
object_name["DONE"] = DONE

class ObjectNounDict(object):
    def __init__(self, pairs: Optional[dict[type[Object], type[Noun]]] = None) -> None:
        self.pairs: dict[type[Object], type[Noun]] = pairs if pairs is not None else {}
    def __getitem__(self, obj: type[Object]) -> type[Noun]:
        for k, v in self.pairs.items():
            if issubclass(obj, k):
                return v
        raise KeyError(obj)
    def __setitem__(self, obj: type[Object], noun: type[Noun]) -> None:
        self.pairs[obj] = noun
    def __delitem__(self, obj: type[Object]) -> None:
        for k in self.pairs.keys():
            if issubclass(obj, k):
                del self.pairs[k]
    def get(self, obj: type[Object]) -> Optional[type[Noun]]:
        for k, v in self.pairs.items():
            if issubclass(obj, k):
                return v
        return None

class NounObjectDict(object):
    def __init__(self, pairs: Optional[dict[type[Noun], type[Object]]] = None) -> None:
        self.pairs: dict[type[Noun], type[Object]] = pairs if pairs is not None else {}
    def __getitem__(self, noun: type[Noun]) -> type[Object]:
        for k, v in self.pairs.items():
            if issubclass(noun, k):
                return v
        raise KeyError(noun)
    def __setitem__(self, noun: type[Noun], obj: type[Object]) -> None:
        self.pairs[noun] = obj
    def __delitem__(self, noun: type[Noun]) -> None:
        for k in self.pairs.keys():
            if issubclass(noun, k):
                del self.pairs[k]
    def get(self, noun: type[Noun]) -> Optional[type[Object]]:
        for k, v in self.pairs.items():
            if issubclass(noun, k):
                return v
        return None
    def swapped(self) -> ObjectNounDict:
        return ObjectNounDict({v: k for k, v in self.pairs.items()})

nouns_objs_dicts = NounObjectDict()
nouns_objs_dicts[BABA] = Baba
nouns_objs_dicts[KEKE] = Keke
nouns_objs_dicts[ME] = Me
nouns_objs_dicts[PATRICK] = Patrick
nouns_objs_dicts[SKULL] = Skull
nouns_objs_dicts[GHOST] = Ghost
nouns_objs_dicts[WALL] = Wall
nouns_objs_dicts[HEDGE] = Hedge
nouns_objs_dicts[ICE] = Ice
nouns_objs_dicts[TILE] = Tile
nouns_objs_dicts[GRASS] = Grass
nouns_objs_dicts[WATER] = Water
nouns_objs_dicts[LAVA] = Lava
nouns_objs_dicts[DOOR] = Door
nouns_objs_dicts[KEY] = Key
nouns_objs_dicts[BOX] = Box
nouns_objs_dicts[ROCK] = Rock
nouns_objs_dicts[FRUIT] = Fruit
nouns_objs_dicts[BELT] = Belt
nouns_objs_dicts[SUN] = Sun
nouns_objs_dicts[MOON] = Moon
nouns_objs_dicts[STAR] = Star
nouns_objs_dicts[WHAT] = What
nouns_objs_dicts[LOVE] = Love
nouns_objs_dicts[FLAG] = Flag
nouns_objs_dicts[CURSOR] = Cursor
nouns_objs_dicts[EMPTY] = Empty
nouns_objs_dicts[LEVEL] = Level
nouns_objs_dicts[WORLD] = World
nouns_objs_dicts[CLONE] = Clone
nouns_objs_dicts[TEXT] = Text
nouns_objs_dicts[GAME] = Game

not_in_all: tuple[type[Object], ...] = (Text, Empty, Level, WorldPointer, Transform, Sprite, Game)
in_not_all: tuple[type[Object], ...] = (Text, Empty, Transform, Sprite, Game)
not_in_editor: tuple[type[Object], ...] = (Empty, EMPTY, Text, Transform, Sprite, Game)