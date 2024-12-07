from collections import namedtuple
from typing import Literal
from enum import Enum

Coordinate = namedtuple("Coordinate", ("x", "y"))
CoordTuple = tuple[int, int]

class Direction(Enum):
    W = 0x2
    A = 0x4
    S = 0x8
    D = 0x1
DirectStr = Literal["W", "A", "S", "D"]
    
class NoDirect(Enum):
    O = 0x10

PlayerOperation = Direction | NoDirect

def swap_direction(direction: Direction) -> Direction:
    match direction:
        case Direction.W:
            return Direction.S
        case Direction.A:
            return Direction.D
        case Direction.S:
            return Direction.W
        case Direction.D:
            return Direction.A

def direction_to_bit(direction: Direction) -> int:
    match direction:
        case Direction.W:
            return 0x2
        case Direction.A:
            return 0x4
        case Direction.S:
            return 0x8
        case Direction.D:
            return 0x1

def direction_to_str(direction: Direction) -> DirectStr:
    match direction:
        case Direction.W:
            return "W"
        case Direction.A:
            return "A"
        case Direction.S:
            return "S"
        case Direction.D:
            return "D"

def str_to_direction(direction: DirectStr) -> Direction:
    match direction:
        case "W":
            return Direction.W
        case "A":
            return Direction.A
        case "S":
            return Direction.S
        case "D":
            return Direction.D

def front_position(coord: Coordinate, direct: Direction) -> Coordinate:
    match direct:
        case Direction.W:
            return Coordinate(coord[0], coord[1] - 1)
        case Direction.A:
            return Coordinate(coord[0] - 1, coord[1])
        case Direction.S:
            return Coordinate(coord[0], coord[1] + 1)
        case Direction.D:
            return Coordinate(coord[0] + 1, coord[1])

def on_line(*coords: Coordinate) -> bool:
    if coords[1][0] - coords[0][0] == 1 and coords[1][1] - coords[0][1] == 0:
        delta = (1, 0)
    elif coords[1][0] - coords[0][0] == 0 and coords[1][1] - coords[0][1] == 1:
        delta = (0, 1)
    else:
        return False
    for i in range(2, len(coords)):
        if not (coords[i][0] - coords[i - 1][0] == delta[0] and coords[i][1] - coords[i - 1][1] == delta[1]):
            return False
    return True