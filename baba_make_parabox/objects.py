from typing import Any
import uuid

import baba_make_parabox.basics as basics
import baba_make_parabox.spaces as spaces

class Object(object):
    class_name: str = "Object"
    sprite_name: str
    def __init__(self, pos: spaces.Coord, facing: spaces.Orient = "W") -> None:
        self.uuid: uuid.UUID = uuid.uuid4()
        self.x: int = pos[0]
        self.y: int = pos[1]
        self.facing: spaces.Orient = facing
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return self.class_name
    def __repr__(self) -> str:
        return self.class_name
    def to_json(self) -> dict[str, basics.JsonObject]:
        return {"type": self.class_name, "position": [self.x, self.y], "orientation": self.facing}

class Text(Object):
    class_name: str = "Text"

class Noun(Text):
    class_name: str = "Noun"

class Operator(Text):
    class_name: str = "Operator"

class Property(Text):
    class_name: str = "Property"

class Baba(Object):
    class_name: str = "Baba"
    sprite_name: str = "baba"

class Keke(Object):
    class_name: str = "Keke"
    sprite_name: str = "keke"

class Wall(Object):
    class_name: str = "Wall"
    sprite_name: str = "wall"

class Box(Object):
    class_name: str = "Box"
    sprite_name: str = "box"

class Rock(Object):
    class_name: str = "Rock"
    sprite_name: str = "rock"

class Flag(Object):
    class_name: str = "Flag"
    sprite_name: str = "flag"

class Level(Object):
    class_name: str = "Level"
    sprite_name: str = "text_level"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, facing: spaces.Orient = "W") -> None:
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
    sprite_name: str = "text_level"
    def __init__(self, pos: spaces.Coord, name: str, inf_tier: int = 0, facing: spaces.Orient = "W") -> None:
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

class KEKE(Noun):
    class_name: str = "KEKE"
    sprite_name: str = "text_keke"

class WALL(Noun):
    class_name: str = "WALL"
    sprite_name: str = "text_wall"

class BOX(Noun):
    class_name: str = "BOX"
    sprite_name: str = "text_box"

class ROCK(Noun):
    class_name: str = "ROCK"
    sprite_name: str = "text_rock"

class FLAG(Noun):
    class_name: str = "FLAG"
    sprite_name: str = "text_flag"

class EMPTY(Noun):
    class_name: str = "EMPTY"
    sprite_name: str = "text_empty"

class TEXT(Noun):
    class_name: str = "TEXT"
    sprite_name: str = "text_text"

class LEVEL(Noun):
    class_name: str = "LEVEL"
    sprite_name: str = "text_level"

class CLONE(Noun):
    class_name: str = "LEVEL"
    sprite_name: str = "text_level"

class IS(Operator):
    class_name: str = "IS"
    sprite_name: str = "text_is"

class YOU(Property):
    class_name: str = "YOU"
    sprite_name: str = "text_you"

class STOP(Property):
    class_name: str = "STOP"
    sprite_name: str = "text_stop"

class PUSH(Property):
    class_name: str = "PUSH"
    sprite_name: str = "text_push"

class MOVE(Property):
    class_name: str = "MOVE"
    sprite_name: str = "text_move"

class WIN(Property):
    class_name: str = "WIN"
    sprite_name: str = "text_win"

object_name: dict[str, type[Object]] = {
    "Baba": Baba,
    "Keke": Keke,
    "Wall": Wall,
    "Box": Box,
    "Rock": Rock,
    "Flag": Flag,
    "Level": Level,
    "Clone": Clone,
    "BABA": BABA,
    "KEKE": KEKE,
    "WALL": WALL,
    "BOX": BOX,
    "ROCK": ROCK,
    "FLAG": FLAG,
    "EMPTY": EMPTY,
    "TEXT": TEXT,
    "LEVEL": LEVEL,
    "CLONE": CLONE,
    "IS": IS,
    "YOU": YOU,
    "STOP": STOP,
    "PUSH": PUSH,
    "MOVE": MOVE,
    "WIN": WIN
}

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