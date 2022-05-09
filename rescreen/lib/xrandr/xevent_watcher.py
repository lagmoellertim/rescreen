import atexit
import re
import subprocess
from threading import Thread
from typing import Callable, Optional

from loguru import logger

from rescreen.lib.utils.decorator import debounce


class XEventWatcher(Thread):
    def __init__(self):
        super().__init__()
        self.__connection_event_callbacks = set()
        self.__any_event_callbacks = set()
        self.__displays = set()
        self.__process: Optional[subprocess.Popen] = None
        atexit.register(self.stop)

    def add_connection_event_callback(self, callback: Callable[[], None]) -> None:
        self.__connection_event_callbacks.add(callback)

    def add_any_event_callback(self, callback: Callable[[], None]) -> None:
        self.__any_event_callbacks.add(callback)

    def __update_detected_displays(self) -> bool:
        result = subprocess.run(["xrandr", "--listactivemonitors"], check=True, capture_output=True)
        output = result.stdout.decode("utf-8")

        current_displays = set(re.findall(r" \d+:.*  (.*)\n", output, re.M))

        added_displays = current_displays.difference(self.__displays)
        removed_displays = self.__displays.difference(current_displays)

        logger.debug(f"Displays {added_displays} added, Displays {removed_displays} removed")

        self.__displays = current_displays

        return len(added_displays) > 0 or len(removed_displays) > 0

    @debounce(3)
    def emit_all_events(self):
        logger.info("Debounced XSession Event occurred, notifying callbacks")
        for callback in self.__any_event_callbacks:
            callback()

    @debounce(3)
    def emit_connection_changed(self):
        logger.info("Debounced XSession Display Connection Event occurred, notifying callbacks")
        for callback in self.__connection_event_callbacks:
            callback()

    def run(self) -> None:
        command = ["xev", "-root", "-event", "randr"]

        with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
            self.__process = process
            for stdout_line in process.stdout:
                line = stdout_line.decode("utf-8").strip()
                logger.debug(f"XSession Event: {line}")
                if "RR_Disconnected" in line or "RR_Connected" in line:
                    if self.__update_detected_displays():
                        self.emit_connection_changed()
                self.emit_all_events()

            self.__process = None
            process.stdout.close()
            return_code = process.wait()

            if return_code > 0 and return_code != 2:
                raise subprocess.CalledProcessError(return_code, command)

    def stop(self):
        if self.__process:
            self.__process.terminate()
