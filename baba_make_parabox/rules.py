from typing import Optional

import baba_make_parabox.objects as objects

class NounsObjsDicts(object):
    pairs: dict[type[objects.Noun], type[objects.Object]]
    def __init__(self) -> None:
        self.pairs = {}
    def new_pair(self, noun: type[objects.Noun], obj: type[objects.Object]) -> None:
        self.pairs[noun] = obj
    def get_obj(self, noun: type[objects.Noun]) -> Optional[type[objects.Object]]:
        return self.pairs.get(noun)
    def get_noun(self, obj: type[objects.Object]) -> Optional[type[objects.Noun]]:
        return {v: k for k, v in self.pairs.items()}.get(obj, None)

nouns_objs_dicts = NounsObjsDicts()

nouns_objs_dicts.new_pair(objects.BABA, objects.Baba)
nouns_objs_dicts.new_pair(objects.KEKE, objects.Keke)
nouns_objs_dicts.new_pair(objects.WALL, objects.Wall)
nouns_objs_dicts.new_pair(objects.BOX, objects.Box)
nouns_objs_dicts.new_pair(objects.ROCK, objects.Rock)
nouns_objs_dicts.new_pair(objects.FLAG, objects.Flag)
nouns_objs_dicts.new_pair(objects.LEVEL, objects.Level)
nouns_objs_dicts.new_pair(objects.CLONE, objects.Clone)
nouns_objs_dicts.new_pair(objects.TEXT, objects.Text)

NounIsProperty = tuple[type[objects.Noun], type[objects.IS], type[objects.Property]]
NounIsNoun = tuple[type[objects.Noun], type[objects.IS], type[objects.Noun]]
Rule = NounIsProperty | NounIsNoun | tuple[type[objects.Object], ...] | list[type[objects.Object]]

default_rule_list = []
default_rule_list.append((objects.TEXT, objects.IS, objects.PUSH))
default_rule_list.append((objects.LEVEL, objects.IS, objects.PUSH))
default_rule_list.append((objects.CLONE, objects.IS, objects.PUSH))