from rescreen.lib import environment
from rescreen.lib.configuration import Configuration
from rescreen.lib.configuration_manager import load_configuration
from rescreen.lib.state import State
from rescreen.lib.xrandr import ChangeListener, get_current_display_data


def on_xrandr_connection_event():
    current_configuration = Configuration.from_state(
        State.from_xrandr_and_environment(
            get_current_display_data(), environment.check_and_get_desktop_environment()
        )
    )

    try:
        load_configuration(current_configuration)
    except Exception as e:
        print(e)


def main():
    environment.check_dependencies()
    change_listener = ChangeListener()
    change_listener.add_connection_event_callback(on_xrandr_connection_event)
    change_listener.start()
    change_listener.join()


if __name__ == "__main__":
    main()
