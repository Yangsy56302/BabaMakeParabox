import json
import os

from BabaMakeParabox import basics

class Language(dict[str, str]):
    def __getitem__(self, key: str) -> str:
        return super().get(key, key)

language_dict: dict[str, Language] = {}

for name in [n for n in os.listdir("lang") if n.endswith(".json")]:
    with open(os.path.join("lang", name), "r", encoding="utf-8") as file:
        language_dict[name[:-5]] = Language(json.load(file))

current_language = language_dict[basics.options["lang"] if basics.options["lang"] != "id_FK" else "en_US"]

def set_current_language(name: str) -> None:
    global current_language
    current_language = language_dict.get(name, language_dict["en_US"])

yes = ["y", "Y", "yes", "Yes", "YES"]
no = ["n", "N", "no", "No", "NO"]

def lang_format(message_id: str, /, **formats) -> str:
    return current_language[message_id].format(lang = current_language[message_id], **formats)

def lang_print(message_id: str, /, **formats) -> None:
    print(current_language[message_id].format(lang = current_language[message_id], **formats))

def lang_input(message_id: str, /, **formats) -> str:
    return input(current_language[message_id].format(lang = current_language[message_id], **formats))

def cls() -> None:
    if basics.current_os == basics.windows:
        print("\x1B[2J\x1B[0f", end=None)
    else:
        print("\x1B[2J\x1B[3J\x1B[H", end=None)