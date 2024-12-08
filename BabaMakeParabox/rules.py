from dataclasses import dataclass
from typing import Any, Callable, Optional

from BabaMakeParabox import objects

Rule = list[type[objects.Text]]

@dataclass(init=True, repr=True)
class PrefixInfo():
    negated: bool
    prefix_type: type[objects.Prefix]

@dataclass(init=True, repr=True)
class InfixNounInfo():
    negated: bool
    infix_noun_type: type[objects.Noun | objects.Property]

@dataclass(init=True, repr=True)
class InfixInfo():
    negated: bool
    infix_type: type[objects.Infix]
    infix_noun_info_list: list[InfixNounInfo]

@dataclass(init=True, repr=True)
class PropInfo():
    prop_negated_tier: int
    prop_type: type[objects.Noun | objects.Property]

@dataclass(init=True, repr=True)
class OperInfo():
    oper_type: type[objects.Operator]
    prop_list: list[PropInfo]

@dataclass(init=True, repr=True)
class RuleInfo():
    prefix_info_list: list[PrefixInfo]
    noun_negated_tier: int
    noun_type: type[objects.Noun]
    infix_info_list: list[InfixInfo]
    oper_list: list[OperInfo]

def do_nothing(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    return info

def set_prefix(info: RuleInfo, prefix_type: type[objects.Prefix]) -> RuleInfo:
    info.prefix_info_list.insert(0, PrefixInfo(False, prefix_type))
    return info

def set_infix(info: RuleInfo, infix_type: type[objects.Infix]) -> RuleInfo:
    info.infix_info_list[0].infix_type = infix_type
    return info

def set_infix_noun(info: RuleInfo, infix_noun_type: type[objects.Noun | objects.Property]) -> RuleInfo:
    if len(info.infix_info_list) == 0:
        info.infix_info_list.insert(0, InfixInfo(False, objects.Infix, []))
    elif info.infix_info_list[0].infix_type != objects.Infix:
        info.infix_info_list.insert(0, InfixInfo(False, objects.Infix, []))
    info.infix_info_list[0].infix_noun_info_list.insert(0, InfixNounInfo(False, infix_noun_type))
    return info

def set_noun(info: RuleInfo, noun_type: type[objects.Noun]) -> RuleInfo:
    info.noun_type = noun_type
    return info

def set_oper(info: RuleInfo, oper_type: type[objects.Operator]) -> RuleInfo:
    info.oper_list[0].oper_type = oper_type
    info.oper_list.insert(0, OperInfo(objects.Operator, []))
    return info

def set_prop(info: RuleInfo, prop_type: type[objects.Noun | objects.Property]) -> RuleInfo:
    info.oper_list[0].prop_list.insert(0, PropInfo(0, prop_type))
    return info

def negate_prefix(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    if len(info.prefix_info_list) != 0:
        info.prefix_info_list[0].negated = not info.prefix_info_list[0].negated
    else:
        info.noun_negated_tier += 1
    return info

def negate_infix(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.infix_info_list[0].negated = not info.infix_info_list[0].negated
    return info

def negate_infix_noun(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.infix_info_list[0].infix_noun_info_list[0].negated = not info.infix_info_list[0].infix_noun_info_list[0].negated
    return info

def negate_noun(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.noun_negated_tier += 1
    return info

def negate_prop(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.oper_list[0].prop_list[0].prop_negated_tier += 1
    return info

def text_text_noun(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.noun_type = objects.get_noun_from_type(info.noun_type)
    return info

def text_text_infix_noun(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.infix_info_list[0].infix_noun_info_list[0].infix_noun_type = objects.get_noun_from_type(info.infix_info_list[0].infix_noun_info_list[0].infix_noun_type)
    return info

def text_text_prop(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.oper_list[0].prop_list[0].prop_type = objects.get_noun_from_type(info.oper_list[0].prop_list[0].prop_type)
    return info

how_to_match_rule: dict[str, list[tuple[
    list[type[objects.Text]],
    list[type[objects.Text]],
    str,
    Callable[[RuleInfo, Any], RuleInfo]
]]] = {
    "before prefix": [ # start, before prefix, or noun
        ([objects.TextNot], [], "before prefix", negate_prefix),
        ([objects.Prefix], [], "after prefix", set_prefix),
        ([objects.TextText_], [], "text_ noun", text_text_noun),
        ([objects.Noun], [], "before infix", set_noun),
    ],
    "after prefix": [ # after prefix, before new prefix, or noun
        ([objects.TextNot], [], "after prefix", negate_noun),
        ([objects.TextAnd], [], "before prefix", do_nothing),
        ([objects.TextText_], [], "text_ noun", text_text_noun),
        ([objects.Noun], [], "before infix", set_noun),
    ],
    "before infix": [ # after noun, before infix type, new noun, and operator
        ([objects.TextNot], [], "before infix", negate_infix),
        ([objects.Infix], [], "in infix", set_infix),
        ([objects.TextAnd], [], "before prefix", text_text_prop),
        ([objects.Operator], [], "before property", set_oper),
    ],
    "in infix": [ # after infix type, before infix noun
        ([objects.TextNot], [], "in infix", set_infix),
        ([objects.TextText_], [], "text_ infix", text_text_infix_noun),
        ([objects.Noun, objects.Property], [], "after infix", set_infix_noun),
    ],
    "after infix": [ # after infix noun, before operator, or new infix
        ([objects.TextAnd], [], "new infix", do_nothing),
        ([objects.Operator], [], "before property", set_oper),
    ],
    "new infix": [ # before new infix type, or new infix noun
        ([objects.Infix], [], "in infix", set_infix),
        ([objects.TextText_], [], "text_ infix", text_text_infix_noun),
        ([objects.Noun, objects.Property], [], "after infix", set_infix_noun),
    ],
    "before property": [ # after operator, before property
        ([objects.TextNot], [], "before property", negate_prop),
        ([objects.TextText_], [], "text_ property", text_text_prop),
        ([objects.Noun, objects.Property], [], "after property", set_prop),
    ],
    "after property": [ # after property, may before new property, or new operator
        ([objects.TextAnd], [], "new property", do_nothing),
    ],
    "new property": [ # before new property, or new operator
        ([objects.TextNot], [], "new property", negate_prop),
        ([objects.Operator], [], "before property", set_oper),
        ([objects.TextText_], [], "text_ property", text_text_prop),
        ([objects.Noun, objects.Property], [], "after property", set_prop),
    ],
    "text_ noun": [ # metatext of noun
        ([objects.TextText_], [], "text_ noun", text_text_noun),
        ([objects.Text], [objects.TextText_], "before infix", set_noun),
    ],
    "text_ infix": [ # metatext of infix
        ([objects.TextText_], [], "text_ infix", text_text_infix_noun),
        ([objects.Text], [objects.TextText_], "after infix", set_infix_noun),
    ],
    "text_ property": [ # metatext of property
        ([objects.TextText_], [], "text_ property", text_text_prop),
        ([objects.Text], [objects.TextText_], "after property", set_prop),
    ]
}

def get_info_from_rule(rule: Rule, stage: str = "before prefix") -> Optional[RuleInfo]:
    for match_type, unmatch_type, next_stage, func in how_to_match_rule[stage]:
        if len(rule) == 0 and next_stage == "new property":
            return RuleInfo([], 0, objects.Noun, [], [OperInfo(objects.Operator, [])])
        if issubclass(rule[0], tuple(match_type)) and not issubclass(rule[0], tuple(unmatch_type)):
            new_info = get_info_from_rule(rule[1:], next_stage)
            if new_info is not None:
                info_list = func(new_info, rule[0])
                return info_list
    raise ValueError(rule[0])

def handle_text_text_(rule: Rule) -> Rule:
    metanumber = 0
    new_rule = []
    for text_type in rule:
        if text_type == objects.TextText_:
            metanumber += 1
        elif metanumber != 0:
            new_text_type = text_type
            for _ in range(metanumber):
                new_text_type = objects.get_noun_from_type(new_text_type)
            new_rule.append(new_text_type)
            metanumber = 0
        else:
            new_rule.append(text_type)
    return new_rule

default_rule_list: list[Rule] = []
default_rule_list.append([objects.TextText, objects.TextIs, objects.TextPush])
default_rule_list.append([objects.TextCursor, objects.TextIs, objects.TextSelect])
default_rule_list.append([objects.TextNot, objects.TextMeta, objects.TextLevel, objects.TextIs, objects.TextStop])
default_rule_list.append([objects.TextNot, objects.TextMeta, objects.TextSpace, objects.TextIs, objects.TextPush])
default_rule_list.append([objects.TextNot, objects.TextMeta, objects.TextClone, objects.TextIs, objects.TextPush])
default_rule_list.append([objects.TextMeta, objects.TextClone, objects.TextIs, objects.TextNot, objects.TextLeave])

PropertyList = list[tuple[type[objects.Object], int]]