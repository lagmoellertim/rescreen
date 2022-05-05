import subprocess
from typing import List
from typing import Optional

from rescreen.lib.interfaces import Orientation


class DisplaySettings:
    def __init__(self, port):
        self.__port = port
        self.__kwargs = {}

    def __set_arg(self, key, value):
        if (key == "off" and len(self.__kwargs) != 0 and value) or (key != "off" and self.__kwargs.get("off")):
            raise AttributeError("Display can't have options and be inactive")
        self.__kwargs[key] = value

    def set_scale(self, scale: float) -> "DisplaySettings":
        self.__set_arg("scale", f"{scale}x{scale}")
        return self

    def set_pos(self, x_pos: int, y_pos: int) -> "DisplaySettings":
        self.__set_arg("pos", f"{int(x_pos)}x{int(y_pos)}")
        return self

    def set_inactive(self) -> "DisplaySettings":
        self.__set_arg("off", True)
        return self

    def set_mode(self, width: int, height: int) -> "DisplaySettings":
        self.__set_arg("mode", f"{int(width)}x{int(height)}")
        return self

    def set_refresh_rate(self, refresh_rate: str) -> "DisplaySettings":
        self.__set_arg("refresh", refresh_rate)
        return self

    def set_panning(self, virtual_width: int, virtual_height: int, x_offset: Optional[int] = None,
                    y_offset: Optional[int] = None) -> "DisplaySettings":
        if x_offset is not None and y_offset is not None:
            self.__set_arg("panning", f"{int(virtual_width)}x{int(virtual_height)}+{int(x_offset)}+{int(y_offset)}")
        else:
            self.__set_arg("panning", f"{int(virtual_width)}x{int(virtual_width)}")

        return self

    def set_orientation(self, orientation: Orientation) -> "DisplaySettings":
        orientationMap = {
            Orientation.Normal: "normal",
            Orientation.Left: "left",
            Orientation.Right: "right",
            Orientation.Inverted: "inverted"
        }

        self.__set_arg("rotate", orientationMap[orientation])
        return self

    def set_primary(self) -> "DisplaySettings":
        self.__set_arg("primary", True)
        return self

    def set_filter(self, filter_name: str) -> "DisplaySettings":
        self.__set_arg("filter", filter_name)
        return self

    def get_xrandr_args(self):
        args = ["--output", self.__port]
        for key, value in self.__kwargs.items():
            args.append(f"--{key}")

            if type(value) != bool:
                args.append(value)

        return args


class Settings:
    def __init__(self):
        self.__kwargs = {}
        self.__display_settings: List[DisplaySettings] = []

    def add_display_settings(self, display_configuration: DisplaySettings) -> "Settings":
        self.__display_settings.append(display_configuration)
        return self

    def set_frame_buffer(self, width: int, height: int):
        self.__kwargs["fb"] = f"{int(width)}x{int(height)}"
        return self

    def get_xrandr_args(self):
        args = []
        for key, value in self.__kwargs.items():
            args.append(f"--{key}")

            if type(value) != bool:
                args.append(value)

        for display_configuration in self.__display_settings:
            args.extend(display_configuration.get_xrandr_args())

        return args

    def apply(self):
        subprocess.call(["xrandr", *self.get_xrandr_args()])
