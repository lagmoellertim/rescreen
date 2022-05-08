import dataclasses
from typing import List, Optional

from rescreen.lib.app_settings import AppSettings
from rescreen.lib.environment import DesktopEnvironmentInterface
from rescreen.lib.interfaces import (
    Modes,
    Port,
    Resolution,
    RefreshRate,
    Offset,
    Orientation,
)
from rescreen.lib.xrandr import DisplayData
from .. import xrandr, environment


@dataclasses.dataclass
class DisplayState:
    port: Port
    name: str
    edid: str
    internal: bool

    resolution_scale: float
    available_resolution_scales: List[float]

    display_number: int
    modes: Modes

    resolution: Resolution
    refresh_rate: RefreshRate

    virtual_offset: Offset
    orientation: Orientation

    enabled: bool
    primary: bool

    @property
    def virtual_resolution(self) -> Resolution:
        return tuple(i * self.resolution_scale for i in self.resolution)

    @property
    def available_resolutions(self):
        return sorted(
            self.modes.keys(),
            key=lambda resolution: resolution[0] * resolution[1],
            reverse=True,
        )

    def get_available_refresh_rates(self, resolution: Resolution):
        return sorted(
            self.modes[resolution],
            key=float,
            reverse=True,
        )

    @staticmethod
    def from_display_data(data: DisplayData, display_number: int):
        resolution_scale = data.virtual_resolution[0] / data.current_resolution[0]

        if resolution_scale <= 0:  # Invalid valid
            resolution_scale = 1

        available_resolution_scales = list(
            sorted({resolution_scale, *AppSettings.instance().resolution_scale_options})
        )

        return DisplayState(
            display_number=display_number,
            name=data.name,
            edid=data.edid,
            modes=data.modes,
            port=data.port,
            primary=data.primary,
            enabled=data.enabled,
            resolution=data.current_resolution,
            refresh_rate=data.current_refresh_rate,
            resolution_scale=resolution_scale,
            available_resolution_scales=available_resolution_scales,
            virtual_offset=data.offset,
            orientation=data.orientation,
            internal=data.internal,
        )


@dataclasses.dataclass
class State:
    ui_scale: float
    available_ui_scales: List[float]
    current_desktop_environment: Optional[DesktopEnvironmentInterface]
    displays: List[DisplayState]

    @property
    def active_displays(self) -> List[DisplayState]:
        return [display for display in self.displays if display.enabled]

    def get_mirrored_displays(self, target_display: DisplayState) -> List[DisplayState]:
        result = []

        for display in self.active_displays:
            if (
                display != target_display
                and display.enabled
                and display.virtual_offset == target_display.virtual_offset
                and display.virtual_resolution == target_display.virtual_resolution
            ):
                result.append(display)

        return result

    @staticmethod
    def from_xrandr_and_environment(
        data: List[DisplayData], desktop_environment: Optional[DesktopEnvironmentInterface]
    ) -> "State":
        displays = [
            DisplayState.from_display_data(display_data, i + 1)
            for i, display_data in enumerate(data)
        ]

        ui_scale = 1
        available_ui_scales = [1]
        if desktop_environment is not None:
            ui_scale = desktop_environment.get_ui_scale()
            if ui_scale <= 0:
                ui_scale = 1

            available_ui_scales = list(
                sorted({*available_ui_scales, *desktop_environment.get_available_ui_scales()})
            )

        return State(
            displays=displays,
            ui_scale=ui_scale,
            current_desktop_environment=desktop_environment,
            available_ui_scales=available_ui_scales,
        )

    @staticmethod
    def current_state() -> "State":
        current_desktop_environment = environment.check_and_get_desktop_environment()

        return State.from_xrandr_and_environment(
            data=xrandr.get_current_display_data(), desktop_environment=current_desktop_environment
        )
