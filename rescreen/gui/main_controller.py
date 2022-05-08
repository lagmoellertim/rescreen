import subprocess
import sys
from typing import Optional

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

from rescreen.gui import utils
from rescreen.lib.configuration import Configuration
from rescreen.lib.configuration_manager import ConfigurationManager
from rescreen.lib.interfaces import Resolution, RefreshRate, Offset, Orientation
from rescreen.lib.state import State, DisplayState


class MainController(QObject):
    on_current_display_changed = Signal()
    on_current_display_config_changed = Signal()
    on_preview_changed = Signal()

    def __init__(self):
        super().__init__()
        self.__state: Optional[State] = None
        self.__current_display: Optional[DisplayState] = None

    def reload_config(self, emit=True):
        try:
            self.__state = State.current_state()
        except EnvironmentError as exception:
            utils.error("Environment Error", str(exception))
            sys.exit(-1)
        except subprocess.CalledProcessError as exception:
            utils.error("XRandR Error", str(exception))
            sys.exit(-1)

        if len(self.__state.displays) > 0:
            self.__current_display = self.__state.displays[0]

        if emit:
            self.on_current_display_changed.emit()
            self.on_current_display_config_changed.emit()
            self.on_preview_changed.emit()

        if self.__state.current_desktop_environment is None:
            utils.error(
                "The Desktop Environment was not recognized, the UI scaling option will be disabled"
            )

    def get_current_state(self):
        return self.__state

    def get_current_display(self):
        return self.__current_display

    def set_current_resolution(self, resolution: Resolution, emit=True):
        if not self.__current_display:
            return

        self.__current_display.resolution = resolution
        self.set_current_refresh_rate(
            self.__current_display.get_available_refresh_rates(resolution)[0],
            emit=False,
        )

        if emit:
            self.on_current_display_config_changed.emit()

    def set_current_refresh_rate(self, refresh_rate: RefreshRate, emit=True):
        if not self.__current_display:
            return

        self.__current_display.refresh_rate = refresh_rate

        if emit:
            self.on_current_display_config_changed.emit()

    def set_current_display(self, display: DisplayState, emit=True):
        self.__current_display = display

        if emit:
            self.on_current_display_changed.emit()

    def set_current_orientation(self, orientation: Orientation, emit=True):
        if not self.__current_display:
            return

        self.__current_display.orientation = orientation

        if emit:
            self.on_current_display_config_changed.emit()

    @staticmethod
    def set_display_offset(display: DisplayState, virtual_offset: Offset
    ) -> None:
        display.virtual_offset = virtual_offset

    def set_ui_scaling(self, ui_scale: float) -> None:
        if not self.__state:
            return

        self.__state.ui_scale = ui_scale

        self.on_current_display_config_changed.emit()

    def set_resolution_scaling(self, resolution_scale: float) -> None:
        if not self.__current_display:
            return

        self.__current_display.resolution_scale = resolution_scale

        self.on_current_display_config_changed.emit()

    def set_primary(self) -> None:
        if not self.__current_display or not self.__state:
            return

        if self.__current_display.enabled:
            for display in self.__state.active_displays:
                display.primary = False

            self.__current_display.primary = True

        self.on_current_display_config_changed.emit()

    def set_enabled(self, value: bool) -> None:
        if not self.__current_display:
            return

        self.__current_display.enabled = value

        self.on_current_display_config_changed.emit()

    def apply_config(self) -> None:
        current_configuration = Configuration.from_state(self.__state)

        try:
            current_configuration.apply(user_confirmation_method=utils.prompt)
        except subprocess.CalledProcessError as exception:
            utils.error("XRandR Error", exception.stderr.decode("utf-8"))
            return
        except Exception as exception:
            utils.error("Error", str(exception))
            return

        manager = ConfigurationManager()

        try:
            manager.save_configuration(current_configuration)
        except OSError as exception:
            utils.error("Error", str(exception))
