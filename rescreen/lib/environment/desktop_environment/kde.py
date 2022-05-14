import os
import subprocess
from pathlib import Path
from subprocess import PIPE, STDOUT
from typing import List

from .interface import DesktopEnvironmentInterface


class KDE(DesktopEnvironmentInterface):
    name = "kde"

    BASE_FONT_DPI = 96
    CONFIG_DIR = Path("~/.config/")

    SCALING_CONFIG = "kdeglobals"
    FONT_CONFIG = "kcmfonts"
    CURSOR_CONFIG = "kcminputrc"
    CURSOR_STARTUP_CONFIG = "startupconfig"

    @classmethod
    def set_cursor_size(cls, cursor_size: int) -> None:
        subprocess.call(
            [
                "kwriteconfig5",
                "--file",
                str(cls.CONFIG_DIR.expanduser() / cls.CURSOR_CONFIG),
                "--group",
                "Mouse",
                "--key",
                "cursorSize",
                str(cursor_size),
            ]
        )

    @classmethod
    def is_current_desktop_environment(cls) -> bool:
        if os.environ.get("DESKTOP_SESSION") == "plasma":
            return True

        if os.environ.get("XDG_SESSION_DESKTOP") == "KDE":
            return True

        return False

    @staticmethod
    def logout() -> None:
        subprocess.call(["qdbus", "org.kde.ksmserver", "/KSMServer", "logout", "0", "3", "3"])

    @classmethod
    def pre_xrandr_hook(cls, scaling: float) -> bool:
        if scaling == cls.get_ui_scale():
            return True

        if not cls.get_user_confirmation(
                "To apply the display configuration, a session restart is required. "
                "All currently open applications will be closed. Continue?"
        ):
            return False

        config_dir = cls.CONFIG_DIR.expanduser()

        scaling = int(scaling)

        subprocess.call(
            [
                "kwriteconfig5",
                "--file",
                str(config_dir / cls.SCALING_CONFIG),
                "--group",
                "KScreen",
                "--key",
                "ScaleFactor",
                str(scaling),
            ]
        )

        screen_scale_factors = (
            subprocess.check_output(
                [
                    "kreadconfig5",
                    "--file",
                    str(config_dir / cls.SCALING_CONFIG),
                    "--group",
                    "KScreen",
                    "--key",
                    "ScreenScaleFactors",
                    "--default",
                    "",
                ]
            )
                .decode("utf-8")
                .strip()
        )

        new_screen_scale_factors = ""
        for pair in screen_scale_factors.split(";"):
            try:
                port, _ = pair.split("=")
                new_screen_scale_factors += f"{port}={scaling};"
            except ValueError:
                continue

        subprocess.call(
            [
                "kwriteconfig5",
                "--file",
                str(config_dir / cls.SCALING_CONFIG),
                "--group",
                "KScreen",
                "--key",
                "ScreenScaleFactors",
                new_screen_scale_factors,
            ]
        )

        font_dpi = int(96 * scaling)

        subprocess.call(
            [
                "kwriteconfig5",
                "--file",
                str(config_dir / cls.FONT_CONFIG),
                "--group",
                "General",
                "--key",
                "forceFontDPI",
                str(font_dpi),
            ]
        )

        if scaling == 2:
            cls.set_cursor_size(36)
        else:
            cls.set_cursor_size(24)

        process = subprocess.Popen(
            ["xrdb", "-quiet", "-merge", "-nocpp"], stdout=PIPE, stdin=PIPE, stderr=STDOUT
        )

        process.communicate(input=f"Xft.dpi: {font_dpi}\n".encode("utf-8"))

        cls.logout()

        return False

    @classmethod
    def post_xrandr_hook(cls, scaling: float) -> None:
        try:
            subprocess.run("killall plasmashell", check=True, shell=True)
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                pass  # No plasmashell found
            else:
                raise e

        subprocess.run("PLASMA_USE_QT_SCALING=1 kstart5 plasmashell", check=True, shell=True)

    @classmethod
    def get_ui_scale(cls) -> float:
        scale_factor = (
            subprocess.check_output(
                [
                    "kreadconfig5",
                    "--file",
                    str(cls.CONFIG_DIR.expanduser() / cls.SCALING_CONFIG),
                    "--group",
                    "KScreen",
                    "--key",
                    "ScaleFactor",
                    "--default",
                    "1",
                ]
            )
                .decode("utf-8")
                .strip()
        )
        return float(scale_factor)

    @classmethod
    def get_available_ui_scales(cls) -> List[float]:
        return [1, 2]
