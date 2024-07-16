from typing import Optional

import BabaMakeParabox.objects as objects

Rule = list[type[objects.Text]]

basic_rule_types = [[objects.Noun, objects.IS, objects.Property],
                    [objects.Noun, objects.IS, objects.Noun]]

def analysis_rule(rule: Rule) -> list[tuple[bool, type[objects.Noun], int, type[objects.Text]]]:
    raw_and_indexes = list(map(lambda t: issubclass(t, objects.AND), rule))
    and_indexes = []
    for i in range(len(raw_and_indexes)):
        if raw_and_indexes[i] == True:
            and_indexes.append(i)
    oper_index = list(map(lambda t: issubclass(t, objects.Operator), rule)).index(True)
    noun_list = [[]]
    prop_list = [[]]
    first_stage = True
    for i in range(len(rule)):
        if first_stage:
            if i == oper_index:
                first_stage = False
            elif i in and_indexes:
                noun_list.append([])
            else:
                noun_list[-1].append(rule[i])
        else:
            if i in and_indexes:
                prop_list.append([])
            else:
                prop_list[-1].append(rule[i])
    return_value = []
    for noun in noun_list:
        for prop in prop_list:
            simple_rule = noun + [rule[oper_index]] + prop
            noun_index = list(map(lambda t: issubclass(t, objects.Noun), simple_rule)).index(True)
            noun_type: type[objects.Noun] = simple_rule[noun_index] # type: ignore
            noun_negated = simple_rule[:noun_index].count(objects.NOT) % 2 == 1
            prop_index = list(map(lambda t: issubclass(t, (objects.Noun, objects.Property)), simple_rule[noun_index + 2:])).index(True)
            prop_type: type[objects.Text] = simple_rule[prop_index + noun_index + 2] # type: ignore
            prop_negated_count = simple_rule[noun_index:].count(objects.NOT)
            return_value.append((noun_negated, noun_type, prop_negated_count, prop_type))
    return return_value

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