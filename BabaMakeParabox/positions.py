from collections import namedtuple
from typing import Literal, TypedDict
from enum import Enum

Coordinate = namedtuple("Coordinate", ("x", "y"))
CoordTuple = tuple[int, int]
CoordTupleFloat = tuple[float, float]

DirectInt = Literal[0x2, 0x4, 0x8, 0x1]
DirectStr = Literal["W", "A", "S", "D"]

class Direction(Enum):
    W = "W"
    A = "A"
    S = "S"
    D = "D"
    def to_bit(self) -> DirectInt:
        match self:
            case Direction.W:
                return 0x2
            case Direction.A:
                return 0x4
            case Direction.S:
                return 0x8
            case Direction.D:
                return 0x1
            case _:
                raise ValueError(self)
    def to_str(self) -> DirectStr:
        match self:
            case Direction.W:
                return "W"
            case Direction.A:
                return "A"
            case Direction.S:
                return "S"
            case Direction.D:
                return "D"
            case _:
                raise ValueError(self)

NullDirectInt = Literal[0x10]
NullDirectStr = Literal["O"]
class NullDirection(Enum):
    O = 0x10
    def to_bit(self) -> NullDirectInt:
        match self:
            case NullDirection.O:
                return 0x10
            case _:
                raise ValueError(self)
    def to_str(self) -> NullDirectStr:
        match self:
            case NullDirection.O:
                return "O"
            case _:
                raise ValueError(self)

NullableDirection = Direction | NullDirection
NullableDirectInt = DirectInt | NullDirectInt
NullableDirectStr = DirectStr | NullDirectStr

def bit_to_direct(direction: DirectInt) -> Direction:
    match direction:
        case 0x2:
            return Direction.W
        case 0x4:
            return Direction.A
        case 0x8:
            return Direction.S
        case 0x1:
            return Direction.D

def str_to_direct(direction: DirectStr) -> Direction:
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

def turn_left(direction: Direction) -> Direction:
    match direction:
        case Direction.W:
            return Direction.A
        case Direction.A:
            return Direction.S
        case Direction.S:
            return Direction.D
        case Direction.D:
            return Direction.W

def turn_right(direction: Direction) -> Direction:
    match direction:
        case Direction.W:
            return Direction.D
        case Direction.A:
            return Direction.W
        case Direction.S:
            return Direction.A
        case Direction.D:
            return Direction.S

def turn(old_direction: Direction, new_direction: Direction) -> Direction:
    match new_direction:
        case Direction.W:
            return swap_direction(old_direction)
        case Direction.A:
            return turn_right(old_direction)
        case Direction.S:
            return old_direction
        case Direction.D:
            return turn_left(old_direction)

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

class SpaceTransform(TypedDict):
    direct: DirectStr
    flip: bool

default_space_transform: SpaceTransform = {
    "direct": "S",
    "flip": False
}

def inverse_transform(transform: SpaceTransform) -> SpaceTransform:
    match transform["direct"]:
        case "W" | "S":
            return transform.copy()
        case "A":
            return {"direct": "A" if transform["flip"] else "D", "flip": transform["flip"]}
        case "D":
            return {"direct": "D" if transform["flip"] else "A", "flip": transform["flip"]}

def get_stacked_transform(transformend: SpaceTransform, transfer: SpaceTransform) -> SpaceTransform:
    result = transformend.copy()
    if transfer["flip"]:
        match result["direct"]:
            case "W" | "S":
                result["flip"] = not result["flip"]
            case "A":
                result["direct"] = "D"
            case "D":
                result["direct"] = "A"
    match transfer["direct"]:
        case "W" | "S":
            pass
        case "A":
            match result["flip"]:
                case "W" | "S":
                    result["flip"] = not result["flip"]
        case "D":
            match result["flip"]:
                case "A" | "D":
                    result["flip"] = not result["flip"]
    result["direct"] = turn(str_to_direct(result["direct"]), str_to_direct(transfer["direct"])).to_str()
    return result

def transform_absolute_size(transform: SpaceTransform, size: CoordTupleFloat) -> CoordTupleFloat:
    if transform["flip"]:
        size = (-size[0], size[1])
    match transform["direct"]:
        case "W":
            size = (-size[0], -size[1])
        case "S":
            pass
        case "A":
            size = (size[1], -size[0])
        case "D":
            size = (-size[1], size[0])
    return size

def transform_absolute_pos(transform: SpaceTransform, pos: CoordTupleFloat, size: CoordTupleFloat) -> CoordTupleFloat:
    if transform["flip"]:
        pos = (size[0] - pos[0], pos[1])
    match transform["direct"]:
        case "W":
            pos = (size[0] - pos[0], size[1] - pos[1])
        case "S":
            pass
        case "A":
            pos = (pos[1], size[0] - pos[0])
        case "D":
            pos = (size[1] - pos[1], pos[0])
    return pos

def transform_relative_pos(transform: SpaceTransform, pos: CoordTupleFloat) -> CoordTupleFloat:
    if transform["flip"]:
        pos = (1.0 - pos[0], pos[1])
    match transform["direct"]:
        case "W":
            pos = (1.0 - pos[0], 1.0 - pos[1])
        case "S":
            pass
        case "A":
            pos = (pos[1], 1.0 - pos[0])
        case "D":
            pos = (1.0 - pos[1], pos[0])
    return pos