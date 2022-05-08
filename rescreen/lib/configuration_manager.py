from pathlib import Path
from typing import Optional

from loguru import logger

from rescreen.lib.configuration import Configuration
from rescreen.lib.utils import paths


class ConfigurationManager:
    def __init__(self) -> None:
        (
            self.__write_config_path,
            self.__read_config_paths,
        ) = paths.get_config_paths(Path("configurations"))

    def find_configuration_file(self, configuration: Configuration) -> Optional[Path]:
        for config_path in self.__read_config_paths:
            file = config_path / f"{configuration.display_setup_hash}.yaml"
            if file.is_file():
                return file

        return None

    def save_configuration(self, configuration: Configuration) -> None:
        path = self.__write_config_path / f"{configuration.display_setup_hash}.yaml"

        logger.info(f"Saving configuration to {path}")
        logger.debug(configuration.json())

        with open(path, "w+", encoding="utf-8") as file:
            configuration.to_yaml(file)

    def exists(self, configuration: Configuration) -> bool:
        return self.find_configuration_file(configuration) is not None

    def load_configuration(self, configuration: Configuration) -> Configuration:
        filename = self.find_configuration_file(configuration)

        if filename is None:
            error = "No configuration for the current setup found"
            logger.warning(error)
            raise AttributeError(error)

        with open(filename, "r", encoding="utf-8") as file:
            return Configuration.from_yaml(file)
