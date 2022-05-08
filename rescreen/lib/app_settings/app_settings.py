import json
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel
from ruamel.yaml import YAML

from rescreen.lib.utils import paths


class _AppSettings(BaseModel):
    resolution_scale_options: List[float] = [1, 1.25, 1.5, 1.75, 2]

    @staticmethod
    def read_settings() -> "_AppSettings":
        _, read_paths = paths.get_config_paths()

        for path in read_paths:
            if (file_path := path / "config.yaml").is_file():
                with open(file_path, "r", encoding="utf-8") as file:
                    yaml = YAML(typ="safe")
                    instance = _AppSettings.parse_raw(json.dumps(yaml.load(file)))

                    logger.info(f"Found valid settings at '{file_path}'")
                    logger.debug(f"Settings: {instance}")
                    return instance

        logger.info("No settings found, writing default settings")

        instance = _AppSettings()
        instance.write_settings()
        return instance

    def write_settings(self) -> None:
        write_path, _ = paths.get_config_paths()

        settings_path = write_path / "config.yaml"

        with open(settings_path, "w+", encoding="utf-8") as file:
            logger.info(f"Writing settings to {settings_path}")
            logger.debug(f"Settings: {self}")
            yaml = YAML(typ="safe")
            yaml.dump(json.loads(self.json()), file)


class AppSettings:
    __instance: Optional["_AppSettings"] = None

    @classmethod
    def instance(cls):
        if cls.__instance:
            return cls.__instance
        cls.__instance = _AppSettings.read_settings()
        return cls.__instance

    def __init__(self):
        raise SyntaxError("Can't initialize a singleton")

    def __call__(self, *args, **kwargs):
        raise SyntaxError("Can't call a singleton")
