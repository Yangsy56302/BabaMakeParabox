from typing import Literal, Final

Coord = tuple[int, int]
Orient = Literal[0x1, 0x2, 0x4, 0x8]
PlayerOperation = Orient | Literal[0x10]

W: Final[Orient] = 0x2
A: Final[Orient] = 0x4
S: Final[Orient] = 0x8
D: Final[Orient] = 0x1
O: Final[PlayerOperation] = 0x10

def swap_orientation(direction: Orient) -> Orient:
    match direction:
        case 0x2:
            return S
        case 0x4:
            return D
        case 0x8:
            return W
        case 0x1:
            return A

def orient_to_str(direction: Orient) -> str:
    match direction:
        case 0x2:
            return "W"
        case 0x4:
            return "A"
        case 0x8:
            return "S"
        case 0x1:
            return "D"

def str_to_orient(direction: str) -> Orient:
    match direction:
        case "W":
            return W
        case "A":
            return A
        case "S":
            return S
        case "D":
            return D
        case _:
            raise ValueError()

def pos_facing(pos: Coord, orient: Orient) -> Coord:
    match orient:
        case 0x2:
            return (pos[0], pos[1] - 1)
        case 0x4:
            return (pos[0] - 1, pos[1])
        case 0x8:
            return (pos[0], pos[1] + 1)
        case 0x1:
            return (pos[0] + 1, pos[1])

def on_line(*poses: Coord) -> bool:
    if poses[1][0] - poses[0][0] == 1 and poses[1][1] - poses[0][1] == 0:
        delta = (1, 0)
    elif poses[1][0] - poses[0][0] == 0 and poses[1][1] - poses[0][1] == 1:
        delta = (0, 1)
    else:
        return False
    for i in range(2, len(poses)):
        if not (poses[i][0] - poses[i - 1][0] == delta[0] and poses[i][1] - poses[i - 1][1] == delta[1]):
            return False
    return True