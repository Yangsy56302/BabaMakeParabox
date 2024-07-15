from typing import Optional

import BabaMakeParabox.objects as objects

Rule = list[type[objects.Text]]

basic_rule_types = [[objects.Noun, objects.IS, objects.Property],
                    [objects.Noun, objects.IS, objects.Noun]]

def analysis_rule(rule: Rule) -> tuple[bool, type[objects.Noun], int, type[objects.Text]]:
    noun_index = list(map(lambda t: t != objects.NOT, rule)).index(True)
    noun_type: type[objects.Noun] = rule[noun_index] # type: ignore
    noun_negated = rule[:noun_index].count(objects.NOT) % 2 == 1
    prop_index = list(map(lambda t: t != objects.NOT, rule[noun_index + 2:])).index(True)
    prop_type: type[objects.Text] = rule[prop_index + noun_index + 2] # type: ignore
    prop_negated_count = rule[noun_index:].count(objects.NOT)
    return (noun_negated, noun_type, prop_negated_count, prop_type)

default_rule_list: list[Rule] = []
default_rule_list.append([objects.CURSOR, objects.IS, objects.SELECT])
default_rule_list.append([objects.TEXT, objects.IS, objects.PUSH])
default_rule_list.append([objects.WORLD, objects.IS, objects.PUSH])
default_rule_list.append([objects.CLONE, objects.IS, objects.PUSH])
default_rule_list.append([objects.LEVEL, objects.IS, objects.STOP])

advanced_rule_list: list[Rule] = []
advanced_rule_list.append([objects.BABA, objects.IS, objects.YOU])
advanced_rule_list.append([objects.WALL, objects.IS, objects.STOP])
advanced_rule_list.append([objects.ROCK, objects.IS, objects.PUSH])
advanced_rule_list.append([objects.FLAG, objects.IS, objects.WIN])
advanced_rule_list.extend(default_rule_list)