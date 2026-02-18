import logging
import os
from pathlib import Path

import libximc.highlevel as ximc
import yaml


class DeviceNotFoundError(Exception):
    """Raised when expected device uris are not found"""

    pass


def load_devices(use_sim: bool) -> dict:
    """Load device uris for pitch and yaw controllers"""

    return create_simulated_devices() if use_sim else load_real_devices()


def load_real_devices() -> dict:
    """Discover and validate real device uris against config"""

    logging.info("Looking for real standa devices")

    target_uris = {
        "pitch": os.getenv("DEVICE_PITCH_URI"),
        "yaw": os.getenv("DEVICE_YAW_URI"),
    }

    logging.debug("Target uris:")
    for v in target_uris.values():
        logging.debug(v)

    devices = ximc.enumerate_devices(ximc.EnumerateFlags.ENUMERATE_ALL_COM)
    real_uris = [device["uri"] for device in devices]

    logging.debug("Real device uris:")
    for uri in real_uris:
        logging.debug(f"  {uri}")

    missing_devices = []

    for name, uri in target_uris.items():
        if uri in real_uris:
            logging.info(f"Found {name} controller")
        else:
            missing_devices.append(name)

    if missing_devices:
        raise DeviceNotFoundError(
            f"Expected devices not found: {', '.join(missing_devices)}"
        )

    return target_uris


def create_simulated_devices() -> dict:
    """Create simulated devices and return uris"""
    logging.info("Creating simulated standa devices")

    sim_dir = Path.cwd() / "sim"

    device_uri_base = f"xi-emu:///{sim_dir}/simulated_motor_controller"

    return {
        "pitch": f"{device_uri_base}_pitch.bin",
        "yaw": f"{device_uri_base}_yaw.bin",
    }


def load_or_create_saved_pos() -> dict:
    """Load saved positions from yaml file or create if not exists"""

    if Path("saved.yaml").exists():
        saved_positions = load_yaml("saved.yaml")
    else:
        saved_positions = {"pitch": 0, "yaw": 0}
        save_pos(saved_positions)

    return saved_positions


def load_yaml(filename: str) -> dict:
    """Load data from yaml"""

    with open(filename) as file:
        data = yaml.safe_load(file)

        return data


def save_pos(data: dict) -> None:
    """save dict data to saved.yaml"""

    with open("saved.yaml", "w") as file:
        yaml.dump(data, file, default_flow_style=False)
