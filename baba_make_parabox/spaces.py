from typing import Literal

Coord = tuple[int, int]
Orient = Literal["W", "A", "S", "D"]
PlayerOperation = Orient | Literal["_"]

def swap_orientation(direction: Orient) -> Orient:
    match direction:
        case "W":
            return "S"
        case "A":
            return "D"
        case "S":
            return "W"
        case "D":
            return "A"

def pos_facing(pos: Coord, facing: Orient) -> Coord:
    match facing:
        case "W":
            return (pos[0], pos[1] - 1)
        case "A":
            return (pos[0] - 1, pos[1])
        case "S":
            return (pos[0], pos[1] + 1)
        case "D":
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