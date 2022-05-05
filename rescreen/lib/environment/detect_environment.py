import dataclasses
import enum
import os
import platform
import subprocess
from typing import Optional

from .desktop_environment import DesktopEnvironmentInterface, desktop_environment_collection


class OperatingSystem(enum.Enum):
    Windows = "windows"
    Linux = "linux"
    Darwin = "darwin"


class SessionType(enum.Enum):
    X11 = "x11"
    Wayland = "wayland"


@dataclasses.dataclass
class Environment:
    operating_system: OperatingSystem
    session_type: Optional[SessionType]


def detect_session_type() -> Optional[SessionType]:
    if "XDG_SESSION_TYPE" in os.environ:
        session = os.environ.get("XDG_SESSION_TYPE")

        if session == "x11":
            return SessionType.X11
        elif session == "wayland":
            return SessionType.Wayland

    session = (subprocess.check_output(
        "loginctl show-session $(loginctl show-user $(whoami) -p Display --value) -p Type --value", shell=True)
               .decode("utf-8")
               .strip())

    if session == "x11":
        return SessionType.X11
    elif session == "wayland":
        return SessionType.Wayland


def detect_operating_system() -> OperatingSystem:
    operating_system = platform.system()

    if operating_system == "Linux":
        return OperatingSystem.Linux
    elif operating_system == "Windows":
        return OperatingSystem.Windows
    elif operating_system == "Darwin":
        return OperatingSystem.Darwin


def check_and_get_desktop_environment() -> Optional[DesktopEnvironmentInterface]:
    if (operating_system := detect_operating_system()) != OperatingSystem.Linux:
        raise EnvironmentError(f"This library only supports Linux, {operating_system} was found.")

    if (session_type := detect_session_type()) != SessionType.X11:
        raise EnvironmentError(f"This library only supports x11, {session_type} was found")

    for desktop_environment in desktop_environment_collection:
        if desktop_environment.is_current_desktop_environment():
            return desktop_environment

    raise EnvironmentError(f"The current desktop environment is not supported")
