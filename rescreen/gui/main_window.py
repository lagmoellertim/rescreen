from typing import Union

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QCheckBox, QRadioButton, QComboBox

from rescreen.gui.main_controller import MainController
from rescreen.lib.interfaces import Orientation
from rescreen.lib.utils.misc import calculate_aspect_ratio
from .layouts.main_layout import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, controller: MainController, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setupUi(self)
        self.preview.set_controller(controller)
        self.retranslateUi(self)

        icon = QIcon()
        icon.addFile(
            "/usr/share/icons/rescreen.png",
            QSize(),
            QIcon.Normal,
            QIcon.Off,
        )
        self.setWindowIcon(icon)

        self.controller = controller
        self.controller.on_current_display_changed.connect(self.update_all)
        self.controller.on_current_display_config_changed.connect(self.update_config)

        self.refresh_button.clicked.connect(lambda: self.controller.reload_config())
        self.apply_button.clicked.connect(lambda: self.controller.apply_config())

    def update_display_selection(self):
        try:
            self.display_selection_dropdown.currentIndexChanged.disconnect()
        except RuntimeError:
            pass

        self.display_selection_dropdown.clear()

        current_display = self.controller.get_current_display()
        connected_displays = []

        if self.controller.get_current_state():
            connected_displays = self.controller.get_current_state().displays

            for i, display in enumerate(connected_displays):
                self.display_selection_dropdown.addItem(
                    f"{display.display_number}. {display.name} ({display.port})",
                    display,
                )

                if display == current_display:
                    self.display_selection_dropdown.setCurrentIndex(i)

        self.display_selection_dropdown.currentIndexChanged.connect(self.on_display_changed)

        if current_display is None and len(connected_displays) > 0:
            self.controller.set_current_display(connected_displays[0])

    def __setup_display_settings_radio_and_checkbox(self, item: Union[QCheckBox, QRadioButton]):
        if self.controller.get_current_display():
            item.setDisabled(False)
            return True

        else:
            item.setChecked(False)
            item.setDisabled(True)

        return False

    def __setup_display_settings_dropdown(self, item: QComboBox):
        current_display = self.controller.get_current_display()

        if current_display:
            if current_display.enabled:
                item.setDisabled(False)
            else:
                item.setDisabled(True)
            item.clear()
            return True
        else:
            item.setDisabled(True)
            item.clear()

        return False

    def update_enabled_checkbox(self):
        try:
            self.enabled_checkbox.clicked.disconnect()
        except RuntimeError:
            pass

        if self.__setup_display_settings_radio_and_checkbox(self.enabled_checkbox):
            self.enabled_checkbox.setChecked(self.controller.get_current_display().enabled)

        self.enabled_checkbox.clicked.connect(self.on_enabled_changed)

    def update_primary_display_radio(self):
        try:
            self.primary_display_radio.clicked.disconnect()
        except RuntimeError:
            pass

        if self.__setup_display_settings_radio_and_checkbox(self.primary_display_radio):
            self.primary_display_radio.setChecked(self.controller.get_current_display().primary)

        self.primary_display_radio.clicked.connect(self.on_primary_display_changed)

    def update_orientation_selection(self):
        try:
            self.orientation_dropdown.currentIndexChanged.disconnect()
        except RuntimeError:
            pass

        if self.__setup_display_settings_dropdown(self.orientation_dropdown):
            self.orientation_dropdown.addItem("Landscape", Orientation.NORMAL)
            self.orientation_dropdown.addItem("Portrait Left", Orientation.LEFT)
            self.orientation_dropdown.addItem("Portrait Right", Orientation.RIGHT)
            self.orientation_dropdown.addItem("Landscape (flipped)", Orientation.INVERTED)

            orientationMapping = {
                Orientation.NORMAL: 0,
                Orientation.LEFT: 1,
                Orientation.RIGHT: 2,
                Orientation.INVERTED: 3,
            }

            self.orientation_dropdown.setCurrentIndex(
                orientationMapping[self.controller.get_current_display().orientation]
            )

        self.orientation_dropdown.currentIndexChanged.connect(self.on_orientation_changed)

    def update_resolution_selection(self):
        try:
            self.resolution_dropdown.currentIndexChanged.disconnect()
        except RuntimeError:
            pass

        if self.__setup_display_settings_dropdown(self.resolution_dropdown):
            current_display = self.controller.get_current_display()

            for i, resolution in enumerate(current_display.available_resolutions):
                aspect_ratio = calculate_aspect_ratio(resolution[0], resolution[1])
                self.resolution_dropdown.addItem(
                    f"{resolution[0]} x {resolution[1]} ({aspect_ratio[0]}:{aspect_ratio[1]})",
                    resolution,
                )

                if resolution == current_display.resolution:
                    self.resolution_dropdown.setCurrentIndex(i)

        self.resolution_dropdown.currentIndexChanged.connect(self.on_resolution_changed)

    def update_refresh_rate_selection(self):
        try:
            self.refresh_rate_dropdown.currentIndexChanged.disconnect()
        except RuntimeError:
            pass

        current_display = self.controller.get_current_display()

        if self.__setup_display_settings_dropdown(self.refresh_rate_dropdown):
            for i, refresh_rate in enumerate(
                current_display.get_available_refresh_rates(current_display.resolution)
            ):
                self.refresh_rate_dropdown.addItem(refresh_rate, refresh_rate)

                if refresh_rate == current_display.refresh_rate:
                    self.refresh_rate_dropdown.setCurrentIndex(i)

        self.refresh_rate_dropdown.currentIndexChanged.connect(self.on_refresh_rate_changed)

    def update_ui_scaling_selection(self):
        try:
            self.ui_scale_dropdown.currentIndexChanged.disconnect()
        except RuntimeError:
            pass

        if self.__setup_display_settings_dropdown(self.ui_scale_dropdown):
            for i, scale in enumerate(self.controller.get_current_state().available_ui_scales):
                self.ui_scale_dropdown.addItem(f"{int(scale * 100)} %", scale)

                if scale == self.controller.get_current_state().ui_scale:
                    self.ui_scale_dropdown.setCurrentIndex(i)

            if self.controller.get_current_state().current_desktop_environment is None:
                self.ui_scale_dropdown.setDisabled(True)

        self.ui_scale_dropdown.currentIndexChanged.connect(self.on_ui_scaling_changed)

    def update_resolution_scaling(self):
        try:
            self.resolution_scale_dropdown.currentIndexChanged.disconnect()
        except RuntimeError:
            pass

        if self.__setup_display_settings_dropdown(self.resolution_scale_dropdown):
            for i, scale in enumerate(
                self.controller.get_current_display().available_resolution_scales
            ):
                self.resolution_scale_dropdown.addItem(f"{int(scale * 100)} %", scale)

                if scale == self.controller.get_current_display().resolution_scale:
                    self.resolution_scale_dropdown.setCurrentIndex(i)

        self.resolution_scale_dropdown.currentIndexChanged.connect(
            self.on_resolution_scaling_changed
        )

    def on_resolution_changed(self, _):
        self.controller.set_current_resolution(self.resolution_dropdown.currentData())

    def on_refresh_rate_changed(self, _):
        self.controller.set_current_refresh_rate(self.refresh_rate_dropdown.currentData())

    def on_display_changed(self, _):
        self.controller.set_current_display(self.display_selection_dropdown.currentData())

    def on_orientation_changed(self, _):
        self.controller.set_current_orientation(self.orientation_dropdown.currentData())

    def on_ui_scaling_changed(self, _):
        self.controller.set_ui_scaling(self.ui_scale_dropdown.currentData())

    def on_resolution_scaling_changed(self, _):
        self.controller.set_resolution_scaling(self.resolution_scale_dropdown.currentData())

    def on_primary_display_changed(self, _):
        self.controller.set_primary()

    def on_enabled_changed(self, value: bool):
        self.controller.set_enabled(value)

    def update_config(self):
        self.update_resolution_selection()
        self.update_refresh_rate_selection()
        self.update_orientation_selection()
        self.update_ui_scaling_selection()
        self.update_resolution_scaling()
        self.update_primary_display_radio()
        self.update_enabled_checkbox()

    def update_all(self):
        self.update_display_selection()
        self.update_config()
