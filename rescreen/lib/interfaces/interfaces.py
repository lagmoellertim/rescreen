import enum
from typing import Tuple, Dict, List

Port = str
Resolution = Tuple[int, int]
Offset = Tuple[int, int]
RefreshRate = str
Modes = Dict[Resolution, List[RefreshRate]]
PortModesMapping = Dict[Port, Modes]


class Orientation(enum.Enum):
    Normal = "normal"
    Left = "left"
    Right = "right"
    Inverted = "inverted"
