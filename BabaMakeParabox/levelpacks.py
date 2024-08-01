from typing import Any, Optional, TypedDict

from BabaMakeParabox import basics, objects, rules, levels

class Levelpack(object):
    def __init__(self, name: str, level_list: list[levels.Level], main_level: Optional[str] = None, rule_list: Optional[list[rules.Rule]] = None) -> None:
        self.name: str = name
        self.level_list: list[levels.Level] = list(level_list)
        self.main_level: str = main_level if main_level is not None else self.level_list[0].name
        self.rule_list: list[rules.Rule] = rule_list if rule_list is not None else rules.default_rule_list
        if rule_list is not None:
            for level in self.level_list:
                level.rule_list.extend(self.rule_list)
                level.rule_list = basics.remove_same_elements(level.rule_list)
    def get_level(self, name: str) -> Optional[levels.Level]:
        level = list(filter(lambda l: name == l.name, self.level_list))
        return level[0] if len(level) != 0 else None
    def get_exist_level(self, name: str) -> levels.Level:
        level = list(filter(lambda l: name == l.name, self.level_list))
        return level[0]
    def set_level(self, level: levels.Level) -> None:
        for i in range(len(self.level_list)):
            if level == self.level_list[i]:
                self.level_list[i] = level
                return
        self.level_list.append(level)
    def to_json(self) -> dict[str, Any]:
        json_object = {"ver": basics.versions, "name": self.name, "level_list": [], "main_level": self.main_level, "rule_list": []}
        for level in self.level_list:
            json_object["level_list"].append(level.to_json())
        for rule in self.rule_list:
            json_object["rule_list"].append([])
            for obj in rule:
                json_object["rule_list"][-1].append({v: k for k, v in objects.object_name.items()}[obj])
        return json_object

class LevelpackJson(TypedDict):
    ver: str
    name: str
    main_level: str
    level_list: list[levels.LevelJson]
    rule_list: list[list[str]]

def json_to_levelpack(json_object: LevelpackJson) -> Levelpack:
    ver = json_object.get("ver")
    level_list = []
    for level in json_object["level_list"]:
        level_list.append(levels.json_to_level(level, ver))
    rule_list: list[rules.Rule] = []
    for rule in json_object["rule_list"]:
        rule_list.append([])
        for obj_type in rule:
            rule_list[-1].append(objects.object_name[obj_type]) # type: ignore
    return Levelpack(name=json_object["name"],
                     level_list=level_list,
                     main_level=json_object["main_level"],
                     rule_list=rule_list)