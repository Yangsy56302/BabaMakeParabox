from dataclasses import dataclass
from enum import Enum, StrEnum
from tqdm import tqdm, trange
import json
import os
from typing import Any, Final, Literal, NotRequired, Optional, TypeGuard, TypedDict, Self
import math
import uuid
import bmp.base
import bmp.color
import bmp.lang
import bmp.loc
import bmp.ref

class SpaceObjectExtra(TypedDict):
    static_transform: bmp.loc.SpaceTransform
    dynamic_transform: bmp.loc.SpaceTransform

default_space_extra: SpaceObjectExtra = {
    "static_transform": bmp.loc.default_space_transform.copy(),
    "dynamic_transform": bmp.loc.default_space_transform.copy()
}

class LevelObjectIcon(TypedDict):
    name: str
    color: bmp.color.ColorHex

class LevelObjectExtra(TypedDict):
    icon: LevelObjectIcon

class PathExtra(TypedDict):
    unlocked: bool
    conditions: dict[str, int]

default_level_extra: LevelObjectExtra = {"icon": {"name": "empty", "color": 0xFFFFFF}}

# dict[type[property], dict[negated_number, negated_count]]

@dataclass(init=True, repr=True)
class PropertyInfo[T: "Text"]():
    obj: T
    negated: bool

type PropertyDict = dict[type["Text"], list[PropertyInfo]]

class PropertyStorage(object):
    def __init__(self, prop: Optional[PropertyDict] = None) -> None:
        self.__dict: PropertyDict = prop if prop is not None else {}
    def __bool__(self) -> bool:
        return len(self.__dict) != 0
    def get_info(self) -> str:
        string = f"property storage {self.__dict}"
        return "<" + string + ">"
    @staticmethod
    def calc_count(info_list: list[PropertyInfo], negated: bool = False) -> int:
        if len(info_list) == 0:
            return 0
        if len(info_list) == 1:
            return int(info_list[0].negated == negated)
        return sum([1 for i in info_list if i.negated == negated])
    def update(self, prop: "Text", negated: bool = False) -> None:
        self.__dict.setdefault(type(prop), [])
        self.__dict[type(prop)].append(PropertyInfo(
            obj = prop,
            negated = negated,
        ))
    def exist(self, prop: type["Text"]) -> bool:
        return len(self.__dict.get(prop, [])) != 0
    def count(self, prop: type["Text"], *, negated: bool = False) -> int:
        if self.__dict.get(prop) is None:
            return 0
        return self.calc_count(self.__dict[prop], negated)
    def clear(self) -> None:
        self.__dict.clear()
    def enabled(self, prop: type["Text"]) -> bool:
        return self.count(prop, negated=False) > 0
    def disabled(self, prop: type["Text"]) -> bool:
        return self.count(prop, negated=True) > 0
    def enabled_info[T: "Text"](self, prop: type[T]) -> list[PropertyInfo[T]]:
        return [] if self.disabled(prop) else [i for i in self.__dict.get(prop, []) if not i.negated]
    def disabled_info[T: "Text"](self, prop: type[T]) -> list[PropertyInfo[T]]:
        return [i for i in self.__dict.get(prop, []) if i.negated]
    def enabled_dict(self) -> dict[type["Text"], list[PropertyInfo["Text"]]]:
        return {k: self.enabled_info(k) for k in self.__dict.keys()}
    def disabled_dict(self) -> dict[type["Text"], list[PropertyInfo["Text"]]]:
        return {k: self.disabled_info(k) for k in self.__dict.keys()}
    def enabled_count(self) -> dict[type["Text"], int]:
        return {_k: _v for _k, _v in {k: self.calc_count(v, False) for k, v in self.__dict.items()}.items() if _v != 0}
    def disabled_count(self) -> dict[type["Text"], int]:
        return {_k: _v for _k, _v in {k: self.calc_count(v, True) for k, v in self.__dict.items()}.items() if _v != 0}
    def copy(self) -> "PropertyStorage":
        return PropertyStorage(self.__dict.copy())

class OldObjectState(object):
    def __init__(
        self,
        *,
        uid: Optional[uuid.UUID] = None,
        pos: Optional[bmp.loc.Coord[int]] = None,
        orient: Optional[bmp.loc.Orient] = None,
        prop: Optional[PropertyStorage] = None,
        space: Optional[bmp.ref.SpaceID] = None,
        level: Optional[bmp.ref.LevelID] = None
    ) -> None:
        self.uid: Optional[uuid.UUID] = uid
        self.pos: Optional[bmp.loc.Coord[int]] = pos
        self.orient: Optional[bmp.loc.Orient] = orient
        self.prop: Optional[PropertyStorage] = prop
        self.space: Optional[bmp.ref.SpaceID] = space
        self.level: Optional[bmp.ref.LevelID] = level

special_operators: tuple[type["Operator"], ...]

class SpriteCategory(StrEnum):
    NONE = "none"
    STATIC = "static"
    TILED = "tiled"
    ANIMATED = "animated"
    DIRECTIONAL = "directional"
    ANIMATED_DIRECTIONAL = "animated_directional"
    CHARACTER = "character"

class ObjectJson41(TypedDict):
    type: str
    pos: bmp.loc.Coord[int]
    orient: bmp.loc.OrientStr
    space_id: NotRequired[bmp.ref.SpaceIDJson]
    space_extra: NotRequired[SpaceObjectExtra]
    level_id: NotRequired[bmp.ref.LevelIDJson]
    level_extra: NotRequired[LevelObjectExtra]
    path_extra: NotRequired[PathExtra]

type ObjectJson = ObjectJson41

class Object(object):
    ref_type: type["Object"]
    json_name: str
    sprite_name: str
    sprite_palette: bmp.color.PaletteIndex
    sprite_category: SpriteCategory = SpriteCategory.NONE
    sprite_varients: dict[SpriteCategory, list[int]] = {
        SpriteCategory.STATIC: [0x0],
        SpriteCategory.TILED: list(i for i in range(0x10)),
        SpriteCategory.ANIMATED: list(i for i in range(0x4)),
        SpriteCategory.DIRECTIONAL: list(i * 0x8 for i in range(0x4)),
        SpriteCategory.ANIMATED_DIRECTIONAL: 
            list(i * 0x8 for i in range(0x4)) + \
            list(i * 0x8 + 0x1 for i in range(0x4)) + \
            list(i * 0x8 + 0x2 for i in range(0x4)) + \
            list(i * 0x8 + 0x3 for i in range(0x4)),
        SpriteCategory.CHARACTER:
            list(i * 0x8 for i in range(0x4)) + \
            list(i * 0x8 + 0x1 for i in range(0x4)) + \
            list(i * 0x8 + 0x2 for i in range(0x4)) + \
            list(i * 0x8 + 0x3 for i in range(0x4)),
    }
    def __init__(
        self,
        pos: bmp.loc.Coord[int] = (-1, -1),
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: Optional[bmp.ref.LevelID] = None
    ) -> None:
        self.uid: uuid.UUID = uuid.uuid4()
        self.pos: bmp.loc.Coord[int] = pos
        self.orient: bmp.loc.Orient = direct
        self.direct_mapping: dict[bmp.loc.Orient, bmp.loc.Orient] = {d: d for d in bmp.loc.Orient}
        self.old_state: OldObjectState = OldObjectState()
        self.space_id: Optional[bmp.ref.SpaceID] = space_id
        self.level_id: Optional[bmp.ref.LevelID] = level_id
        self.properties: PropertyStorage = PropertyStorage()
        self.operator_properties: dict[type["Operator"], PropertyStorage] = {o: PropertyStorage() for o in special_operators}
        self.move_number: int = 0
        self.sprite_state: int = 0
    def __eq__(self, obj: "Object") -> bool:
        return self.uid == obj.uid
    def __hash__(self) -> int:
        return hash(self.uid)
    @classmethod
    def get_name(cls, *, language_name: str = bmp.lang.current_language_name) -> str:
        lang_key = f"object.name.{cls.json_name}"
        if lang_key not in bmp.lang.current_language_name:
            if lang_key not in bmp.lang.language_dict[bmp.lang.english]:
                return bmp.base.snake_to_camel(cls.json_name, is_big=True)
            return bmp.lang.fformat(lang_key, language_name=bmp.lang.english)
        return bmp.lang.fformat(lang_key, language_name=language_name)
    def get_info(self) -> str:
        string = f"object {self.json_name} at {self.pos} facing {self.orient}"
        return "<" + string + ">"
    @property
    def x(self) -> int:
        return self.pos[0]
    @x.setter
    def x(self, value: int) -> None:
        self.pos = (value, self.pos[1])
    @property
    def y(self) -> int:
        return self.pos[1]
    @y.setter
    def y(self, value: int) -> None:
        self.pos = (self.pos[0], value)
    def reset_uuid(self) -> None:
        self.uid = uuid.uuid4()
    def set_direct_mapping(self, mapping: dict[bmp.loc.Orient, bmp.loc.Orient]) -> None:
        self.orient = mapping[self.direct_mapping[self.orient]]
        self.direct_mapping = mapping.copy()
    def set_sprite(self, connected: Optional[dict[bmp.loc.Orient, bool]] = None, round_num: int = 0) -> None:
        match self.sprite_category:
            case "none":
                pass
            case "static":
                self.sprite_state = 0
            case "tiled":
                connected = {o: False for o in bmp.loc.Orient} if connected is None else connected
                self.sprite_state = (connected[bmp.loc.Orient.D] * 0x1) | (connected[bmp.loc.Orient.W] * 0x2) | (connected[bmp.loc.Orient.A] * 0x4) | (connected[bmp.loc.Orient.S] * 0x8)
            case "animated":
                self.sprite_state = round_num % 0x4
            case "directional":
                self.sprite_state = int(math.log2(int(self.orient.value))) * 0x8
            case "animated_directional":
                self.sprite_state = int(math.log2(int(self.orient.value))) * 0x8 | round_num % 0x4
            case "character":
                if self.move_number > 0:
                    sprite_state_without_orient = (self.sprite_state & 0x3) + 1 if (self.sprite_state & 0x3) != 0x3 else 0x0
                    self.sprite_state = int(math.log2(int(self.orient.value))) * 0x8 | sprite_state_without_orient
                else:
                    self.sprite_state = int(math.log2(int(self.orient.value))) * 0x8 | (self.sprite_state & 0x3)
    @classmethod
    def get_color(cls) -> bmp.color.ColorHex:
        return bmp.color.current_palette[cls.sprite_palette]
    def transform(self: "Object", /, _type: type["Object"]) -> "Object": ...
    def to_json(self) -> ObjectJson:
        json_object: ObjectJson = {"type": self.json_name, "pos": self.pos, "orient": self.orient.name}
        if self.space_id is not None:
            json_object = {**json_object, "space_id": self.space_id.to_json()}
        if self.level_id is not None:
            json_object = {**json_object, "level_id": self.level_id.to_json()}
        return json_object

class NotRealObject(Object):
    pass
Object.ref_type = NotRealObject

class Cursor(Object):
    json_name = "cursor"
    sprite_name = "cursor"
    sprite_category = SpriteCategory.STATIC
    sprite_palette: bmp.color.PaletteIndex = (4, 2)

class Spore(Object):
    json_name = "spore"
    sprite_name = "spore"
    sprite_category = SpriteCategory.STATIC
    sprite_palette: bmp.color.PaletteIndex = (0, 3)

class Blossom(Object):
    json_name = "blossom"
    sprite_name = "blossom"
    sprite_category = SpriteCategory.STATIC
    sprite_palette: bmp.color.PaletteIndex = (0, 3)

class SpaceObject(Object):
    sprite_name = "space"
    sprite_category = SpriteCategory.STATIC
    light_overlay: bmp.color.ColorHex = 0x000000
    dark_overlay: bmp.color.ColorHex = 0xFFFFFF
    def __init__(
        self,
        pos: bmp.loc.Coord[int],
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: Optional[bmp.ref.LevelID] = None,
        space_extra: SpaceObjectExtra = default_space_extra
    ) -> None:
        super().__init__(pos, direct, space_id=space_id, level_id=level_id)
        self.space_extra: SpaceObjectExtra = space_extra.copy()
    def get_info(self) -> str:
        string = super().get_info()[1:-1]
        string += f" stand for space {self.space_id!r}"
        return "<" + string + ">"
    def transform(self: "SpaceObject", /, _type: type["Object"]) -> "Object": ...
    def to_json(self) -> ObjectJson:
        return {**super().to_json(), "space_extra": self.space_extra}

class Space(SpaceObject):
    dark_overlay: bmp.color.ColorHex = 0xC0C0C0
    json_name = "space"
    sprite_palette: bmp.color.PaletteIndex = (1, 3)
        
class Clone(SpaceObject):
    light_overlay: bmp.color.ColorHex = 0x404040
    json_name = "clone"
    sprite_palette: bmp.color.PaletteIndex = (1, 4)

space_object_types: list[type[SpaceObject]] = [Space, Clone]
default_space_object_type: type[SpaceObject] = Space

class LevelObject(Object):
    sprite_category: SpriteCategory = SpriteCategory.STATIC
    def __init__(
        self,
        pos: bmp.loc.Coord[int],
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: Optional[bmp.ref.LevelID],
        level_extra: LevelObjectExtra = default_level_extra
    ) -> None:
        super().__init__(pos, direct, space_id=space_id, level_id=level_id)
        self.level_extra: LevelObjectExtra = level_extra
    def get_info(self) -> str:
        string = super().get_info()[1:-1]
        string += f" stand for level {self.level_id!r}"
        return "<" + string + ">"
    def transform(self: "LevelObject", /, _type: type["Object"]) -> "Object": ...
    def to_json(self) -> ObjectJson:
        return {**super().to_json(), "level_extra": self.level_extra}

class Level(LevelObject):
    json_name = "level"
    sprite_name = "level"
    sprite_palette: bmp.color.PaletteIndex = (4, 1)

level_object_types: tuple[type[LevelObject], ...] = (Level, )
default_level_object_type: type[LevelObject] = Level

class CollectibleJson(TypedDict):
    type: str
    source: bmp.ref.LevelIDJson

class Collectible(object):
    def __init__(self, object_type: type[Object], source: bmp.ref.LevelID) -> None:
        self.object_type: type[Object] = object_type
        self.source: bmp.ref.LevelID = source
    def __eq__(self, collectible: "Collectible") -> bool:
        return type(self) == type(collectible) and self.object_type is collectible.object_type and self.source == collectible.source
    def __hash__(self) -> int:
        return hash((self.object_type.json_name, self.source))
    def to_json(self) -> CollectibleJson:
        return {"type": self.object_type.json_name, "source": self.source.to_json()}

class Path(Object):
    json_name = "path"
    sprite_name = "line"
    sprite_category: SpriteCategory = SpriteCategory.TILED
    sprite_palette: bmp.color.PaletteIndex = (0, 2)
    def __init__(
        self,
        pos: bmp.loc.Coord[int],
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: Optional[bmp.ref.LevelID] = None,
        unlocked: bool = False,
        conditions: Optional[dict[type[Object], int]] = None
    ) -> None:
        super().__init__(pos, direct, space_id=space_id, level_id=level_id)
        self.unlocked: bool = unlocked
        self.conditions: dict[type[Object], int] = conditions if conditions is not None else {}
    def to_json(self) -> ObjectJson:
        return {**super().to_json(), "path_extra": {"unlocked": self.unlocked, "conditions": {k.json_name: v for k, v in self.conditions.items()}}}

class Game(Object):
    def __init__(
        self,
        pos: bmp.loc.Coord[int],
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: Optional[bmp.ref.LevelID] = None,
        ref_type: type[Object]
    ) -> None:
        super().__init__(pos, direct, space_id=space_id, level_id=level_id)
        self.ref_type = ref_type
    json_name = "game"

class TextRenderState(StrEnum):
    UNUSED = "unused"
    USED = "used"
    # CROSSED = "crossed"

class Text(Object):
    json_name = "text"
    sprite_category = SpriteCategory.STATIC
    sprite_palette: bmp.color.PaletteIndex = (0, 3)
    def __init__(
        self,
        pos: tuple[int, int] = (-1, -1),
        direct: bmp.loc.Orient = bmp.loc.Orient.S,
        *,
        space_id: Optional[bmp.ref.SpaceID] = None,
        level_id: Optional[bmp.ref.LevelID] = None
    ) -> None:
        super().__init__(pos, direct, space_id=space_id, level_id=level_id)
        self.render_state: TextRenderState = TextRenderState.UNUSED
    @classmethod
    def get_name(cls, *, language_name: str = bmp.lang.current_language_name) -> str:
        lang_key = f"object.name.{cls.json_name}"
        if lang_key not in bmp.lang.current_language_name:
            if lang_key not in bmp.lang.language_dict[bmp.lang.english]:
                return cls.json_name[5:].upper()
            return bmp.lang.fformat(lang_key, language_name=bmp.lang.english)
        return bmp.lang.fformat(lang_key, language_name=language_name)

class Noun(Text):
    ref_type: type["Object"]
    def isreferenceof(self, other: Object, **kwds) -> bool: ...

class Prefix(Text):
    pass

class Infix(Text):
    pass

class Operator(Text):
    pass

class Property(Text):
    pass

class GeneralNoun(Noun):
    def isreferenceof(self, other: Object, **kwds) -> bool:
        return isinstance(other, self.ref_type)

class TextCursor(GeneralNoun):
    ref_type = Cursor
    json_name = "text_cursor"
    sprite_name = "text_cursor"
    sprite_palette: bmp.color.PaletteIndex = (2, 4)

class TextSpore(GeneralNoun):
    ref_type = Spore
    json_name = "text_spore"
    sprite_name = "text_spore"
    sprite_palette: bmp.color.PaletteIndex = (0, 3)

class TextBlossom(GeneralNoun):
    ref_type = Blossom
    json_name = "text_blossom"
    sprite_name = "text_blossom"
    sprite_palette: bmp.color.PaletteIndex = (0, 3)

class TextText(GeneralNoun):
    ref_type = Text
    json_name = "text_text"
    sprite_name = "text_text"
    sprite_palette: bmp.color.PaletteIndex = (4, 1)

class TextLevelObject(GeneralNoun):
    ref_type = LevelObject

class TextLevel(GeneralNoun):
    ref_type = Level
    json_name = "text_level"
    sprite_name = "text_level"
    sprite_palette = ref_type.sprite_palette

class TextSpaceObject(GeneralNoun):
    ref_type = SpaceObject

class TextSpace(GeneralNoun):
    ref_type = Space
    json_name = "text_space"
    sprite_name = "text_space"
    sprite_palette = ref_type.sprite_palette

class TextClone(GeneralNoun):
    ref_type = Clone
    json_name = "text_clone"
    sprite_name = "text_clone"
    sprite_palette = ref_type.sprite_palette

class TextPath(GeneralNoun):
    ref_type = Path
    json_name = "text_path"
    sprite_name = "text_path"
    sprite_palette = ref_type.sprite_palette

class TextGame(GeneralNoun):
    ref_type = Game
    json_name = "text_game"
    sprite_name = "text_game"
    sprite_palette: bmp.color.PaletteIndex = (4, 2)

class TextOften(Prefix):
    json_name = "text_often"
    sprite_name = "text_often"
    sprite_palette: bmp.color.PaletteIndex = (5, 4)

class TextSeldom(Prefix):
    json_name = "text_seldom"
    sprite_name = "text_seldom"
    sprite_palette: bmp.color.PaletteIndex = (3, 2)

class TextMeta(Prefix):
    json_name = "text_meta"
    sprite_name = "text_meta"
    sprite_palette: bmp.color.PaletteIndex = (4, 1)

class TextText_(Text):
    json_name = "text_text_"
    sprite_name = "text_text_underline"
    sprite_palette: bmp.color.PaletteIndex = (4, 0)

class RangeInfix(Infix):
    find_range: list[bmp.loc.Coord[int]]

class TextOn(RangeInfix):
    json_name = "text_on"
    sprite_name = "text_on"
    find_range = [(0, 0)]

class TextNear(RangeInfix):
    json_name = "text_near"
    sprite_name = "text_near"
    find_range = [(x, y) for x in range(-1, 2) for y in range(-1, 2)]

class TextNextto(RangeInfix):
    json_name = "text_nextto"
    sprite_name = "text_nextto"
    find_range = [
        (-1, 0), (+1, 0),
        (0, -1), (0, +1),
    ]

class TextWithout(Infix):
    json_name = "text_without"
    sprite_name = "text_without"

class TextFeeling(Infix):
    json_name = "text_feeling"
    sprite_name = "text_feeling"

class TextIs(Operator):
    json_name = "text_is"
    sprite_name = "text_is"

class TextHas(Operator):
    json_name = "text_has"
    sprite_name = "text_has"

class TextMake(Operator):
    json_name = "text_make"
    sprite_name = "text_make"

class TextWrite(Operator):
    json_name = "text_write"
    sprite_name = "text_write"

special_operators: tuple[type[Operator], ...] = (TextHas, TextMake, TextWrite)

class TextNot(Text):
    json_name = "text_not"
    sprite_name = "text_not"
    sprite_palette: bmp.color.PaletteIndex = (2, 2)

class TextAnd(Text):
    json_name = "text_and"
    sprite_name = "text_and"
    sprite_palette: bmp.color.PaletteIndex = (0, 3)

class TextYou(Property):
    json_name = "text_you"
    sprite_name = "text_you"
    sprite_palette: bmp.color.PaletteIndex = (4, 1)

class TextMove(Property):
    json_name = "text_move"
    sprite_name = "text_move"
    sprite_palette: bmp.color.PaletteIndex = (5, 4)

class TextStop(Property):
    json_name = "text_stop"
    sprite_name = "text_stop"
    sprite_palette: bmp.color.PaletteIndex = (5, 1)

class TextPush(Property):
    json_name = "text_push"
    sprite_name = "text_push"
    sprite_palette: bmp.color.PaletteIndex = (6, 1)

class TextSink(Property):
    json_name = "text_sink"
    sprite_name = "text_sink"
    sprite_palette: bmp.color.PaletteIndex = (1, 3)

class TextFloat(Property):
    json_name = "text_float"
    sprite_name = "text_float"
    sprite_palette: bmp.color.PaletteIndex = (1, 4)

class TextOpen(Property):
    json_name = "text_open"
    sprite_name = "text_open"
    sprite_palette: bmp.color.PaletteIndex = (2, 4)

class TextShut(Property):
    json_name = "text_shut"
    sprite_name = "text_shut"
    sprite_palette: bmp.color.PaletteIndex = (2, 2)

class TextHot(Property):
    json_name = "text_hot"
    sprite_name = "text_hot"
    sprite_palette: bmp.color.PaletteIndex = (2, 3)

class TextMelt(Property):
    json_name = "text_melt"
    sprite_name = "text_melt"
    sprite_palette: bmp.color.PaletteIndex = (1, 3)

class TextWin(Property):
    json_name = "text_win"
    sprite_name = "text_win"
    sprite_palette: bmp.color.PaletteIndex = (2, 4)

class TextDefeat(Property):
    json_name = "text_defeat"
    sprite_name = "text_defeat"
    sprite_palette: bmp.color.PaletteIndex = (2, 1)

class TextShift(Property):
    json_name = "text_shift"
    sprite_name = "text_shift"
    sprite_palette: bmp.color.PaletteIndex = (1, 3)

class TextTele(Property):
    json_name = "text_tele"
    sprite_name = "text_tele"
    sprite_palette: bmp.color.PaletteIndex = (1, 4)

class TransformProperty(Property):
    sprite_palette: bmp.color.PaletteIndex = (1, 4)

class DirectionalProperty(TransformProperty):
    ref_direct: bmp.loc.Orient
    ref_transform: bmp.loc.SpaceTransform

class DirectFixProperty(DirectionalProperty):
    pass

class TextUp(DirectFixProperty):
    json_name = "text_up"
    sprite_name = "text_up"
    ref_direct = bmp.loc.Orient.W
    ref_transform = {"direct": ref_direct.name, "flip": False}

class TextDown(DirectFixProperty):
    json_name = "text_down"
    sprite_name = "text_down"
    ref_direct = bmp.loc.Orient.S
    ref_transform = {"direct": ref_direct.name, "flip": False}

class TextLeft(DirectFixProperty):
    json_name = "text_left"
    sprite_name = "text_left"
    ref_direct = bmp.loc.Orient.A
    ref_transform = {"direct": ref_direct.name, "flip": False}

class TextRight(DirectFixProperty):
    json_name = "text_right"
    sprite_name = "text_right"
    ref_direct = bmp.loc.Orient.D
    ref_transform = {"direct": ref_direct.name, "flip": False}

direct_fix_properties: list[type[DirectFixProperty]] = [TextLeft, TextUp, TextRight, TextDown]

class DirectRotateProperty(DirectionalProperty):
    pass

class TextTurn(DirectRotateProperty):
    json_name = "text_turn"
    sprite_name = "text_turn"
    ref_direct = bmp.loc.Orient.A
    ref_transform = {"direct": ref_direct.name, "flip": False}

class TextDeturn(DirectRotateProperty):
    json_name = "text_deturn"
    sprite_name = "text_deturn"
    ref_direct = bmp.loc.Orient.D
    ref_transform = {"direct": ref_direct.name, "flip": False}

direct_rotate_properties: list[type[DirectRotateProperty]] = [TextTurn, TextDeturn]

class DirectMappingProperty(TransformProperty):
    ref_mapping: dict[bmp.loc.Orient, bmp.loc.Orient]
    ref_transform: bmp.loc.SpaceTransform

class TextFlip(DirectMappingProperty):
    json_name = "text_flip"
    sprite_name = "text_flip"
    ref_mapping = {
        bmp.loc.Orient.W: bmp.loc.Orient.W,
        bmp.loc.Orient.S: bmp.loc.Orient.S,
        bmp.loc.Orient.A: bmp.loc.Orient.D,
        bmp.loc.Orient.D: bmp.loc.Orient.A,
    }
    ref_transform = {"direct": "S", "flip": True}

direct_mapping_properties: list[type[DirectMappingProperty]] = [TextFlip]

class TextEnter(Property):
    json_name = "text_enter"
    sprite_name = "text_enter"
    sprite_palette: bmp.color.PaletteIndex = (5, 4)
    
class TextLeave(Property):
    json_name = "text_leave"
    sprite_name = "text_leave"
    sprite_palette: bmp.color.PaletteIndex = (2, 2)

class TextBonus(Property):
    json_name = "text_bonus"
    sprite_name = "text_bonus"
    sprite_palette: bmp.color.PaletteIndex = (4, 1)

class TextHide(Property):
    json_name = "text_hide"
    sprite_name = "text_hide"
    sprite_palette: bmp.color.PaletteIndex = (3, 2)

class TextWord(Property):
    json_name = "text_word"
    sprite_name = "text_word"
    sprite_palette: bmp.color.PaletteIndex = (0, 3)

class TextSelect(Property):
    json_name = "text_select"
    sprite_name = "text_select"
    sprite_palette: bmp.color.PaletteIndex = (2, 4)

class TextTextPlus(Property):
    json_name = "text_text+"
    sprite_name = "text_text_plus"
    sprite_palette: bmp.color.PaletteIndex = (4, 1)

class TextTextMinus(Property):
    json_name = "text_text-"
    sprite_name = "text_text_minus"
    sprite_palette: bmp.color.PaletteIndex = (4, 2)

class TextEnd(Property):
    json_name = "text_end"
    sprite_name = "text_end"
    sprite_palette: bmp.color.PaletteIndex = (0, 3)

class TextDone(Property):
    json_name = "text_done"
    sprite_name = "text_done"
    sprite_palette: bmp.color.PaletteIndex = (0, 3)

class Metatext(GeneralNoun):
    ref_type: type[Text]
    basic_ref_type: type[Text]
    meta_tier: int

class SpecialNoun(Noun):
    ref_type: type[NotRealObject] = NotRealObject
    sprite_palette = (0, 3)
    def isreferenceof(self, other: Object, **kwds) -> bool:
        raise NotImplementedError()

class FixedNoun(SpecialNoun):
    def isreferenceof(self, other: Object, **kwds) -> bool:
        return False

class RangedNoun(SpecialNoun):
    ref_type: tuple[type[Noun], ...]
    def isreferenceof(self, other: Object, **kwds) -> bool:
        return any(map(lambda n: n().isreferenceof(other), self.ref_type))

class TextEmpty(SpecialNoun):
    json_name = "text_empty"
    sprite_name = "text_empty"

class TextAll(RangedNoun):
    json_name = "text_all"
    sprite_name = "text_all"
    def isreferenceof(self, other: Object, all_list: list[type[Object]], **kwds) -> bool:
        return any(map(lambda n: get_noun_from_type(n)().isreferenceof(other), all_list))

class GroupNoun(RangedNoun):
    def isreferenceof(self, other: Object, **kwds) -> bool:
        return other.properties.enabled(type(self))

class TextGroup(GroupNoun):
    json_name = "text_group"
    sprite_name = "text_group"
    sprite_palette = (3, 2)

group_noun_types: tuple[type[GroupNoun], ...] = (TextGroup, )

class SpecificSpaceNoun(FixedNoun):
    delta_infinite_tier: int
    def isreferenceof(self, other: Object, **kwds) -> TypeGuard[SpaceObject]:
        return isinstance(other, SpaceObject)

class TextInfinity(SpecificSpaceNoun):
    json_name = "text_infinity"
    sprite_name = "text_infinity"
    delta_infinite_tier = 1
    def isreferenceof(self, other: SpaceObject, **kwds) -> bool:
        if super().isreferenceof(other):
            if other.space_id is not None and other.space_id.infinite_tier > 0:
                return True
        return False

class TextEpsilon(SpecificSpaceNoun):
    json_name = "text_epsilon"
    sprite_name = "text_epsilon"
    delta_infinite_tier = -1
    def isreferenceof(self, other: SpaceObject, **kwds) -> bool:
        if super().isreferenceof(other):
            if other.space_id is not None and other.space_id.infinite_tier < 0:
                return True
        return False

class TextParabox(RangedNoun):
    ref_type = (TextInfinity, TextEpsilon)
    json_name = "text_parabox"
    sprite_name = "text_parabox"
    def isreferenceof(self, other: Object, **kwds) -> TypeGuard[SpaceObject]:
        if super().isreferenceof(other):
            if other.space_id is not None and other.space_id.infinite_tier != 0:
                return True
        return False

def object_transform(self: Object, /, _type: type[Object]) -> Object:
    if isinstance(self, _type):
        return self
    elif _type == Text:
        return get_noun_from_type(type(self))(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
        )
    elif issubclass(_type, SpaceObject):
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
            space_extra = default_space_extra,
        )
    elif issubclass(_type, LevelObject):
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
            level_extra = {
                "icon": {
                    "name": self.sprite_name,
                    "color": self.get_color(),
                }
            },
        )
    elif issubclass(_type, Game):
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
            ref_type = type(self),
        )
    else:
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
        )
Object.transform = object_transform

def space_object_transform(self: SpaceObject, /, _type: type[Object]) -> Object:
    if isinstance(self, _type):
        return self
    elif _type == Text:
        return get_noun_from_type(type(self))(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
        )
    elif issubclass(_type, SpaceObject):
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
            space_extra = self.space_extra,
        )
    elif issubclass(_type, LevelObject):
        return _type(
            self.pos,
            self.orient,
            level_id = self.space_id.to_level_id() if self.space_id is not None else self.level_id,
            space_id = self.space_id,
            level_extra = {
                "icon": {
                    "name": self.sprite_name,
                    "color": self.get_color(),
                }
            },
        )
    elif issubclass(_type, Game):
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
            ref_type = type(self),
        )
    else:
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
        )
SpaceObject.transform = space_object_transform

def level_object_transform(self: LevelObject, /, _type: type[Object]) -> Object:
    if isinstance(self, _type):
        return self
    elif _type == Text:
        return get_noun_from_type(type(self))(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
        )
    elif issubclass(_type, SpaceObject):
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = None, # not final state
            space_extra = default_space_extra,
        )
    elif issubclass(_type, LevelObject):
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
            level_extra = self.level_extra,
        )
    elif issubclass(_type, Game):
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
            ref_type = type(self),
        )
    else:
        return _type(
            self.pos,
            self.orient,
            level_id = self.level_id,
            space_id = self.space_id,
        )
LevelObject.transform = level_object_transform

builtin_object_class_list: list[type[Object]] = [
    *level_object_types,
    *space_object_types,
    Cursor, Spore, Blossom, Path, Game,
]
builtin_noun_class_list: list[type[GeneralNoun]] = [
    TextCursor, TextSpore, TextBlossom, TextText, TextSpace, TextClone, TextLevel, TextPath, TextGame
]
special_noun_class_list: list[type[SpecialNoun]] = [
    TextAll, TextInfinity, TextEpsilon, TextParabox
]
other_text_class_list: list[type[Text]] = [
    TextText_, TextOften, TextSeldom, TextMeta,
    TextOn, TextNear, TextNextto, TextWithout, TextFeeling,
    TextIs, TextHas, TextMake, TextWrite,
    TextNot, TextAnd
]
prop_class_list: list[type[Property]] = [
    TextYou, TextMove, TextStop, TextPush,
    TextSink, TextFloat, TextOpen, TextShut, TextHot, TextMelt,
    TextWin, TextDefeat, TextShift, TextTele,
    TextUp, TextDown, TextLeft, TextRight, TextTurn, TextDeturn, TextFlip,
    TextEnter, TextLeave, TextBonus, TextHide, TextWord, TextSelect, TextTextPlus, TextTextMinus, TextEnd, TextDone
]

instance_exclusive: tuple[type[Object], ...] = (Text, Game)
nouns_not_in_all: tuple[type[Noun], ...] = (SpecialNoun, TextAll, TextText, TextLevelObject, TextSpaceObject, TextGame)
types_not_in_all: tuple[type[Object], ...] = (Text, LevelObject, SpaceObject, Game)
nouns_in_not_all: tuple[type[Noun], ...] = (TextText, )
types_in_not_all: tuple[type[Object], ...] = (Text, )

metatext_class_list_at_tier: list[list[type[Metatext]]]
current_metatext_tier: int

generic_noun_class_list: list[type[GeneralNoun]]
generic_object_class_list: list[type[Object]]
noun_class_list: list[type[Noun]]
text_class_list: list[type[Text]]
object_class_list: list[type[Object]]
name_to_class: dict[str, type[Object]]

class_to_noun: dict[type[Object], type[Noun]]

class SpriteDefinition(TypedDict):
    name: NotRequired[str]
    category: NotRequired[SpriteCategory]
    palette: NotRequired[bmp.color.PaletteIndex]

default_sprite_definition: Final[SpriteDefinition] = {
    "category": SpriteCategory.STATIC,
    "palette": (0, 3)
}

class ObjectDefinition(TypedDict):
    noun: NotRequired["ObjectDefinition"]
    sprite: NotRequired[SpriteDefinition]

def generate_metatext(T: type[Text]) -> type[Metatext]:
    new_type_name = bmp.base.snake_to_camel("text_" + T.json_name, is_big=True)
    new_type_vars: dict[str, Any] = {
        "json_name": "text_" + T.json_name,
        "sprite_name": "text_" + T.sprite_name,
        "ref_type": T,
        "basic_ref_type": T.basic_ref_type if issubclass(T, Metatext) else T,
        "meta_tier": (T.meta_tier if issubclass(T, Metatext) else 0) + 1,
        "sprite_palette": tuple(T.sprite_palette)
    }
    new_type: type[Metatext] = type(new_type_name, (Metatext, ), new_type_vars)
    return new_type

def create_object_class(obj_name: str, obj_def: ObjectDefinition) -> tuple[type[Object], type[GeneralNoun]]:
    noun_def = obj_def.get("noun", {})
    obj_cls_var: dict[str, Any] = {
        "json_name": obj_name,
        "ref_type": NotRealObject,
        "sprite_name": obj_def.get("sprite", default_sprite_definition).get("name", obj_name),
        "sprite_category": obj_def.get("sprite", default_sprite_definition).get("category", default_sprite_definition["category"]),
        "sprite_palette": tuple(obj_def.get("sprite", default_sprite_definition).get("palette", default_sprite_definition["palette"])),
    }
    obj_cls: type[Object] = type(bmp.base.snake_to_camel(obj_name, is_big=True), (Object, ), obj_cls_var)
    noun_cls_var: dict[str, Any] = {
        "json_name": "text_" + obj_name,
        "ref_type": obj_cls,
        "sprite_name": "text_" + obj_cls_var["sprite_name"],
        "sprite_category": "static",
        "sprite_palette": tuple(obj_cls_var["sprite_palette"]),
    }
    _noun_sprite_def = noun_def.get("sprite", {}) 
    if _noun_sprite_def is not None:
        _noun_sprite_name = _noun_sprite_def.get("name")
        if _noun_sprite_name is not None:
            noun_cls_var["sprite_name"] = _noun_sprite_name
        _noun_sprite_category = _noun_sprite_def.get("category")
        if _noun_sprite_category is not None:
            noun_cls_var["sprite_category"] = _noun_sprite_category
        _noun_sprite_palette = _noun_sprite_def.get("palette")
        if _noun_sprite_palette is not None:
            noun_cls_var["sprite_palette"] = tuple(_noun_sprite_palette)
    noun_cls: type[GeneralNoun] = type(bmp.base.snake_to_camel("text_" + obj_name, is_big=True), (GeneralNoun, ), noun_cls_var)
    return obj_cls, noun_cls

def reload_object_class_list() -> None:
    global generic_noun_class_list, generic_object_class_list, \
        noun_class_list, text_class_list, object_class_list, \
            metatext_class_list_at_tier, current_metatext_tier, \
                name_to_class, class_to_noun
    generic_noun_class_list = []
    generic_object_class_list = []
    with open(os.path.join(".", "data", "def", "object.json"), mode="r", encoding="utf-8") as file:
        object_definition_dict: dict[str, ObjectDefinition] = json.load(file)
        for object_name, object_definition in tqdm(
            object_definition_dict.items(),
            desc = bmp.lang.fformat("generating.game.objects"),
            unit = bmp.lang.fformat("object.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            new_object_class, new_noun_class = create_object_class(object_name, object_definition)
            generic_object_class_list.append(new_object_class)
            generic_noun_class_list.append(new_noun_class)
    noun_class_list = [
        *builtin_noun_class_list,
        *special_noun_class_list,
        *generic_noun_class_list,
    ]
    text_class_list = [
        *noun_class_list,
        *other_text_class_list,
        *prop_class_list,
    ]
    if bmp.opt.options["gameplay"]["metatext"]["enabled"]:
        current_metatext_tier = bmp.opt.options["gameplay"]["metatext"]["tier"]
        if current_metatext_tier < 1:
            raise ValueError(current_metatext_tier)
        metatext_class_list_at_tier = [[]]
        metatext_class_list_at_tier.append([generate_metatext(n) for n in text_class_list])
        for metatext_tier in trange(
            2, current_metatext_tier + 1,
            desc = bmp.lang.fformat("generating.objects"),
            unit = bmp.lang.fformat("metatext.name"),
            position = 0,
            **bmp.lang.default_tqdm_args,
        ):
            metatext_class_list_at_tier.append([generate_metatext(n) for n in metatext_class_list_at_tier[metatext_tier - 1]])
    for metatext_class_list in metatext_class_list_at_tier:
        generic_noun_class_list.extend(metatext_class_list)
    noun_class_list = [
        *builtin_noun_class_list,
        *special_noun_class_list,
        *generic_noun_class_list,
    ]
    text_class_list = [
        *noun_class_list,
        *other_text_class_list,
        *prop_class_list,
    ]
    object_class_list = [
        *builtin_object_class_list,
        *generic_object_class_list,
        *text_class_list,
    ]
    name_to_class = {t.json_name: t for t in object_class_list}
    name_to_class["world"] = Space
    name_to_class["text_world"] = TextSpace
    class_to_noun = {t.ref_type: t for t in builtin_noun_class_list + generic_noun_class_list}
    # maybe useless
    # class_to_noun[Game] = TextGame

reload_object_class_list()

def same_float_prop(obj_1: Object, obj_2: Object):
    return not (obj_1.properties.enabled(TextFloat) ^ obj_2.properties.enabled(TextFloat))

def get_noun_from_type(object_type: type[Object]) -> type[Noun]:
    global current_metatext_tier
    global class_to_noun, object_class_list, name_to_class, builtin_noun_class_list, text_class_list
    return_value: Optional[type[Noun]] = class_to_noun.get(object_type)
    if return_value is not None:
        return return_value
    for new_object_type, noun_type in class_to_noun.items():
        if object_type == new_object_type:
            return noun_type
        elif object_type.json_name == new_object_type.json_name:
            return noun_type
        elif issubclass(object_type, new_object_type) and not issubclass(noun_type, TextText):
            return_value = noun_type
    if return_value is None:
        return TextText
    return return_value

type AnyObjectJson = ObjectJson41 | ObjectJson

def formatted_after_41(json_object: AnyObjectJson, ver: str) -> TypeGuard[ObjectJson41]:
    return bmp.base.compare_versions(ver, "4.1") >= 0

def formatted_currently(json_object: AnyObjectJson, ver: str) -> TypeGuard[ObjectJson]:
    return bmp.base.compare_versions(ver, bmp.base.version) == 0

def formatted_from_future(json_object: AnyObjectJson, ver: str) -> TypeGuard[AnyObjectJson]:
    return bmp.base.compare_versions(ver, bmp.base.version) > 0

def update_json_format(json_object: AnyObjectJson, ver: str) -> ObjectJson:
    return json_object # old levelpacks aren't able to update in 4.1

def json_to_object(json_object: ObjectJson) -> Object:
    global current_metatext_tier
    global class_to_noun, object_class_list, name_to_class, builtin_noun_class_list, text_class_list
    object_type = name_to_class.get(json_object["type"])
    space_id: Optional[bmp.ref.SpaceID] = None
    level_id: Optional[bmp.ref.LevelID] = None
    space_id_json = json_object.get("space_id")
    if space_id_json is not None:
        space_id = bmp.ref.SpaceID(**space_id_json)
    level_id_json = json_object.get("level_id")
    if level_id_json is not None:
        level_id = bmp.ref.LevelID(**level_id_json)
    org_space_extra: SpaceObjectExtra = json_object.get("space_extra", default_space_extra)
    org_level_extra: LevelObjectExtra = json_object.get("level_extra", default_level_extra)
    space_extra: SpaceObjectExtra = default_space_extra.copy()
    if org_space_extra is not None:
        space_extra.update(org_space_extra)
    level_extra: LevelObjectExtra = default_level_extra.copy()
    if org_level_extra is not None:
        level_extra.update(org_level_extra)
    pos: bmp.loc.Coord[int] = (json_object["pos"][0], json_object["pos"][1])
    direct = bmp.loc.Orient[json_object["orient"]]
    if object_type is None:
        raise ValueError(json_object["type"])
    if issubclass(object_type, LevelObject):
        if level_id is not None:
            return object_type(
                pos = pos,
                direct = direct,
                space_id = space_id,
                level_id = level_id,
                level_extra = level_extra,
            )
        raise ValueError(level_id)
    if issubclass(object_type, SpaceObject):
        if space_id is not None:
            return object_type(
                pos = pos,
                direct = direct,
                space_id = space_id,
                level_id = level_id,
                space_extra = space_extra,
            )
        raise ValueError(space_id)
    if issubclass(object_type, Path):
        path_extra = json_object.get("path_extra")
        if path_extra is None:
            path_extra = {"unlocked": False, "conditions": {}}
        conditions: dict[type[Object], int] = {name_to_class[k]: v for k, v in path_extra["conditions"].items()}
        return object_type(
            pos = pos,
            direct = direct,
            space_id = space_id,
            level_id = level_id,
            unlocked = path_extra["unlocked"],
            conditions = conditions,
        )
    return object_type(
        pos = pos,
        direct = direct,
        space_id = space_id,
        level_id = level_id,
    )