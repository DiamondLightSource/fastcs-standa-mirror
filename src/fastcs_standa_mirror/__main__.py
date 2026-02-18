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
    load_or_create_saved_pos,
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
    parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Get device uris
    device_pitch_uri = os.getenv("DEVICE_PITCH_URI")
    device_yaw_uri = os.getenv("DEVICE_YAW_URI")

    if device_pitch_uri is None or device_yaw_uri is None:
        raise ValueError("DEVICE_PITCH_URI and DEVICE_YAW_URI must be set")

    # Detect if we're using a sim
    use_sim = device_pitch_uri.startswith("SIM") or device_yaw_uri.startswith("SIM")

    # Load pv prefix
    pv_prefix = os.getenv("PV_PREFIX")

    if pv_prefix is None:
        raise ValueError("PV_PREFIX environment variable must be set")

    if use_sim:
        logging.info(f"Using simulated devices with PV_PREFIX -> {pv_prefix}")
    else:
        print(pv_prefix)

    saved_positions = load_or_create_saved_pos()
    uris = load_devices(use_sim=use_sim)

    # epics setup
    gui_options = EpicsGUIOptions(
        output_path=Path(".") / "bob/Mirror.bob", title="Mirror Controller"
    )

    epics_ca = EpicsCATransport(
        gui=gui_options, epicsca=EpicsIOCOptions(pv_prefix=pv_prefix)
    )

    # run fastcs instance
    controller = MirrorController(uris["pitch"], uris["yaw"], saved_positions)
    fastcs = FastCS(controller, [epics_ca])

    fastcs.run()


if __name__ == "__main__":
    main()
