import re
import subprocess
from pathlib import Path
import tar_tools
import os

import argparse

def create_package(version: str, input_path: Path, output_path: Path, revision=1):
    pkg_dir = output_path / f"rescreen_{version}-{revision}_all"
    pkg_dir.mkdir(exist_ok=True)
    tar_tools.tar_directory(output_path / "src.tar.gz", input_path, "src/")
    tar_tools.untar(output_path / "src.tar.gz", output_path)
    src_dir = output_path / "src"

    subprocess.run(["make"], cwd=src_dir, check=True)

    env = os.environ.copy()
    env["DESTDIR"] = pkg_dir
    subprocess.run(["make", "install"], env=env, cwd=src_dir)

    debian_dir = pkg_dir / "DEBIAN"
    debian_dir.mkdir(exist_ok=True)

    with open(Path(__file__).parent / "control_template", "r") as f:
        control = "".join(f.readlines())
        control = re.sub("^Version:.*$", f"Version: {version}-{revision}", control, flags=re.M)

    with open(debian_dir / "control", "w+") as f:
        f.write(control)

    subprocess.run(["dpkg-deb", "--build", "--root-owner-group", pkg_dir], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate DEB Packages for rescreen')
    parser.add_argument("-v", "--version", help="Version to use for the Package", required=True)
    parser.add_argument("-r", "--revision", help="Revision to use for the Package", default=1, type=int)
    parser.add_argument("-o", "--output", help="Path to the directory where the deb "
                                               "Package should be stored", required=True, type=Path)
    parser.add_argument("-i", "--input", help="Path to the rescreen source", required=True,
                        type=Path)

    args = parser.parse_args()
    create_package(version=args.version, revision=args.revision, input_path=args.input, output_path=args.output)
