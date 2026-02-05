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
        "--sim",
        action="store_true",
        dest="use_sim",
        help="Use simulated device",
    )

    parsed_args = parser.parse_args()
    use_sim = parsed_args.use_sim

    # Validate device URIs and PV_PREFIX only if not using simulation
    if not use_sim:
        load_dotenv()

        pv_prefix = os.getenv("PV_PREFIX")
        print(pv_prefix)
        if pv_prefix is None:
            raise ValueError("PV_PREFIX environment variable must be set")

        device_pitch_uri = os.getenv("DEVICE_PITCH_URI")
        device_yaw_uri = os.getenv("DEVICE_YAW_URI")
        if device_pitch_uri is None or device_yaw_uri is None:
            raise ValueError("DEVICE_PITCH_URI and DEVICE_YAW_URI must be set")

    else:
        pv_prefix = "MIRROR-SIM-001"
        logging.info(f"Simulated device PV_PREFIX -> {pv_prefix}")

    home_positions = load_or_create_home_pos()
    uris = load_devices(use_sim=use_sim)

    # epics setup
    gui_options = EpicsGUIOptions(
        output_path=Path(".") / "bob/Mirror.bob", title="Mirror Controller"
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
