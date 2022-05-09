import os
import pwd
import sys
from multiprocessing import Process
from typing import Dict

from PySide6.QtWidgets import QApplication
from loguru import logger

from rescreen.gui.utils import prompt
from rescreen.lib.configuration import Configuration
from rescreen.lib.configuration_manager import ConfigurationManager
from rescreen.lib.state import State
from rescreen.lib.xrandr import XEventWatcher


class ServiceWorker(Process):
    def __init__(
        self,
        user_data: pwd.struct_passwd,
        environment_vars: Dict[str, str],
    ):
        self.__user_data = user_data
        self.__environment_vars = environment_vars
        super().__init__()

    def run(self) -> None:
        try:
            os.setgroups(os.getgrouplist(self.__user_data.pw_name, self.__user_data.pw_gid))
            os.setresgid(
                self.__user_data.pw_gid,
                self.__user_data.pw_gid,
                self.__user_data.pw_gid,
            )
            os.setresuid(
                self.__user_data.pw_uid,
                self.__user_data.pw_uid,
                self.__user_data.pw_uid,
            )
            os.chdir(self.__user_data.pw_dir)
            os.environ.clear()
            os.environ.update(self.__environment_vars)
        except PermissionError:
            logger.exception("Not authorized to change linux environment")
            sys.exit(126)

        logger.info(f"Service Worker started for XSession {self.__environment_vars['DISPLAY']}")
        logger.debug(f"User Data: {self.__user_data}")
        logger.debug(f"Environment: {self.__environment_vars}")

        listener = XEventWatcher()
        listener.daemon = True
        listener.add_connection_event_callback(self.load_current_profile)
        self.load_current_profile()
        listener.start()

        listener.join()

    @staticmethod
    def load_current_profile():
        try:
            current_configuration = Configuration.from_state(State.current_state())
        except Exception:
            logger.exception("Failed to load current state")
            return

        manager = ConfigurationManager()

        if manager.exists(current_configuration):
            configuration = ConfigurationManager().load_configuration(current_configuration)

            try:
                application = QApplication()
                configuration.apply(prompt)
                application.exit()
            except Exception:
                logger.exception("Failed to apply configuration")
