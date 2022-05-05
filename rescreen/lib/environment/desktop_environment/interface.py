from abc import ABC, abstractmethod
from typing import List


class DesktopEnvironmentInterface(ABC):
    name: str

    @staticmethod
    @abstractmethod
    def is_current_desktop_environment() -> bool:
        pass

    @staticmethod
    @abstractmethod
    def pre_xrandr_hook(scaling: float):
        pass

    @staticmethod
    @abstractmethod
    def post_xrandr_hook(scaling: float):
        pass

    @staticmethod
    @abstractmethod
    def get_ui_scale() -> float:
        pass

    @staticmethod
    @abstractmethod
    def get_available_ui_scales() -> List[float]:
        pass
