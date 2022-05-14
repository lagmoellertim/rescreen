import os
from pathlib import Path
from typing import Tuple, List, Optional


def get_config_paths(suffix: Optional[Path] = None) -> Tuple[Path, List[Path]]:
    config_home = "~/.config"
    if "XDG_CONFIG_HOME" in os.environ:
        config_home = os.environ["XDG_CONFIG_HOME"]

    config_dirs = "/etc/xdg"
    if "XDG_CONFIG_DIRS" in os.environ:
        config_dirs = os.environ["XDG_CONFIG_DIRS"]

    config_home_path = (
            Path(config_home).expanduser().absolute()
            / "rescreen"
    )

    if suffix:
        config_home_path /= suffix

    config_paths = []
    for path_str in config_dirs.split(":"):
        path = Path(path_str).expanduser().absolute() / "rescreen"
        if suffix:
            path /= suffix
        config_paths.append(path)

    if not config_home_path.is_dir():
        config_home_path.mkdir(parents=True)

    write_config_path = config_home_path
    read_config_paths = [config_home_path, *config_paths]

    return write_config_path, read_config_paths
