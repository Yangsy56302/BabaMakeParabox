# Baba Make Parabox

**Baba Make Parabox** is a fan-made sokoban-like metagame by **Yangsy56302**.
The original games are **Baba Is You** and **Patrick's Parabox**,
separately made by **Arvi Hempuli** and **Patrick Traynor**.

## How to run

Note: batch files with **py_** prefix only works with python files,
and batch files with **exe_** prefix only works with execution files.

If you want to run the source code, download These Things:
- **Python *(latest)***: [Link](https://www.python.org/downloads/)
- **PIP**: Should install with Python
- **Pygame**: Run `pip install -U pygame` in Terminal or something similar to Terminal
- **PyInstaller *(optional, if you need .exe)***: Run `pip install -U pyinstaller` in Terminal too

Run **prefix_test.bat** to start a official game test.

Run **prefix_input.bat** to play a world from json file in the **worlds** folder.

Run **prefix_edit.bat** to edit and save a world from json file in the **worlds** folder, or create one.

You can run **prefix_help.bat** for more information with how to run the game in terminal.

If you need to make an .exe file, run **py_to_exe.bat**.

### How to control

- WSAD: You move.
- Space: You wait for something.
- Z: Undo, max 100 times.
- R: Restart.
- Minus / Equals: Select level for camera to focus.

### How to win

Simply put something that is **YOU** to something that is **WIN**.

And remember:

1. Sometimes the rules itself can be changed;
2. Sometimes some of the rules can not be changed;
3. Sometimes you need to get inside of the sublevel;
4. Sometimes you need to create a paradox.

## How to make a custom world (recommend)

Don't you remember what I said? just run **prefix_edit.bat**.

### How to control

- WSAD: Move cursor.
- IKJL: Change orientation.
- Q / E: Select object.
- Tab: Switch object / noun.
- Enter: Place object on cursor.
- Backspace: Destroy all objects on cursor.
- Minus / Equals: Select level.
- Lshift + Enter: Place level object (direct to current level).
- Rshift + Enter: Place clone object (direct to current level).
- P: New level (information from terminal inputs).
- Z: Undo, max 100 times.
- X: Cut all objects on cursor.
- C: Copy all objects on cursor.
- V: Paste all objects on cursor.
- Close Window: Save and quit.

## How to code a custom world (not recommend)

1. `from baba_make_parabox import *`.
    - Or `import baba_make_parabox as bmp` if you are afraid of duplicated name.
2. Define some **levels** (`levels.level`):
    - The first argument (`name`) is the name (also id) of this level, its type is `str`;
    - The second argument (`size`) is the size of this level, its type is `spaces.Coord` (`tuple[int, int]`);
    - The third (and also the last) argument (`inf_tier`) is the infinity tier of this level, its type is `int`, and its default value is `0`.
3. Put **objects** (`objects.Object` and its subclass) in the level:
    - The first argument is the position of this object, its type is `spaces.Coord`;
    - The second (and commonly the last) argument is the orientation of this object, its type is `spaces.Orient`, and its default value is `"W"`.
    - **Real objects and texts are different**:
        - TEXTS_ARE_ALL_CAPS
        - RealObjectsAreBigCamelCase
    - Common object like `Baba`, `Wall`, `Box` or `Rock`;
    - Text like `BABA` `IS` `YOU`;
    - `Level` and `Clone`:
        - they have extra arguments: `name` and `inf_tier`.
    - And yes, `LEVEL` and `CLONE`;
    - **DO NOT USE `Text`, `Noun`, `Operator` AND `Property`**;
    - ...
4. Define a **world** (`worlds.world`):
    - The first argument is the name of this world, its type is `str`;
    - The second argument is a `list` of the levels in this world;
    - The third argument is a `list` of the global rules of this world, its type is `rules.Rule` (like `tuple[type[objects.Noun], type[objects.IS], type[objects.Property]]` or something similar).
5. Run `baba_make_parabox.play`, its only argument is your custom world.
    - Run `baba_make_parabox.stop` to stop the game if you want to.

Now you can test and play your custom world with `-c` terminal argument!

## List of Versions

| Number |    Time    | Informations |
|--------|------------|--------------|
| 1.0    | 2024.07.05 | Initialized. |
| 1.1    | 2024.07.06 | Keke is Move; Undo and Restart; Baba make Levels |
| 1.11   | 2024.07.06 | Level is Previous and Next |
| 1.2    | 2024.07.06 | Flag is Win; Game is EXE |
| 1.3    | 2024.07.06 | Baba is Keke; World is Input and Output |
| 1.31   | 2024.07.06 | Terminal is More; Text is not Hide; Level is Red |
| 1.4    | 2024.07.06 | Baba make Worlds |

## Bug Reports and Advices

Send your message to yangsy56302@163.com!

## Support

Not open for now.