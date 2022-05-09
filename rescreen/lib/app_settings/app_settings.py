import json
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel
import yaml

from rescreen.lib.utils import paths


class Tweaks(BaseModel):
    add_offset_to_xrandr_scale: float = 0
    disable_panning_on_internal_display: bool = True
    disable_panning_on_external_display: bool = False


class _AppSettings(BaseModel):
    resolution_scale_options: List[float] = [1, 1.25, 1.5, 1.75, 2]
    internal_port_names = ["eDP", "LVDS"]
    tweaks: Tweaks = Tweaks()

    @staticmethod
    def read_settings() -> "_AppSettings":
        _, read_paths = paths.get_config_paths()

        for path in read_paths:
            if (file_path := path / "rescreen.yaml").is_file():
                with open(file_path, "r", encoding="utf-8") as file:
                    raw_config = yaml.safe_load(file)
                    if raw_config is None:
                        raw_config = {}

                    instance = _AppSettings.parse_raw(json.dumps(raw_config))

                    logger.info(f"Found valid settings at '{file_path}'")
                    logger.debug(f"Settings: {instance}")
                    return instance

        logger.info("No settings found, writing default settings")

        instance = _AppSettings()
        instance.write_settings()
        return instance

    def write_settings(self) -> None:
        write_path, _ = paths.get_config_paths()

        settings_path = write_path / "rescreen.yaml"

        with open(settings_path, "w+", encoding="utf-8") as file:
            logger.info(f"Writing settings to {settings_path}")
            logger.debug(f"Settings: {self}")
            yaml.safe_dump(json.loads(self.json()), file)


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
