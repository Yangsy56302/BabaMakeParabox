from typing import Any, NotRequired, Optional, TypeGuard, TypedDict
import math
import uuid
from BabaMakeParabox import basics, colors, spaces
from BabaMakeParabox.spaces import Coord

class WorldPointerExtraJson(TypedDict):
    name: str
    infinite_tier: int

class LevelPointerIconJson(TypedDict):
    name: str
    color: colors.ColorHex

class LevelPointerExtraJson(TypedDict):
    name: str
    icon: LevelPointerIconJson

class BmpObjectJson(TypedDict):
    type: str
    position: spaces.Coord
    orientation: spaces.OrientStr
    world: NotRequired[WorldPointerExtraJson]
    level: NotRequired[LevelPointerExtraJson]

PropertiesDict = dict[type["BmpObject"], dict[int, int]]

def temp_calc(negnum_list: list[int], negated_number: int = 0):
    negnum_list.sort(reverse=True)
    current_negnum = negnum_list[0]
    current_count = 0
    for n in negnum_list:
        if n < negated_number:
            break
        elif n == current_negnum:
            current_count += 1
        elif current_negnum - n == 1:
            current_count = min(0, -current_count) + 1
            current_negnum = n
        else:
            current_count = 1
            current_negnum = n
    return max(0, current_count) if current_negnum == negated_number else 0

class Properties(object):
    def __init__(self, prop: Optional[PropertiesDict] = None) -> None:
        self.__dict: PropertiesDict = prop if prop is not None else {}
    @staticmethod
    def calc_count(negnum_dict: dict[int, int], negated_number: int = 0) -> int:
        negnum_list = []
        for neg, num in negnum_dict.items():
            negnum_list.extend([neg] * num)
        negnum_list.sort(reverse=True)
        current_negnum = negnum_list[0]
        current_count = 0
        for n in negnum_list:
            if n < negated_number:
                break
            elif n == current_negnum:
                current_count += 1
            elif current_negnum - n == 1:
                current_count = min(0, -current_count) + 1
                current_negnum = n
            else:
                current_count = 1
                current_negnum = n
        return max(0, current_count) if current_negnum == negated_number else 0
    def overwrite(self, prop: type["BmpObject"], negated: bool) -> None:
        self.__dict[prop] = {int(negated): 1}
    def update(self, prop: type["BmpObject"], negated_level: int) -> None:
        self.__dict.setdefault(prop, {})
        self.__dict[prop].setdefault(negated_level, 0)
        self.__dict[prop][negated_level] += 1
    def remove(self, prop: type["BmpObject"], *, negated_level: int) -> None:
        self.__dict.setdefault(prop, {})
        self.__dict[prop].setdefault(negated_level, 0)
        self.__dict[prop][negated_level] -= 1
    def exist(self, prop: type["BmpObject"]) -> bool:
        return len(self.__dict.get(prop, {}).items()) != 0
    def get(self, prop: type["BmpObject"], *, negated_number: int = 0) -> int:
        if len(self.__dict.get(prop, {}).items()) == 0:
            return 0
        return self.calc_count(self.__dict[prop], negated_number)
    def has(self, prop: type["BmpObject"], *, negated_number: int = 0) -> bool:
        if len(self.__dict.get(prop, {}).items()) == 0:
            return False
        if self.calc_count(self.__dict[prop], negated_number) > 0:
            return True
        return False
    def clear(self) -> None:
        self.__dict.clear()
    def to_dict(self) -> dict[type["BmpObject"], int]:
        return {k: self.calc_count(v) for k, v in self.__dict.items()}

class BmpObject(object):
    json_name: str
    sprite_name: str
    display_name: str
    def __init__(self, pos: spaces.Coord, orient: spaces.Orient = spaces.Orient.S, *, world_info: Optional[WorldPointerExtraJson] = None, level_info: Optional[LevelPointerExtraJson] = None) -> None:
        self.uuid: uuid.UUID = uuid.uuid4()
        self.x: int = pos[0]
        self.y: int = pos[1]
        self.orient: spaces.Orient = orient
        self.world_info: Optional[WorldPointerExtraJson] = world_info
        self.level_info: Optional[LevelPointerExtraJson] = level_info
        self.properties: Properties = Properties()
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
    def set_sprite(self, **kwds) -> None:
        self.sprite_state = 0
    def to_json(self) -> BmpObjectJson:
        json_object: BmpObjectJson = {"type": self.json_name, "position": (self.x, self.y), "orientation": spaces.orient_to_str(self.orient)}
        if self.world_info is not None:
            json_object = {**json_object, "world": self.world_info}
        if self.level_info is not None:
            json_object = {**json_object, "level": self.level_info}
        return json_object

class Static(BmpObject):
    def set_sprite(self, **kwds) -> None:
        self.sprite_state = 0

class Tiled(BmpObject):
    def set_sprite(self, connected: Optional[dict[spaces.Orient, bool]] = None, **kwds) -> None:
        connected = {spaces.Orient.W: False, spaces.Orient.S: False, spaces.Orient.A: False, spaces.Orient.D: False} if connected is None else connected
        self.sprite_state = (connected[spaces.Orient.D] * 0x1) | (connected[spaces.Orient.W] * 0x2) | (connected[spaces.Orient.A] * 0x4) | (connected[spaces.Orient.S] * 0x8)

class Animated(BmpObject):
    def set_sprite(self, round_num: int = 0, **kwds) -> None:
        self.sprite_state = round_num % 4

class Directional(BmpObject):
    def set_sprite(self, **kwds) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8

class AnimatedDirectional(BmpObject):
    def set_sprite(self, round_num: int = 0, **kwds) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | round_num % 4

class Character(BmpObject):
    def set_sprite(self, **kwds) -> None:
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
    display_name: str = "Baba"

class Keke(Character):
    json_name: str = "keke"
    sprite_name: str = "keke"
    display_name: str = "Keke"

class Me(Character):
    json_name: str = "me"
    sprite_name: str = "me"
    display_name: str = "Me"

class Patrick(Directional):
    json_name: str = "patrick"
    sprite_name: str = "patrick"
    display_name: str = "Patrick"

class Skull(Directional):
    json_name: str = "skull"
    sprite_name: str = "skull"
    display_name: str = "Skull"

class Ghost(Directional):
    json_name: str = "ghost"
    sprite_name: str = "ghost"
    display_name: str = "Ghost"

class Wall(Tiled):
    json_name: str = "wall"
    sprite_name: str = "wall"
    display_name: str = "Wall"

class Hedge(Tiled):
    json_name: str = "hedge"
    sprite_name: str = "hedge"
    display_name: str = "Hedge"

class Ice(Tiled):
    json_name: str = "ice"
    sprite_name: str = "ice"
    display_name: str = "Ice"

class Tile(Static):
    json_name: str = "tile"
    sprite_name: str = "tile"
    display_name: str = "Tile"

class Grass(Tiled):
    json_name: str = "grass"
    sprite_name: str = "grass"
    display_name: str = "Grass"

class Water(Tiled):
    json_name: str = "water"
    sprite_name: str = "water"
    display_name: str = "Water"

class Lava(Tiled):
    json_name: str = "lava"
    sprite_name: str = "lava"
    display_name: str = "Lava"

class Door(Static):
    json_name: str = "door"
    sprite_name: str = "door"
    display_name: str = "Door"

class Key(Static):
    json_name: str = "key"
    sprite_name: str = "key"
    display_name: str = "Key"

class Box(Static):
    json_name: str = "box"
    sprite_name: str = "box"
    display_name: str = "Box"

class Rock(Static):
    json_name: str = "rock"
    sprite_name: str = "rock"
    display_name: str = "Rock"

class Fruit(Static):
    json_name: str = "fruit"
    sprite_name: str = "fruit"
    display_name: str = "Fruit"

class Belt(AnimatedDirectional):
    json_name: str = "belt"
    sprite_name: str = "belt"
    display_name: str = "Belt"

class Sun(Static):
    json_name: str = "sun"
    sprite_name: str = "sun"
    display_name: str = "Sun"

class Moon(Static):
    json_name: str = "moon"
    sprite_name: str = "moon"
    display_name: str = "Moon"

class Star(Static):
    json_name: str = "star"
    sprite_name: str = "star"
    display_name: str = "Star"

class What(Static):
    json_name: str = "what"
    sprite_name: str = "what"
    display_name: str = "What"

class Love(Static):
    json_name: str = "love"
    sprite_name: str = "love"
    display_name: str = "Love"

class Flag(Static):
    json_name: str = "flag"
    sprite_name: str = "flag"
    display_name: str = "Flag"

class Line(Tiled):
    json_name: str = "line"
    sprite_name: str = "line"
    display_name: str = "Line"

class Dot(Tiled):
    json_name: str = "dot"
    sprite_name: str = "dot"
    display_name: str = "Dot"

class Cursor(Static):
    json_name: str = "cursor"
    sprite_name: str = "cursor"
    display_name: str = "Cursor"

class All(BmpObject):
    pass

class Empty(BmpObject):
    pass

class LevelPointer(BmpObject):
    level_info: LevelPointerExtraJson
    def __init__(self, pos: tuple[int, int], orient: spaces.Orient = spaces.Orient.S, *, world_info: Optional[WorldPointerExtraJson] = None, level_info: LevelPointerExtraJson) -> None:
        super().__init__(pos, orient, world_info=world_info, level_info=level_info)

class Level(LevelPointer):
    json_name: str = "level"
    sprite_name: str = "level"
    display_name: str = "Level"

class WorldPointer(BmpObject):
    world_info: WorldPointerExtraJson
    def __init__(self, pos: tuple[int, int], orient: spaces.Orient = spaces.Orient.S, *, world_info: WorldPointerExtraJson, level_info: Optional[LevelPointerExtraJson] = None) -> None:
        super().__init__(pos, orient, world_info=world_info, level_info=level_info)

class World(WorldPointer):
    json_name: str = "world"
    sprite_name: str = "world"
    display_name: str = "World"
        
class Clone(WorldPointer):
    json_name: str = "clone"
    sprite_name: str = "clone"
    display_name: str = "Clone"

class Game(BmpObject):
    def __init__(self, pos: tuple[int, int], orient: spaces.Orient = spaces.Orient.S, *, obj_type: type[BmpObject], world_info: WorldPointerExtraJson | None = None, level_info: LevelPointerExtraJson | None = None) -> None:
        super().__init__(pos, orient, world_info=world_info, level_info=level_info)
        self.obj_type: type[BmpObject] = obj_type
    @property
    def sprite_name(self) -> str:
        return self.obj_type.sprite_name
    @sprite_name.getter
    def sprite_name(self) -> str:
        return self.obj_type.sprite_name
    json_name: str = "game"
    display_name: str = "Game"

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
    display_name: str = "BABA"

class TextKeke(Noun):
    obj_type: type[BmpObject] = Keke
    json_name: str = "text_keke"
    sprite_name: str = "text_keke"
    display_name: str = "KEKE"

class TextMe(Noun):
    obj_type: type[BmpObject] = Me
    json_name: str = "text_me"
    sprite_name: str = "text_me"
    display_name: str = "ME"

class TextPatrick(Noun):
    obj_type: type[BmpObject] = Patrick
    json_name: str = "text_patrick"
    sprite_name: str = "text_patrick"
    display_name: str = "PATRICK"

class TextSkull(Noun):
    obj_type: type[BmpObject] = Skull
    json_name: str = "text_skull"
    sprite_name: str = "text_skull"
    display_name: str = "SKULL"

class TextGhost(Noun):
    obj_type: type[BmpObject] = Ghost
    json_name: str = "text_ghost"
    sprite_name: str = "text_ghost"
    display_name: str = "GHOST"

class TextWall(Noun):
    obj_type: type[BmpObject] = Wall
    json_name: str = "text_wall"
    sprite_name: str = "text_wall"
    display_name: str = "WALL"

class TextHedge(Noun):
    obj_type: type[BmpObject] = Hedge
    json_name: str = "text_hedge"
    sprite_name: str = "text_hedge"
    display_name: str = "HEDGE"

class TextIce(Noun):
    obj_type: type[BmpObject] = Ice
    json_name: str = "text_ice"
    sprite_name: str = "text_ice"
    display_name: str = "ICE"

class TextTile(Noun):
    obj_type: type[BmpObject] = Tile
    json_name: str = "text_tile"
    sprite_name: str = "text_tile"
    display_name: str = "TILE"

class TextGrass(Noun):
    obj_type: type[BmpObject] = Grass
    json_name: str = "text_grass"
    sprite_name: str = "text_grass"
    display_name: str = "GARSS"

class TextWater(Noun):
    obj_type: type[BmpObject] = Water
    json_name: str = "text_water"
    sprite_name: str = "text_water"
    display_name: str = "WATER"

class TextLava(Noun):
    obj_type: type[BmpObject] = Lava
    json_name: str = "text_lava"
    sprite_name: str = "text_lava"
    display_name: str = "LAVA"

class TextDoor(Noun):
    obj_type: type[BmpObject] = Door
    json_name: str = "text_door"
    sprite_name: str = "text_door"
    display_name: str = "DOOR"

class TextKey(Noun):
    obj_type: type[BmpObject] = Key
    json_name: str = "text_key"
    sprite_name: str = "text_key"
    display_name: str = "KEY"

class TextBox(Noun):
    obj_type: type[BmpObject] = Box
    json_name: str = "text_box"
    sprite_name: str = "text_box"
    display_name: str = "BOX"

class TextRock(Noun):
    obj_type: type[BmpObject] = Rock
    json_name: str = "text_rock"
    sprite_name: str = "text_rock"
    display_name: str = "ROCK"

class TextFruit(Noun):
    obj_type: type[BmpObject] = Fruit
    json_name: str = "text_fruit"
    sprite_name: str = "text_fruit"
    display_name: str = "FRUIT"

class TextBelt(Noun):
    obj_type: type[BmpObject] = Belt
    json_name: str = "text_belt"
    sprite_name: str = "text_belt"
    display_name: str = "BELT"

class TextSun(Noun):
    obj_type: type[BmpObject] = Sun
    json_name: str = "text_sun"
    sprite_name: str = "text_sun"
    display_name: str = "SUN"

class TextMoon(Noun):
    obj_type: type[BmpObject] = Moon
    json_name: str = "text_moon"
    sprite_name: str = "text_moon"
    display_name: str = "MOON"

class TextStar(Noun):
    obj_type: type[BmpObject] = Star
    json_name: str = "text_star"
    sprite_name: str = "text_star"
    display_name: str = "STAR"

class TextWhat(Noun):
    obj_type: type[BmpObject] = What
    json_name: str = "text_what"
    sprite_name: str = "text_what"
    display_name: str = "WHAT"

class TextLove(Noun):
    obj_type: type[BmpObject] = Love
    json_name: str = "text_love"
    sprite_name: str = "text_love"
    display_name: str = "LOVE"

class TextFlag(Noun):
    obj_type: type[BmpObject] = Flag
    json_name: str = "text_flag"
    sprite_name: str = "text_flag"
    display_name: str = "FLAG"

class TextLine(Noun):
    obj_type: type[BmpObject] = Line
    json_name: str = "text_line"
    sprite_name: str = "text_line"
    display_name: str = "LINE"

class TextDot(Noun):
    obj_type: type[BmpObject] = Dot
    json_name: str = "text_dot"
    sprite_name: str = "text_dot"
    display_name: str = "DOT"

class TextCursor(Noun):
    obj_type: type[BmpObject] = Cursor
    json_name: str = "text_cursor"
    sprite_name: str = "text_cursor"
    display_name: str = "CURSOR"

class TextAll(Noun):
    obj_type: type[BmpObject] = All
    json_name: str = "text_all"
    sprite_name: str = "text_all"
    display_name: str = "ALL"

class TextEmpty(Noun):
    obj_type: type[BmpObject] = Empty
    json_name: str = "text_empty"
    sprite_name: str = "text_empty"
    display_name: str = "EMPTY"

class TextText(Noun):
    obj_type: type[BmpObject] = Text
    json_name: str = "text_text"
    sprite_name: str = "text_text"
    display_name: str = "TEXT"

class TextLevel(Noun):
    obj_type: type[BmpObject] = Level
    json_name: str = "text_level"
    sprite_name: str = "text_level"
    display_name: str = "LEVEL"

class TextWorld(Noun):
    obj_type: type[BmpObject] = World
    json_name: str = "text_world"
    sprite_name: str = "text_world"
    display_name: str = "WORLD"

class TextClone(Noun):
    obj_type: type[BmpObject] = Clone
    json_name: str = "text_clone"
    sprite_name: str = "text_clone"
    display_name: str = "CLONE"

class TextGame(Noun):
    obj_type: type[BmpObject] = Game
    json_name: str = "text_game"
    sprite_name: str = "text_game"
    display_name: str = "GAME"

class TextOften(Prefix):
    json_name: str = "text_often"
    sprite_name: str = "text_often"
    display_name: str = "OFTEN"

class TextSeldom(Prefix):
    json_name: str = "text_seldom"
    sprite_name: str = "text_seldom"
    display_name: str = "SELDOM"

class TextMeta(Prefix):
    json_name: str = "text_meta"
    sprite_name: str = "text_meta"
    display_name: str = "META"

class TextText_(Text):
    json_name: str = "text_text_"
    sprite_name: str = "text_text_underline"
    display_name: str = "TEXT_"

class TextOn(Infix):
    json_name: str = "text_on"
    sprite_name: str = "text_on"
    display_name: str = "ON"

class TextNear(Infix):
    json_name: str = "text_near"
    sprite_name: str = "text_near"
    display_name: str = "NEAR"

class TextNextto(Infix):
    json_name: str = "text_nextto"
    sprite_name: str = "text_nextto"
    display_name: str = "NEXTTO"

class TextWithout(Infix):
    json_name: str = "text_without"
    sprite_name: str = "text_without"
    display_name: str = "WITHOUT"

class TextFeeling(Infix):
    json_name: str = "text_feeling"
    sprite_name: str = "text_feeling"
    display_name: str = "FEELING"

class TextIs(Operator):
    json_name: str = "text_is"
    sprite_name: str = "text_is"
    display_name: str = "IS"

class TextHas(Operator):
    json_name: str = "text_has"
    sprite_name: str = "text_has"
    display_name: str = "HAS"

class TextMake(Operator):
    json_name: str = "text_make"
    sprite_name: str = "text_make"
    display_name: str = "MAKE"

class TextWrite(Operator):
    json_name: str = "text_write"
    sprite_name: str = "text_write"
    display_name: str = "WRITE"

class TextNot(Text):
    json_name: str = "text_not"
    sprite_name: str = "text_not"
    display_name: str = "NOT"

class TextNeg(Text):
    json_name: str = "text_neg"
    sprite_name: str = "text_neg"
    display_name: str = "NEG"

class TextAnd(Text):
    json_name: str = "text_and"
    sprite_name: str = "text_and"
    display_name: str = "AND"

class TextYou(Property):
    json_name: str = "text_you"
    sprite_name: str = "text_you"
    display_name: str = "YOU"

class TextMove(Property):
    json_name: str = "text_move"
    sprite_name: str = "text_move"
    display_name: str = "MOVE"

class TextStop(Property):
    json_name: str = "text_stop"
    sprite_name: str = "text_stop"
    display_name: str = "STOP"

class TextPush(Property):
    json_name: str = "text_push"
    sprite_name: str = "text_push"
    display_name: str = "PUSH"

class TextSink(Property):
    json_name: str = "text_sink"
    sprite_name: str = "text_sink"
    display_name: str = "SINK"

class TextFloat(Property):
    json_name: str = "text_float"
    sprite_name: str = "text_float"
    display_name: str = "FLOAT"

class TextOpen(Property):
    json_name: str = "text_open"
    sprite_name: str = "text_open"
    display_name: str = "OPEN"

class TextShut(Property):
    json_name: str = "text_shut"
    sprite_name: str = "text_shut"
    display_name: str = "SHUT"

class TextHot(Property):
    json_name: str = "text_hot"
    sprite_name: str = "text_hot"
    display_name: str = "HOT"

class TextMelt(Property):
    json_name: str = "text_melt"
    sprite_name: str = "text_melt"
    display_name: str = "MELT"

class TextWin(Property):
    json_name: str = "text_win"
    sprite_name: str = "text_win"
    display_name: str = "WIN"

class TextDefeat(Property):
    json_name: str = "text_defeat"
    sprite_name: str = "text_defeat"
    display_name: str = "DEFEAT"

class TextShift(Property):
    json_name: str = "text_shift"
    sprite_name: str = "text_shift"
    display_name: str = "SHIFT"

class TextTele(Property):
    json_name: str = "text_tele"
    sprite_name: str = "text_tele"
    display_name: str = "TELE"

class TextEnter(Property):
    json_name: str = "text_enter"
    sprite_name: str = "text_enter"
    display_name: str = "ENTER"

class TextLeave(Property):
    json_name: str = "text_leave"
    sprite_name: str = "text_leave"
    display_name: str = "LEAVE"

class TextWord(Property):
    json_name: str = "text_word"
    sprite_name: str = "text_word"
    display_name: str = "WORD"

class TextSelect(Property):
    json_name: str = "text_select"
    sprite_name: str = "text_select"
    display_name: str = "SELECT"

class TextTextPlus(Property):
    json_name: str = "text_text+"
    sprite_name: str = "text_text_plus"
    display_name: str = "TEXT+"

class TextTextMinus(Property):
    json_name: str = "text_text-"
    sprite_name: str = "text_text_minus"
    display_name: str = "TEXT-"

class TextEnd(Property):
    json_name: str = "text_end"
    sprite_name: str = "text_end"
    display_name: str = "END"

class TextDone(Property):
    json_name: str = "text_done"
    sprite_name: str = "text_done"
    display_name: str = "DONE"

class Metatext(Noun):
    base_obj_type: type[Text]
    meta_tier: int
    
def same_float_prop(obj_1: BmpObject, obj_2: BmpObject):
    return not (obj_1.properties.has(TextFloat) ^ obj_2.properties.has(TextFloat))

noun_class_list: list[type[Noun]] = []
noun_class_list.extend([TextBaba, TextKeke, TextMe, TextPatrick, TextSkull, TextGhost])
noun_class_list.extend([TextWall, TextHedge, TextIce, TextTile, TextGrass, TextWater, TextLava])
noun_class_list.extend([TextDoor, TextKey, TextBox, TextRock, TextFruit, TextBelt, TextSun, TextMoon, TextStar, TextWhat, TextLove, TextFlag])
noun_class_list.extend([TextLine, TextDot, TextCursor, TextAll, TextText, TextLevel, TextWorld, TextClone, TextGame])

text_class_list: list[type[Text]] = []
text_class_list.extend(noun_class_list)
text_class_list.extend([TextText_, TextOften, TextSeldom, TextMeta])
text_class_list.extend([TextOn, TextNear, TextNextto, TextWithout, TextFeeling])
text_class_list.extend([TextIs, TextHas, TextMake, TextWrite])
text_class_list.extend([TextNot, TextNeg, TextAnd])
text_class_list.extend([TextYou, TextMove, TextStop, TextPush, TextSink, TextFloat, TextOpen, TextShut, TextHot, TextMelt, TextWin, TextDefeat, TextShift, TextTele])
text_class_list.extend([TextEnter, TextLeave, TextWord, TextSelect, TextTextPlus, TextTextMinus, TextEnd, TextDone])

object_used: list[type[BmpObject]] = []
object_used.extend([Baba, Keke, Me, Patrick, Skull, Ghost])
object_used.extend([Wall, Hedge, Ice, Tile, Grass, Water, Lava])
object_used.extend([Door, Key, Box, Rock, Fruit, Belt, Sun, Moon, Star, What, Love, Flag])
object_used.extend([Line, Dot, Cursor, Level, World, Clone])
object_used.extend(text_class_list)

object_class_used = object_used[:]
object_class_used.extend([All, Empty, Text, Game, TextEmpty])

object_name: dict[str, type[BmpObject]] = {t.json_name: t for t in object_used}

not_in_all: tuple[type[BmpObject], ...] = (All, Empty, Text, Level, WorldPointer, Game)
in_not_all: tuple[type[BmpObject], ...] = (Text, Empty, Game)
not_in_editor: tuple[type[BmpObject], ...] = (All, Empty, TextEmpty, Text, Game)

metatext_class_dict: dict[int, list[type[Metatext]]] = {}
current_metatext_tier: int = basics.options["metatext"]["tier"]

def generate_metatext(T: type[Text]) -> type[Metatext]:
    new_type_name = "Text" + T.__name__
    new_type_tier = new_type_name.count("Text") - (1 if new_type_name[-4:] != "Text" and new_type_name[-5:] != "Text_" else 2)
    new_type_base = T.base_obj_type if issubclass(T, Metatext) else T
    new_type_vars: dict[str, Any] = {"json_name": "text_" + T.json_name,
                                     "sprite_name": T.sprite_name,
                                     "obj_type": T,
                                     "base_obj_type": new_type_base,
                                     "meta_tier": new_type_tier,
                                     "display_name": "TEXT_" + T.display_name}
    new_type: type[Metatext] = type(new_type_name, (Metatext, ), new_type_vars)
    return new_type

def generate_metatext_at_tier(tier: int) -> list[type[Metatext]]:
    if metatext_class_dict.get(tier) is not None:
        return metatext_class_dict[tier]
    if tier < 1:
        raise ValueError(str(tier))
    if tier == 1:
        new_metatext_class_list: list[type[Metatext]] = []
        for noun in text_class_list:
            new_metatext_class_list.append(generate_metatext(noun))
        metatext_class_dict[1] = new_metatext_class_list
        for new_type in new_metatext_class_list:
            object_class_used.append(new_type)
            object_used.append(new_type)
            object_name[new_type.json_name] = new_type
            noun_class_list.append(new_type)
            text_class_list.append(new_type)
        return new_metatext_class_list
    old_metatext_class_list = generate_metatext_at_tier(tier - 1)
    new_metatext_class_list: list[type[Metatext]] = []
    for noun in old_metatext_class_list:
        new_metatext_class_list.append(generate_metatext(noun))
    metatext_class_dict[tier] = new_metatext_class_list
    for new_type in new_metatext_class_list:
        object_class_used.append(new_type)
        object_used.append(new_type)
        object_name[new_type.json_name] = new_type
        noun_class_list.append(new_type)
        text_class_list.append(new_type)
    return new_metatext_class_list

def get_noun_from_type(obj_type: type[BmpObject]) -> type[Noun]:
    global current_metatext_tier
    global object_class_used, object_used, object_name, noun_class_list, text_class_list
    return_value: type[Noun] = TextText
    for noun_type in noun_class_list:
        if obj_type.__name__ == noun_type.obj_type.__name__:
            return noun_type
        if issubclass(obj_type, noun_type.obj_type):
            return_value = noun_type
    if return_value == TextText:
        current_metatext_tier += 1
        generate_metatext_at_tier(current_metatext_tier)
        return get_noun_from_type(obj_type)
    return return_value

if basics.options["metatext"]["enabled"]:
    generate_metatext_at_tier(basics.options["metatext"]["tier"])

def json_to_object(json_object: BmpObjectJson, ver: Optional[str] = None) -> BmpObject:
    global current_metatext_tier
    global object_class_used, object_used, object_name, noun_class_list, text_class_list
    if ver is not None and basics.compare_versions(ver, "3.321") == -1:
        world_info = json_object.get("world")
        level_info = json_object.get("level")
        if type(json_object) == dict and type(level_info) == dict:
            level_info["icon"] = json_object.get("icon")
    else:
        world_info = json_object.get("world")
        level_info = json_object.get("level")
    object_type = object_name.get(json_object["type"])
    if object_type is None:
        current_metatext_tier += 1
        generate_metatext_at_tier(current_metatext_tier)
        return json_to_object(json_object, ver)
    return object_type(pos=json_object["position"],
                       orient=spaces.str_to_orient(json_object["orientation"]),
                       world_info=world_info,
                       level_info=level_info)