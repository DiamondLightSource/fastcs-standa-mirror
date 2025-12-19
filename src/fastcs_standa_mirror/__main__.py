"""Interface for ``python -m fastcs_standa_mirror``."""

import logging
import os
from argparse import ArgumentParser
from pathlib import Path

from dotenv import load_dotenv
from fastcs.launch import FastCS
from fastcs.transports.epics import EpicsGUIOptions, EpicsIOCOptions
from fastcs.transports.epics.ca.transport import EpicsCATransport

from fastcs_standa_mirror.mirror_controller import MirrorController
from fastcs_standa_mirror.utils import (
    load_devices,
    load_or_create_home_pos,
)

from . import __version__

__all__ = ["main"]

logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Argument parser for the CLI."""
    parser = ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "--use-virtual",
        action="store_true",
        dest="use_virtual",
        help="Enable virtual mode",
    )

    parsed_args = parser.parse_args()
    use_virtual = parsed_args.use_virtual

    # initial varaiables setup
    load_dotenv()

    pv_prefix = os.getenv("PV_PREFIX", "STANDA-MIRROR")
    home_positions = load_or_create_home_pos()
    uris = load_devices(use_virtual=use_virtual)

    # epics setupo
    gui_options = EpicsGUIOptions(
        output_path=Path(".") / "gui/Mirror.bob", title="Mirror Controller"
    )

    epics_ca = EpicsCATransport(
        gui=gui_options, epicsca=EpicsIOCOptions(pv_prefix=pv_prefix)
    )

    # run fastcs instance
    controller = MirrorController(uris["pitch"], uris["yaw"], home_positions)
    fastcs = FastCS(controller, [epics_ca])

    fastcs.run()


if __name__ == "__main__":
    main()
