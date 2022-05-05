from rescreen.lib import environment
from rescreen.lib.xrandr import Settings, DisplaySettings

from .configuration import Configuration


def generate_xrandr_settings(configuration: Configuration) -> Settings:
    settings = Settings()

    for display in configuration.displays:
        display_settings = DisplaySettings(display.port)

        if not display.enabled:
            display_settings.set_inactive()
        else:
            (display_settings.set_scale(display.resolution_scale)
             .set_mode(*display.resolution)
             .set_refresh_rate(display.refresh_rate)
             .set_pos(*display.virtual_offset)
             .set_orientation(display.orientation)
             .set_panning(*display.virtual_resolution, *display.virtual_offset))

        if display.primary:
            display_settings.set_primary()

        settings.add_display_settings(display_settings)

    return settings


def apply_configuration(configuration: Configuration):
    desktop_environment = environment.check_and_get_desktop_environment()
    xrandr_settings = generate_xrandr_settings(configuration)

    desktop_environment.pre_xrandr_hook(configuration.ui_scale)
    xrandr_settings.apply()
    desktop_environment.post_xrandr_hook(configuration.ui_scale)
