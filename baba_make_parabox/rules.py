from typing import Optional

import baba_make_parabox.objects as objects

Rule = list[type[objects.Text]]

default_rule_list: list[Rule] = []
default_rule_list.append([objects.TEXT, objects.IS, objects.PUSH])
default_rule_list.append([objects.LEVEL, objects.IS, objects.STOP])
default_rule_list.append([objects.CLONE, objects.IS, objects.STOP])