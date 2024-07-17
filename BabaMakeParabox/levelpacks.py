from typing import Any, Optional

from BabaMakeParabox import basics
from BabaMakeParabox import objects
from BabaMakeParabox import rules
from BabaMakeParabox import levels

class levelpack(object):
    class_name: str = "levelpack"
    def __init__(self, name: str, level_list: list[levels.level], main_level: Optional[str] = None, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name
        self.level_list: list[levels.level] = list(level_list)
        self.main_level: str = main_level if main_level is not None else self.level_list[0].name
        self.rule_list: list[rules.Rule] = rule_list if rule_list is not None else rules.default_rule_list
        if rule_list is not None:
            for level in self.level_list:
                level.rule_list.extend(self.rule_list)
                level.rule_list = basics.remove_same_elements(level.rule_list)
    def __str__(self) -> str:
        return self.class_name
    def __repr__(self) -> str:
        return self.class_name
    def get_level(self, name: str) -> Optional[levels.level]:
        level = list(filter(lambda l: name == l.name, self.level_list))
        return level[0] if len(level) != 0 else None
    def get_exist_level(self, name: str) -> levels.level:
        level = list(filter(lambda l: name == l.name, self.level_list))
        return level[0]
    def set_level(self, level: levels.level) -> None:
        for i in range(len(self.level_list)):
            if level.name == self.level_list[i].name:
                self.level_list[i] = level
                return
        self.level_list.append(level)
    def to_json(self) -> dict[str, Any]:
        json_object = {"name": self.name, "level_list": [], "main_level": self.main_level, "rule_list": []}
        for level in self.level_list:
            json_object["level_list"].append(level.to_json())
        for rule in self.rule_list:
            json_object["rule_list"].append([])
            for obj in rule:
                json_object["rule_list"][-1].append({v: k for k, v in objects.object_name.items()}[obj])
        return json_object

def json_to_levelpack(json_object: dict[str, Any]) -> levelpack: # oh hell no * 4
    level_list = []
    for level in json_object["level_list"]: # type: ignore
        level_list.append(levels.json_to_level(level)) # type: ignore
    rule_list = []
    for rule in json_object["rule_list"]: # type: ignore
        rule_list.append([])
        for obj_type in rule: # type: ignore
            rule_list[-1].append(objects.object_name[obj_type])
    return levelpack(name=json_object["name"], # type: ignore
                     level_list=level_list, # type: ignore
                     main_level=json_object["main_level"], # type: ignore
                     rule_list=rule_list) # type: ignore