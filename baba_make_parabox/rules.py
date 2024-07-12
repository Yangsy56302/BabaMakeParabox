from typing import Optional

import baba_make_parabox.objects as objects

Rule = list[type[objects.Text]]

rule_types = [[objects.Noun, objects.IS, objects.Property],
              [objects.Noun, objects.IS, objects.Noun]]

default_rule_list: list[Rule] = []
default_rule_list.append([objects.CURSOR, objects.IS, objects.SELECT])
default_rule_list.append([objects.TEXT, objects.IS, objects.PUSH])
default_rule_list.append([objects.WORLD, objects.IS, objects.PUSH])
default_rule_list.append([objects.CLONE, objects.IS, objects.PUSH])
default_rule_list.append([objects.LEVEL, objects.IS, objects.STOP])