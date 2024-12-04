import json
import os
from typing import Final

from BabaMakeParabox import basics

class Language(dict[str, str]):
    def __getitem__(self, key: str) -> str:
        return super().get(key, key)

language_dict: dict[str, Language] = {}

for name in [n for n in os.listdir("lang") if n.endswith(".json")]:
    with open(os.path.join("lang", name), "r", encoding="utf-8") as file:
        language_dict[os.path.splitext(os.path.basename(name))[0]] = Language(json.load(file))

english: str = "en_US"
current_language_name: str = basics.options["lang"] if basics.options["lang"] != "" else english

def set_current_language(name: str) -> None:
    global current_language_name
    current_language_name = name if name in list(language_dict.keys()) else english

yes = ("y", "Y", "yes", "Yes", "YES")
no = ("n", "N", "no", "No", "NO")

def lang_format(message_id: str, /, **formats) -> str:
    return language_dict[current_language_name][message_id].format(**formats)

def lang_print(message_id: str, /, **formats) -> None:
    print(language_dict[current_language_name][message_id].format(**formats))

def lang_input(message_id: str, /, **formats) -> str:
    return input(language_dict[current_language_name][message_id].format(**formats))

def cls() -> None:
    if basics.current_os == basics.windows:
        print("\x1B[2J\x1B[0f", end=None)
    else:
        print("\x1B[2J\x1B[3J\x1B[H", end=None)