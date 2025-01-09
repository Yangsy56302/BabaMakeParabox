import json
import os
import math
from typing import Optional

import bmp.base

width: int = 80
height: int = 25

class Language(dict[str, str]):
    def __getitem__(self, key: str) -> str:
        return super().get(key, key)

language_dict: dict[str, Language] = {}

for name in [n for n in os.listdir("lang") if n.endswith(".json")]:
    with open(os.path.join("lang", name), "r", encoding="utf-8") as file:
        language_dict[os.path.splitext(os.path.basename(name))[0]] = Language(json.load(file))

chinese: str = "zh_CN"
english: str = "en_US"
current_language_name: str = bmp.base.options["lang"] if bmp.base.options["lang"] != "" else chinese

def set_current_language(name: str) -> None:
    global current_language_name
    current_language_name = name if name in list(language_dict.keys()) else chinese
    yes.update()

yes: set[str] = {"y", "Y", "yes", "Yes", "YES", "t", "T", "true", "True", "TRUE", "1", "是", "是的"}
no: set[str] = {"n", "N", "no", "No", "NO", "f", "F", "false", "False", "FALSE", "0", "否", "不是"}

def lang_format(message_id: str, /, **formats) -> str:
    return language_dict[current_language_name][message_id].format(**formats)

def lang_print(message_id: str, /, **formats) -> None:
    print(language_dict[current_language_name][message_id].format(**formats))

def lang_input(message_id: str, /, **formats) -> str:
    return input(language_dict[current_language_name][message_id].format(**formats))

def seperator_line(title: Optional[str] = None) -> str:
    if title is None:
        return "#=" + ("-" * (width - 4)) + "=#"
    else:
        return "#=" + ("-" * math.floor((width - 8 - len(title)) / 2)) + ">[" + title + \
            "]<" + ("-" * math.ceil((width - 8 - len(title)) / 2)) + "=#"

def cls() -> None:
    if bmp.base.current_os == bmp.base.windows:
        print("\x1B[2J\x1B[0f", end=None)
    else:
        print("\x1B[2J\x1B[3J\x1B[H", end=None)