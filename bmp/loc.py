from typing import Literal, TypedDict
from enum import Enum

type Coord[T] = tuple[T, T]

OrientInt = Literal[0x2, 0x8, 0x4, 0x1]
OrientStr = Literal["W", "S", "A", "D"]

class Orient(Enum):
    W = "W"
    S = "S"
    A = "A"
    D = "D"
    def to_bit(self) -> OrientInt:
        match self:
            case Orient.W:
                return 0x2
            case Orient.S:
                return 0x8
            case Orient.A:
                return 0x4
            case Orient.D:
                return 0x1
            case _:
                raise ValueError(self)
    def to_str(self) -> OrientStr:
        match self:
            case Orient.W:
                return "W"
            case Orient.S:
                return "S"
            case Orient.A:
                return "A"
            case Orient.D:
                return "D"
            case _:
                raise ValueError(self)

def bit_to_direct(direction: OrientInt) -> Orient:
    match direction:
        case 0x2:
            return Orient.W
        case 0x4:
            return Orient.A
        case 0x8:
            return Orient.S
        case 0x1:
            return Orient.D

def str_to_direct(direction: OrientStr) -> Orient:
    match direction:
        case "W":
            return Orient.W
        case "A":
            return Orient.A
        case "S":
            return Orient.S
        case "D":
            return Orient.D

def front_position(coord: Coord[int], direct: Orient) -> Coord[int]:
    match direct:
        case Orient.W:
            return (coord[0], coord[1] - 1)
        case Orient.A:
            return (coord[0] - 1, coord[1])
        case Orient.S:
            return (coord[0], coord[1] + 1)
        case Orient.D:
            return (coord[0] + 1, coord[1])

def swap_direction(direction: Orient) -> Orient:
    match direction:
        case Orient.W:
            return Orient.S
        case Orient.A:
            return Orient.D
        case Orient.S:
            return Orient.W
        case Orient.D:
            return Orient.A

def turn_left(direction: Orient) -> Orient:
    match direction:
        case Orient.W:
            return Orient.A
        case Orient.A:
            return Orient.S
        case Orient.S:
            return Orient.D
        case Orient.D:
            return Orient.W

def turn_right(direction: Orient) -> Orient:
    match direction:
        case Orient.W:
            return Orient.D
        case Orient.A:
            return Orient.W
        case Orient.S:
            return Orient.A
        case Orient.D:
            return Orient.S

def turn(old_direction: Orient, new_direction: Orient) -> Orient:
    match new_direction:
        case Orient.W:
            return swap_direction(old_direction)
        case Orient.A:
            return turn_right(old_direction)
        case Orient.S:
            return old_direction
        case Orient.D:
            return turn_left(old_direction)

def on_line(*coords: Coord[int]) -> bool:
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
    direct: OrientStr
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

def transform_absolute_size(transform: SpaceTransform, size: Coord) -> Coord:
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

def transform_absolute_pos(transform: SpaceTransform, pos: Coord, size: Coord) -> Coord:
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

def transform_relative_pos(transform: SpaceTransform, pos: Coord) -> Coord:
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