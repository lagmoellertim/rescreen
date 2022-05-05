from rescreen.lib import environment
from .state_structure import State
from .. import xrandr


def get_current_state() -> State:
    return State.from_xrandr_and_environment(
        xrandr.get_current_display_data(),
        environment.check_and_get_desktop_environment()
    )
