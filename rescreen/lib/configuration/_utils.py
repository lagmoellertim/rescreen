from typing import TYPE_CHECKING, Callable

from loguru import logger

from rescreen.lib import environment
from rescreen.lib.xrandr import Settings, DisplaySettings

if TYPE_CHECKING:
    from .configuration import Configuration


def to_xrandr_settings(configuration: "Configuration") -> Settings:
    settings = Settings()

    for display in configuration.displays:
        display_settings = DisplaySettings(display.port)

        if not display.enabled:
            display_settings.set_inactive()
        else:
            (
                display_settings.set_scale(display.resolution_scale)
                .set_mode(*display.resolution)
                .set_refresh_rate(display.refresh_rate)
                .set_pos(*display.virtual_offset)
                .set_orientation(display.orientation)
            )

            if not display.internal:
                display_settings.set_panning(*display.virtual_resolution, *display.virtual_offset)

        if display.primary:
            display_settings.set_primary()

        settings.add_display_settings(display_settings)

    return settings


def apply(configuration: "Configuration", user_confirmation_method: Callable[[str], bool]) -> None:
    desktop_environment = environment.check_and_get_desktop_environment()
    xrandr_settings = to_xrandr_settings(configuration)

    desktop_environment.get_user_confirmation = user_confirmation_method

    logger.info("Pre-XRandR-Hook gets executed")
    if desktop_environment.pre_xrandr_hook(configuration.ui_scale):
        logger.info("XRandR gets executed")
        xrandr_settings.apply()
        logger.info("Post-XRandR-Hook gets executed")
        desktop_environment.post_xrandr_hook(configuration.ui_scale)
    else:
        logger.info("Pre-XRandR-Hook stopped XRandR and Post-XRandR-Hook from execution")
