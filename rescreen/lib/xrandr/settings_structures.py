import subprocess
from typing import List, Dict
from typing import Optional

from loguru import logger

from rescreen.lib.interfaces import Orientation


class DisplaySettings:
    def __init__(self, port: str):
        self.__port = port
        self.__kwargs: Dict[str, Optional[str]] = {}

    def __set_arg(self, key: str, value: Optional[str] = None) -> None:
        if (key == "off" and len(self.__kwargs) != 0) or (key != "off" and "off" in self.__kwargs):
            raise AttributeError("Display can't have options and be inactive")
        self.__kwargs[key] = value

    def set_scale(self, scale: float) -> "DisplaySettings":
        self.__set_arg("scale", f"{scale}x{scale}")
        return self

    def set_pos(self, x_pos: int, y_pos: int) -> "DisplaySettings":
        self.__set_arg("pos", f"{int(x_pos)}x{int(y_pos)}")
        return self

    def set_inactive(self) -> "DisplaySettings":
        self.__set_arg("off")
        return self

    def set_mode(self, width: int, height: int) -> "DisplaySettings":
        self.__set_arg("mode", f"{int(width)}x{int(height)}")
        return self

    def set_refresh_rate(self, refresh_rate: str) -> "DisplaySettings":
        self.__set_arg("refresh", refresh_rate)
        return self

    def set_panning(
        self,
        virtual_width: int,
        virtual_height: int,
        x_offset: Optional[int] = None,
        y_offset: Optional[int] = None,
    ) -> "DisplaySettings":
        if x_offset is not None and y_offset is not None:
            self.__set_arg(
                "panning",
                f"{int(virtual_width)}x{int(virtual_height)}+{int(x_offset)}+{int(y_offset)}",
            )
        else:
            self.__set_arg("panning", f"{int(virtual_width)}x{int(virtual_width)}")

        return self

    def set_orientation(self, orientation: Orientation) -> "DisplaySettings":
        self.__set_arg("rotate", orientation.value)
        return self

    def set_primary(self) -> "DisplaySettings":
        self.__set_arg("primary")
        return self

    def set_filter(self, filter_name: str) -> "DisplaySettings":
        self.__set_arg("filter", filter_name)
        return self

    def get_xrandr_args(self) -> List[str]:
        args = ["--output", self.__port]
        for key, value in self.__kwargs.items():
            args.append(f"--{key}")

            if value is not None:
                args.append(value)

        return args


class Settings:
    def __init__(self):
        self.__display_settings: List[DisplaySettings] = []
        self.__kwargs: Dict[str, Optional[str]] = {}

    def add_display_settings(self, display_configuration: DisplaySettings) -> "Settings":
        self.__display_settings.append(display_configuration)
        return self

    def set_frame_buffer(self, width: int, height: int) -> "Settings":
        self.__kwargs["fb"] = f"{int(width)}x{int(height)}"
        return self

    def get_xrandr_args(self) -> List[str]:
        args = []
        for key, value in self.__kwargs.items():
            args.append(f"--{key}")

            if value is not None:
                args.append(value)

        for display_configuration in self.__display_settings:
            args.extend(display_configuration.get_xrandr_args())

        return args

    def apply(self) -> None:
        command = ["xrandr", *self.get_xrandr_args()]
        logger.debug(f"XRandR Settings Command: {command}")
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as exception:
            logger.exception(
                "XRandR couldn't apply the current configuration",
            )
            raise exception
