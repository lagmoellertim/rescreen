import dataclasses
import enum
import os
import platform
import subprocess
from typing import Optional

from loguru import logger

from .desktop_environment import (
    DesktopEnvironmentInterface,
    desktop_environment_collection,
)


class OperatingSystem(enum.Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    DARWIN = "darwin"

    def __str__(self):
        return self.value


class SessionType(enum.Enum):
    X11 = "x11"
    WAYLAND = "wayland"

    def __str__(self):
        return self.value


@dataclasses.dataclass
class Environment:
    operating_system: OperatingSystem
    session_type: Optional[SessionType]


def detect_session_type() -> Optional[SessionType]:
    if "XDG_SESSION_TYPE" in os.environ:
        session = os.environ.get("XDG_SESSION_TYPE")

        if session == "x11":
            return SessionType.X11
        if session == "wayland":
            return SessionType.WAYLAND

    session = (
        subprocess.check_output(
            "loginctl show-session $(loginctl show-user $(whoami) -p Display --value) -p Type --value",
            shell=True,
        )
        .decode("utf-8")
        .strip()
    )

    if session == "x11":
        return SessionType.X11
    if session == "wayland":
        return SessionType.WAYLAND


def detect_operating_system() -> Optional[OperatingSystem]:
    operating_system = platform.system()

    if operating_system == "Linux":
        return OperatingSystem.LINUX
    if operating_system == "Windows":
        return OperatingSystem.WINDOWS
    if operating_system == "Darwin":
        return OperatingSystem.DARWIN


def check_and_get_desktop_environment() -> Optional[DesktopEnvironmentInterface]:
    if (operating_system := detect_operating_system()) != OperatingSystem.LINUX:
        logger.critical(f"Invalid Operating System found: {operating_system}")
        raise EnvironmentError(f"This library only supports Linux, {operating_system} was found")

    if (session_type := detect_session_type()) != SessionType.X11:
        logger.critical(f"Invalid Session Type found: {session_type}")
        raise EnvironmentError(f"This library only supports x11, {session_type} was found")

    for desktop_environment in desktop_environment_collection:
        if desktop_environment.is_current_desktop_environment():
            logger.info(f"Found Desktop Environment: {desktop_environment.name}")
            return desktop_environment

    logger.warning("No desktop environment that is currently supported was found")
    return None
