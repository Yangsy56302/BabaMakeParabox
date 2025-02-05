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
    def get_info(self) -> str:
        return f'<level "{self.name}">'
    def to_space_id(self) -> "SpaceID":
        index = self.name.find(seperator)
        if index != -1:
            name = self.name[:index]
            infinite_tier = int(self.name[index + len(seperator):])
            return SpaceID(name, infinite_tier)
        return SpaceID(self.name)
    def to_json(self) -> LevelIDJson:
        return {"name": self.name}

class SpaceIDJson(TypedDict):
    name: str
    infinite_tier: int

class SpaceID(object):
    hash_name: str = "SpaceID"
    def __init__(self, name: str, infinite_tier: int = 0) -> None:
        self.name = name
        self.infinite_tier: int = infinite_tier
    def __eq__(self, other: "SpaceID") -> bool:
        if type(self) != type(other):
            return NotImplemented
        return type(other) == type(self) and other.name == self.name and other.infinite_tier == self.infinite_tier
    def __ne__(self, other: "SpaceID") -> bool:
        if type(self) != type(other):
            return NotImplemented
        return not self.__eq__(other)
    def __hash__(self) -> int:
        return hash((self.hash_name, self.name, self.infinite_tier))
    def __str__(self) -> str:
        return (f'{self.name} (inf: {self.infinite_tier})') if self.infinite_tier != 0 else self.name
    def get_info(self) -> str:
        return f'<space "{self.name}", inf: {self.infinite_tier}>'
    def __add__(self, other: int) -> "SpaceID":
        if not isinstance(other, int):
            return NotImplemented
        return type(self)(self.name, self.infinite_tier + other)
    def __iadd__(self, other: int) -> "SpaceID":
        self.infinite_tier += other
        return self
    def __sub__(self, other: int) -> "SpaceID":
        if not isinstance(other, int):
            return NotImplemented
        return type(self)(self.name, self.infinite_tier - other)
    def __isub__(self, other: int) -> "SpaceID":
        self.infinite_tier -= other
        return self
    def to_level_id(self) -> "LevelID":
        if self.infinite_tier != 0:
            return LevelID(self.name + seperator + str(self.infinite_tier))
        return LevelID(self.name)
    def to_json(self) -> SpaceIDJson:
        return {"name": self.name, "infinite_tier": self.infinite_tier}