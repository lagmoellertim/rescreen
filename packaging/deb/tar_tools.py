import subprocess
from pathlib import Path


def tar_directory(tar_output_file: Path, directory_path: Path, tar_path_prefix="./"):
    tar_path_prefix = tar_path_prefix.replace("/", "\\/")
    args = [
        "tar",
        "--exclude-vcs-ignores",
        "--exclude-vcs",
        "--exclude", "build",
        "--exclude", "*.tar.gz",
        "--exclude", "*.tar",
        "-zcf",
        str(tar_output_file),
        ".",
        "--transform",
        f"s/.\\//{tar_path_prefix}/"
    ]

    subprocess.run(args, check=True, cwd=directory_path)


def untar(tar_input_file: Path, tar_output: Path):
    subprocess.run(["tar", "xf", str(tar_input_file), "--directory", str(tar_output)], check=True)
