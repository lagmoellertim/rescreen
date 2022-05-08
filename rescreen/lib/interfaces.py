import enum
from typing import Tuple, Dict, List

Port = str
Resolution = Tuple[int, int]
Offset = Tuple[int, int]
RefreshRate = str
Modes = Dict[Resolution, List[RefreshRate]]
PortModesMapping = Dict[Port, Modes]


class Orientation(str, enum.Enum):
    NORMAL = "normal"
    LEFT = "left"
    RIGHT = "right"
    INVERTED = "inverted"
