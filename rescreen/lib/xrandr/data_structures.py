import dataclasses

from rescreen.lib.interfaces import (
    Resolution,
    Offset,
    Modes,
    RefreshRate,
    Orientation,
)


@dataclasses.dataclass
class DisplayData:
    name: str
    port: str
    edid: str
    internal: bool

    virtual_resolution: Resolution
    resolution_mm: Resolution
    offset: Offset
    orientation: Orientation

    primary: bool
    enabled: bool

    modes: Modes
    current_resolution: Resolution
    current_refresh_rate: RefreshRate
