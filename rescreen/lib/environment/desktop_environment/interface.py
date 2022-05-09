from abc import ABC, abstractmethod
from typing import List


class DesktopEnvironmentInterface(ABC):
    name: str

    # Implemented externally
    @staticmethod
    def get_user_confirmation(_: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def is_current_desktop_environment(cls) -> bool:
        pass

    @classmethod
    @abstractmethod
    def pre_xrandr_hook(cls, scaling: float) -> bool:
        pass

    @classmethod
    @abstractmethod
    def post_xrandr_hook(cls, scaling: float) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_ui_scale(cls) -> float:
        pass

    @classmethod
    @abstractmethod
    def get_available_ui_scales(cls) -> List[float]:
        pass
