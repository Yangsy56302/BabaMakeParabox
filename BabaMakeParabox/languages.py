import json
import os

from BabaMakeParabox import basics

language_dict: dict[str, dict[str, str]] = {}

for name in [n for n in os.listdir("lang") if n.endswith(".json")]:
    with open(os.path.join("lang", name), "r", encoding="utf-8") as file:
        language_dict[name[:-5]] = json.load(file)

current_language = language_dict[basics.options["lang"] if basics.options["lang"] != "id_FK" else "en_US"]

def set_current_language(name: str) -> None:
    global current_language
    current_language = language_dict.get(name, language_dict["en_US"])