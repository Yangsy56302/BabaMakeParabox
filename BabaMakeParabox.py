import BabaMakeParabox as bmp

def start():
    settings = {}
    if bmp.basics.options["lang"] not in bmp.languages.language_dict.keys():
        print("English: input en_US")
        print("简体中文: 输入 zh_CN")
        print("Others: input languages filename without .json extension")
        lang = input(">>> ")
        bmp.languages.set_current_language(lang)
        bmp.basics.options["lang"] = lang
    else:
        bmp.languages.set_current_language(bmp.basics.options["lang"])
    print(bmp.languages.current_language["main.welcome"])
    print(bmp.languages.current_language["main.change_options"])
    change_options = input(bmp.languages.current_language["input.string"]) != ""
    if change_options:
        print(bmp.languages.current_language["main.change_options.fps"])
        computer_level = int(input(bmp.languages.current_language["input.number"]))
        match computer_level:
            case 1:
                bmp.basics.options.update({"fps": 5, "fpw": 1, "input_cooldown": 1, "world_display_recursion_depth": 1, "compressed_json_output": True})
            case 2:
                bmp.basics.options.update({"fps": 15, "fpw": 3, "input_cooldown": 2, "world_display_recursion_depth": 2, "compressed_json_output": True})
            case 3:
                bmp.basics.options.update({"fps": 30, "fpw": 5, "input_cooldown": 4, "world_display_recursion_depth": 3, "compressed_json_output": True})
            case 4:
                bmp.basics.options.update({"fps": 60, "fpw": 10, "input_cooldown": 8, "world_display_recursion_depth": 4, "compressed_json_output": False})
        print(bmp.languages.current_language["main.change_options.done"])
    print(bmp.languages.current_language["main.play_or_edit"])
    play_or_edit = int(input(bmp.languages.current_language["input.number"]))
    if play_or_edit == 1:
        settings["play"] = True
        print(bmp.languages.current_language["main.open.levelpack"])
        settings["input"] = input(bmp.languages.current_language["input.file.path.relative"])
    else:
        settings["edit"] = True
        print(bmp.languages.current_language["main.open.levelpack"])
        print(bmp.languages.current_language["main.open.levelpack.empty.editor"])
        settings["input"] = input(bmp.languages.current_language["input.file.path.relative"])
        print(bmp.languages.current_language["main.save.levelpack"])
        print(bmp.languages.current_language["main.save.levelpack.empty.editor"])
        settings["output"] = input(bmp.languages.current_language["input.file.path.relative"])
    print()
    bmp.main(settings)

start()