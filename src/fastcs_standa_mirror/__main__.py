"""Interface for ``python -m fastcs_standa_mirror``."""

import logging
from functools import cache
from pathlib import Path

import typer
import yaml
from fastcs.launch import FastCS
from fastcs.transports.epics import EpicsGUIOptions
from fastcs.transports.epics.ca.transport import EpicsCATransport

from fastcs_standa_mirror.config import Config
from fastcs_standa_mirror.mirror_controller import MirrorController
from fastcs_standa_mirror.utils import (
    load_devices,
    load_or_create_saved_pos,
    patch_move_flags,
)

from . import __version__

__all__ = ["main"]

logging.basicConfig(level=logging.INFO)

app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print the version and exit",
    ),
):
    pass


@cache
def load_config(config_file: Path) -> Config:
    return Config(**yaml.safe_load(config_file.read_text()))


@app.command()
def run(config_file: Path):
    config = load_config(config_file)

    pv_prefix = config.transport[0].ioc.pv_prefix
    logging.info(f"PV PREFIX = {pv_prefix}")

    saved_positions = load_or_create_saved_pos()
    uris = load_devices(config.controller.serial_settings)

    epics_ca = EpicsCATransport(
        gui=EpicsGUIOptions(
            output_dir=Path(config.transport[0].gui.output_path),
            title=config.transport[0].gui.title,
        )
    )

    patch_move_flags()

    # run fastcs instance
    controller = MirrorController(uris, saved_positions)
    controller.set_path([pv_prefix])
    fastcs = FastCS(controller, [epics_ca])

    fastcs.run()


if __name__ == "__main__":
    app()
