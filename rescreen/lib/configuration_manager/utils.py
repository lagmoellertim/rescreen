import os
from pathlib import Path

from rescreen.lib.configuration import Configuration


def get_config_path():
    config_home_path = Path(os.environ.setdefault("XDG_CONFIG_HOME", "~/.config")).expanduser().absolute()
    config_path = config_home_path / "rescreen"
    if not config_path.is_dir():
        config_path.mkdir(parents=True)

    return config_path


CONFIG_PATH = get_config_path()


def get_configuration_file(configuration: Configuration):
    return CONFIG_PATH / f"{configuration.display_setup_hash}.yaml"


def save_configuration(configuration: Configuration):
    with open(get_configuration_file(configuration), "w+") as f:
        configuration.to_yaml(f)


def load_configuration(configuration: Configuration):
    filename = get_configuration_file(configuration)

    if filename.is_file():
        with open(filename, "r") as f:
            return Configuration.from_yaml(f)

    raise AttributeError(f"No Configuration for the current setup found")
