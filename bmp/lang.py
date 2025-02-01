import json
import os
import math
from typing import Any, Callable, Optional, ParamSpec

import bmp.base
import bmp.opt
import bmp.color

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
current_language_name: str = bmp.opt.options["lang"] if bmp.opt.options["lang"] != "" else chinese

def set_current_language(name: str) -> None:
    global current_language_name
    current_language_name = name if name in list(language_dict.keys()) else chinese
    yes.update()

yes: set[str] = {"y", "Y", "yes", "Yes", "YES", "t", "T", "true", "True", "TRUE", "1", "是", "是的"}
no: set[str] = {"n", "N", "no", "No", "NO", "f", "F", "false", "False", "FALSE", "0", "否", "不是"}

def fformat(message_id: str, /, *, language_name: str = current_language_name, **formats) -> str:
    return language_dict[language_name][message_id].format(**formats)

def fprint(message_id: str, /, *, language_name: str = current_language_name, **formats) -> None:
    print(fformat(message_id, language_name=language_name, **formats))

def fwarn(message_id: str, /, *, language_name: str = current_language_name, **formats) -> None:
    print(fformat(message_id, language_name=language_name, **formats), flush=True)

def finput(message_id: str, /, *, language_name: str = current_language_name, **formats) -> str:
    return input(fformat(message_id, language_name=language_name, **formats))

def input_typed_wrapper[T: object](__type: type[T], /, *, init_func: Optional[Callable[[str], T]] = None):
    _init_func: Callable[[str], T]
    if init_func is None:
        _init_func = __type
    else:
        _init_func = init_func
    def wrapped(message: str, /, default: Optional[T] = None) -> T:
        nonlocal _init_func
        return_value: T
        while True:
            _input_str: str = input(message)
            try:
                if _input_str == "" and default is not None:
                    return_value = default
                else:
                    return_value = _init_func(_input_str)
            except ValueError:
                bmp.lang.fwarn("warn.value.invalid", value=_input_str, cls=__type.__name__)
            else:
                break
        return return_value
    return wrapped

def str_to_bool(_str: str, /, default: Optional[bool] = None) -> bool:
    if _str in yes:
        return True
    elif _str in no:
        return False
    elif default:
        return default
    else:
        raise ValueError(_str)

input_str = input
input_int = input_typed_wrapper(int)
input_float = input_typed_wrapper(float)
input_bool = input_typed_wrapper(bool, init_func=str_to_bool)
input_yes = input_typed_wrapper(bool, init_func=lambda s: str_to_bool(s, True))
input_no = input_typed_wrapper(bool, init_func=lambda s: str_to_bool(s, False))
input_color = input_typed_wrapper(bmp.color.ColorHex, init_func=bmp.color.str_or_palette_to_hex)

def input_optional_wrapper[T: object](_func: Callable[..., T], /) -> Callable[..., Optional[T]]:
    def wrapped(*args, **kwds) -> Optional[T]:
        try:
            return _func(*args, **kwds)
        except ValueError:
            return None
    return wrapped

input_int_optional = input_optional_wrapper(input_int)
input_float_optional = input_optional_wrapper(input_float)

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

default_tqdm_args: dict[str, Any] = {
    "dynamic_ncols": True,
    "mininterval": 0.0625,
    "maxinterval": 1,
    "leave": False
}