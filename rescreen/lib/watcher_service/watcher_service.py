import multiprocessing
import pwd
import sys
import time
from pathlib import Path
from typing import Dict

from loguru import logger

from rescreen.lib.watcher_service.service_worker import ServiceWorker


class WatcherService:
    def __init__(self, session_detection_interval=5):
        self.session_detection_interval = session_detection_interval
        self.__service_workers: Dict[str:ServiceWorker] = {}
        self.__logging_queue = multiprocessing.Queue(-1)
        self.__stop = False

    def __update_service_workers(self):
        maybe_working = []
        for path in Path("/proc").iterdir():
            if not path.is_dir():
                continue

            environ_file = path / "environ"

            if not environ_file.is_file():
                continue

            uid = environ_file.stat().st_uid

            if uid < 1000:
                continue

            environment_vars = {}

            try:
                with open(environ_file, "rb") as file:
                    for environ_entry in file.read().split(b"\0"):
                        try:
                            environ_entry = environ_entry.decode("ascii")
                        except UnicodeDecodeError:
                            continue

                        name, sep, value = environ_entry.partition("=")
                        if name and sep:
                            if name == "DISPLAY" and "." in value:
                                value = value[: value.find(".")]

                            environment_vars[name] = value

                    if "DISPLAY" not in environment_vars:
                        continue

                    if "XAUTHORITY" not in environment_vars:
                        maybe_working.append((environment_vars, uid))
                        continue

                    if not self._add_service_worker(uid, environment_vars):
                        continue
            except (OSError, PermissionError):
                logger.exception("Permission error while trying to access process files")
                sys.exit(126)

        for environment_vars, uid in maybe_working:
            if not self._add_service_worker(uid, environment_vars):
                continue

    def _add_service_worker(self, uid: int, environment_vars: Dict[str, str]) -> bool:
        display = environment_vars["DISPLAY"]

        if display in self.__service_workers.keys():
            return False

        try:
            user_data = pwd.getpwuid(uid)
        except KeyError:
            return False

        service_worker = ServiceWorker(user_data, environment_vars)
        service_worker.start()
        self.__service_workers[display] = service_worker
        return True

    def start(self):
        self.__stop = False
        logger.info("Watcher Service started")

        while not self.__stop:
            new_service_workers: Dict[str:ServiceWorker] = {}

            for display, service_worker in self.__service_workers.items():
                if service_worker.is_alive():
                    new_service_workers[display] = service_worker
                elif service_worker.exitcode == 126:
                    logger.critical("Permission error in Service Worker")
                    sys.exit(126)

            self.__service_workers = new_service_workers

            self.__update_service_workers()
            time.sleep(self.session_detection_interval)

    def stop(self):
        self.__stop = True
