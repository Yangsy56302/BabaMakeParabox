from typing import Any, Optional
import math
import uuid

from BabaMakeParabox import colors, spaces

class Object(object):
    class_name: str = "Object"
    sprite_name: str
    def __init__(self, pos: spaces.Coord, facing: spaces.Orient = spaces.S) -> None:
        self.uuid: uuid.UUID = uuid.uuid4()
        self.x: int = pos[0]
        self.y: int = pos[1]
        self.facing: spaces.Orient = facing
        self.properties: list[tuple[type["Text"], int]] = []
        self.moved: bool = False
        self.sprite_state: int = 0
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return self.class_name
    def __repr__(self) -> str:
        return self.class_name
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
            if old_prop == prop:
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
        return {"type": self.class_name, "position": [self.x, self.y], "orientation": spaces.orient_to_str(self.facing)} # type: ignore

class Static(Object):
    class_name: str = "Static"
    def set_sprite(self) -> None:
        self.sprite_state = 0
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Tiled(Object):
    class_name: str = "Tiled"
    def set_sprite(self, connected: dict[spaces.Orient, bool]) -> None:
        self.sprite_state = (connected[spaces.D] * 0x1) | (connected[spaces.W] * 0x2) | (connected[spaces.A] * 0x4) | (connected[spaces.S] * 0x8)
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Animated(Object):
    class_name: str = "Animated"
    def set_sprite(self, round_num: int) -> None:
        self.sprite_state = round_num % 4
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Directional(Object):
    class_name: str = "Directional"
    def set_sprite(self) -> None:
        self.sprite_state = int(math.log2(self.facing)) * 0x8
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class AnimatedDirectional(Object):
    class_name: str = "AnimatedDirectional"
    def set_sprite(self, round_num: int) -> None:
        self.sprite_state = int(math.log2(self.facing)) * 0x8 | round_num % 4
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Character(Object):
    class_name: str = "Character"
    def set_sprite(self) -> None:
        self.sleeping = False
        if not self.sleeping:
            if self.moved:
                temp_state = (self.sprite_state & 0x3) + 1 if (self.sprite_state & 0x3) != 0x3 else 0x0
                self.sprite_state = int(math.log2(self.facing)) * 0x8 | temp_state
            else:
                self.sprite_state = int(math.log2(self.facing)) * 0x8 | (self.sprite_state & 0x3)
        else:
            self.sprite_state = int(math.log2(self.facing)) * 0x8 | 0x7
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Baba(Character):
    class_name: str = "Baba"
    sprite_name: str = "baba"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Keke(Character):
    class_name: str = "Keke"
    sprite_name: str = "keke"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Me(Character):
    class_name: str = "Me"
    sprite_name: str = "me"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Patrick(Directional):
    class_name: str = "Patrick"
    sprite_name: str = "patrick"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Skull(Directional):
    class_name: str = "Skull"
    sprite_name: str = "skull"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Ghost(Directional):
    class_name: str = "Ghost"
    sprite_name: str = "ghost"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Wall(Tiled):
    class_name: str = "Wall"
    sprite_name: str = "wall"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Hedge(Tiled):
    class_name: str = "Hedge"
    sprite_name: str = "hedge"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Ice(Tiled):
    class_name: str = "Ice"
    sprite_name: str = "ice"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Tile(Static):
    class_name: str = "Tile"
    sprite_name: str = "tile"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Grass(Tiled):
    class_name: str = "Grass"
    sprite_name: str = "grass"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Water(Tiled):
    class_name: str = "Water"
    sprite_name: str = "water"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Lava(Tiled):
    class_name: str = "Lava"
    sprite_name: str = "lava"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Door(Static):
    class_name: str = "Door"
    sprite_name: str = "door"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Key(Static):
    class_name: str = "Key"
    sprite_name: str = "key"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Box(Static):
    class_name: str = "Box"
    sprite_name: str = "box"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Rock(Static):
    class_name: str = "Rock"
    sprite_name: str = "rock"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Fruit(Static):
    class_name: str = "Fruit"
    sprite_name: str = "fruit"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Belt(AnimatedDirectional):
    class_name: str = "Belt"
    sprite_name: str = "belt"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Sun(Static):
    class_name: str = "Sun"
    sprite_name: str = "sun"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Moon(Static):
    class_name: str = "Moon"
    sprite_name: str = "moon"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Star(Static):
    class_name: str = "Star"
    sprite_name: str = "star"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class What(Static):
    class_name: str = "What"
    sprite_name: str = "what"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Love(Static):
    class_name: str = "Love"
    sprite_name: str = "love"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Flag(Static):
    class_name: str = "Flag"
    sprite_name: str = "flag"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Cursor(Static):
    class_name: str = "Cursor"
    sprite_name: str = "cursor"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Empty(Object):
    class_name: str = "Empty"
    sprite_name: str = "empty"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Level(Object):
    class_name: str = "Level"
    sprite_name: str = "level"
    def __init__(self, pos: spaces.Coord, name: str, icon_name: str = "empty", icon_color: colors.ColorHex = colors.WHITE, facing: spaces.Orient = spaces.S) -> None:
        super().__init__(pos, facing)
        self.name: str = name
        self.icon_name: str = icon_name
        self.icon_color: colors.ColorHex = icon_color
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return " ".join([self.class_name, self.name])
    def __repr__(self) -> str:
        return " ".join([self.class_name, self.name])
    def to_json(self) -> dict[str, Any]:
        json_object = super().to_json()
        json_object.update({"level": {"name": self.name}}) # type: ignore
        json_object.update({"icon": {"name": self.icon_name, "color": self.icon_color}}) # type: ignore
        return json_object # type: ignore

class WorldPointer(Object):
    class_name: str = "WorldContainer"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, facing: spaces.Orient = spaces.S) -> None:
        super().__init__(pos, facing)
        self.name: str = name
        self.inf_tier: int = inf_tier
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def __repr__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def to_json(self) -> dict[str, Any]:
        json_object = super().to_json()
        json_object.update({"world": {"name": self.name, "infinite_tier": self.inf_tier}}) # type: ignore
        return json_object # type: ignore

class World(WorldPointer):
    class_name: str = "World"
    sprite_name: str = "world"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, facing: spaces.Orient = spaces.S) -> None:
        super().__init__(pos, name, inf_tier, facing)
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())
        
class Clone(WorldPointer):
    class_name: str = "Clone"
    sprite_name: str = "clone"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, facing: spaces.Orient = spaces.S) -> None:
        super().__init__(pos, name, inf_tier, facing)
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Transform(Object):
    class_name: str = "Transform"
    def __init__(self, pos: spaces.Coord, info: dict[str, Any], facing: spaces.Orient = spaces.S) -> None:
        super().__init__(pos, facing)
        self.from_type: type[Object] = info["from"]["type"]
        self.from_name: str = info["from"]["name"]
        if issubclass(self.from_type, WorldPointer):
            self.from_inf_tier: int = info["from"]["inf_tier"]
        self.to_type: type[Object] = info["to"]["type"]
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Sprite(Object):
    class_name: str = "Sprite"
    def __init__(self, pos: spaces.Coord, sprite_name: str, facing: spaces.Orient = spaces.S) -> None:
        super().__init__(pos, facing)
        self.sprite_name: str = sprite_name
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())
    def to_json(self) -> dict[str, Any]:
        json_object = super().to_json()
        json_object.update({"sprite": {"name": self.sprite_name}}) # type: ignore
        return json_object # type: ignore

class Game(Object):
    class_name: str = "Game"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Text(Object):
    class_name: str = "Text"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Noun(Text):
    class_name: str = "Noun"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Operator(Text):
    class_name: str = "Operator"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Property(Text):
    class_name: str = "Property"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class BABA(Noun):
    class_name: str = "BABA"
    sprite_name: str = "text_baba"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class KEKE(Noun):
    class_name: str = "KEKE"
    sprite_name: str = "text_keke"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class ME(Noun):
    class_name: str = "ME"
    sprite_name: str = "text_me"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class PATRICK(Noun):
    class_name: str = "PATRICK"
    sprite_name: str = "text_patrick"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class SKULL(Noun):
    class_name: str = "SKULL"
    sprite_name: str = "text_skull"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class GHOST(Noun):
    class_name: str = "GHOST"
    sprite_name: str = "text_ghost"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WALL(Noun):
    class_name: str = "WALL"
    sprite_name: str = "text_wall"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class HEDGE(Noun):
    class_name: str = "HEDGE"
    sprite_name: str = "text_hedge"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class ICE(Noun):
    class_name: str = "ICE"
    sprite_name: str = "text_ice"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class TILE(Noun):
    class_name: str = "TILE"
    sprite_name: str = "text_tile"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class GRASS(Noun):
    class_name: str = "GRASS"
    sprite_name: str = "text_grass"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WATER(Noun):
    class_name: str = "WATER"
    sprite_name: str = "text_water"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class LAVA(Noun):
    class_name: str = "LAVA"
    sprite_name: str = "text_lava"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class DOOR(Noun):
    class_name: str = "DOOR"
    sprite_name: str = "text_door"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class KEY(Noun):
    class_name: str = "KEY"
    sprite_name: str = "text_key"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class BOX(Noun):
    class_name: str = "BOX"
    sprite_name: str = "text_box"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class ROCK(Noun):
    class_name: str = "ROCK"
    sprite_name: str = "text_rock"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class FRUIT(Noun):
    class_name: str = "FRUIT"
    sprite_name: str = "text_fruit"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class BELT(Noun):
    class_name: str = "BELT"
    sprite_name: str = "text_belt"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class SUN(Noun):
    class_name: str = "SUN"
    sprite_name: str = "text_sun"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class MOON(Noun):
    class_name: str = "MOON"
    sprite_name: str = "text_moon"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class STAR(Noun):
    class_name: str = "STAR"
    sprite_name: str = "text_star"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WHAT(Noun):
    class_name: str = "WHAT"
    sprite_name: str = "text_what"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class LOVE(Noun):
    class_name: str = "LOVE"
    sprite_name: str = "text_love"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class FLAG(Noun):
    class_name: str = "FLAG"
    sprite_name: str = "text_flag"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class CURSOR(Noun):
    class_name: str = "CURSOR"
    sprite_name: str = "text_cursor"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class ALL(Noun):
    class_name: str = "ALL"
    sprite_name: str = "text_all"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class EMPTY(Noun):
    class_name: str = "EMPTY"
    sprite_name: str = "text_empty"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class TEXT(Noun):
    class_name: str = "TEXT"
    sprite_name: str = "text_text"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class LEVEL(Noun):
    class_name: str = "LEVEL"
    sprite_name: str = "text_level"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WORLD(Noun):
    class_name: str = "WORLD"
    sprite_name: str = "text_world"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class CLONE(Noun):
    class_name: str = "CLONE"
    sprite_name: str = "text_clone"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class GAME(Noun):
    class_name: str = "GAME"
    sprite_name: str = "text_game"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class IS(Operator):
    class_name: str = "IS"
    sprite_name: str = "text_is"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class NOT(Text):
    class_name: str = "NOT"
    sprite_name: str = "text_not"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class AND(Text):
    class_name: str = "AND"
    sprite_name: str = "text_and"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class YOU(Property):
    class_name: str = "YOU"
    sprite_name: str = "text_you"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class MOVE(Property):
    class_name: str = "MOVE"
    sprite_name: str = "text_move"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class STOP(Property):
    class_name: str = "STOP"
    sprite_name: str = "text_stop"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class PUSH(Property):
    class_name: str = "PUSH"
    sprite_name: str = "text_push"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class SINK(Property):
    class_name: str = "SINK"
    sprite_name: str = "text_sink"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class FLOAT(Property):
    class_name: str = "FLOAT"
    sprite_name: str = "text_float"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class OPEN(Property):
    class_name: str = "OPEN"
    sprite_name: str = "text_open"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class SHUT(Property):
    class_name: str = "SHUT"
    sprite_name: str = "text_shut"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class HOT(Property):
    class_name: str = "HOT"
    sprite_name: str = "text_hot"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class MELT(Property):
    class_name: str = "MELT"
    sprite_name: str = "text_melt"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WIN(Property):
    class_name: str = "WIN"
    sprite_name: str = "text_win"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class DEFEAT(Property):
    class_name: str = "DEFEAT"
    sprite_name: str = "text_defeat"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class SHIFT(Property):
    class_name: str = "SHIFT"
    sprite_name: str = "text_shift"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class TELE(Property):
    class_name: str = "TELE"
    sprite_name: str = "text_tele"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WORD(Property):
    class_name: str = "WORD"
    sprite_name: str = "text_word"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class SELECT(Property):
    class_name: str = "SELECT"
    sprite_name: str = "text_select"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class END(Property):
    class_name: str = "END"
    sprite_name: str = "text_end"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class DONE(Property):
    class_name: str = "DONE"
    sprite_name: str = "text_done"
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

def json_to_object(json_object: dict[str, Any]) -> Object: # oh hell no
    type_name: str = json_object["type"] # type: ignore
    object_type: type[Object] = object_name[type_name]
    if issubclass(object_type, WorldPointer):
        if json_object.get("world") is not None:
            return object_type(pos=tuple(json_object["position"]), # type: ignore
                            name=json_object["world"]["name"], # type: ignore
                            inf_tier=json_object["world"]["infinite_tier"], # type: ignore
                            facing=spaces.str_to_orient(json_object["orientation"])) # type: ignore
        else:
            return object_type(pos=tuple(json_object["position"]), # type: ignore
                            name=json_object["level"]["name"], # type: ignore
                            inf_tier=json_object["level"]["infinite_tier"], # type: ignore
                            facing=spaces.str_to_orient(json_object["orientation"])) # type: ignore
    elif object_type == Level:
        if json_object.get("icon") is not None:
            if isinstance(json_object["icon"]["color"], int):
                return object_type(pos=tuple(json_object["position"]), # type: ignore
                                   name=json_object["level"]["name"], # type: ignore
                                   icon_name=json_object["icon"]["name"], # type: ignore
                                   icon_color=json_object["icon"]["color"], # type: ignore
                                   facing=spaces.str_to_orient(json_object["orientation"])) # type: ignore
            else:
                return object_type(pos=tuple(json_object["position"]), # type: ignore
                                   name=json_object["level"]["name"], # type: ignore
                                   icon_name=json_object["icon"]["name"], # type: ignore
                                   icon_color=colors.rgb_to_hex(*json_object["icon"]["color"]), # type: ignore
                                   facing=spaces.str_to_orient(json_object["orientation"])) # type: ignore
        else:
            return object_type(pos=tuple(json_object["position"]), # type: ignore
                               name=json_object["level"]["name"], # type: ignore
                               facing=spaces.str_to_orient(json_object["orientation"])) # type: ignore
    elif issubclass(object_type, Sprite):
        return object_type(pos=tuple(json_object["position"]), # type: ignore
                           facing=spaces.str_to_orient(json_object["orientation"]),
                           sprite_name=json_object["sprite"]["name"]) # type: ignore
    else:
        return object_type(pos=tuple(json_object["position"]), # type: ignore
                           facing=spaces.str_to_orient(json_object["orientation"])) # type: ignore

object_name: dict[str, type[Object]] = {
    "Baba": Baba,
    "Keke": Keke,
    "Me": Me,
    "Patrick": Patrick,
    "Skull": Skull,
    "Ghost": Ghost,
    "Wall": Wall,
    "Hedge": Hedge,
    "Ice": Ice,
    "Tile": Tile,
    "Grass": Grass,
    "Water": Water,
    "Lava": Lava,
    "Box": Box,
    "Rock": Rock,
    "Fruit": Fruit,
    "Belt": Belt,
    "Sun": Sun,
    "Moon": Moon,
    "Star": Star,
    "What": What,
    "Love": Love,
    "Flag": Flag,
    "Cursor": Cursor,
    "Empty": Empty,
    "Level": Level,
    "World": World,
    "Clone": Clone,
    "BABA": BABA,
    "KEKE": KEKE,
    "ME": ME,
    "PATRICK": PATRICK,
    "SKULL": SKULL,
    "GHOST": GHOST,
    "WALL": WALL,
    "HEDGE": HEDGE,
    "ICE": ICE,
    "TILE": TILE,
    "GRASS": GRASS,
    "WATER": WATER,
    "LAVA": LAVA,
    "BOX": BOX,
    "ROCK": ROCK,
    "FRUIT": FRUIT,
    "BELT": BELT,
    "SUN": SUN,
    "MOON": MOON,
    "STAR": STAR,
    "WHAT": WHAT,
    "LOVE": LOVE,
    "FLAG": FLAG,
    "CURSOR": CURSOR,
    "ALL": ALL,
    "EMPTY": EMPTY,
    "TEXT": TEXT,
    "LEVEL": LEVEL,
    "WORLD": WORLD,
    "CLONE": CLONE,
    "GAME": GAME,
    "IS": IS,
    "NOT": NOT,
    "AND": AND,
    "YOU": YOU,
    "MOVE": MOVE,
    "STOP": STOP,
    "PUSH": PUSH,
    "SINK": SINK,
    "FLOAT": FLOAT,
    "OPEN": OPEN,
    "SHUT": SHUT,
    "HOT": HOT,
    "MELT": MELT,
    "WIN": WIN,
    "DEFEAT": DEFEAT,
    "SHIFT": SHIFT,
    "TELE": TELE,
    "WORD": WORD,
    "SELECT": SELECT,
    "END": END,
    "DONE": DONE
}

class NounsObjsDicts(object):
    pairs: dict[type[Noun], type[Object]]
    def __init__(self) -> None:
        self.pairs = {}
    def new_pair(self, noun: type[Noun], obj: type[Object]) -> None:
        self.pairs[noun] = obj
    def get_obj(self, noun: type[Noun]) -> Optional[type[Object]]:
        for get_noun, get_object in self.pairs.items():
            if issubclass(noun, get_noun):
                return get_object
    def get_exist_obj(self, noun: type[Noun]) -> type[Object]:
        for get_noun, get_object in self.pairs.items():
            if issubclass(noun, get_noun):
                return get_object
        raise ValueError()
    def get_noun(self, obj: type[Object]) -> Optional[type[Noun]]:
        pairs = {v: k for k, v in self.pairs.items()}
        for get_object, get_noun in pairs.items():
            if issubclass(obj, get_object):
                return get_noun
    def get_exist_noun(self, obj: type[Object]) -> type[Noun]:
        pairs = {v: k for k, v in self.pairs.items()}
        for get_object, get_noun in pairs.items():
            if issubclass(obj, get_object):
                return get_noun
        raise ValueError()

nouns_objs_dicts = NounsObjsDicts()

nouns_objs_dicts.new_pair(BABA, Baba)
nouns_objs_dicts.new_pair(KEKE, Keke)
nouns_objs_dicts.new_pair(ME, Me)
nouns_objs_dicts.new_pair(PATRICK, Patrick)
nouns_objs_dicts.new_pair(SKULL, Skull)
nouns_objs_dicts.new_pair(GHOST, Ghost)
nouns_objs_dicts.new_pair(WALL, Wall)
nouns_objs_dicts.new_pair(HEDGE, Hedge)
nouns_objs_dicts.new_pair(ICE, Ice)
nouns_objs_dicts.new_pair(TILE, Tile)
nouns_objs_dicts.new_pair(GRASS, Grass)
nouns_objs_dicts.new_pair(WATER, Water)
nouns_objs_dicts.new_pair(LAVA, Lava)
nouns_objs_dicts.new_pair(DOOR, Door)
nouns_objs_dicts.new_pair(KEY, Key)
nouns_objs_dicts.new_pair(BOX, Box)
nouns_objs_dicts.new_pair(ROCK, Rock)
nouns_objs_dicts.new_pair(FRUIT, Fruit)
nouns_objs_dicts.new_pair(BELT, Belt)
nouns_objs_dicts.new_pair(SUN, Sun)
nouns_objs_dicts.new_pair(MOON, Moon)
nouns_objs_dicts.new_pair(STAR, Star)
nouns_objs_dicts.new_pair(WHAT, What)
nouns_objs_dicts.new_pair(LOVE, Love)
nouns_objs_dicts.new_pair(FLAG, Flag)
nouns_objs_dicts.new_pair(CURSOR, Cursor)
nouns_objs_dicts.new_pair(EMPTY, Empty)
nouns_objs_dicts.new_pair(LEVEL, Level)
nouns_objs_dicts.new_pair(WORLD, World)
nouns_objs_dicts.new_pair(CLONE, Clone)
nouns_objs_dicts.new_pair(TEXT, Text)
nouns_objs_dicts.new_pair(GAME, Game)

not_in_all: tuple[type[Object], ...] = (Text, Empty, Level, WorldPointer, Game, Sprite)
in_not_all: tuple[type[Object], ...] = (Text, Empty, Game, Sprite)
not_in_editor: tuple[type[Object], ...] = (Empty, EMPTY, Text, Game, GAME, Sprite)