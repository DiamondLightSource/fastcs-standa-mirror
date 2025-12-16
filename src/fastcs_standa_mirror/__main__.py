"""Interface for ``python -m fastcs_standa_mirror``."""

from argparse import ArgumentParser
from pathlib import Path

from fastcs.launch import FastCS
from fastcs.transports.epics import EpicsGUIOptions, EpicsIOCOptions
from fastcs.transports.epics.ca.transport import EpicsCATransport

# from fastcs.transports.epics.pva.pvi import add_pvi_info
# from fastcs.transports.epics.pva.transport import EpicsPVATransport
from fastcs_standa_mirror.mirror_controller import MirrorController

# import libximc.highlevel as ximc
from fastcs_standa_mirror.utils import create_virtual_device_uris

from . import __version__

__all__ = ["main"]


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

    pv_prefix = "VISR-Standa:"

    gui_options = EpicsGUIOptions(
        output_path=Path(".") / "gui/Mirror.bob", title="Mirror Controller"
    )

    epics_ca = EpicsCATransport(
        gui=gui_options, epicsca=EpicsIOCOptions(pv_prefix=pv_prefix)
    )

    # epics_pva = EpicsPVATransport(epicspva=EpicsIOCOptions(pv_prefix=pv_prefix))

    if use_virtual:
        print("No physical device, creating virtual devices")

        uris = create_virtual_device_uris()
        controller = MirrorController(uris[0], uris[1])

        # Create FastCS with both CA and PVA
        fastcs = FastCS(controller, [epics_ca])  # , epics_pva])

        # Add PVI information for Phoebus auto-generation
        # add_pvi_info(
        #     provider=epics_pva,
        #     pv_prefix=pv_prefix,
        #     controller_api=fastcs._controller,
        #     description="Two-axis mirror controller for VISR project",
        # )

        fastcs.run()
    # else:

    #     devices = ximc.enumerate_devices(
    #       ximc.EnumerateFlags.ENUMERATE_NETWORK | ximc.EnumerateFlags.ENUMERATE_PROBE
    #     )

    #     print("Found {} real device(s):".format(len(devices)))

    #     for device in devices:
    #         print("  {}".format(device))


if __name__ == "__main__":
    main()
