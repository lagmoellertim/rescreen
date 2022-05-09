import hashlib
import json
from typing import List, Optional, Any, Dict, Callable
import yaml
from pydantic import BaseModel, validator

from rescreen.lib.interfaces import (
    Resolution,
    RefreshRate,
    Offset,
    Orientation,
    Port,
)
from rescreen.lib.state.state import State, DisplayState
from . import _utils


class DisplayConfiguration(BaseModel):
    """
    Dataclass used for describing a display setup. With this class, the setup can be applied and
    saved/loaded to/from a file
    """

    port: Port
    edid: str
    internal: bool = False

    enabled: bool = True
    primary: bool = False

    resolution: Optional[Resolution] = None
    refresh_rate: Optional[RefreshRate] = None
    virtual_offset: Offset = (0, 0)
    orientation: Orientation = Orientation.NORMAL

    resolution_scale: float = 1

    @validator("resolution", "refresh_rate", always=True)
    def validator(cls, value: Optional[Resolution], values: Dict[str, Any]) -> Any:
        if values.get("enabled") and value is None:
            raise ValueError("must be supplied if display is enabled")
        return value

    @property
    def virtual_resolution(self) -> Optional[Resolution]:
        if self.resolution is None:
            return None

        return (
            int(self.resolution[0] * self.resolution_scale),
            int(self.resolution[1] * self.resolution_scale),
        )

    @staticmethod
    def from_display_state(data: DisplayState) -> "DisplayConfiguration":
        return DisplayConfiguration(
            port=data.port,
            enabled=data.enabled,
            primary=data.primary,
            resolution=data.resolution,
            refresh_rate=data.refresh_rate,
            virtual_offset=data.virtual_offset,
            orientation=data.orientation,
            resolution_scale=data.resolution_scale,
            edid=data.edid,
            internal=data.internal,
        )


class Configuration(BaseModel):
    displays: List[DisplayConfiguration]
    ui_scale: float = 1

    @property
    def display_setup_id(self) -> str:
        return "-".join(sorted([f"{display.port}-{display.edid}" for display in self.displays]))

    @property
    def display_setup_hash(self) -> str:
        return hashlib.sha512(self.display_setup_id.encode("utf-8")).hexdigest()

    @staticmethod
    def from_state(data: State) -> "Configuration":
        displays = [
            DisplayConfiguration.from_display_state(display_state)
            for display_state in data.displays
        ]

        return Configuration(displays=displays, ui_scale=data.ui_scale)

    def to_yaml(self, file):
        yaml.safe_dump(json.loads(self.json()), file)

    @staticmethod
    def from_yaml(file):
        return Configuration.parse_raw(json.dumps(yaml.safe_load(file)))

    def to_xrandr_settings(self):
        return _utils.to_xrandr_settings(self)

    def apply(self, user_confirmation_method: Callable[[str], bool]):
        return _utils.apply(self, user_confirmation_method)
