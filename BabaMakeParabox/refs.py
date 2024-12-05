from typing import TypedDict, Final

seperator: Final[str] = " : "

class LevelIDJson(TypedDict):
    name: str

class LevelID(object):
    hash_name: str = "LevelID"
    def __init__(self, name: str) -> None:
        self.name = name
    def __eq__(self, level_id: "LevelID") -> bool:
        return type(level_id) == type(self) and level_id.name == self.name
    def __hash__(self) -> int:
        return hash((self.hash_name, self.name))
    def __str__(self) -> str:
        return self.name
    def __repr__(self) -> str:
        return f"LevelID('{self.name}')"
    def to_world_id(self) -> "WorldID":
        index = self.name.find(seperator)
        if index != -1:
            name = self.name[:index]
            infinite_tier = int(self.name[index + len(seperator):])
            return WorldID(name, infinite_tier)
        return WorldID(self.name)
    def to_json(self) -> LevelIDJson:
        return {"name": self.name}

class WorldIDJson(TypedDict):
    name: str
    infinite_tier: int

class WorldID(object):
    hash_name: str = "WorldID"
    def __init__(self, name: str, infinite_tier: int = 0) -> None:
        self.name = name
        self.infinite_tier: int = infinite_tier
    def __eq__(self, other: "WorldID") -> bool:
        if type(self) != type(other):
            return NotImplemented
        return type(other) == type(self) and other.name == self.name and other.infinite_tier == self.infinite_tier
    def __ne__(self, other: "WorldID") -> bool:
        if type(self) != type(other):
            return NotImplemented
        return not self.__eq__(other)
    def __hash__(self) -> int:
        return hash((self.hash_name, self.name, self.infinite_tier))
    def __repr__(self) -> str:
        return f"WorldID('{self.name}', {self.infinite_tier})"
    def __add__(self, other: int) -> "WorldID":
        if not isinstance(other, int):
            return NotImplemented
        return type(self)(self.name, self.infinite_tier + other)
    def __iadd__(self, other: int) -> "WorldID":
        self.infinite_tier += other
        return self
    def __sub__(self, other: int) -> "WorldID":
        if not isinstance(other, int):
            return NotImplemented
        return type(self)(self.name, self.infinite_tier - other)
    def __isub__(self, other: int) -> "WorldID":
        self.infinite_tier -= other
        return self
    def to_level_id(self) -> "LevelID":
        if self.infinite_tier != 0:
            return LevelID(self.name + seperator + str(self.infinite_tier))
        return LevelID(self.name)
    def to_json(self) -> WorldIDJson:
        return {"name": self.name, "infinite_tier": self.infinite_tier}