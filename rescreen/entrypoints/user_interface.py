import sys
from sys import exit

from PySide6.QtWidgets import *

from rescreen.lib import xrandr
from rescreen.ui import MainWindow, MainController

def main():
    application = QApplication(sys.argv)

    main_controller = MainController()
    main_window = MainWindow(main_controller)
    main_window.show()
    main_controller.reload_config()

    change_listener = xrandr.ChangeListener()
    change_listener.daemon = True
    change_listener.add_any_event_callback(main_controller.reload_config)
    change_listener.start()

    exit(application.exec())

if __name__ == "__main__":
    main()