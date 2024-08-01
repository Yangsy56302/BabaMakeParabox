from typing import Any, Optional, TypeGuard, TypeVar, TypedDict
import types
import math
import uuid
from BabaMakeParabox import basics, colors, spaces

class BmpObjectJson(TypedDict):
    type: str
    position: spaces.Coord
    orientation: spaces.OrientStr

class BmpObject(object):
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
    def set_sprite(self) -> None:
        self.sprite_state = 0

class Tiled(BmpObject):
    def set_sprite(self, connected: dict[spaces.Orient, bool]) -> None:
        self.sprite_state = (connected[spaces.Orient.D] * 0x1) | (connected[spaces.Orient.W] * 0x2) | (connected[spaces.Orient.A] * 0x4) | (connected[spaces.Orient.S] * 0x8)

class Animated(BmpObject):
    def set_sprite(self, round_num: int) -> None:
        self.sprite_state = round_num % 4

class Directional(BmpObject):
    def set_sprite(self) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8

class AnimatedDirectional(BmpObject):
    def set_sprite(self, round_num: int) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | round_num % 4

class Character(BmpObject):
    def set_sprite(self) -> None:
        sleeping = False
        if not sleeping:
            if self.moved:
                temp_state = (self.sprite_state & 0x3) + 1 if (self.sprite_state & 0x3) != 0x3 else 0x0
                self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | temp_state
            else:
                self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | (self.sprite_state & 0x3)
        else:
            self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | 0x7

class Baba(Character):
    json_name: str = "baba"
    sprite_name: str = "baba"

class Keke(Character):
    json_name: str = "keke"
    sprite_name: str = "keke"

class Me(Character):
    json_name: str = "me"
    sprite_name: str = "me"

class Patrick(Directional):
    json_name: str = "patrick"
    sprite_name: str = "patrick"

class Skull(Directional):
    json_name: str = "skull"
    sprite_name: str = "skull"

class Ghost(Directional):
    json_name: str = "ghost"
    sprite_name: str = "ghost"

class Wall(Tiled):
    json_name: str = "wall"
    sprite_name: str = "wall"

class Hedge(Tiled):
    json_name: str = "hedge"
    sprite_name: str = "hedge"

class Ice(Tiled):
    json_name: str = "ice"
    sprite_name: str = "ice"

class Tile(Static):
    json_name: str = "tile"
    sprite_name: str = "tile"

class Grass(Tiled):
    json_name: str = "grass"
    sprite_name: str = "grass"

class Water(Tiled):
    json_name: str = "water"
    sprite_name: str = "water"

class Lava(Tiled):
    json_name: str = "lava"
    sprite_name: str = "lava"

class Door(Static):
    json_name: str = "door"
    sprite_name: str = "door"

class Key(Static):
    json_name: str = "key"
    sprite_name: str = "key"

class Box(Static):
    json_name: str = "box"
    sprite_name: str = "box"

class Rock(Static):
    json_name: str = "rock"
    sprite_name: str = "rock"

class Fruit(Static):
    json_name: str = "fruit"
    sprite_name: str = "fruit"

class Belt(AnimatedDirectional):
    json_name: str = "belt"
    sprite_name: str = "belt"

class Sun(Static):
    json_name: str = "sun"
    sprite_name: str = "sun"

class Moon(Static):
    json_name: str = "moon"
    sprite_name: str = "moon"

class Star(Static):
    json_name: str = "star"
    sprite_name: str = "star"

class What(Static):
    json_name: str = "what"
    sprite_name: str = "what"

class Love(Static):
    json_name: str = "love"
    sprite_name: str = "love"

class Flag(Static):
    json_name: str = "flag"
    sprite_name: str = "flag"

class Cursor(Static):
    json_name: str = "cursor"
    sprite_name: str = "cursor"

class All(BmpObject):
    pass

class Empty(BmpObject):
    pass

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
    def __init__(self, pos: spaces.Coord, name: str, infinite_tier: int = 0, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.name: str = name
        self.infinite_tier: int = infinite_tier
    def to_json(self) -> WorldPointerJson:
        basic_json_object = super().to_json()
        extra_json_object: WorldPointerExtraJson = {"world": {"name": self.name, "infinite_tier": self.infinite_tier}}
        return {**basic_json_object, **extra_json_object}

class World(WorldPointer):
    json_name: str = "world"
    sprite_name: str = "world"
    def __init__(self, pos: spaces.Coord, name: str, infinite_tier: int = 0, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, name, infinite_tier, orient)
        
class Clone(WorldPointer):
    json_name: str = "clone"
    sprite_name: str = "clone"
    def __init__(self, pos: spaces.Coord, name: str, infinite_tier: int = 0, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, name, infinite_tier, orient)

class Transform(BmpObject):
    def __init__(self, pos: spaces.Coord, info: dict[str, Any], orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.from_type: type[BmpObject] = info["from"]["type"]
        self.from_name: str = info["from"]["name"]
        if issubclass(self.from_type, WorldPointer):
            self.from_infinite_tier: int = info["from"]["infinite_tier"]
        self.to_type: type[BmpObject] = info["to"]["type"]

class SpriteInfoJson(TypedDict):
    name: str
    
class SpriteExtraJson(TypedDict):
    sprite: SpriteInfoJson

class SpriteJson(BmpObjectJson, SpriteExtraJson):
    pass

class Sprite(BmpObject):
    def __init__(self, pos: spaces.Coord, sprite_name: str, orient: spaces.Orient = spaces.Orient.S) -> None:
        super().__init__(pos, orient)
        self.sprite_name: str = sprite_name
    def to_json(self) -> SpriteJson:
        basic_json_object = super().to_json()
        extra_json_object: SpriteExtraJson = {"sprite": {"name": self.sprite_name}}
        return {**basic_json_object, **extra_json_object}

class Game(BmpObject):
    pass

class Text(BmpObject):
    pass

class Noun(Text):
    obj_type: type[BmpObject]

class Prefix(Text):
    pass

class Infix(Text):
    pass

class Operator(Text):
    pass

class Property(Text):
    pass

class TextBaba(Noun):
    obj_type: type[BmpObject] = Baba
    json_name: str = "text_baba"
    sprite_name: str = "text_baba"

class TextKeke(Noun):
    obj_type: type[BmpObject] = Keke
    json_name: str = "text_keke"
    sprite_name: str = "text_keke"

class TextMe(Noun):
    obj_type: type[BmpObject] = Me
    json_name: str = "text_me"
    sprite_name: str = "text_me"

class TextPatrick(Noun):
    obj_type: type[BmpObject] = Patrick
    json_name: str = "text_patrick"
    sprite_name: str = "text_patrick"

class TextSkull(Noun):
    obj_type: type[BmpObject] = Skull
    json_name: str = "text_skull"
    sprite_name: str = "text_skull"

class TextGhost(Noun):
    obj_type: type[BmpObject] = Ghost
    json_name: str = "text_ghost"
    sprite_name: str = "text_ghost"

class TextWall(Noun):
    obj_type: type[BmpObject] = Wall
    json_name: str = "text_wall"
    sprite_name: str = "text_wall"

class TextHedge(Noun):
    obj_type: type[BmpObject] = Hedge
    json_name: str = "text_hedge"
    sprite_name: str = "text_hedge"

class TextIce(Noun):
    obj_type: type[BmpObject] = Ice
    json_name: str = "text_ice"
    sprite_name: str = "text_ice"

class TextTile(Noun):
    obj_type: type[BmpObject] = Tile
    json_name: str = "text_tile"
    sprite_name: str = "text_tile"

class TextGrass(Noun):
    obj_type: type[BmpObject] = Grass
    json_name: str = "text_grass"
    sprite_name: str = "text_grass"

class TextWater(Noun):
    obj_type: type[BmpObject] = Water
    json_name: str = "text_water"
    sprite_name: str = "text_water"

class TextLava(Noun):
    obj_type: type[BmpObject] = Lava
    json_name: str = "text_lava"
    sprite_name: str = "text_lava"

class TextDoor(Noun):
    obj_type: type[BmpObject] = Door
    json_name: str = "text_door"
    sprite_name: str = "text_door"

class TextKey(Noun):
    obj_type: type[BmpObject] = Key
    json_name: str = "text_key"
    sprite_name: str = "text_key"

class TextBox(Noun):
    obj_type: type[BmpObject] = Box
    json_name: str = "text_box"
    sprite_name: str = "text_box"

class TextRock(Noun):
    obj_type: type[BmpObject] = Rock
    json_name: str = "text_rock"
    sprite_name: str = "text_rock"

class TextFruit(Noun):
    obj_type: type[BmpObject] = Fruit
    json_name: str = "text_fruit"
    sprite_name: str = "text_fruit"

class TextBelt(Noun):
    obj_type: type[BmpObject] = Belt
    json_name: str = "text_belt"
    sprite_name: str = "text_belt"

class TextSun(Noun):
    obj_type: type[BmpObject] = Sun
    json_name: str = "text_sun"
    sprite_name: str = "text_sun"

class TextMoon(Noun):
    obj_type: type[BmpObject] = Moon
    json_name: str = "text_moon"
    sprite_name: str = "text_moon"

class TextStar(Noun):
    obj_type: type[BmpObject] = Star
    json_name: str = "text_star"
    sprite_name: str = "text_star"

class TextWhat(Noun):
    obj_type: type[BmpObject] = What
    json_name: str = "text_what"
    sprite_name: str = "text_what"

class TextLove(Noun):
    obj_type: type[BmpObject] = Love
    json_name: str = "text_love"
    sprite_name: str = "text_love"

class TextFlag(Noun):
    obj_type: type[BmpObject] = Flag
    json_name: str = "text_flag"
    sprite_name: str = "text_flag"

class TextCursor(Noun):
    obj_type: type[BmpObject] = Cursor
    json_name: str = "text_cursor"
    sprite_name: str = "text_cursor"

class TextAll(Noun):
    obj_type: type[BmpObject] = All
    json_name: str = "text_all"
    sprite_name: str = "text_all"

class TextEmpty(Noun):
    obj_type: type[BmpObject] = Empty
    json_name: str = "text_empty"
    sprite_name: str = "text_empty"

class TextText(Noun):
    obj_type: type[BmpObject] = Text
    json_name: str = "text_text"
    sprite_name: str = "text_text"

class TextLevel(Noun):
    obj_type: type[BmpObject] = Level
    json_name: str = "text_level"
    sprite_name: str = "text_level"

class TextWorld(Noun):
    obj_type: type[BmpObject] = World
    json_name: str = "text_world"
    sprite_name: str = "text_world"

class TextClone(Noun):
    obj_type: type[BmpObject] = Clone
    json_name: str = "text_clone"
    sprite_name: str = "text_clone"

class TextGame(Noun):
    obj_type: type[BmpObject] = Game
    json_name: str = "text_game"
    sprite_name: str = "text_game"

class TextMeta(Prefix):
    json_name: str = "text_meta"
    sprite_name: str = "text_meta"

class TextText_(Text):
    json_name: str = "text_text_"
    sprite_name: str = "text_text_"

class TextOn(Infix):
    json_name: str = "text_on"
    sprite_name: str = "text_on"

class TextNear(Infix):
    json_name: str = "text_near"
    sprite_name: str = "text_near"

class TextNextto(Infix):
    json_name: str = "text_nextto"
    sprite_name: str = "text_nextto"

class TextFeeling(Infix):
    json_name: str = "text_feeling"
    sprite_name: str = "text_feeling"

class TextIs(Operator):
    json_name: str = "text_is"
    sprite_name: str = "text_is"

class TextHas(Operator):
    json_name: str = "text_has"
    sprite_name: str = "text_has"

class TextMake(Operator):
    json_name: str = "text_make"
    sprite_name: str = "text_make"

class TextWrite(Operator):
    json_name: str = "text_write"
    sprite_name: str = "text_write"

class TextNot(Text):
    json_name: str = "text_not"
    sprite_name: str = "text_not"

class TextAnd(Text):
    json_name: str = "text_and"
    sprite_name: str = "text_and"

class TextYou(Property):
    json_name: str = "text_you"
    sprite_name: str = "text_you"

class TextMove(Property):
    json_name: str = "text_move"
    sprite_name: str = "text_move"

class TextStop(Property):
    json_name: str = "text_stop"
    sprite_name: str = "text_stop"

class TextPush(Property):
    json_name: str = "text_push"
    sprite_name: str = "text_push"

class TextSink(Property):
    json_name: str = "text_sink"
    sprite_name: str = "text_sink"

class TextFloat(Property):
    json_name: str = "text_float"
    sprite_name: str = "text_float"

class TextOpen(Property):
    json_name: str = "text_open"
    sprite_name: str = "text_open"

class TextShut(Property):
    json_name: str = "text_shut"
    sprite_name: str = "text_shut"

class TextHot(Property):
    json_name: str = "text_hot"
    sprite_name: str = "text_hot"

class TextMelt(Property):
    json_name: str = "text_melt"
    sprite_name: str = "text_melt"

class TextWin(Property):
    json_name: str = "text_win"
    sprite_name: str = "text_win"

class TextDefeat(Property):
    json_name: str = "text_defeat"
    sprite_name: str = "text_defeat"

class TextShift(Property):
    json_name: str = "text_shift"
    sprite_name: str = "text_shift"

class TextTele(Property):
    json_name: str = "text_tele"
    sprite_name: str = "text_tele"

class TextWord(Property):
    json_name: str = "text_word"
    sprite_name: str = "text_word"

class TextSelect(Property):
    json_name: str = "text_select"
    sprite_name: str = "text_select"

class TextEnd(Property):
    json_name: str = "text_end"
    sprite_name: str = "text_end"

class TextDone(Property):
    json_name: str = "text_done"
    sprite_name: str = "text_done"

class Metatext(Noun):
    meta_tier: int

object_used: list[type[BmpObject]] = []
object_used.extend([Baba, Keke, Me, Patrick, Skull, Ghost])
object_used.extend([Wall, Hedge, Ice, Tile, Grass, Water, Lava])
object_used.extend([Door, Key, Box, Rock, Fruit, Belt, Sun, Moon, Star, What, Love, Flag])
object_used.extend([Cursor, Level, World, Clone])
object_used.extend([TextBaba, TextKeke, TextMe, TextPatrick, TextSkull, TextGhost])
object_used.extend([TextWall, TextHedge, TextIce, TextTile, TextGrass, TextWater, TextLava])
object_used.extend([TextBox, TextRock, TextFruit, TextBelt, TextSun, TextMoon, TextStar, TextWhat, TextLove, TextFlag])
object_used.extend([TextCursor, TextAll, TextText, TextLevel, TextWorld, TextClone, TextGame])
object_used.extend([TextText_, TextMeta])
object_used.extend([TextOn, TextNear, TextNextto, TextFeeling])
object_used.extend([TextIs, TextHas, TextMake, TextWrite])
object_used.extend([TextNot, TextAnd])
object_used.extend([TextYou, TextMove, TextStop, TextPush, TextSink, TextFloat, TextOpen, TextShut, TextHot, TextMelt, TextWin, TextDefeat, TextShift, TextTele])
object_used.extend([TextWord, TextSelect, TextEnd, TextDone])

object_class_used = object_used[:]
object_class_used.extend([All, Empty, Text, Game, TextEmpty])

object_name: dict[str, type[BmpObject]] = {t.json_name: t for t in object_used}

noun_list: list[type[Noun]] = []
noun_list.extend([TextBaba, TextKeke, TextMe, TextPatrick, TextSkull, TextGhost])
noun_list.extend([TextWall, TextHedge, TextIce, TextTile, TextGrass, TextWater, TextLava])
noun_list.extend([TextDoor, TextKey, TextBox, TextRock, TextFruit, TextBelt, TextSun, TextMoon, TextStar, TextWhat, TextLove, TextFlag])
noun_list.extend([TextCursor, TextAll, TextText, TextLevel, TextWorld, TextClone, TextGame])

text_list: list[type[Text]] = []
text_list.extend([TextBaba, TextKeke, TextMe, TextPatrick, TextSkull, TextGhost])
text_list.extend([TextWall, TextHedge, TextIce, TextTile, TextGrass, TextWater, TextLava])
text_list.extend([TextDoor, TextKey, TextBox, TextRock, TextFruit, TextBelt, TextSun, TextMoon, TextStar, TextWhat, TextLove, TextFlag])
text_list.extend([TextCursor, TextAll, TextText, TextLevel, TextWorld, TextClone, TextGame])
text_list.extend([TextText_, TextMeta])
text_list.extend([TextOn, TextNear, TextNextto, TextFeeling])
text_list.extend([TextIs, TextHas, TextMake, TextWrite])
text_list.extend([TextNot, TextAnd])
text_list.extend([TextYou, TextMove, TextStop, TextPush, TextSink, TextFloat, TextOpen, TextShut, TextHot, TextMelt, TextWin, TextDefeat, TextShift, TextTele])
text_list.extend([TextWord, TextSelect, TextEnd, TextDone])

def get_noun_from_obj(obj_type: type[BmpObject]) -> Optional[type[Noun]]:
    return_value: Optional[type[Noun]] = None
    for noun_type in noun_list:
        if obj_type == noun_type.obj_type:
            return noun_type
        if issubclass(obj_type, noun_type.obj_type):
            return_value = noun_type
    return return_value

def get_exist_noun_from_obj(obj_type: type[BmpObject]) -> type[Noun]:
    return_value: Optional[type[Noun]] = None
    for noun_type in noun_list:
        if obj_type == noun_type.obj_type:
            return noun_type
        if issubclass(obj_type, noun_type.obj_type):
            return_value = noun_type
    if return_value is None:
        return TextText
    return return_value

not_in_all: tuple[type[BmpObject], ...] = (All, Empty, Text, Level, WorldPointer, Transform, Sprite, Game)
in_not_all: tuple[type[BmpObject], ...] = (Text, Empty, Transform, Sprite, Game)
not_in_editor: tuple[type[BmpObject], ...] = (All, Empty, TextEmpty, Text, Transform, Sprite, Game)

def generate_metatext(T: type[Text]) -> type[Metatext]:
    new_type_name = "Text" + T.__name__
    new_type_tier = new_type_name.count("Text") - (1 if new_type_name[-4:] != "Text" else 2)
    new_type_vars: dict[str, Any] = {"json_name": "text_" + T.json_name, "sprite_name": T.sprite_name, "obj_type": T, "meta_tier": new_type_tier}
    new_type: type[Metatext] = type(new_type_name, (Metatext, ), new_type_vars)
    return new_type

def generate_metatext_at_tier(tier: int) -> tuple[list[type[Metatext]], list[type[Metatext]]]:
    if tier < 1:
        raise ValueError(str(tier))
    new_metatext_list: list[type[Metatext]] = []
    if tier == 1:
        for noun in text_list:
            new_metatext_list.append(generate_metatext(noun))
        return new_metatext_list, []
    old_metatext_list, older_metatext_list = generate_metatext_at_tier(tier - 1)
    for noun in old_metatext_list:
        new_metatext_list.append(generate_metatext(noun))
    return new_metatext_list, older_metatext_list + old_metatext_list

if basics.options["metatext"]["enabled"]:
    max_metatext_list, other_metatext_list = generate_metatext_at_tier(basics.options["metatext"]["tier"])
    for new_type in max_metatext_list + other_metatext_list:
        object_class_used.append(new_type)
        object_used.append(new_type)
        object_name[new_type.json_name] = new_type
        noun_list.append(new_type)
        text_list.append(new_type)

def is_correct_bmp_object_json(T):
    def func(json_object: BmpObjectJson) -> TypeGuard[T]:
        return True # i dk why this works
    return func

is_world_pointer_json = is_correct_bmp_object_json(WorldPointerJson)
is_level_json = is_correct_bmp_object_json(LevelPointerJson)
is_sprite_json = is_correct_bmp_object_json(SpriteJson)

def json_to_object(json_object: BmpObjectJson, ver: Optional[str] = None) -> BmpObject:
    object_type = object_name[json_object["type"]]
    if issubclass(object_type, WorldPointer):
        if is_world_pointer_json(json_object):
            return object_type(pos=json_object["position"],
                               name=json_object["world"]["name"],
                               infinite_tier=json_object["world"]["infinite_tier"],
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