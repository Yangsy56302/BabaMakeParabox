# Baba Make Parabox

**Baba Make Parabox** is a fan-made sokoban-like metagame by **Yangsy56302**.
The original games are **Baba Is You** and **Patrick's Parabox**,
separately made by **Arvi Hempuli** and **Patrick Traynor**.

## How to run

Download These Things:
- **Python *(latest)***: [Link](https://www.python.org/downloads/)
- **PIP**: Should install with Python
- **Pygame**: Run `pip install pygame` in Terminal or something similar to Terminal

Then run **test.bat** to start a official game test.

## Controls

- WSAD: You move.
- Space: You wait for something.
- Z: Undo, max 100 times.
- R: Restart.

## How to code a custom world

1. `from baba_make_parabox import *`, then `import baba_make_parabox.main`.
    - Or `import baba_make_parabox as bmp` if you are afraid of duplicated name.
2. Define some **level**s (`levels.level`):
    - The first argument is the name (also id) of this level, its type is `str`;
    - The second argument is the infinity tier of this level, its type is `int`;
    - The third (and also the last) argument is the size of this level, its type is `spaces.Coord` (`tuple[int, int]`).
3. Put **objects** (`objects.Object` and its subclass) in the level:
    - The first argument is the position of this object, its type is `spaces.Coord`;
    - The second (and commonly the last) argument is the orientation of this object, its type is `spaces.Orient`;
    - **Real objects and texts are different**:
        - TEXTS_ARE_ALL_CAPS
        - RealObjectsAreBigCamelCase
    - Common object like `Baba`, `Wall`, `Box` or `Rock`;
    - Text like `BABA` `IS` `YOU`;
    - `Level` and `Clone`:
        - they have extra arguments: `name` and `inf_tier`.
    - And yes, `LEVEL` and `CLONE`;
    - **DO NOT USE `Text`, `Noun`, `Operator` AND `Property`**;
    - `WIN` has no effect (Not implemented yet);
    - ...
4. Define a **world** (`worlds.world`):
    - All non-keyword arguments are the levels in this world;
    - `rule_list` is the global rules of this world, its type is `rules.Rule` (like `tuple[type[objects.Noun], type[objects.IS], type[objects.Property]]` or something similar).
5. Run `baba_make_parabox.main`, its only argument is your custom world.

Now you can test and play your custom world!

## List of Versions

| Number |    Time    | Informations |
|--------|------------|--------------|
| 1.0    | 2024.07.05 | Initialized. |

## Bug Reports and Advices

Send your message to yangsy56302@163.com!

## Support

Not open for now.