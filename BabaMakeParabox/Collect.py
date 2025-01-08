from typing import TypedDict
from BabaMakeParabox import Ref

class CollectibleJson(TypedDict):
    type: str
    source: Ref.LevelIDJson

class Collectible(object):
    json_name: str
    def __init__(self, source: Ref.LevelID) -> None:
        self.source: Ref.LevelID = source
    def __eq__(self, collectible: "Collectible") -> bool:
        return type(self) == type(collectible) and self.source == collectible.source
    def __hash__(self) -> int:
        return hash((self.json_name, self.source))
    def to_json(self) -> CollectibleJson:
        return {"type": self.json_name, "source": self.source.to_json()}

class Spore(Collectible):
    json_name: str = "spore"

class Blossom(Collectible):
    json_name: str = "blossom"

class Bonus(Collectible):
    json_name: str = "bonus"

collectible_dict: dict[type[Collectible], str] = {Spore: Spore.json_name, Blossom: Blossom.json_name, Bonus: Bonus.json_name}