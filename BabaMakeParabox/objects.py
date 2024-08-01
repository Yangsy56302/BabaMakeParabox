from typing import Any, Optional, TypeGuard, TypeVar, TypedDict
import math
import uuid
from BabaMakeParabox import colors, spaces

class BmpObjectJson(TypedDict):
    type: str
    position: spaces.Coord
    orientation: spaces.OrientStr

class BmpObject(object):
    typename: str = "BmpObject"
    json_name: str
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
    def __eq__(self, obj: "BmpObject") -> bool:
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
    def to_json(self) -> BmpObjectJson:
        return {"type": self.json_name, "position": (self.x, self.y), "orientation": spaces.orient_to_str(self.orient)}

class Static(BmpObject):
    typename: str = "Static"
    def set_sprite(self) -> None:
        self.sprite_state = 0

class Tiled(BmpObject):
    typename: str = "Tiled"
    def set_sprite(self, connected: dict[spaces.Orient, bool]) -> None:
        self.sprite_state = (connected[spaces.Orient.D] * 0x1) | (connected[spaces.Orient.W] * 0x2) | (connected[spaces.Orient.A] * 0x4) | (connected[spaces.Orient.S] * 0x8)

class Animated(BmpObject):
    typename: str = "Animated"
    def set_sprite(self, round_num: int) -> None:
        self.sprite_state = round_num % 4

class Directional(BmpObject):
    typename: str = "Directional"
    def set_sprite(self) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8

class AnimatedDirectional(BmpObject):
    typename: str = "AnimatedDirectional"
    def set_sprite(self, round_num: int) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | round_num % 4

class Character(BmpObject):
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

class Baba(Character):
    typename: str = "Baba"
    json_name: str = "baba"
    sprite_name: str = "baba"

class Keke(Character):
    typename: str = "Keke"
    json_name: str = "keke"
    sprite_name: str = "keke"

class Me(Character):
    typename: str = "Me"
    json_name: str = "me"
    sprite_name: str = "me"

class Patrick(Directional):
    typename: str = "Patrick"
    json_name: str = "patrick"
    sprite_name: str = "patrick"

class Skull(Directional):
    typename: str = "Skull"
    json_name: str = "skull"
    sprite_name: str = "skull"

class Ghost(Directional):
    typename: str = "Ghost"
    json_name: str = "ghost"
    sprite_name: str = "ghost"

class Wall(Tiled):
    typename: str = "Wall"
    json_name: str = "wall"
    sprite_name: str = "wall"

class Hedge(Tiled):
    typename: str = "Hedge"
    json_name: str = "hedge"
    sprite_name: str = "hedge"

class Ice(Tiled):
    typename: str = "Ice"
    json_name: str = "ice"
    sprite_name: str = "ice"

class Tile(Static):
    typename: str = "Tile"
    json_name: str = "tile"
    sprite_name: str = "tile"

class Grass(Tiled):
    typename: str = "Grass"
    json_name: str = "grass"
    sprite_name: str = "grass"

class Water(Tiled):
    typename: str = "Water"
    json_name: str = "water"
    sprite_name: str = "water"

class Lava(Tiled):
    typename: str = "Lava"
    json_name: str = "lava"
    sprite_name: str = "lava"

class Door(Static):
    typename: str = "Door"
    json_name: str = "door"
    sprite_name: str = "door"

class Key(Static):
    typename: str = "Key"
    json_name: str = "key"
    sprite_name: str = "key"

class Box(Static):
    typename: str = "Box"
    json_name: str = "box"
    sprite_name: str = "box"

class Rock(Static):
    typename: str = "Rock"
    json_name: str = "rock"
    sprite_name: str = "rock"

class Fruit(Static):
    typename: str = "Fruit"
    json_name: str = "fruit"
    sprite_name: str = "fruit"

class Belt(AnimatedDirectional):
    typename: str = "Belt"
    json_name: str = "belt"
    sprite_name: str = "belt"

class Sun(Static):
    typename: str = "Sun"
    json_name: str = "sun"
    sprite_name: str = "sun"

class Moon(Static):
    typename: str = "Moon"
    json_name: str = "moon"
    sprite_name: str = "moon"

class Star(Static):
    typename: str = "Star"
    json_name: str = "star"
    sprite_name: str = "star"

class What(Static):
    typename: str = "What"
    json_name: str = "what"
    sprite_name: str = "what"

class Love(Static):
    typename: str = "Love"
    json_name: str = "love"
    sprite_name: str = "love"

class Flag(Static):
    typename: str = "Flag"
    json_name: str = "flag"
    sprite_name: str = "flag"

class Cursor(Static):
    typename: str = "Cursor"
    json_name: str = "cursor"
    sprite_name: str = "cursor"

class All(BmpObject):
    typename: str = "All"
    json_name: str = "all"
    sprite_name: str = "all"

class Empty(BmpObject):
    typename: str = "Empty"
    json_name: str = "empty"
    sprite_name: str = "empty"

class LevelPointerInfoJson(TypedDict):
    name: str

class LevelPointerIconJson(TypedDict):
    name: str
    color: colors.ColorHex

class LevelPointerExtraJson(TypedDict):
    level: LevelPointerInfoJson
    icon: LevelPointerIconJson

class LevelPointerJson(BmpObjectJson, LevelPointerExtraJson):
    pass

class LevelPointer(BmpObject):
    typename: str = "LevelPointer"
    def __init__(self, pos: spaces.Coord, name: str, icon_name: str = "empty", icon_color: colors.ColorHex = colors.WHITE, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.name: str = name
        self.icon_name: str = icon_name
        self.icon_color: colors.ColorHex = icon_color
    def to_json(self) -> LevelPointerJson:
        basic_json_object = super().to_json()
        extra_json_object: LevelPointerExtraJson = {"level": {"name": self.name}, "icon": {"name": self.icon_name, "color": self.icon_color}}
        return {**basic_json_object, **extra_json_object}

class Level(LevelPointer):
    typename: str = "Level"
    json_name: str = "level"
    sprite_name: str = "level"
    def __init__(self, pos: spaces.Coord, name: str, icon_name: str = "empty", icon_color: colors.ColorHex = colors.WHITE, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, name, icon_name, icon_color, orient)

class WorldPointerInfoJson(TypedDict):
    name: str
    infinite_tier: int
    
class WorldPointerExtraJson(TypedDict):
    world: WorldPointerInfoJson

class WorldPointerJson(BmpObjectJson, WorldPointerExtraJson):
    pass

class WorldPointer(BmpObject):
    typename: str = "WorldContainer"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.name: str = name
        self.inf_tier: int = inf_tier
    def to_json(self) -> WorldPointerJson:
        basic_json_object = super().to_json()
        extra_json_object: WorldPointerExtraJson = {"world": {"name": self.name, "infinite_tier": self.inf_tier}}
        return {**basic_json_object, **extra_json_object}

class World(WorldPointer):
    typename: str = "World"
    json_name: str = "world"
    sprite_name: str = "world"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, name, inf_tier, orient)
        
class Clone(WorldPointer):
    typename: str = "Clone"
    json_name: str = "clone"
    sprite_name: str = "clone"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, name, inf_tier, orient)

class Transform(BmpObject):
    typename: str = "Transform"
    def __init__(self, pos: spaces.Coord, info: dict[str, Any], orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.from_type: type[BmpObject] = info["from"]["type"]
        self.from_name: str = info["from"]["name"]
        if issubclass(self.from_type, WorldPointer):
            self.from_inf_tier: int = info["from"]["inf_tier"]
        self.to_type: type[BmpObject] = info["to"]["type"]

class SpriteInfoJson(TypedDict):
    name: str
    
class SpriteExtraJson(TypedDict):
    sprite: SpriteInfoJson

class SpriteJson(BmpObjectJson, SpriteExtraJson):
    pass

class Sprite(BmpObject):
    typename: str = "Sprite"
    def __init__(self, pos: spaces.Coord, sprite_name: str, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.sprite_name: str = sprite_name
    def to_json(self) -> SpriteJson:
        basic_json_object = super().to_json()
        extra_json_object: SpriteExtraJson = {"sprite": {"name": self.sprite_name}}
        return {**basic_json_object, **extra_json_object}

class Game(BmpObject):
    typename: str = "Game"
    json_name: str = "game"
    sprite_name: str = "game"

class Text(BmpObject):
    typename: str = "Text"
    json_name: str = "text"
    sprite_name: str = "text"

class Noun(Text):
    typename: str = "Noun"

class Prefix(Text):
    typename: str = "Prefix"

class Infix(Text):
    typename: str = "Infix"

class Operator(Text):
    typename: str = "Operator"

class Property(Text):
    typename: str = "Property"

class BABA(Noun):
    typename: str = "BABA"
    json_name: str = "text_baba"
    sprite_name: str = "text_baba"

class KEKE(Noun):
    typename: str = "KEKE"
    json_name: str = "text_keke"
    sprite_name: str = "text_keke"

class ME(Noun):
    typename: str = "ME"
    json_name: str = "text_me"
    sprite_name: str = "text_me"

class PATRICK(Noun):
    typename: str = "PATRICK"
    json_name: str = "text_patrick"
    sprite_name: str = "text_patrick"

class SKULL(Noun):
    typename: str = "SKULL"
    json_name: str = "text_skull"
    sprite_name: str = "text_skull"

class GHOST(Noun):
    typename: str = "GHOST"
    json_name: str = "text_ghost"
    sprite_name: str = "text_ghost"

class WALL(Noun):
    typename: str = "WALL"
    json_name: str = "text_wall"
    sprite_name: str = "text_wall"

class HEDGE(Noun):
    typename: str = "HEDGE"
    json_name: str = "text_hedge"
    sprite_name: str = "text_hedge"

class ICE(Noun):
    typename: str = "ICE"
    json_name: str = "text_ice"
    sprite_name: str = "text_ice"

class TILE(Noun):
    typename: str = "TILE"
    json_name: str = "text_tile"
    sprite_name: str = "text_tile"

class GRASS(Noun):
    typename: str = "GRASS"
    json_name: str = "text_grass"
    sprite_name: str = "text_grass"

class WATER(Noun):
    typename: str = "WATER"
    json_name: str = "text_water"
    sprite_name: str = "text_water"

class LAVA(Noun):
    typename: str = "LAVA"
    json_name: str = "text_lava"
    sprite_name: str = "text_lava"

class DOOR(Noun):
    typename: str = "DOOR"
    json_name: str = "text_door"
    sprite_name: str = "text_door"

class KEY(Noun):
    typename: str = "KEY"
    json_name: str = "text_key"
    sprite_name: str = "text_key"

class BOX(Noun):
    typename: str = "BOX"
    json_name: str = "text_box"
    sprite_name: str = "text_box"

class ROCK(Noun):
    typename: str = "ROCK"
    json_name: str = "text_rock"
    sprite_name: str = "text_rock"

class FRUIT(Noun):
    typename: str = "FRUIT"
    json_name: str = "text_fruit"
    sprite_name: str = "text_fruit"

class BELT(Noun):
    typename: str = "BELT"
    json_name: str = "text_belt"
    sprite_name: str = "text_belt"

class SUN(Noun):
    typename: str = "SUN"
    json_name: str = "text_sun"
    sprite_name: str = "text_sun"

class MOON(Noun):
    typename: str = "MOON"
    json_name: str = "text_moon"
    sprite_name: str = "text_moon"

class STAR(Noun):
    typename: str = "STAR"
    json_name: str = "text_star"
    sprite_name: str = "text_star"

class WHAT(Noun):
    typename: str = "WHAT"
    json_name: str = "text_what"
    sprite_name: str = "text_what"

class LOVE(Noun):
    typename: str = "LOVE"
    json_name: str = "text_love"
    sprite_name: str = "text_love"

class FLAG(Noun):
    typename: str = "FLAG"
    json_name: str = "text_flag"
    sprite_name: str = "text_flag"

class CURSOR(Noun):
    typename: str = "CURSOR"
    json_name: str = "text_cursor"
    sprite_name: str = "text_cursor"

class ALL(Noun):
    typename: str = "ALL"
    json_name: str = "text_all"
    sprite_name: str = "text_all"

class EMPTY(Noun):
    typename: str = "EMPTY"
    json_name: str = "text_empty"
    sprite_name: str = "text_empty"

class TEXT(Noun):
    typename: str = "TEXT"
    json_name: str = "text_text"
    sprite_name: str = "text_text"

class LEVEL(Noun):
    typename: str = "LEVEL"
    json_name: str = "text_level"
    sprite_name: str = "text_level"

class WORLD(Noun):
    typename: str = "WORLD"
    json_name: str = "text_world"
    sprite_name: str = "text_world"

class CLONE(Noun):
    typename: str = "CLONE"
    json_name: str = "text_clone"
    sprite_name: str = "text_clone"

class GAME(Noun):
    typename: str = "GAME"
    json_name: str = "text_game"
    sprite_name: str = "text_game"

class META(Prefix):
    typename: str = "META"
    json_name: str = "text_meta"
    sprite_name: str = "text_meta"

class ON(Infix):
    typename: str = "ON"
    json_name: str = "text_on"
    sprite_name: str = "text_on"

class NEAR(Infix):
    typename: str = "NEAR"
    json_name: str = "text_near"
    sprite_name: str = "text_near"

class NEXTTO(Infix):
    typename: str = "NEXTTO"
    json_name: str = "text_nextto"
    sprite_name: str = "text_nextto"

class FEELING(Infix):
    typename: str = "FEELING"
    json_name: str = "text_feeling"
    sprite_name: str = "text_feeling"

class IS(Operator):
    typename: str = "IS"
    json_name: str = "text_is"
    sprite_name: str = "text_is"

class HAS(Operator):
    typename: str = "HAS"
    json_name: str = "text_has"
    sprite_name: str = "text_has"

class MAKE(Operator):
    typename: str = "MAKE"
    json_name: str = "text_make"
    sprite_name: str = "text_make"

class WRITE(Operator):
    typename: str = "WRITE"
    json_name: str = "text_write"
    sprite_name: str = "text_write"

class NOT(Text):
    typename: str = "NOT"
    json_name: str = "text_not"
    sprite_name: str = "text_not"

class AND(Text):
    typename: str = "AND"
    json_name: str = "text_and"
    sprite_name: str = "text_and"

class YOU(Property):
    typename: str = "YOU"
    json_name: str = "text_you"
    sprite_name: str = "text_you"

class MOVE(Property):
    typename: str = "MOVE"
    json_name: str = "text_move"
    sprite_name: str = "text_move"

class STOP(Property):
    typename: str = "STOP"
    json_name: str = "text_stop"
    sprite_name: str = "text_stop"

class PUSH(Property):
    typename: str = "PUSH"
    json_name: str = "text_push"
    sprite_name: str = "text_push"

class SINK(Property):
    typename: str = "SINK"
    json_name: str = "text_sink"
    sprite_name: str = "text_sink"

class FLOAT(Property):
    typename: str = "FLOAT"
    json_name: str = "text_float"
    sprite_name: str = "text_float"

class OPEN(Property):
    typename: str = "OPEN"
    json_name: str = "text_open"
    sprite_name: str = "text_open"

class SHUT(Property):
    typename: str = "SHUT"
    json_name: str = "text_shut"
    sprite_name: str = "text_shut"

class HOT(Property):
    typename: str = "HOT"
    json_name: str = "text_hot"
    sprite_name: str = "text_hot"

class MELT(Property):
    typename: str = "MELT"
    json_name: str = "text_melt"
    sprite_name: str = "text_melt"

class WIN(Property):
    typename: str = "WIN"
    json_name: str = "text_win"
    sprite_name: str = "text_win"

class DEFEAT(Property):
    typename: str = "DEFEAT"
    json_name: str = "text_defeat"
    sprite_name: str = "text_defeat"

class SHIFT(Property):
    typename: str = "SHIFT"
    json_name: str = "text_shift"
    sprite_name: str = "text_shift"

class TELE(Property):
    typename: str = "TELE"
    json_name: str = "text_tele"
    sprite_name: str = "text_tele"

class WORD(Property):
    typename: str = "WORD"
    json_name: str = "text_word"
    sprite_name: str = "text_word"

class SELECT(Property):
    typename: str = "SELECT"
    json_name: str = "text_select"
    sprite_name: str = "text_select"

class END(Property):
    typename: str = "END"
    json_name: str = "text_end"
    sprite_name: str = "text_end"

class DONE(Property):
    typename: str = "DONE"
    json_name: str = "text_done"
    sprite_name: str = "text_done"

old_object_name: dict[str, type[BmpObject]] = {}
old_object_name["Baba"] = Baba
old_object_name["Keke"] = Keke
old_object_name["Me"] = Me
old_object_name["Patrick"] = Patrick
old_object_name["Skull"] = Skull
old_object_name["Ghost"] = Ghost
old_object_name["Wall"] = Wall
old_object_name["Hedge"] = Hedge
old_object_name["Ice"] = Ice
old_object_name["Tile"] = Tile
old_object_name["Grass"] = Grass
old_object_name["Water"] = Water
old_object_name["Lava"] = Lava
old_object_name["Box"] = Box
old_object_name["Rock"] = Rock
old_object_name["Fruit"] = Fruit
old_object_name["Belt"] = Belt
old_object_name["Sun"] = Sun
old_object_name["Moon"] = Moon
old_object_name["Star"] = Star
old_object_name["What"] = What
old_object_name["Love"] = Love
old_object_name["Flag"] = Flag
old_object_name["Cursor"] = Cursor
old_object_name["Empty"] = Empty
old_object_name["Level"] = Level
old_object_name["World"] = World
old_object_name["Clone"] = Clone
old_object_name["BABA"] = BABA
old_object_name["KEKE"] = KEKE
old_object_name["ME"] = ME
old_object_name["PATRICK"] = PATRICK
old_object_name["SKULL"] = SKULL
old_object_name["GHOST"] = GHOST
old_object_name["WALL"] = WALL
old_object_name["HEDGE"] = HEDGE
old_object_name["ICE"] = ICE
old_object_name["TILE"] = TILE
old_object_name["GRASS"] = GRASS
old_object_name["WATER"] = WATER
old_object_name["LAVA"] = LAVA
old_object_name["BOX"] = BOX
old_object_name["ROCK"] = ROCK
old_object_name["FRUIT"] = FRUIT
old_object_name["BELT"] = BELT
old_object_name["SUN"] = SUN
old_object_name["MOON"] = MOON
old_object_name["STAR"] = STAR
old_object_name["WHAT"] = WHAT
old_object_name["LOVE"] = LOVE
old_object_name["FLAG"] = FLAG
old_object_name["CURSOR"] = CURSOR
old_object_name["ALL"] = ALL
old_object_name["EMPTY"] = EMPTY
old_object_name["TEXT"] = TEXT
old_object_name["LEVEL"] = LEVEL
old_object_name["WORLD"] = WORLD
old_object_name["CLONE"] = CLONE
old_object_name["GAME"] = GAME
old_object_name["META"] = META
old_object_name["ON"] = ON
old_object_name["NEAR"] = NEAR
old_object_name["NEXTTO"] = NEXTTO
old_object_name["FEELING"] = FEELING
old_object_name["IS"] = IS
old_object_name["HAS"] = HAS
old_object_name["MAKE"] = MAKE
old_object_name["WRITE"] = WRITE
old_object_name["NOT"] = NOT
old_object_name["AND"] = AND
old_object_name["YOU"] = YOU
old_object_name["MOVE"] = MOVE
old_object_name["STOP"] = STOP
old_object_name["PUSH"] = PUSH
old_object_name["SINK"] = SINK
old_object_name["FLOAT"] = FLOAT
old_object_name["OPEN"] = OPEN
old_object_name["SHUT"] = SHUT
old_object_name["HOT"] = HOT
old_object_name["MELT"] = MELT
old_object_name["WIN"] = WIN
old_object_name["DEFEAT"] = DEFEAT
old_object_name["SHIFT"] = SHIFT
old_object_name["TELE"] = TELE
old_object_name["WORD"] = WORD
old_object_name["SELECT"] = SELECT
old_object_name["END"] = END
old_object_name["DONE"] = DONE

object_class_used: list[type[BmpObject]] = []
object_class_used.extend([Baba, Keke, Me, Patrick, Skull, Ghost])
object_class_used.extend([Wall, Hedge, Ice, Tile, Grass, Water, Lava])
object_class_used.extend([Box, Rock, Fruit, Belt, Sun, Moon, Star, What, Love, Flag])
object_class_used.extend([Cursor, All, Empty, Text, Level, World, Clone, Game])
object_class_used.extend([BABA, KEKE, ME, PATRICK, SKULL, GHOST])
object_class_used.extend([WALL, HEDGE, ICE, TILE, GRASS, WATER, LAVA])
object_class_used.extend([BOX, ROCK, FRUIT, BELT, SUN, MOON, STAR, WHAT, LOVE, FLAG])
object_class_used.extend([CURSOR, ALL, EMPTY, TEXT, LEVEL, WORLD, CLONE, GAME])
object_class_used.extend([META])
object_class_used.extend([ON, NEAR, NEXTTO, FEELING])
object_class_used.extend([IS, HAS, MAKE, WRITE])
object_class_used.extend([NOT, AND])
object_class_used.extend([YOU, MOVE, STOP, PUSH, SINK, FLOAT, OPEN, SHUT, HOT, MELT, WIN, DEFEAT, SHIFT, TELE])
object_class_used.extend([WORD, SELECT, END, DONE])

object_name: dict[str, type[BmpObject]] = {t.json_name : t for t in object_class_used}

class ObjectNounDict(object):
    def __init__(self, pairs: Optional[dict[type[BmpObject], type[Noun]]] = None) -> None:
        self.pairs: dict[type[BmpObject], type[Noun]] = pairs if pairs is not None else {}
    def __getitem__(self, obj: type[BmpObject]) -> type[Noun]:
        for k, v in self.pairs.items():
            if issubclass(obj, k):
                return v
        raise KeyError(obj)
    def __setitem__(self, obj: type[BmpObject], noun: type[Noun]) -> None:
        self.pairs[obj] = noun
    def __delitem__(self, obj: type[BmpObject]) -> None:
        for k in self.pairs.keys():
            if issubclass(obj, k):
                del self.pairs[k]
    def get(self, obj: type[BmpObject]) -> Optional[type[Noun]]:
        for k, v in self.pairs.items():
            if issubclass(obj, k):
                return v
        return None

class NounObjectDict(object):
    def __init__(self, pairs: Optional[dict[type[Noun], type[BmpObject]]] = None) -> None:
        self.pairs: dict[type[Noun], type[BmpObject]] = pairs if pairs is not None else {}
    def __getitem__(self, noun: type[Noun]) -> type[BmpObject]:
        for k, v in self.pairs.items():
            if issubclass(noun, k):
                return v
        raise KeyError(noun)
    def __setitem__(self, noun: type[Noun], obj: type[BmpObject]) -> None:
        self.pairs[noun] = obj
    def __delitem__(self, noun: type[Noun]) -> None:
        for k in self.pairs.keys():
            if issubclass(noun, k):
                del self.pairs[k]
    def get(self, noun: type[Noun]) -> Optional[type[BmpObject]]:
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
nouns_objs_dicts[ALL] = All
nouns_objs_dicts[EMPTY] = Empty
nouns_objs_dicts[LEVEL] = Level
nouns_objs_dicts[WORLD] = World
nouns_objs_dicts[CLONE] = Clone
nouns_objs_dicts[TEXT] = Text
nouns_objs_dicts[GAME] = Game

not_in_all: tuple[type[BmpObject], ...] = (All, Empty, Text, Level, WorldPointer, Transform, Sprite, Game)
in_not_all: tuple[type[BmpObject], ...] = (Text, Empty, Transform, Sprite, Game)
not_in_editor: tuple[type[BmpObject], ...] = (All, Empty, EMPTY, Text, Transform, Sprite, Game)

def is_correct_bmp_object_json(T):
    def func(json_object: BmpObjectJson) -> TypeGuard[T]:
        return True # i dk why this works
    return func

is_world_pointer_json = is_correct_bmp_object_json(WorldPointerJson)
is_level_json = is_correct_bmp_object_json(LevelPointerJson)
is_sprite_json = is_correct_bmp_object_json(SpriteJson)

def json_to_object(json_object: BmpObjectJson, ver: Optional[str] = None) -> BmpObject:
    typename: str = json_object["type"]
    if ver is None:
        object_type = old_object_name[typename]
    else:
        object_type = object_name[typename]
    if issubclass(object_type, WorldPointer):
        if is_world_pointer_json(json_object):
            return object_type(pos=json_object["position"],
                               name=json_object["world"]["name"],
                               inf_tier=json_object["world"]["infinite_tier"],
                               orient=spaces.str_to_orient(json_object["orientation"]))
        raise KeyError("HOW")
    elif issubclass(object_type, Level):
        if is_level_json(json_object):
            return object_type(pos=json_object["position"],
                               name=json_object["level"]["name"],
                               icon_name=json_object["icon"]["name"],
                               icon_color=json_object["icon"]["color"],
                               orient=spaces.str_to_orient(json_object["orientation"]))
        raise KeyError("HOW")
    elif issubclass(object_type, Sprite):
        if is_sprite_json(json_object):
            return object_type(pos=json_object["position"],
                               sprite_name=json_object["sprite"]["name"],
                               orient=spaces.str_to_orient(json_object["orientation"]))
        raise KeyError("HOW")
    else:
        return object_type(pos=json_object["position"],
                           orient=spaces.str_to_orient(json_object["orientation"]))