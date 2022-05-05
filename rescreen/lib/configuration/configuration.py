import dataclasses
import hashlib
from typing import List, Optional

from ruamel.yaml import YAML

from rescreen.lib.interfaces import Resolution, RefreshRate, Offset, Orientation, Port
from rescreen.lib.state.state_structure import State, DisplayState


@dataclasses.dataclass
class DisplayConfiguration:
    port: Port
    edid: str

    enabled: bool = True
    primary: bool = False

    resolution: Optional[Resolution] = None
    refresh_rate: Optional[RefreshRate] = None
    virtual_offset: Offset = (0, 0)
    orientation: Orientation = Orientation.Normal

    resolution_scale: float = 1

    def __post_init__(self):
        if self.enabled and (self.resolution is None or self.refresh_rate is None):
            raise AttributeError("Resolution or Refresh Rate not specified")

    @property
    def virtual_resolution(self):
        return tuple(i * self.resolution_scale for i in self.resolution)

    def to_dict(self):
        data = {"enabled": self.enabled, "edid": self.edid}

        if self.enabled:
            data["primary"] = self.primary
            data["resolution"] = self.resolution
            data["refresh_rate"] = self.refresh_rate
            data["virtual_offset"] = self.virtual_offset
            data["orientation"] = str(self.orientation.value)
            data["resolution_scale"] = self.resolution_scale

        return data

    @staticmethod
    def from_display_state(data: DisplayState) -> "DisplayConfiguration":
        return DisplayConfiguration(
            port=data.port, enabled=data.enabled, primary=data.primary, resolution=data.resolution,
            refresh_rate=data.refresh_rate, virtual_offset=data.virtual_offset, orientation=data.orientation,
            resolution_scale=data.resolution_scale, edid=data.edid
        )

    @staticmethod
    def from_dict(port: str, data: dict) -> "DisplayConfiguration":
        return DisplayConfiguration(port=port, enabled=data.setdefault("enabled", True),
                                    primary=data.setdefault("primary", False),
                                    resolution=data.setdefault("resolution", None),
                                    refresh_rate=data.setdefault("refresh_rate", None),
                                    virtual_offset=data.setdefault("virtual_offset", (0, 0)),
                                    orientation=Orientation(data.setdefault("orientation", Orientation.Normal)),
                                    resolution_scale=data.setdefault("resolution_scale", 1), edid=data["edid"])


@dataclasses.dataclass
class Configuration:
    displays: List[DisplayConfiguration]
    ui_scale: float = 1

    @property
    def display_setup_id(self) -> str:
        return "-".join(sorted([f"{display.port}-{display.edid}" for display in self.displays]))

    @property
    def display_setup_hash(self) -> str:
        return hashlib.sha512(self.display_setup_id).hexdigest()

    def to_dict(self) -> dict:
        return {
            "ui_scale": self.ui_scale,
            "displays": {display.port: display.to_dict() for display in self.displays}
        }

    def to_yaml(self, file):
        yaml = YAML(typ='safe')
        yaml.dump(self.to_dict(), file)

    @staticmethod
    def from_state(data: State):
        displays = [DisplayConfiguration.from_display_state(display_state) for display_state in data.displays]

        return Configuration(
            displays=displays,
            ui_scale=data.ui_scale
        )

    @staticmethod
    def from_dict(data: dict) -> "Configuration":
        displays = []
        if "displays" in data and isinstance(data["displays"], dict):
            for port, display_data in data["displays"].items():
                displays.append(DisplayConfiguration.from_dict(port, display_data))

        return Configuration(displays, ui_scale=float(data.setdefault("ui_scale", 1)))

    @staticmethod
    def from_yaml(file):
        yaml = YAML(typ='safe')
        return Configuration.from_dict(yaml.load(file))
