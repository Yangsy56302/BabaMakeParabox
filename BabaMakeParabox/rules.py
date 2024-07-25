from BabaMakeParabox import objects

Rule = list[type[objects.Text]]

def to_atom_rules(rule_list: list[Rule]) -> list[Rule]:
    return_value: list[Rule] = []
    for rule in rule_list:
        noun_list: list[list[type[objects.Text]]] = [[]]
        prop_list: list[list[type[objects.Text]]] = [[]]
        current_oper = objects.IS
        stage = objects.Noun
        for text_type in rule:
            if stage == objects.Noun:
                if issubclass(text_type, objects.Operator):
                    stage = objects.Property
                    current_oper = text_type
                if issubclass(text_type, objects.Infix):
                    stage = objects.Infix
                    noun_list = [l + [text_type] for l in noun_list]
                elif issubclass(text_type, objects.AND):
                    noun_list.append([])
                else:
                    noun_list[-1].append(text_type)
            elif stage == objects.Infix:
                if issubclass(text_type, objects.Operator):
                    stage = objects.Property
                    current_oper = text_type
                else:
                    noun_list = [l + [text_type] for l in noun_list]
            elif stage == objects.Property:
                if issubclass(text_type, objects.AND):
                    prop_list.append([])
                elif len(prop_list[-1]) == 0 and issubclass(text_type, objects.Operator):
                    current_oper = text_type
                elif len(prop_list[-1]) == 0 and not issubclass(text_type, objects.Operator):
                    prop_list[-1].append(current_oper)
                    prop_list[-1].append(text_type)
                else:
                    prop_list[-1].append(text_type)
        for noun in noun_list:
            for prop in prop_list:
                return_value.append(noun + prop)
    return return_value

InfixInfo = tuple[bool, type[objects.Infix], bool, type[objects.Text]]
PrefixInfo = tuple[bool, type[objects.Prefix]]
RuleInfo = list[tuple[list[PrefixInfo], bool, type[objects.Noun], list[InfixInfo], type[objects.Operator], int, type[objects.Text]]]

def analysis_rule(atom_rule: Rule) -> RuleInfo:
    return_value: RuleInfo = []
    prefix_indexes = list(map(lambda t: issubclass(t, objects.Prefix), reversed(atom_rule)))
    last_prefix_index = len(atom_rule) - prefix_indexes.index(True) - 1 if True in prefix_indexes else -1
    noun_index = list(map(lambda t: issubclass(t, objects.Noun), atom_rule)).index(True)
    noun_type: type[objects.Noun] = atom_rule[noun_index] # type: ignore
    noun_negated = atom_rule[last_prefix_index + 1:noun_index].count(objects.NOT) % 2 == 1
    oper_index = list(map(lambda t: issubclass(t, objects.Operator), atom_rule)).index(True)
    oper_type: type[objects.Operator] = atom_rule[oper_index] # type: ignore
    prop_index = list(map(lambda t: issubclass(t, (objects.Noun, objects.Property)), atom_rule[oper_index:])).index(True)
    prop_type: type[objects.Text] = atom_rule[prop_index + oper_index] # type: ignore
    prop_negated_count = atom_rule[oper_index:].count(objects.NOT)
    prefix_info_list = []
    prefix_slice = atom_rule[:last_prefix_index + 1]
    if len(prefix_slice) != 0:
        current_prefix_type = objects.Prefix
        current_prefix_negated = False
        for obj_type in prefix_slice:
            if issubclass(obj_type, objects.Prefix):
                current_prefix_type = obj_type
                prefix_info_list.append((current_prefix_negated, current_prefix_type))
            elif issubclass(obj_type, objects.NOT):
                current_prefix_negated = not current_prefix_negated
            elif issubclass(obj_type, objects.AND):
                current_prefix_negated = False
    infix_info_list = []
    infix_slice = atom_rule[noun_index + 1:oper_index]
    if len(infix_slice) != 0:
        current_negated = False
        current_infix_type = objects.Infix
        current_infix_negated = False
        current_infix_noun = objects.Object
        current_infix_noun_negated = False
        for obj_type in infix_slice:
            if issubclass(obj_type, objects.Infix):
                current_infix_type = obj_type
                current_infix_negated = current_negated
                current_negated = False
            elif issubclass(obj_type, objects.NOT):
                current_negated = not current_negated
            elif issubclass(obj_type, objects.AND):
                pass
            else:
                current_infix_noun = obj_type
                current_infix_noun_negated = current_negated
                current_negated = False
                infix_info_list.append((current_infix_negated, current_infix_type, current_infix_noun_negated, current_infix_noun))
    return_value.append((prefix_info_list, noun_negated, noun_type, infix_info_list, oper_type, prop_negated_count, prop_type))
    return return_value

default_rule_list: list[Rule] = []
default_rule_list.append([objects.CURSOR, objects.IS, objects.SELECT])
default_rule_list.append([objects.TEXT, objects.IS, objects.PUSH])
default_rule_list.append([objects.NOT, objects.META, objects.WORLD, objects.IS, objects.PUSH])
default_rule_list.append([objects.NOT, objects.META, objects.CLONE, objects.IS, objects.PUSH])
default_rule_list.append([objects.NOT, objects.META, objects.LEVEL, objects.IS, objects.STOP])

advanced_rule_list: list[Rule] = []
advanced_rule_list.append([objects.BABA, objects.IS, objects.YOU])
advanced_rule_list.append([objects.WALL, objects.IS, objects.STOP])
advanced_rule_list.append([objects.ROCK, objects.IS, objects.PUSH])
advanced_rule_list.append([objects.FLAG, objects.IS, objects.WIN])
advanced_rule_list.extend(default_rule_list)