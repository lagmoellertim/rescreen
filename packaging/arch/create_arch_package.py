import argparse
import re
import subprocess
from pathlib import Path
from typing import Optional
import tar_tools


def generate_pkgbuild(
    version: str, output_path: Path, from_local_dir: Optional[Path] = None, revision=1
):
    source = "$pkgname-$pkgver.tar.gz::$url/archive/$pkgver.tar.gz"

    if from_local_dir is not None:
        filename = f"local-rescreen-{version}.tar.gz"
        source = filename
        local_dir = from_local_dir.expanduser().absolute()
        tar_tools.tar_directory(output_path / filename, local_dir, f"rescreen-{version}/")

    with open(Path(__file__).parent / "PKGBUILD_TEMPLATE", "r") as f:
        pkgbuild = "".join(f.readlines())
        pkgbuild = re.sub(r"pkgver=.*", f"pkgver={version}", pkgbuild)
        pkgbuild = re.sub(r"pkgrel=.*", f"pkgrel={revision}", pkgbuild)
        pkgbuild = re.sub(r"source=\(['\"].*['\"]\)", f'source=("{source}")', pkgbuild)

    with open(output_path / "PKGBUILD", "w+") as f:
        f.write(pkgbuild)


def checksum_pkgbuild(path: Path):
    sha512_regex_pattern = r"""sha512sums=\(['"](.*)['"]\)"""
    try:
        result = subprocess.run(["makepkg", "-g"], cwd=path, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise e
    regex_result = re.findall(sha512_regex_pattern, result.stdout.decode("utf-8"))

    if not regex_result:
        raise AttributeError("SHA512Sum not in SubProcess Output")
    sha512sum = regex_result[0]

    with open(path / "PKGBUILD", "r+") as f:
        result = re.sub(sha512_regex_pattern, f"sha512sums=('{sha512sum}')", "".join(f.readlines()))
        f.seek(0)
        f.write(result)
        f.truncate()


def create_package(path: Path):
    subprocess.run(["makepkg", "-f", "--noconfirm", "--nodeps"], cwd=path, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Arch Packages for rescreen")
    parser.add_argument("-v", "--version", help="Version to use for the Package", required=True)
    parser.add_argument(
        "-r", "--revision", help="Revision to use for the Package", default=1, type=int
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the directory where the deb " "Package should be stored",
        required=True,
        type=Path,
    )
    parser.add_argument("-i", "--input", help="Path to the rescreen source", type=Path)

    parser.add_argument(
        "-ic",
        "--ignore-checksum",
        help="Don't add a Checksum to the PKGBUILD",
        action="store_false",

        dest="checksum",
    )
    parser.add_argument(
        "-ip",
        "--ignore-package-build",
        help="Don't create a package from the PKGBUILD File",
        action="store_false",
        dest="create_package",
    )

    args = parser.parse_args()

    output = args.output
    from_local_dir = None
    if "input" in args:
        from_local_dir = args.input

    generate_pkgbuild(
        version=args.version, revision=args.revision, from_local_dir=from_local_dir, output_path=output
    )

    if args.checksum:
        checksum_pkgbuild(output)

    if args.create_package:
        create_package(output)
