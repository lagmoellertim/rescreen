import re
import subprocess
from threading import Thread
from typing import Callable

from rescreen.lib.utils import debounce


class ChangeListener(Thread):
    def __init__(self):
        super().__init__()
        self.__connection_event_callbacks = set()
        self.__any_event_callbacks = set()
        self.__displays = set()

    def add_connection_event_callback(self, callback: Callable):
        self.__connection_event_callbacks.add(callback)

    def add_any_event_callback(self, callback: Callable):
        self.__any_event_callbacks.add(callback)

    def __update_detected_displays(self):
        output = subprocess.check_output(["xrandr", "--listactivemonitors"]).decode("utf-8")

        current_displays = set(re.findall(r" \d+:.*  (.*)\n", output, re.M))

        added_displays = current_displays.difference(self.__displays)
        removed_displays = self.__displays.difference(current_displays)

        self.__displays = current_displays

        return len(added_displays) > 0 or len(removed_displays) > 0

    @debounce(2)
    def emit_all_events(self):
        for callback in self.__any_event_callbacks:
            callback()

    @debounce(2)
    def emit_connection_changed(self):
        for callback in self.__connection_event_callbacks:
            callback()

    def run(self) -> None:
        command = ["xev", "-root", "-event", "randr", "-1"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        for stdout_line in iter(process.stdout.readline, ""):
            line = stdout_line.decode("utf-8")
            if "RR_Disconnected" in line or "RR_Connected" in line:
                if self.__update_detected_displays():
                    self.emit_connection_changed()
            self.emit_all_events()

            print(line)

        process.stdout.close()
        return_code = process.wait()

        if return_code:
            raise subprocess.CalledProcessError(return_code, command)



