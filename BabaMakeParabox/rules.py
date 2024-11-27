from dataclasses import dataclass
from typing import Any, Callable, Never, TypedDict

from BabaMakeParabox import objects

Rule = list[type[objects.Text]]

@dataclass(init=True)
class PrefixInfo():
    negated: bool
    prefix_type: type[objects.Prefix]

@dataclass(init=True)
class InfixNounInfo():
    negated: bool
    infix_noun_type: type[objects.Noun | objects.Property]

@dataclass(init=True)
class InfixInfo():
    negated: bool
    infix_type: type[objects.Infix]
    infix_noun_info_list: list[InfixNounInfo]

@dataclass(init=True)
class RuleInfo():
    prefix_info_list: list[PrefixInfo]
    noun_negated_list: list[type[objects.TextNot | objects.TextNeg]]
    noun_type: type[objects.Noun]
    infix_info_list: list[InfixInfo]
    oper_type: type[objects.Operator]
    prop_negated_list: list[type[objects.TextNot | objects.TextNeg]]
    prop_type: type[objects.Noun | objects.Property]

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
    info.oper_type = oper_type
    return info

def set_prop(info: RuleInfo, prop_type: type[objects.Noun | objects.Property]) -> RuleInfo:
    info.prop_type = prop_type
    return info

def negate_prefix(info: RuleInfo, negate_type: type[objects.TextNot | objects.TextNeg]) -> RuleInfo:
    if len(info.prefix_info_list) != 0:
        info.prefix_info_list[0].negated = not info.prefix_info_list[0].negated
    else:
        info.noun_negated_list.insert(0, negate_type)
    return info

def negate_infix(info: RuleInfo, negate_type: type[objects.TextNot | objects.TextNeg]) -> RuleInfo:
    info.infix_info_list[0].negated = not info.infix_info_list[0].negated
    return info

def negate_infix_noun(info: RuleInfo, negate_type: type[objects.TextNot | objects.TextNeg]) -> RuleInfo:
    info.infix_info_list[0].infix_noun_info_list[0].negated = not info.infix_info_list[0].infix_noun_info_list[0].negated
    return info

def negate_noun(info: RuleInfo, negate_type: type[objects.TextNot | objects.TextNeg]) -> RuleInfo:
    info.noun_negated_list.insert(0, negate_type)
    return info

def negate_prop(info: RuleInfo, negate_type: type[objects.TextNot | objects.TextNeg]) -> RuleInfo:
    info.prop_negated_list.insert(0, negate_type)
    return info

def text_text_noun(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.noun_type = objects.get_noun_from_type(info.noun_type)
    return info

def text_text_infix_noun(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.infix_info_list[0].infix_noun_info_list[0].infix_noun_type = objects.get_noun_from_type(info.infix_info_list[0].infix_noun_info_list[0].infix_noun_type)
    return info

def text_text_prop(info: RuleInfo, placeholder: type[objects.Text]) -> RuleInfo:
    info.prop_type = objects.get_noun_from_type(info.noun_type)
    return info

def analysis_rule(rule: Rule, stage: str = "before prefix") -> list[RuleInfo]:
    match_list: list[tuple[list[type[objects.Text]], list[type[objects.Text]], str, Callable[[RuleInfo, Any], RuleInfo]]] = []
    info_list: list[RuleInfo] = []
    if stage == "before prefix": # start, before prefix, or noun
        match_list = [
            ([objects.TextNot, objects.TextNeg], [], "before prefix", negate_prefix),
            ([objects.Prefix], [], "after prefix", set_prefix),
            ([objects.TextText_], [], "text_ noun", text_text_noun),
            ([objects.Noun], [], "before infix", set_noun),
        ]
    elif stage == "after prefix": # after prefix, before new prefix, or noun
        match_list = [
            ([objects.TextNot, objects.TextNeg], [], "after prefix", negate_noun),
            ([objects.TextAnd], [], "before prefix", do_nothing),
            ([objects.TextText_], [], "text_ noun", text_text_noun),
            ([objects.Noun], [], "before infix", set_noun),
        ]
    elif stage == "before infix": # after noun, before infix type, new noun, and operator
        match_list = [
            ([objects.TextNot, objects.TextNeg], [], "before infix", negate_infix),
            ([objects.Infix], [], "in infix", set_infix),
            ([objects.TextAnd], [], "before prefix", text_text_prop),
            ([objects.Operator], [], "before property", set_oper),
        ]
    elif stage == "in infix": # after infix type, before infix noun
        match_list = [
            ([objects.TextNot, objects.TextNeg], [], "in infix", set_infix),
            ([objects.TextText_], [], "text_ infix", text_text_infix_noun),
            ([objects.Noun, objects.Property], [], "after infix", set_infix_noun),
        ]
    elif stage == "after infix": # after infix noun, before operator, or new infix
        match_list = [
            ([objects.TextAnd], [], "new infix", do_nothing),
            ([objects.Operator], [], "before property", set_oper),
        ]
    elif stage == "new infix": # before new infix type, or new infix noun
        match_list = [
            ([objects.Infix], [], "in infix", set_infix),
            ([objects.TextText_], [], "text_ infix", text_text_infix_noun),
            ([objects.Noun, objects.Property], [], "after infix", set_infix_noun),
        ]
    elif stage == "before property": # after operator, before property
        match_list = [
            ([objects.TextNot, objects.TextNeg], [], "before property", negate_prop),
            ([objects.TextText_], [], "text_ property", text_text_prop),
            ([objects.Noun, objects.Property], [], "after property", set_prop),
        ]
    elif stage == "after property": # after property, may before new property
        match_list = [
            ([objects.TextAnd], [], "before property", do_nothing),
        ]
        info_list = [RuleInfo([], [], objects.Noun, [], objects.Operator, [], objects.Property)]
    elif stage == "text_ noun": # metatext
        match_list = [
            ([objects.TextText_], [], "text_ noun", text_text_noun),
            ([objects.Text], [objects.TextText_], "before infix", set_noun),
        ]
    elif stage == "text_ infix": # metatext
        match_list = [
            ([objects.TextText_], [], "text_ infix", text_text_infix_noun),
            ([objects.Text], [objects.TextText_], "after infix", set_infix_noun),
        ]
    elif stage == "text_ property": # metatext
        match_list = [
            ([objects.TextText_], [], "text_ property", text_text_prop),
            ([objects.Text], [objects.TextText_], "after property", set_prop),
        ]
    else:
        raise ValueError(stage)
    if len(rule) == 0:
        return info_list
    for match_type, unmatch_type, next_stage, func in match_list:
        if issubclass(rule[0], tuple(match_type)):
            if len(unmatch_type) == 0 or issubclass(rule[0], tuple(unmatch_type)):
                info_list = analysis_rule(rule[1:], next_stage)
                info_list = [func(i, rule[0]) for i in info_list]
    return info_list # rest in piece, more-than-200-lines-long-and-extremely-fucking-confusing function(BabaMakeParabox.worlds.World.get_rules_from_pos_and_orient)

default_rule_list: list[Rule] = []
default_rule_list.append([objects.TextText, objects.TextIs, objects.TextPush])
default_rule_list.append([objects.TextCursor, objects.TextIs, objects.TextSelect])
default_rule_list.append([objects.TextMeta, objects.TextWorld, objects.TextIs,
                          objects.TextEnter, objects.TextAnd, objects.TextLeave])
default_rule_list.append([objects.TextMeta, objects.TextClone, objects.TextIs,
                          objects.TextEnter])
default_rule_list.append([objects.TextNot, objects.TextMeta, objects.TextWorld, objects.TextAnd,
                          objects.TextNot, objects.TextMeta, objects.TextClone, objects.TextIs, objects.TextPush])
default_rule_list.append([objects.TextNot, objects.TextMeta, objects.TextLevel, objects.TextIs, objects.TextStop])

PropertyList = list[tuple[type[objects.BmpObject], int]]