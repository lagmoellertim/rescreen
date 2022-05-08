import os
import re
import subprocess
from typing import List

from .interface import DesktopEnvironmentInterface


class Gnome(DesktopEnvironmentInterface):
    name = "gnome"

    @classmethod
    def is_current_desktop_environment(cls) -> bool:
        if os.environ.get("DESKTOP_SESSION") == "gnome":
            return True

        if os.environ.get("XDG_SESSION_DESKTOP") == "gnome":
            return True

        return False

    @classmethod
    def pre_xrandr_hook(cls, scaling: float):
        subprocess.call(
            [
                "gsettings",
                "set",
                "org.gnome.desktop.interface",
                "scaling-factor",
                str(int(scaling)),
            ]
        )

        subprocess.call(
            [
                "gsettings",
                "set",
                "org.gnome.settings-daemon.plugins.xsettings",
                "overrides",
                f"{{'Gdk/WindowScalingFactor': <{int(scaling)}>}}",
            ]
        )

        return True

    @classmethod
    def post_xrandr_hook(cls, scaling: float):
        pass

    @classmethod
    def get_ui_scale(cls) -> float:
        ui_scale = float(
            subprocess.check_output(
                [
                    "gsettings",
                    "get",
                    "org.gnome.desktop.interface",
                    "scaling-factor",
                ]
            )
            .decode("utf-8")
            .split(" ")[1]
        )

        result = re.findall(
            r"Gdk\/WindowScalingFactor[\'\"]\W*:\W*<(\d*)>",
            subprocess.check_output(
                [
                    "gsettings",
                    "get",
                    "org.gnome.settings-daemon.plugins.xsettings",
                    "overrides",
                ]
            ).decode("utf-8"),
        )

        if len(result) > 0:
            ui_scale = max(ui_scale, float(result[0]))

        return ui_scale

    @classmethod
    def get_available_ui_scales(cls) -> List[float]:
        return [1, 2]
