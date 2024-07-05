import baba_make_parabox.objects as objects

class NounsObjsDicts(object):
    pairs: dict[type[objects.Noun], type[objects.Object]]
    def __init__(self) -> None:
        self.pairs = {}
    def new_pair(self, noun: type[objects.Noun], obj: type[objects.Object]) -> None:
        self.pairs[noun] = obj
    def get_obj(self, noun: type[objects.Noun]) -> type[objects.Object]:
        return self.pairs[noun]
    def get_noun(self, obj: type[objects.Object]) -> type[objects.Noun]:
        return {v: k for k, v in self.pairs.items()}[obj]

nouns_objs_dicts = NounsObjsDicts()

nouns_objs_dicts.new_pair(objects.BABA, objects.Baba)
nouns_objs_dicts.new_pair(objects.WALL, objects.Wall)
nouns_objs_dicts.new_pair(objects.BOX, objects.Box)
nouns_objs_dicts.new_pair(objects.ROCK, objects.Rock)
nouns_objs_dicts.new_pair(objects.FLAG, objects.Flag)
nouns_objs_dicts.new_pair(objects.LEVEL, objects.Level)
nouns_objs_dicts.new_pair(objects.CLONE, objects.Clone)
nouns_objs_dicts.new_pair(objects.TEXT, objects.Text)

NounIsProperty = tuple[type[objects.Noun], type[objects.IS], type[objects.Property]]
NounIsNoun = tuple[type[objects.Noun], type[objects.IS], type[objects.Noun]]
Rule = NounIsProperty | NounIsNoun