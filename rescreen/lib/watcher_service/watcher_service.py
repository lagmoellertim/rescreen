import enum
import multiprocessing
import pwd
import sys
import time
import dataclasses
from pathlib import Path
from typing import Dict, Tuple
from queue import PriorityQueue
from loguru import logger

from rescreen.lib.watcher_service.service_worker import ServiceWorker


class EnvironmentQuality(int, enum.Enum):
    HIGH = 1
    MEDIUM = 3
    LOW = 5


@dataclasses.dataclass(order=True)
class ComparableEnvironment:
    priority: float
    environment: Dict[str, str] = dataclasses.field(compare=False)
    uid: int = dataclasses.field(compare=False)


class WatcherService:
    def __init__(self, session_detection_interval=5):
        self.session_detection_interval = session_detection_interval
        self.__service_workers: Dict[str:ServiceWorker] = {}
        self.__logging_queue = multiprocessing.Queue(-1)
        self.__stop = False

    def __update_service_workers(self):
        envs_per_session: Dict[str, PriorityQueue[ComparableEnvironment]] = {}

        for path in Path("/proc").iterdir():
            if not path.is_dir():
                continue

            environ_file = path / "environ"

            if not environ_file.is_file():
                continue

            cmdline = None
            cmdline_file = path / "cmdline"

            if cmdline_file.is_file():
                with open(cmdline_file, "r", encoding="utf-8") as f:
                    cmdline = f.readline().strip()

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

                    env_score = 1 / len(environment_vars)

                    display = environment_vars["DISPLAY"]

                    envs_per_session.setdefault(display, PriorityQueue())

                    if "XAUTHORITY" not in environment_vars:
                        envs_per_session[display].put(
                            ComparableEnvironment(
                                priority=EnvironmentQuality.LOW.value + env_score,
                                environment=environment_vars,
                                uid=uid
                            )
                        )
                        continue

                    # Basic Requirements for Service Worker environment should be fulfilled here

                    if cmdline in ["/usr/bin/kded5"]:
                        envs_per_session[display].put(
                            ComparableEnvironment(
                                priority=EnvironmentQuality.HIGH.value + env_score,
                                environment=environment_vars,
                                uid=uid
                            )
                        )
                        continue

                    envs_per_session[display].put(
                        ComparableEnvironment(
                            priority=EnvironmentQuality.MEDIUM.value + env_score,
                            environment=environment_vars,
                            uid=uid
                        )
                    )

            except (OSError, PermissionError):
                logger.exception("Permission error while trying to access process files")
                sys.exit(126)

        for display, queue in envs_per_session.items():
            if display in self.__service_workers.keys():
                continue

            while not queue.empty():
                item = queue.get()

                try:
                    user_data = pwd.getpwuid(item.uid)
                except KeyError:
                    continue

                service_worker = ServiceWorker(user_data, item.environment)
                service_worker.start()
                self.__service_workers[display] = service_worker
                break

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
