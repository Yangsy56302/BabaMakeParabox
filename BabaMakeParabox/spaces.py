from typing import Literal, Final
from enum import Enum

Coord = tuple[int, int]

class Orient(Enum):
    W = 0x2
    A = 0x4
    S = 0x8
    D = 0x1
    
class NullOrient(Enum):
    O = 0x10

OrientStr = Literal["W", "A", "S", "D"]

PlayerOperation = Orient | NullOrient

def swap_orientation(direction: Orient) -> Orient:
    match direction:
        case Orient.W:
            return Orient.S
        case Orient.A:
            return Orient.D
        case Orient.S:
            return Orient.W
        case Orient.D:
            return Orient.A

def orient_to_int(direction: Orient) -> int:
    match direction:
        case Orient.W:
            return 0x2
        case Orient.A:
            return 0x4
        case Orient.S:
            return 0x8
        case Orient.D:
            return 0x1

def orient_to_str(direction: Orient) -> OrientStr:
    match direction:
        case Orient.W:
            return "W"
        case Orient.A:
            return "A"
        case Orient.S:
            return "S"
        case Orient.D:
            return "D"

def str_to_orient(direction: OrientStr) -> Orient:
    match direction:
        case "W":
            return Orient.W
        case "A":
            return Orient.A
        case "S":
            return Orient.S
        case "D":
            return Orient.D

def pos_facing(pos: Coord, orient: Orient) -> Coord:
    match orient:
        case Orient.W:
            return (pos[0], pos[1] - 1)
        case Orient.A:
            return (pos[0] - 1, pos[1])
        case Orient.S:
            return (pos[0], pos[1] + 1)
        case Orient.D:
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