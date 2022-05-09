import re
import subprocess
from typing import List, Optional

from loguru import logger

from rescreen.lib.interfaces import Orientation
from rescreen.lib.xrandr import DisplayData
from rescreen.lib.app_settings import AppSettings

def get_current_display_data(
    x_display: Optional[str] = None,
) -> List[DisplayData]:
    pattern = re.compile(
        r"^(?P<port>\S*) connected (?:(?P<primary>primary)?(?:\s?)(?P<virtual_width>\d*)x("
        r"?P<virtual_height>\d*)\+(?P<x_offset>\d*)\+(?P<y_offset>\d*) )?(?:("
        r"?P<orientation>normal|left|right|inverted) )?\((?P<params>.*)\)(?: (?P<width_mm>\d*)mm "
        r"x (?P<height_mm>\d*)mm)?.*\n(?P<metadata>(?:\s+[^\n]*\n)*)",
        re.M,
    )
    edid_pattern = re.compile(r"EDID:\s*\n(?P<edid>(?:\t\t.*\n)*)", re.M)
    mode_pattern = re.compile(
        r"   (?P<width>\d*)x(?P<height>\d*)(?P<interlaced>i|)\s*(?P<submodes>.*)",
        re.M,
    )
    submode_pattern = re.compile(
        r"(?P<refresh_rate>[\d\.]+)(?P<active>\*|)(?P<preferred>\+|)", re.M
    )

    command = ["xrandr"]

    if x_display:
        command.extend(["--display", x_display])

    command.append("--props")

    logger.info("Fetching XRandR Display Data")
    output = subprocess.check_output(command).decode("utf-8")
    logger.debug(f"Raw XRandR Displays: {output}")

    displays = []

    for parsed_display in [m.groupdict() for m in pattern.finditer(output)]:
        current_resolution = None
        current_refresh_rate = None

        internal = parsed_display["port"].startswith(
            tuple(AppSettings.instance().internal_port_names)
        )

        raw_edid = edid_pattern.search(parsed_display["metadata"])
        edid = None
        if raw_edid:
            edid = raw_edid.groupdict()["edid"].replace("\n", "").replace("\t", "")
        else:
            raise ValueError("Display does not have an edid value")

        name = None

        if edid:
            process = subprocess.Popen(
                ["edid-decode"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            stdout, stderr = process.communicate(edid.encode("utf-8"))

            if process.returncode == 0:
                result = re.findall(r"Display Product Name: '(.*)'", stdout.decode("utf-8"))
                if result:
                    name = result[0]
            else:
                logger.warning(f"Failed to get product name of display {parsed_display['port']}")
                logger.debug(f"edid-decode Output: {stderr.decode('utf-8')}")

        if name is None:
            if internal:
                name = "Internal Display"
            else:
                name = "Unknown"

        orientation = Orientation.NORMAL
        if parsed_display["orientation"] == "left":
            orientation = Orientation.LEFT
        elif parsed_display["orientation"] == "right":
            orientation = Orientation.RIGHT
        elif parsed_display["orientation"] == "inverted":
            orientation = Orientation.INVERTED

        modes = {}

        first_resolution = None
        first_refresh_rate = None

        for parsed_mode in [
            m.groupdict() for m in mode_pattern.finditer(parsed_display["metadata"])
        ]:
            if bool(parsed_mode["interlaced"]):
                continue

            refresh_rates = []
            mode_is_active = False

            for parsed_submode in [
                m.groupdict() for m in submode_pattern.finditer(parsed_mode["submodes"])
            ]:
                refresh_rate = parsed_submode["refresh_rate"]

                if bool(parsed_submode["active"]):
                    current_refresh_rate = refresh_rate
                    mode_is_active = True

                if first_refresh_rate is None:
                    first_refresh_rate = refresh_rate

                refresh_rates.append(refresh_rate)

            resolution = (int(parsed_mode["width"]), int(parsed_mode["height"]))
            if mode_is_active:
                current_resolution = resolution

            if first_resolution is None:
                first_resolution = resolution

            modes[resolution] = refresh_rates

        internal = parsed_display["port"].startswith(("eDP", "LVDS"))

        if parsed_display["virtual_width"] is None:  # Display is inactive
            display = DisplayData(
                port=parsed_display["port"],
                name=name,
                modes=modes,
                virtual_resolution=first_resolution,
                current_resolution=first_resolution,
                current_refresh_rate=first_refresh_rate,
                enabled=False,
                primary=False,
                edid=edid,
                offset=(0, 0),
                resolution_mm=(0, 0),
                orientation=orientation,
                internal=internal,
            )
        else:
            virtual_resolution = (
                int(parsed_display["virtual_width"]),
                int(parsed_display["virtual_height"]),
            )
            if orientation in [Orientation.LEFT, Orientation.RIGHT]:
                virtual_resolution = (
                    virtual_resolution[1],
                    virtual_resolution[0],
                )

            display = DisplayData(
                port=parsed_display["port"],
                name=name,
                modes=modes,
                virtual_resolution=virtual_resolution,
                resolution_mm=(
                    int(parsed_display["width_mm"]),
                    int(parsed_display["height_mm"]),
                ),
                offset=(
                    int(parsed_display["x_offset"]),
                    int(parsed_display["y_offset"]),
                ),
                primary=parsed_display["primary"] == "primary",
                edid=edid,
                enabled=True,
                current_resolution=current_resolution,
                current_refresh_rate=current_refresh_rate,
                orientation=orientation,
                internal=internal,
            )
        displays.append(display)

    logger.debug(f"Parsed XRandR Displays: {displays}")

    return displays
