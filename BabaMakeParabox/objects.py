from typing import Any, NotRequired, Optional, TypedDict
import math
import uuid
from BabaMakeParabox import basics, collects, colors, refs, spaces
from BabaMakeParabox.spaces import Coord

class WorldPointerExtra(TypedDict):
    pass

default_world_pointer_extra: WorldPointerExtra = {}

class LevelPointerIcon(TypedDict):
    name: str
    color: colors.ColorHex

class LevelPointerExtra(TypedDict):
    icon: LevelPointerIcon

class PathExtra(TypedDict):
    unlocked: bool
    conditions: dict[str, int]

default_level_pointer_extra: LevelPointerExtra = {"icon": {"name": "empty", "color": 0xFFFFFF}}

PropertiesDict = dict[type["Text"], dict[int, int]]

class Properties(object):
    def __init__(self, prop: Optional[PropertiesDict] = None) -> None:
        self.__dict: PropertiesDict = prop if prop is not None else {}
    def __bool__(self) -> bool:
        return len(self.__dict) != 0
    @staticmethod
    def calc_count(negnum_dict: dict[int, int], negated_number: int = 0) -> int:
        if len(negnum_dict) == 0:
            return 0
        if len(negnum_dict) == 1:
            return int(list(negnum_dict.keys())[0] == negated_number)
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
    def overwrite(self, prop: type["Text"], negated: bool) -> None:
        self.__dict[prop] = {int(negated): 1}
    def update(self, prop: type["Text"], negated_level: int) -> None:
        self.__dict.setdefault(prop, {})
        self.__dict[prop].setdefault(negated_level, 0)
        self.__dict[prop][negated_level] += 1
    def remove(self, prop: type["Text"], *, negated_level: int) -> None:
        self.__dict.setdefault(prop, {})
        self.__dict[prop].setdefault(negated_level, 0)
        self.__dict[prop][negated_level] -= 1
    def exist(self, prop: type["Text"]) -> bool:
        return len(self.__dict.get(prop, {}).items()) != 0
    def get_raw(self, prop: type["Text"], *, negated_number: int = 0) -> int:
        if len(self.__dict.get(prop, {}).items()) == 0:
            return 0
        return self.__dict[prop].get(negated_number, 0)
    def get(self, prop: type["Text"], *, negated_number: int = 0) -> int:
        if len(self.__dict.get(prop, {}).items()) == 0:
            return 0
        return self.calc_count(self.__dict[prop], negated_number)
    def has(self, prop: type["Text"], *, negated_number: int = 0) -> bool:
        if len(self.__dict.get(prop, {}).items()) == 0:
            return False
        if self.calc_count(self.__dict[prop], negated_number) > 0:
            return True
        return False
    def clear(self) -> None:
        self.__dict.clear()
    def enabled(self, prop: type["Text"]) -> bool:
        if self.__dict.get(prop) is None:
            return False
        return self.calc_count(self.__dict[prop], 0) > 0
    def disabled(self, prop: type["Text"]) -> bool:
        if self.__dict.get(prop) is None:
            return False
        return self.calc_count(self.__dict[prop], 1) > 0
    def enabled_dict(self) -> dict[type["Text"], int]:
        return {k: self.calc_count(v, 0) for k, v in self.__dict.items()}
    def disabled_dict(self) -> dict[type["Text"], int]:
        return {k: self.calc_count(v, 1) for k, v in self.__dict.items()}

special_operators: list[type["Operator"]] = []

class BmpObjectJson(TypedDict):
    type: str
    position: spaces.Coord
    orientation: spaces.OrientStr
    world_id: NotRequired[refs.WorldIDJson]
    world_pointer_extra: NotRequired[WorldPointerExtra]
    level_id: NotRequired[refs.LevelIDJson]
    level_pointer_extra: NotRequired[LevelPointerExtra]
    path_extra: NotRequired[PathExtra]

class BmpObject(object):
    json_name: str
    sprite_name: str
    display_name: str
    sprite_color: colors.ColorHex
    sprite_varients: list[int] = [0]
    def __init__(self, pos: spaces.Coord, orient: spaces.Orient = spaces.Orient.S, *, world_id: Optional[refs.WorldID] = None, level_id: Optional[refs.LevelID] = None) -> None:
        self.uuid: uuid.UUID = uuid.uuid4()
        self.x: int = pos[0]
        self.y: int = pos[1]
        self.orient: spaces.Orient = orient
        self.world_id: Optional[refs.WorldID] = world_id
        self.level_id: Optional[refs.LevelID] = level_id
        self.properties: Properties = Properties()
        self.special_operator_properties: dict[type["Operator"], Properties] = {o: Properties() for o in special_operators}
        self.move_number: int = 0
        self.sprite_state: int = 0
    def __eq__(self, obj: "BmpObject") -> bool:
        return self.uuid == obj.uuid
    @property
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
        if self.world_id is not None:
            json_object = {**json_object, "world_id": self.world_id.to_json()}
        if self.level_id is not None:
            json_object = {**json_object, "level_id": self.level_id.to_json()}
        return json_object

class Static(BmpObject):
    sprite_varients: list[int] = [0]
    def set_sprite(self, **kwds) -> None:
        self.sprite_state = 0

class Tiled(BmpObject):
    sprite_varients: list[int] = [n for n in range(0x10)]
    def set_sprite(self, connected: Optional[dict[spaces.Orient, bool]] = None, **kwds) -> None:
        connected = {spaces.Orient.W: False, spaces.Orient.S: False, spaces.Orient.A: False, spaces.Orient.D: False} if connected is None else connected
        self.sprite_state = (connected[spaces.Orient.D] * 0x1) | (connected[spaces.Orient.W] * 0x2) | (connected[spaces.Orient.A] * 0x4) | (connected[spaces.Orient.S] * 0x8)

class Animated(BmpObject):
    sprite_varients: list[int] = [n for n in range(0x4)]
    def set_sprite(self, round_num: int = 0, **kwds) -> None:
        self.sprite_state = round_num % 0x4

class Directional(BmpObject):
    sprite_varients: list[int] = [n * 0x8 for n in range(0x4)]
    def set_sprite(self, **kwds) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8

class AnimatedDirectional(BmpObject):
    sprite_varients: list[int] = [n * 0x8 for n in range(0x4)] + [n * 0x8 + 1 for n in range(0x4)] + [n * 0x8 + 2 for n in range(0x4)] + [n * 0x8 + 3 for n in range(0x4)]
    def set_sprite(self, round_num: int = 0, **kwds) -> None:
        self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | round_num % 4

class Character(BmpObject):
    sprite_varients: list[int] = [n * 0x8 for n in range(0x4)] + [n * 0x8 + 1 for n in range(0x4)] + [n * 0x8 + 2 for n in range(0x4)] + [n * 0x8 + 3 for n in range(0x4)]
    def set_sprite(self, **kwds) -> None:
        if self.move_number > 0:
            temp_state = (self.sprite_state & 0x3) + 1 if (self.sprite_state & 0x3) != 0x3 else 0x0
            self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | temp_state
        else:
            self.sprite_state = int(math.log2(spaces.orient_to_int(self.orient))) * 0x8 | (self.sprite_state & 0x3)

class Baba(Character):
    json_name: str = "baba"
    sprite_name: str = "baba"
    display_name: str = "Baba"
    sprite_color: colors.ColorHex = colors.WHITE

class Keke(Character):
    json_name: str = "keke"
    sprite_name: str = "keke"
    display_name: str = "Keke"
    sprite_color: colors.ColorHex = colors.LIGHT_RED

class Me(Character):
    json_name: str = "me"
    sprite_name: str = "me"
    display_name: str = "Me"
    sprite_color: colors.ColorHex = colors.LIGHT_PURPLE

class Patrick(Directional):
    json_name: str = "patrick"
    sprite_name: str = "patrick"
    display_name: str = "Patrick"
    sprite_color: colors.ColorHex = colors.MAGENTA

class Skull(Directional):
    json_name: str = "skull"
    sprite_name: str = "skull"
    display_name: str = "Skull"
    sprite_color: colors.ColorHex = colors.DARK_RED

class Ghost(Directional):
    json_name: str = "ghost"
    sprite_name: str = "ghost"
    display_name: str = "Ghost"
    sprite_color: colors.ColorHex = colors.PINK

class Wall(Tiled):
    json_name: str = "wall"
    sprite_name: str = "wall"
    display_name: str = "Wall"
    sprite_color: colors.ColorHex = colors.DARK_GRAY_BLUE

class Hedge(Tiled):
    json_name: str = "hedge"
    sprite_name: str = "hedge"
    display_name: str = "Hedge"
    sprite_color: colors.ColorHex = colors.DARK_GREEN

class Ice(Tiled):
    json_name: str = "ice"
    sprite_name: str = "ice"
    display_name: str = "Ice"
    sprite_color: colors.ColorHex = colors.DARK_GRAY_BLUE

class Tile(Static):
    json_name: str = "tile"
    sprite_name: str = "tile"
    display_name: str = "Tile"
    sprite_color: colors.ColorHex = colors.DARK_GRAY

class Grass(Tiled):
    json_name: str = "grass"
    sprite_name: str = "grass"
    display_name: str = "Grass"
    sprite_color: colors.ColorHex = colors.DARK_GRAY_GREEN

class Water(Tiled):
    json_name: str = "water"
    sprite_name: str = "water"
    display_name: str = "Water"
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY_BLUE

class Lava(Tiled):
    json_name: str = "lava"
    sprite_name: str = "water"
    display_name: str = "Lava"
    sprite_color: colors.ColorHex = colors.LIGHT_ORANGE

class Door(Static):
    json_name: str = "door"
    sprite_name: str = "door"
    display_name: str = "Door"
    sprite_color: colors.ColorHex = colors.LIGHT_RED

class Key(Static):
    json_name: str = "key"
    sprite_name: str = "key"
    display_name: str = "Key"
    sprite_color: colors.ColorHex = colors.LIGHT_YELLOW

class Box(Static):
    json_name: str = "box"
    sprite_name: str = "box"
    display_name: str = "Box"
    sprite_color: colors.ColorHex = colors.BROWN

class Rock(Static):
    json_name: str = "rock"
    sprite_name: str = "rock"
    display_name: str = "Rock"
    sprite_color: colors.ColorHex = colors.LIGHT_BROWN

class Fruit(Static):
    json_name: str = "fruit"
    sprite_name: str = "fruit"
    display_name: str = "Fruit"
    sprite_color: colors.ColorHex = colors.LIGHT_RED

class Belt(AnimatedDirectional):
    json_name: str = "belt"
    sprite_name: str = "belt"
    display_name: str = "Belt"
    sprite_color: colors.ColorHex = colors.DARK_GRAY_BLUE

class Sun(Static):
    json_name: str = "sun"
    sprite_name: str = "sun"
    display_name: str = "Sun"
    sprite_color: colors.ColorHex = colors.LIGHT_YELLOW

class Moon(Static):
    json_name: str = "moon"
    sprite_name: str = "moon"
    display_name: str = "Moon"
    sprite_color: colors.ColorHex = colors.LIGHT_YELLOW

class Star(Static):
    json_name: str = "star"
    sprite_name: str = "star"
    display_name: str = "Star"
    sprite_color: colors.ColorHex = colors.LIGHT_YELLOW

class What(Static):
    json_name: str = "what"
    sprite_name: str = "what"
    display_name: str = "What"
    sprite_color: colors.ColorHex = colors.WHITE

class Love(Static):
    json_name: str = "love"
    sprite_name: str = "love"
    display_name: str = "Love"
    sprite_color: colors.ColorHex = colors.PINK

class Flag(Static):
    json_name: str = "flag"
    sprite_name: str = "flag"
    display_name: str = "Flag"
    sprite_color: colors.ColorHex = colors.LIGHT_YELLOW

class Line(Tiled):
    json_name: str = "line"
    sprite_name: str = "line"
    display_name: str = "Line"
    sprite_color: colors.ColorHex = colors.WHITE

class Dot(Static):
    json_name: str = "dot"
    sprite_name: str = "dot"
    display_name: str = "Dot"
    sprite_color: colors.ColorHex = colors.WHITE

class Orb(Static):
    json_name: str = "orb"
    sprite_name: str = "orb"
    display_name: str = "Orb"
    sprite_color: colors.ColorHex = colors.MAGENTA

class Cursor(Static):
    json_name: str = "cursor"
    sprite_name: str = "cursor"
    display_name: str = "Cursor"
    sprite_color: colors.ColorHex = colors.PINK

class All(BmpObject):
    pass

class Empty(BmpObject):
    pass

class WorldPointer(BmpObject):
    light_overlay: colors.ColorHex = 0x000000
    dark_overlay: colors.ColorHex = 0xFFFFFF
    def __init__(self, pos: tuple[int, int], orient: spaces.Orient = spaces.Orient.S, *, world_id: refs.WorldID, level_id: Optional[refs.LevelID] = None, world_pointer_extra: WorldPointerExtra = default_world_pointer_extra) -> None:
        self.world_id: refs.WorldID
        super().__init__(pos, orient, world_id=world_id, level_id=level_id)
        self.world_pointer_extra: WorldPointerExtra = world_pointer_extra
    def to_json(self) -> BmpObjectJson:
        return {**super().to_json(), "world_pointer_extra": self.world_pointer_extra}

class World(WorldPointer):
    dark_overlay: colors.ColorHex = 0xC0C0C0
    json_name: str = "world"
    sprite_name: str = "world"
    display_name: str = "World"
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY_BLUE
        
class Clone(WorldPointer):
    light_overlay: colors.ColorHex = 0x404040
    json_name: str = "clone"
    sprite_name: str = "clone"
    display_name: str = "Clone"
    sprite_color: colors.ColorHex = colors.LIGHTER_GRAY_BLUE

world_pointers: list[type[WorldPointer]] = [World, Clone]
default_world_pointer: type[WorldPointer] = World

class LevelPointer(BmpObject):
    def __init__(self, pos: tuple[int, int], orient: spaces.Orient = spaces.Orient.S, *, world_id: Optional[refs.WorldID] = None, level_id: refs.LevelID, level_pointer_extra: LevelPointerExtra = default_level_pointer_extra) -> None:
        self.level_id: refs.LevelID
        super().__init__(pos, orient, world_id=world_id, level_id=level_id)
        self.level_pointer_extra: LevelPointerExtra = level_pointer_extra
    def to_json(self) -> BmpObjectJson:
        return {**super().to_json(), "level_pointer_extra": self.level_pointer_extra}

class Level(LevelPointer):
    json_name: str = "level"
    sprite_name: str = "level"
    display_name: str = "Level"
    sprite_color: colors.ColorHex = colors.MAGENTA

level_pointers: list[type[LevelPointer]] = [Level]
default_level_pointer: type[LevelPointer] = Level

class Path(Tiled):
    json_name: str = "path"
    sprite_name: str = "line"
    display_name: str = "Path"
    sprite_color: colors.ColorHex = colors.SILVER
    def __init__(self, pos: spaces.Coord, orient: spaces.Orient = spaces.Orient.S, *, world_id: Optional[refs.WorldID] = None, level_id: Optional[refs.LevelID] = None, unlocked: bool = False, conditions: Optional[dict[type[collects.Collectible], int]] = None, world_pointer_info: Optional[refs.WorldID] = None, level_pointer_info: Optional[refs.LevelID] = None) -> None:
        super().__init__(pos, orient, world_id=world_pointer_info, level_id=level_pointer_info)
        self.unlocked: bool = unlocked
        self.conditions: dict[type[collects.Collectible], int] = conditions if conditions is not None else {}
    def to_json(self) -> BmpObjectJson:
        return {**super().to_json(), "path_extra": {"unlocked": self.unlocked, "conditions": {k.json_name: v for k, v in self.conditions.items()}}}

class Game(BmpObject):
    def __init__(self, pos: tuple[int, int], orient: spaces.Orient = spaces.Orient.S, *, world_id: Optional[refs.WorldID] = None, level_id: Optional[refs.LevelID] = None, obj_type: type[BmpObject], world_pointer_info: refs.WorldID | None = None, level_pointer_info: refs.LevelID | None = None) -> None:
        super().__init__(pos, orient, world_id=world_pointer_info, level_id=level_pointer_info)
        self.obj_type: type[BmpObject] = obj_type
    json_name: str = "game"
    display_name: str = "Game"
    sprite_color: colors.ColorHex = colors.PINK

class Text(BmpObject):
    pass

class Noun(Text):
    obj_type: type[BmpObject]
    json_name: str
    sprite_name: str
    display_name: str
    sprite_color: colors.ColorHex

class Prefix(Text):
    pass

class Infix(Text):
    sprite_color: colors.ColorHex = colors.WHITE

class Operator(Text):
    sprite_color: colors.ColorHex = colors.WHITE

class Property(Text):
    pass

class TextBaba(Noun):
    obj_type: type[BmpObject] = Baba
    sprite_color: colors.ColorHex = colors.MAGENTA

class TextKeke(Noun):
    obj_type: type[BmpObject] = Keke
    
class TextMe(Noun):
    obj_type: type[BmpObject] = Me

class TextPatrick(Noun):
    obj_type: type[BmpObject] = Patrick

class TextSkull(Noun):
    obj_type: type[BmpObject] = Skull

class TextGhost(Noun):
    obj_type: type[BmpObject] = Ghost

class TextWall(Noun):
    obj_type: type[BmpObject] = Wall
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY

class TextHedge(Noun):
    obj_type: type[BmpObject] = Hedge

class TextIce(Noun):
    obj_type: type[BmpObject] = Ice
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY_BLUE

class TextTile(Noun):
    obj_type: type[BmpObject] = Tile
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY

class TextGrass(Noun):
    obj_type: type[BmpObject] = Grass

class TextWater(Noun):
    obj_type: type[BmpObject] = Water

class TextLava(Noun):
    obj_type: type[BmpObject] = Lava
    sprite_name: str = "text_lava"

class TextDoor(Noun):
    obj_type: type[BmpObject] = Door

class TextKey(Noun):
    obj_type: type[BmpObject] = Key

class TextBox(Noun):
    obj_type: type[BmpObject] = Box

class TextRock(Noun):
    obj_type: type[BmpObject] = Rock
    sprite_color: colors.ColorHex = colors.BROWN

class TextFruit(Noun):
    obj_type: type[BmpObject] = Fruit

class TextBelt(Noun):
    obj_type: type[BmpObject] = Belt
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY_BLUE

class TextSun(Noun):
    obj_type: type[BmpObject] = Sun

class TextMoon(Noun):
    obj_type: type[BmpObject] = Moon

class TextStar(Noun):
    obj_type: type[BmpObject] = Star

class TextWhat(Noun):
    obj_type: type[BmpObject] = What

class TextLove(Noun):
    obj_type: type[BmpObject] = Love

class TextFlag(Noun):
    obj_type: type[BmpObject] = Flag

class TextLine(Noun):
    obj_type: type[BmpObject] = Line

class TextDot(Noun):
    obj_type: type[BmpObject] = Dot

class TextCursor(Noun):
    obj_type: type[BmpObject] = Cursor
    sprite_color: colors.ColorHex = colors.LIGHT_YELLOW

class TextAll(Noun):
    obj_type: type[BmpObject] = All
    json_name: str = "text_all"
    sprite_name: str = "text_all"
    display_name: str = "ALL"
    sprite_color: colors.ColorHex = colors.WHITE

class TextEmpty(Noun):
    obj_type: type[BmpObject] = Empty
    json_name: str = "text_empty"
    sprite_name: str = "text_empty"
    display_name: str = "EMPTY"
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY

class TextText(Noun):
    obj_type: type[BmpObject] = Text
    json_name: str = "text_text"
    sprite_name: str = "text_text"
    display_name: str = "TEXT"
    sprite_color: colors.ColorHex = colors.MAGENTA

class TextWorld(Noun):
    obj_type: type[BmpObject] = World

class TextClone(Noun):
    obj_type: type[BmpObject] = Clone

class TextLevel(Noun):
    obj_type: type[BmpObject] = Level

class TextPath(Noun):
    obj_type: type[BmpObject] = Path
    sprite_name: str = "text_path"

class TextGame(Noun):
    obj_type: type[BmpObject] = Game
    json_name: str = "text_game"
    sprite_name: str = "text_game"
    display_name: str = "GAME"

class TextOften(Prefix):
    json_name: str = "text_often"
    sprite_name: str = "text_often"
    display_name: str = "OFTEN"
    sprite_color: colors.ColorHex = colors.LIGHT_GREEN

class TextSeldom(Prefix):
    json_name: str = "text_seldom"
    sprite_name: str = "text_seldom"
    display_name: str = "SELDOM"
    sprite_color: colors.ColorHex = colors.DARK_BLUE

class TextMeta(Prefix):
    json_name: str = "text_meta"
    sprite_name: str = "text_meta"
    display_name: str = "META"
    sprite_color: colors.ColorHex = colors.MAGENTA

class TextText_(Text):
    json_name: str = "text_text_"
    sprite_name: str = "text_text_underline"
    display_name: str = "TEXT_"
    sprite_color: colors.ColorHex = colors.DARK_MAGENTA

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
    sprite_color: colors.ColorHex = colors.LIGHT_RED

class TextAnd(Text):
    json_name: str = "text_and"
    sprite_name: str = "text_and"
    display_name: str = "AND"
    sprite_color: colors.ColorHex = colors.WHITE

class TextYou(Property):
    json_name: str = "text_you"
    sprite_name: str = "text_you"
    display_name: str = "YOU"
    sprite_color: colors.ColorHex = colors.MAGENTA

class TextMove(Property):
    json_name: str = "text_move"
    sprite_name: str = "text_move"
    display_name: str = "MOVE"
    sprite_color: colors.ColorHex = colors.LIGHT_GREEN

class TextStop(Property):
    json_name: str = "text_stop"
    sprite_name: str = "text_stop"
    display_name: str = "STOP"
    sprite_color: colors.ColorHex = colors.DARK_GREEN

class TextPush(Property):
    json_name: str = "text_push"
    sprite_name: str = "text_push"
    display_name: str = "PUSH"
    sprite_color: colors.ColorHex = colors.BROWN

class TextSink(Property):
    json_name: str = "text_sink"
    sprite_name: str = "text_sink"
    display_name: str = "SINK"
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY_BLUE

class TextFloat(Property):
    json_name: str = "text_float"
    sprite_name: str = "text_float"
    display_name: str = "FLOAT"
    sprite_color: colors.ColorHex = colors.LIGHTER_GRAY_BLUE

class TextOpen(Property):
    json_name: str = "text_open"
    sprite_name: str = "text_open"
    display_name: str = "OPEN"
    sprite_color: colors.ColorHex = colors.LIGHT_YELLOW

class TextShut(Property):
    json_name: str = "text_shut"
    sprite_name: str = "text_shut"
    display_name: str = "SHUT"
    sprite_color: colors.ColorHex = colors.LIGHT_RED

class TextHot(Property):
    json_name: str = "text_hot"
    sprite_name: str = "text_hot"
    display_name: str = "HOT"
    sprite_color: colors.ColorHex = colors.LIGHT_ORANGE

class TextMelt(Property):
    json_name: str = "text_melt"
    sprite_name: str = "text_melt"
    display_name: str = "MELT"
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY_BLUE

class TextWin(Property):
    json_name: str = "text_win"
    sprite_name: str = "text_win"
    display_name: str = "WIN"
    sprite_color: colors.ColorHex = colors.LIGHT_YELLOW

class TextDefeat(Property):
    json_name: str = "text_defeat"
    sprite_name: str = "text_defeat"
    display_name: str = "DEFEAT"
    sprite_color: colors.ColorHex = colors.DARK_RED

class TextShift(Property):
    json_name: str = "text_shift"
    sprite_name: str = "text_shift"
    display_name: str = "SHIFT"
    sprite_color: colors.ColorHex = colors.LIGHT_GRAY_BLUE

class TextTele(Property):
    json_name: str = "text_tele"
    sprite_name: str = "text_tele"
    display_name: str = "TELE"
    sprite_color: colors.ColorHex = colors.LIGHTER_GRAY_BLUE

class TextEnter(Property):
    json_name: str = "text_enter"
    sprite_name: str = "text_enter"
    display_name: str = "ENTER"
    sprite_color: colors.ColorHex = colors.LIGHT_GREEN
    
class TextLeave(Property):
    json_name: str = "text_leave"
    sprite_name: str = "text_leave"
    display_name: str = "LEAVE"
    sprite_color: colors.ColorHex = colors.LIGHT_RED

class TextBonus(Property):
    json_name: str = "text_bonus"
    sprite_name: str = "text_bonus"
    display_name: str = "BONUS"
    sprite_color: colors.ColorHex = colors.MAGENTA

class TextHide(Property):
    json_name: str = "text_hide"
    sprite_name: str = "text_hide"
    display_name: str = "HIDE"
    sprite_color: colors.ColorHex = colors.DARK_BLUE

class TextWord(Property):
    json_name: str = "text_word"
    sprite_name: str = "text_word"
    display_name: str = "WORD"
    sprite_color: colors.ColorHex = colors.WHITE

class TextSelect(Property):
    json_name: str = "text_select"
    sprite_name: str = "text_select"
    display_name: str = "SELECT"
    sprite_color: colors.ColorHex = colors.LIGHT_YELLOW

class TextTextPlus(Property):
    json_name: str = "text_text+"
    sprite_name: str = "text_text_plus"
    display_name: str = "TEXT+"
    sprite_color: colors.ColorHex = colors.MAGENTA

class TextTextMinus(Property):
    json_name: str = "text_text-"
    sprite_name: str = "text_text_minus"
    display_name: str = "TEXT-"
    sprite_color: colors.ColorHex = colors.PINK

class TextEnd(Property):
    json_name: str = "text_end"
    sprite_name: str = "text_end"
    display_name: str = "END"
    sprite_color: colors.ColorHex = colors.WHITE

class TextDone(Property):
    json_name: str = "text_done"
    sprite_name: str = "text_done"
    display_name: str = "DONE"
    sprite_color: colors.ColorHex = colors.WHITE

class Metatext(Noun):
    base_obj_type: type[Text]
    meta_tier: int
    
def same_float_prop(obj_1: BmpObject, obj_2: BmpObject):
    return not (obj_1.properties.has(TextFloat) ^ obj_2.properties.has(TextFloat))

special_operators = [TextHas, TextMake, TextWrite]

noun_class_list: list[type[Noun]] = []
noun_class_list.extend([TextBaba, TextKeke, TextMe, TextPatrick, TextSkull, TextGhost])
noun_class_list.extend([TextWall, TextHedge, TextIce, TextTile, TextGrass, TextWater, TextLava])
noun_class_list.extend([TextDoor, TextKey, TextBox, TextRock, TextFruit, TextBelt, TextSun, TextMoon, TextStar, TextWhat, TextLove, TextFlag])
noun_class_list.extend([TextLine, TextDot, TextCursor, TextAll, TextText])
noun_class_list.extend([TextWorld, TextClone, TextLevel, TextPath, TextGame])

for noun_class in noun_class_list:
    if not hasattr(noun_class, "json_name"):
        setattr(noun_class, "json_name", "text_" + noun_class.obj_type.json_name)
    if not hasattr(noun_class, "sprite_name"):
        setattr(noun_class, "sprite_name", "text_" + noun_class.obj_type.sprite_name)
    if not hasattr(noun_class, "display_name"):
        setattr(noun_class, "display_name", noun_class.obj_type.display_name.upper())
    if not hasattr(noun_class, "sprite_color"):
        setattr(noun_class, "sprite_color", noun_class.obj_type.sprite_color)

text_class_list: list[type[Text]] = []
text_class_list.extend(noun_class_list)
text_class_list.extend([TextText_, TextOften, TextSeldom, TextMeta])
text_class_list.extend([TextOn, TextNear, TextNextto, TextWithout, TextFeeling])
text_class_list.extend([TextIs, TextHas, TextMake, TextWrite])
text_class_list.extend([TextNot, TextAnd])
text_class_list.extend([TextYou, TextMove, TextStop, TextPush, TextSink, TextFloat, TextOpen, TextShut, TextHot, TextMelt, TextWin, TextDefeat, TextShift, TextTele])
text_class_list.extend([TextEnter, TextLeave, TextBonus, TextHide, TextWord, TextSelect, TextTextPlus, TextTextMinus, TextEnd, TextDone])

object_used: list[type[BmpObject]] = []
object_used.extend([Baba, Keke, Me, Patrick, Skull, Ghost])
object_used.extend([Wall, Hedge, Ice, Tile, Grass, Water, Lava])
object_used.extend([Door, Key, Box, Rock, Fruit, Belt, Sun, Moon, Star, What, Love, Flag])
object_used.extend([Line, Dot, Cursor, Level, World, Clone, Game, Path])
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
    new_type_vars: dict[str, Any] = {
        "json_name": "text_" + T.json_name,
        "sprite_name": T.sprite_name,
        "obj_type": T,
        "base_obj_type": new_type_base,
        "meta_tier": new_type_tier,
        "display_name": "TEXT_" + T.display_name,
        "sprite_color": T.sprite_color
    }
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
    world_id: Optional[refs.WorldID] = None
    level_id: Optional[refs.LevelID] = None
    world_pointer_extra: Optional[WorldPointerExtra] = None
    level_pointer_extra: Optional[LevelPointerExtra] = None
    if basics.compare_versions(ver if ver is not None else "0.0", "3.8") == -1:
        old_world_id = json_object.get("world")
        if old_world_id is not None:
            world_id = refs.WorldID(old_world_id.get("name", ""), old_world_id.get("infinite_tier", 0))
        old_level_id = json_object.get("level")
        if old_level_id is not None:
            level_id = refs.LevelID(old_level_id.get("name", ""))
            level_pointer_extra = {"icon": old_level_id.get("icon", default_level_pointer_extra["icon"])}
    else:
        world_id_json = json_object.get("world_id")
        if world_id_json is not None:
            world_id = refs.WorldID(**world_id_json)
        level_id_json = json_object.get("level_id")
        if level_id_json is not None:
            level_id = refs.LevelID(**level_id_json)
        world_pointer_extra = json_object.get("world_pointer_extra")
        level_pointer_extra = json_object.get("level_pointer_extra")
    world_pointer_extra = world_pointer_extra if world_pointer_extra is not None else default_world_pointer_extra
    level_pointer_extra = level_pointer_extra if level_pointer_extra is not None else default_level_pointer_extra
    obj_type = object_name.get(json_object["type"])
    if obj_type is None:
        if json_object["type"].startswith("text_text_"):
            current_metatext_tier += 1
            generate_metatext_at_tier(current_metatext_tier)
            return json_to_object(json_object, ver)
        raise ValueError(json_object["type"])
    if issubclass(obj_type, LevelPointer):
        if level_id is not None:
            return obj_type(pos=json_object["position"],
                            orient=spaces.str_to_orient(json_object["orientation"]),
                            world_id=world_id,
                            level_id=level_id,
                            level_pointer_extra=level_pointer_extra)
        raise ValueError(level_id)
    if issubclass(obj_type, WorldPointer):
        if world_id is not None:
            return obj_type(pos=json_object["position"],
                            orient=spaces.str_to_orient(json_object["orientation"]),
                            world_id=world_id,
                            level_id=level_id,
                            world_pointer_extra=world_pointer_extra)
        raise ValueError(world_id)
    if issubclass(obj_type, Path):
        path_extra = json_object.get("path_extra")
        if path_extra is None:
            path_extra = {"unlocked": False, "conditions": {}}
        reversed_collectible_dict = {v: k for k, v in collects.collectible_dict.items()}
        conditions: dict[type[collects.Collectible], int] = {reversed_collectible_dict[k]: v for k, v in path_extra["conditions"].items()}
        return obj_type(pos=json_object["position"],
                        orient=spaces.str_to_orient(json_object["orientation"]),
                        world_id=world_id,
                        level_id=level_id,
                        unlocked=path_extra["unlocked"],
                        conditions=conditions)
    return obj_type(pos=json_object["position"],
                    orient=spaces.str_to_orient(json_object["orientation"]),
                    world_id=world_id,
                    level_id=level_id)