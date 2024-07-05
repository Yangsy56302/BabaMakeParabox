from typing import Any
import uuid

import baba_make_parabox.spaces as spaces

class Object(object):
    class_name: str = "Object"
    sprite_name: str
    def __init__(self, pos: spaces.Coord, facing: spaces.Direction, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)
        self.uuid: uuid.UUID = uuid.uuid4()
        self.x: int = pos[0]
        self.y: int = pos[1]
        self.facing: spaces.Direction = facing
    def __eq__(self, obj: "Object") -> bool:
        return self.uuid == obj.uuid
    def __str__(self) -> str:
        return self.class_name
    def __repr__(self) -> str:
        return self.class_name

class Text(Object):
    class_name: str = "Text"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class Noun(Text):
    class_name: str = "Noun"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class Operator(Text):
    class_name: str = "Operator"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class Property(Text):
    class_name: str = "Property"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class Baba(Object):
    class_name: str = "Baba"
    sprite_name: str = "baba"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class Wall(Object):
    class_name: str = "Wall"
    sprite_name: str = "wall"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class Box(Object):
    class_name: str = "Box"
    sprite_name: str = "box"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class Rock(Object):
    class_name: str = "Rock"
    sprite_name: str = "rock"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class Flag(Object):
    class_name: str = "Flag"
    sprite_name: str = "flag"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class Level(Object):
    class_name: str = "Level"
    sprite_name: str = "text_level"
    def __init__(self, *args, name, inf_tier, **kwds) -> None:
        super().__init__(*args, **kwds)
        self.name: str = name
        self.inf_tier: int = inf_tier
    def __str__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def __repr__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
        
class Clone(Object):
    class_name: str = "Clone"
    sprite_name: str = "text_level"
    def __init__(self, *args, name, inf_tier, **kwds) -> None:
        super().__init__(*args, **kwds)
        self.name: str = name
        self.inf_tier: int = inf_tier
    def __str__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])
    def __repr__(self) -> str:
        return " ".join([self.class_name, self.name, str(self.inf_tier)])

class EMPTY(Noun):
    class_name: str = "EMPTY"
    sprite_name: str = "text_empty"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class BABA(Noun):
    class_name: str = "BABA"
    sprite_name: str = "text_baba"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class WALL(Noun):
    class_name: str = "WALL"
    sprite_name: str = "text_wall"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class BOX(Noun):
    class_name: str = "BOX"
    sprite_name: str = "text_box"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class ROCK(Noun):
    class_name: str = "ROCK"
    sprite_name: str = "text_rock"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class FLAG(Noun):
    class_name: str = "FLAG"
    sprite_name: str = "text_flag"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class TEXT(Noun):
    class_name: str = "TEXT"
    sprite_name: str = "text_text"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class LEVEL(Noun):
    class_name: str = "LEVEL"
    sprite_name: str = "text_level"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class CLONE(Noun):
    class_name: str = "LEVEL"
    sprite_name: str = "text_level"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class IS(Operator):
    class_name: str = "IS"
    sprite_name: str = "text_is"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class YOU(Property):
    class_name: str = "YOU"
    sprite_name: str = "text_you"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class STOP(Property):
    class_name: str = "STOP"
    sprite_name: str = "text_stop"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class PUSH(Property):
    class_name: str = "PUSH"
    sprite_name: str = "text_push"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

class WIN(Property):
    class_name: str = "WIN"
    sprite_name: str = "text_win"
    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)