from dataclasses import dataclass
from typing import TypedDict

class WorldIDJson(TypedDict):
    name: str
    infinite_tier: int

class WorldID(object):
    hash_name: str = "WorldID"
    def __init__(self, name: str, infinite_tier: int = 0) -> None:
        self.name = name
        self.infinite_tier: int = infinite_tier
    def __eq__(self, world_id: "WorldID") -> bool:
        return type(world_id) == type(self) and world_id.name == self.name and world_id.infinite_tier == self.infinite_tier
    def __hash__(self) -> int:
        return hash((self.hash_name, self.name, self.infinite_tier))
    def to_json(self) -> WorldIDJson:
        return {"name": self.name, "infinite_tier": self.infinite_tier}

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
    def to_json(self) -> LevelIDJson:
        return {"name": self.name}