import argparse
import signal
import subprocess
import sys

from PySide6.QtWidgets import QApplication
from loguru import logger

from rescreen.gui import MainController, MainWindow
from rescreen.gui.utils import error
from rescreen.lib import environment, xrandr
from rescreen.lib.configuration import Configuration
from rescreen.lib.configuration_manager import ConfigurationManager
from rescreen.lib.state import State
from rescreen.lib.utils.terminal import prompt
from rescreen.lib.watcher_service import WatcherService


def main():
    parser = argparse.ArgumentParser(description="Screen Arrangement and Scaling Utility")
    subparsers = parser.add_subparsers(help="Commands", dest="command", required=True)
    base_sub_parser = argparse.ArgumentParser(add_help=False)

    base_sub_parser.add_argument("-l", "--log", help="Enables logging to file", dest="logfile")

    base_sub_parser.add_argument(
        "-d",
        "--debug",
        help="Print lots of debugging statements",
        action="store_const",
        dest="loglevel",
        const="DEBUG",
        default="WARNING",
    )

    base_sub_parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="loglevel",
        const="INFO",
    )

    save_parser = subparsers.add_parser(
        "save", help="Save the current configuration", parents=[base_sub_parser]
    )
    load_parser = subparsers.add_parser(
        "load", help="Load the current configuration", parents=[base_sub_parser]
    )
    watcher_parser = subparsers.add_parser(
        "watcher",
        help="Watcher for detecting display changes (must be run as root)",
        parents=[base_sub_parser],
    )

    gui_parser = subparsers.add_parser(
        "gui", help="Starts the GUI for Screen Configuration", parents=[base_sub_parser]
    )

    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stdout, format="<level>{level: <8}</level> | {message}", level=args.loglevel)

    if args.logfile:
        logger.info(f"Logging to {args.logfile}")
        logger.add(
            args.logfile,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line}@{"
            "process.name} - {message}",
            enqueue=True,
            level=args.loglevel,
        )

    if args.command == "gui":
        return start_gui()

    try:
        environment.check_dependencies()
    except EnvironmentError:
        sys.exit(-1)

    if args.command == "watcher":
        return WatcherService().start()

    try:
        current_configuration = Configuration.from_state(State.current_state())
    except EnvironmentError:
        sys.exit(-1)
    except subprocess.CalledProcessError:
        sys.exit(-1)

    manager = ConfigurationManager()

    if args.command == "load":
        if manager.exists(current_configuration):
            try:
                ConfigurationManager().load_configuration(current_configuration).apply(
                    user_confirmation_method=prompt
                )
            except subprocess.CalledProcessError:
                sys.exit(-1)
            except OSError:
                sys.exit(-1)
        else:
            logger.info("No configuration for current setup found")

    elif args.command == "save":
        try:
            manager.save_configuration(current_configuration)
        except OSError:
            sys.exit(-1)


def start_gui():
    application = QApplication()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        environment.check_dependencies()
    except EnvironmentError as exception:
        error("Missing Dependencies", str(exception))
        sys.exit(-1)

    main_controller = MainController()
    main_window = MainWindow(main_controller)
    main_window.show()
    main_controller.reload_config()

    change_listener = xrandr.XEventWatcher()
    change_listener.daemon = True
    change_listener.add_any_event_callback(main_controller.reload_config)
    change_listener.start()

    exit_code = application.exec()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
