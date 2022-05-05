from typing import Optional

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

from rescreen.lib import state, configuration
from rescreen.lib.configuration import Configuration
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
        self.__state = state.get_current_state()

        if len(self.__state.displays) > 0:
            self.__current_display = self.__state.displays[0]

        if emit:
            self.on_current_display_changed.emit()
            self.on_current_display_config_changed.emit()
            self.on_preview_changed.emit()

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
            emit=False
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

    def set_display_offset(self, display: DisplayState, virtual_offset: Offset, emit=True):
        display.virtual_offset = virtual_offset

    def set_ui_scaling(self, ui_scale: float):
        if not self.__state:
            return

        self.__state.ui_scale = ui_scale

        self.on_current_display_config_changed.emit()

    def set_resolution_scaling(self, resolution_scale: float):
        if not self.__current_display:
            return

        self.__current_display.resolution_scale = resolution_scale

        self.on_current_display_config_changed.emit()

    def set_primary(self):
        if not self.__current_display or not self.__state:
            return

        if self.__current_display.enabled:
            for display in self.__state.active_displays:
                display.primary = False

            self.__current_display.primary = True

        self.on_current_display_config_changed.emit()

    def set_enabled(self, value: bool):
        if not self.__current_display:
            return

        self.__current_display.enabled = value

        self.on_current_display_config_changed.emit()

    def apply_config(self):
        current_configuration = Configuration.from_state(self.__state)
        configuration.apply_configuration(current_configuration)
