from typing import Optional
import uuid

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces

class Object(object):
    class_name: str = "Object"
    sprite_name: str
    def __init__(self, pos: spaces.Coord, facing: spaces.Orient = "S") -> None:
        self.uuid: uuid.UUID = uuid.uuid4()
        self.x: int = pos[0]
        self.y: int = pos[1]
        self.facing: spaces.Orient = facing
        self.properties: list[type["Property"]] = []
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return self.class_name
    def __repr__(self) -> str:
        return self.class_name
    def new_prop(self, prop: type["Property"]) -> None:
        if prop not in self.properties:
            self.properties.append(prop)
    def del_prop(self, prop: type["Property"]) -> None:
        if prop in self.properties:
            self.properties.remove(prop)
    def has_prop(self, prop: type["Property"]) -> bool:
        if prop in self.properties:
            return True
        return False
    def has_props(self, props: list[type["Property"]]) -> bool:
        for prop in props:
            if prop not in self.properties:
                return False
        return True
    def clear_prop(self) -> None:
        self.properties = []
    def to_json(self) -> dict[str, basics.JsonObject]:
        return {"type": self.class_name, "position": [self.x, self.y], "orientation": self.facing}

class Text(Object):
    class_name: str = "Text"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Noun(Text):
    class_name: str = "Noun"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Operator(Text):
    class_name: str = "Operator"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Property(Text):
    class_name: str = "Property"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Baba(Object):
    class_name: str = "Baba"
    sprite_name: str = "baba"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Keke(Object):
    class_name: str = "Keke"
    sprite_name: str = "keke"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Me(Object):
    class_name: str = "Me"
    sprite_name: str = "me"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Wall(Object):
    class_name: str = "Wall"
    sprite_name: str = "wall"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Water(Object):
    class_name: str = "Water"
    sprite_name: str = "water"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Lava(Object):
    class_name: str = "Lava"
    sprite_name: str = "lava"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Door(Object):
    class_name: str = "Door"
    sprite_name: str = "door"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Key(Object):
    class_name: str = "Key"
    sprite_name: str = "key"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Box(Object):
    class_name: str = "Box"
    sprite_name: str = "box"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Rock(Object):
    class_name: str = "Rock"
    sprite_name: str = "rock"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Flag(Object):
    class_name: str = "Flag"
    sprite_name: str = "flag"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class Level(Object):
    class_name: str = "Level"
    sprite_name: str = "level"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, facing: spaces.Orient = "S") -> None:
        super().__init__(pos, facing)
        self.name: str = name
        self.inf_tier: int = inf_tier
    def __str__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def __repr__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def to_json(self) -> basics.JsonObject:
        json_object = super().to_json()
        json_object.update({"level": {"name": self.name, "infinite_tier": self.inf_tier}})
        return json_object
        
class Clone(Object):
    class_name: str = "Clone"
    sprite_name: str = "clone"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, facing: spaces.Orient = "S") -> None:
        super().__init__(pos, facing)
        self.name: str = name
        self.inf_tier: int = inf_tier
    def __str__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def __repr__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def to_json(self) -> basics.JsonObject:
        json_object = super().to_json()
        json_object.update({"level": {"name": self.name, "infinite_tier": self.inf_tier}})
        return json_object

class BABA(Noun):
    class_name: str = "BABA"
    sprite_name: str = "text_baba"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class KEKE(Noun):
    class_name: str = "KEKE"
    sprite_name: str = "text_keke"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class ME(Noun):
    class_name: str = "ME"
    sprite_name: str = "text_me"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WALL(Noun):
    class_name: str = "WALL"
    sprite_name: str = "text_wall"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WATER(Noun):
    class_name: str = "WATER"
    sprite_name: str = "text_water"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class LAVA(Noun):
    class_name: str = "LAVA"
    sprite_name: str = "text_lava"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class DOOR(Noun):
    class_name: str = "DOOR"
    sprite_name: str = "text_door"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class KEY(Noun):
    class_name: str = "KEY"
    sprite_name: str = "text_key"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class BOX(Noun):
    class_name: str = "BOX"
    sprite_name: str = "text_box"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class ROCK(Noun):
    class_name: str = "ROCK"
    sprite_name: str = "text_rock"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class FLAG(Noun):
    class_name: str = "FLAG"
    sprite_name: str = "text_flag"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class TEXT(Noun):
    class_name: str = "TEXT"
    sprite_name: str = "text_text"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class LEVEL(Noun):
    class_name: str = "LEVEL"
    sprite_name: str = "text_level"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class CLONE(Noun):
    class_name: str = "CLONE"
    sprite_name: str = "text_clone"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class IS(Operator):
    class_name: str = "IS"
    sprite_name: str = "text_is"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class YOU(Property):
    class_name: str = "YOU"
    sprite_name: str = "text_you"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class MOVE(Property):
    class_name: str = "MOVE"
    sprite_name: str = "text_move"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class STOP(Property):
    class_name: str = "STOP"
    sprite_name: str = "text_stop"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class PUSH(Property):
    class_name: str = "PUSH"
    sprite_name: str = "text_push"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class SINK(Property):
    class_name: str = "SINK"
    sprite_name: str = "text_sink"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class FLOAT(Property):
    class_name: str = "FLOAT"
    sprite_name: str = "text_float"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class OPEN(Property):
    class_name: str = "OPEN"
    sprite_name: str = "text_open"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class SHUT(Property):
    class_name: str = "SHUT"
    sprite_name: str = "text_shut"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class HOT(Property):
    class_name: str = "HOT"
    sprite_name: str = "text_hot"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class MELT(Property):
    class_name: str = "MELT"
    sprite_name: str = "text_melt"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WIN(Property):
    class_name: str = "WIN"
    sprite_name: str = "text_win"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class DEFEAT(Property):
    class_name: str = "DEFEAT"
    sprite_name: str = "text_defeat"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class SHIFT(Property):
    class_name: str = "SHIFT"
    sprite_name: str = "text_shift"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class TELE(Property):
    class_name: str = "TELE"
    sprite_name: str = "text_tele"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

class WORD(Property):
    class_name: str = "WORD"
    sprite_name: str = "text_word"
    def __str__(self) -> str:
        return str(super())
    def __repr__(self) -> str:
        return repr(super())

def json_to_object(json_object: basics.JsonObject) -> Object: # oh hell no
    type_name: str = json_object["type"] # type: ignore
    object_type: type[Object] = object_name[type_name]
    if object_type in [Level, Clone]:
        return object_type(pos=tuple(json_object["position"]), # type: ignore
                           name=json_object["level"]["name"], # type: ignore
                           inf_tier=json_object["level"]["infinite_tier"], # type: ignore
                           facing=json_object["orientation"]) # type: ignore
    else:
        return object_type(pos=tuple(json_object["position"]), # type: ignore
                           facing=json_object["orientation"]) # type: ignore

object_name: dict[str, type[Object]] = {
    "Baba": Baba,
    "Keke": Keke,
    "Me": Me,
    "Wall": Wall,
    "Water": Water,
    "Lava": Lava,
    "Box": Box,
    "Rock": Rock,
    "Flag": Flag,
    "Level": Level,
    "Clone": Clone,
    "BABA": BABA,
    "KEKE": KEKE,
    "ME": ME,
    "WALL": WALL,
    "WATER": WATER,
    "LAVA": LAVA,
    "BOX": BOX,
    "ROCK": ROCK,
    "FLAG": FLAG,
    "TEXT": TEXT,
    "LEVEL": LEVEL,
    "CLONE": CLONE,
    "IS": IS,
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
    "WORD": WORD
}

class NounsObjsDicts(object):
    pairs: dict[type[Noun], type[Object]]
    def __init__(self) -> None:
        self.pairs = {}
    def new_pair(self, noun: type[Noun], obj: type[Object]) -> None:
        self.pairs[noun] = obj
    def get_obj(self, noun: type[Noun]) -> type[Object]:
        return self.pairs[noun]
    def get_noun(self, obj: type[Object]) -> type[Noun]:
        return {v: k for k, v in self.pairs.items()}[obj]

nouns_objs_dicts = NounsObjsDicts()

nouns_objs_dicts.new_pair(BABA, Baba)
nouns_objs_dicts.new_pair(KEKE, Keke)
nouns_objs_dicts.new_pair(ME, Me)
nouns_objs_dicts.new_pair(WALL, Wall)
nouns_objs_dicts.new_pair(WATER, Water)
nouns_objs_dicts.new_pair(LAVA, Lava)
nouns_objs_dicts.new_pair(DOOR, Door)
nouns_objs_dicts.new_pair(KEY, Key)
nouns_objs_dicts.new_pair(BOX, Box)
nouns_objs_dicts.new_pair(ROCK, Rock)
nouns_objs_dicts.new_pair(FLAG, Flag)
nouns_objs_dicts.new_pair(LEVEL, Level)
nouns_objs_dicts.new_pair(CLONE, Clone)
nouns_objs_dicts.new_pair(TEXT, Text)