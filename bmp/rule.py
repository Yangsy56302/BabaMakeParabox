from dataclasses import dataclass
from typing import Any, Callable, Optional

import bmp.obj

Rule = list[bmp.obj.Text]

@dataclass(init=True, repr=True)
class PrefixInfo():
    negated: bool
    prefix: bmp.obj.Prefix

@dataclass(init=True, repr=True)
class InfixNounInfo():
    negated: bool
    infix_noun: bmp.obj.Noun | bmp.obj.Property

@dataclass(init=True, repr=True)
class InfixInfo():
    negated: bool
    infix: bmp.obj.Infix
    infix_noun_info_list: list[InfixNounInfo]

@dataclass(init=True, repr=True)
class PropInfo():
    prop_negated_tier: int
    prop: bmp.obj.Noun | bmp.obj.Property

@dataclass(init=True, repr=True)
class OperInfo():
    oper: bmp.obj.Operator
    prop_list: list[PropInfo]

@dataclass(init=True, repr=True)
class RuleInfo():
    prefix_info_list: list[PrefixInfo]
    noun_negated_tier: int
    noun: bmp.obj.Noun
    infix_info_list: list[InfixInfo]
    oper_list: list[OperInfo]

def do_nothing(info: RuleInfo, placeholder: bmp.obj.Text) -> RuleInfo:
    return info

def set_prefix(info: RuleInfo, prefix_type: bmp.obj.Prefix) -> RuleInfo:
    info.prefix_info_list.insert(0, PrefixInfo(False, prefix_type))
    return info

def set_infix(info: RuleInfo, infix_type: bmp.obj.Infix) -> RuleInfo:
    info.infix_info_list[0].infix = infix_type
    return info

def set_infix_noun(info: RuleInfo, infix_noun_type: bmp.obj.Noun | bmp.obj.Property) -> RuleInfo:
    if len(info.infix_info_list) == 0:
        info.infix_info_list.insert(0, InfixInfo(False, bmp.obj.Infix(), []))
    elif info.infix_info_list[0].infix != bmp.obj.Infix:
        info.infix_info_list.insert(0, InfixInfo(False, bmp.obj.Infix(), []))
    info.infix_info_list[0].infix_noun_info_list.insert(0, InfixNounInfo(False, infix_noun_type))
    return info

def set_noun(info: RuleInfo, noun_type: bmp.obj.Noun) -> RuleInfo:
    info.noun = noun_type
    return info

def set_oper(info: RuleInfo, oper_type: bmp.obj.Operator) -> RuleInfo:
    info.oper_list[0].oper = oper_type
    info.oper_list.insert(0, OperInfo(bmp.obj.Operator(), []))
    return info

def set_prop(info: RuleInfo, prop_type: bmp.obj.Noun | bmp.obj.Property) -> RuleInfo:
    info.oper_list[0].prop_list.insert(0, PropInfo(0, prop_type))
    return info

def negate_prefix(info: RuleInfo, placeholder: bmp.obj.Text) -> RuleInfo:
    if len(info.prefix_info_list) != 0:
        info.prefix_info_list[0].negated = not info.prefix_info_list[0].negated
    else:
        info.noun_negated_tier += 1
    return info

def negate_infix(info: RuleInfo, placeholder: bmp.obj.Text) -> RuleInfo:
    info.infix_info_list[0].negated = not info.infix_info_list[0].negated
    return info

def negate_infix_noun(info: RuleInfo, placeholder: bmp.obj.Text) -> RuleInfo:
    info.infix_info_list[0].infix_noun_info_list[0].negated = not info.infix_info_list[0].infix_noun_info_list[0].negated
    return info

def negate_noun(info: RuleInfo, placeholder: bmp.obj.Text) -> RuleInfo:
    info.noun_negated_tier += 1
    return info

def negate_prop(info: RuleInfo, placeholder: bmp.obj.Text) -> RuleInfo:
    info.oper_list[0].prop_list[0].prop_negated_tier += 1
    return info

def text_text_noun(info: RuleInfo, placeholder: bmp.obj.Text) -> RuleInfo:
    info.noun = bmp.obj.get_noun_from_type(type(info.noun))()
    return info

def text_text_infix_noun(info: RuleInfo, placeholder: bmp.obj.Text) -> RuleInfo:
    info.infix_info_list[0].infix_noun_info_list[0].infix_noun = bmp.obj.get_noun_from_type(type(info.infix_info_list[0].infix_noun_info_list[0].infix_noun))()
    return info

def text_text_prop(info: RuleInfo, placeholder: bmp.obj.Text) -> RuleInfo:
    info.oper_list[0].prop_list[0].prop = bmp.obj.get_noun_from_type(type(info.oper_list[0].prop_list[0].prop))()
    return info

how_to_match_rule: dict[str, list[tuple[
    list[type[bmp.obj.Text]],
    list[type[bmp.obj.Text]],
    str,
    Callable[[RuleInfo, Any], RuleInfo]
]]] = {
    "before prefix": [ # start, before prefix, or noun
        ([bmp.obj.TextNot], [], "before prefix", negate_prefix),
        ([bmp.obj.Prefix], [], "after prefix", set_prefix),
        ([bmp.obj.TextText_], [], "text_ noun", text_text_noun),
        ([bmp.obj.Noun], [], "before infix", set_noun),
    ],
    "after prefix": [ # after prefix, before new prefix, or noun
        ([bmp.obj.TextNot], [], "after prefix", negate_noun),
        ([bmp.obj.TextAnd], [], "before prefix", do_nothing),
        ([bmp.obj.TextText_], [], "text_ noun", text_text_noun),
        ([bmp.obj.Noun], [], "before infix", set_noun),
    ],
    "before infix": [ # after noun, before infix type, new noun, and operator
        ([bmp.obj.TextNot], [], "before infix", negate_infix),
        ([bmp.obj.Infix], [], "in infix", set_infix),
        ([bmp.obj.TextAnd], [], "before prefix", text_text_prop),
        ([bmp.obj.Operator], [], "before property", set_oper),
    ],
    "in infix": [ # after infix type, before infix noun
        ([bmp.obj.TextNot], [], "in infix", set_infix),
        ([bmp.obj.TextText_], [], "text_ infix", text_text_infix_noun),
        ([bmp.obj.Noun, bmp.obj.Property], [], "after infix", set_infix_noun),
    ],
    "after infix": [ # after infix noun, before operator, or new infix
        ([bmp.obj.TextAnd], [], "new infix", do_nothing),
        ([bmp.obj.Operator], [], "before property", set_oper),
    ],
    "new infix": [ # before new infix type, or new infix noun
        ([bmp.obj.Infix], [], "in infix", set_infix),
        ([bmp.obj.TextText_], [], "text_ infix", text_text_infix_noun),
        ([bmp.obj.Noun, bmp.obj.Property], [], "after infix", set_infix_noun),
    ],
    "before property": [ # after operator, before property
        ([bmp.obj.TextNot], [], "before property", negate_prop),
        ([bmp.obj.TextText_], [], "text_ property", text_text_prop),
        ([bmp.obj.Noun, bmp.obj.Property], [], "after property", set_prop),
    ],
    "after property": [ # after property, may before new property, or new operator
        ([bmp.obj.TextAnd], [], "new property", do_nothing),
    ],
    "new property": [ # before new property, or new operator
        ([bmp.obj.TextNot], [], "new property", negate_prop),
        ([bmp.obj.Operator], [], "before property", set_oper),
        ([bmp.obj.TextText_], [], "text_ property", text_text_prop),
        ([bmp.obj.Noun, bmp.obj.Property], [], "after property", set_prop),
    ],
    "text_ noun": [ # metatext of noun
        ([bmp.obj.TextText_], [], "text_ noun", text_text_noun),
        ([bmp.obj.Text], [bmp.obj.TextText_], "before infix", set_noun),
    ],
    "text_ infix": [ # metatext of infix
        ([bmp.obj.TextText_], [], "text_ infix", text_text_infix_noun),
        ([bmp.obj.Text], [bmp.obj.TextText_], "after infix", set_infix_noun),
    ],
    "text_ property": [ # metatext of property
        ([bmp.obj.TextText_], [], "text_ property", text_text_prop),
        ([bmp.obj.Text], [bmp.obj.TextText_], "after property", set_prop),
    ]
}

def get_info_from_rule(rule: Rule, stage: str = "before prefix") -> Optional[RuleInfo]:
    for match_obj, unmatch_obj, next_stage, func in how_to_match_rule[stage]:
        if len(rule) == 0 and next_stage == "new property":
            return RuleInfo([], 0, bmp.obj.Noun(), [], [OperInfo(bmp.obj.Operator(), [])])
        if isinstance(rule[0], tuple(match_obj)) and not isinstance(rule[0], tuple(unmatch_obj)):
            new_info = get_info_from_rule(rule[1:], next_stage)
            if new_info is not None:
                info_list = func(new_info, rule[0])
                return info_list
    raise ValueError(rule[0])

def handle_text_text_(rule: Rule) -> Rule:
    metanumber = 0
    new_rule = []
    for text_obj in rule:
        if type(text_obj) == bmp.obj.TextText_:
            metanumber += 1
        elif metanumber != 0:
            new_text_obj = text_obj
            for _ in range(metanumber):
                new_text_obj = bmp.obj.get_noun_from_type(type(new_text_obj))(text_obj.pos, text_obj.orient)
            new_rule.append(new_text_obj)
            metanumber = 0
        else:
            new_rule.append(text_obj)
    return new_rule

default_rule_list: list[Rule] = [
    [
        bmp.obj.TextText(),
        bmp.obj.TextIs(),
        bmp.obj.TextPush(),
    ],
    [
        bmp.obj.TextCursor(),
        bmp.obj.TextIs(),
        bmp.obj.TextSelect(),
    ],
    [
        bmp.obj.TextNot(),
        bmp.obj.TextMeta(),
        bmp.obj.TextLevel(),
        bmp.obj.TextIs(),
        bmp.obj.TextStop(),
    ],
    [
        bmp.obj.TextNot(),
        bmp.obj.TextMeta(),
        bmp.obj.TextSpace(),
        bmp.obj.TextIs(),
        bmp.obj.TextPush(),
    ],
    [
        bmp.obj.TextNot(),
        bmp.obj.TextMeta(),
        bmp.obj.TextClone(),
        bmp.obj.TextIs(),
        bmp.obj.TextPush(),
    ],
    [
        bmp.obj.TextMeta(),
        bmp.obj.TextClone(),
        bmp.obj.TextIs(),
        bmp.obj.TextNot(),
        bmp.obj.TextLeave(),
    ],
]

PropertyList = list[tuple[type[bmp.obj.Object], int]]