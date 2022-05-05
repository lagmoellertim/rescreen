import re
import subprocess
from typing import List

import pyedid

from rescreen.lib.interfaces import Orientation
from rescreen.lib.xrandr import DisplayData


def get_current_display_data() -> List[DisplayData]:
    pattern = re.compile(
        r"^(?P<port>\S*) connected (?:(?P<primary>primary)?(?:\s?)(?P<virtual_width>\d*)x(?P<virtual_height>\d*)\+(?P<x_offset>\d*)\+(?P<y_offset>\d*) )?(?:(?P<orientation>normal|left|right|inverted) )?\((?P<params>.*)\)(?: (?P<width_mm>\d*)mm x (?P<height_mm>\d*)mm)?.*\n(?P<metadata>(?:\s+[^\n]*\n)*)",
        re.M)
    edid_pattern = re.compile(r"EDID:\s*\n(?P<edid>(?:\t\t.*\n)*)", re.M)
    mode_pattern = re.compile(r"   (?P<width>\d*)x(?P<height>\d*)(?P<interlaced>i|)\s*(?P<submodes>.*)", re.M)
    submode_pattern = re.compile(r"(?P<refresh_rate>[\d\.]+)(?P<active>\*|)(?P<preferred>\+|)", re.M)

    output = subprocess.check_output(['xrandr', '--props']).decode("utf-8")

    displays = []

    for parsed_display in [m.groupdict() for m in pattern.finditer(output)]:
        current_resolution = None
        current_refresh_rate = None

        internal = parsed_display["port"].startswith(("eDP", "LVDS"))

        raw_edid = edid_pattern.search(parsed_display["metadata"])
        edid = None
        if raw_edid:
            edid = raw_edid.groupdict()["edid"].replace("\n", "").replace("\t", "")

        parsed_edid = pyedid.parse_edid(edid)
        name = "Unknown"
        if parsed_edid.name:
            name = parsed_edid.name
        elif internal:
            name = "Internal Display"

        orientation = Orientation.Normal
        if parsed_display["orientation"] == "left":
            orientation = Orientation.Left
        elif parsed_display["orientation"] == "right":
            orientation = Orientation.Right
        elif parsed_display["orientation"] == "inverted":
            orientation = Orientation.Inverted

        modes = {}

        first_resolution = None
        first_refresh_rate = None

        for parsed_mode in [m.groupdict() for m in mode_pattern.finditer(parsed_display["metadata"])]:
            if bool(parsed_mode["interlaced"]):
                continue

            refresh_rates = []
            mode_is_active = False

            for parsed_submode in [m.groupdict() for m in submode_pattern.finditer(parsed_mode["submodes"])]:
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

        if parsed_display["virtual_width"] is None:  # Display is inactive
            display = DisplayData(port=parsed_display["port"], name=name, modes=modes,
                                  virtual_resolution=first_resolution, current_resolution=first_resolution,
                                  current_refresh_rate=first_refresh_rate, enabled=False, primary=False, edid=edid,
                                  offset=(-1, -1),
                                  resolution_mm=(-1, -1), orientation=orientation, internal=True)
        else:
            virtual_resolution = (int(parsed_display["virtual_width"]), int(parsed_display["virtual_height"]))
            if orientation in [Orientation.Left, Orientation.Right]:
                virtual_resolution = (virtual_resolution[1], virtual_resolution[0])

            display = DisplayData(port=parsed_display["port"], name=name, modes=modes,
                                  virtual_resolution=virtual_resolution,
                                  resolution_mm=(int(parsed_display["width_mm"]), int(parsed_display["height_mm"])),
                                  offset=(int(parsed_display["x_offset"]), int(parsed_display["y_offset"])),
                                  primary=parsed_display["primary"] == "primary", edid=edid, enabled=True,
                                  current_resolution=current_resolution, current_refresh_rate=current_refresh_rate,
                                  orientation=orientation, internal=True)
        displays.append(display)

    return displays
