import logging
import os
from pathlib import Path

import libximc.highlevel as ximc
import yaml


class DeviceNotFoundError(Exception):
    """Raised when expected device uris are not found"""

    pass


def load_devices(use_virtual: bool) -> dict:
    """Load device uris for pitch and yaw controllers"""

    return create_virtual_devices() if use_virtual else load_real_devices()


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


def create_virtual_devices() -> dict:
    """Create virtual devices and return uris"""
    logging.info("Creating virtual standa devices")

    virt_dir = Path.cwd() / "virt"

    device_uri_base = f"xi-emu:///{virt_dir}/virtual_motor_controller"

    return {
        "pitch": f"{device_uri_base}_pitch.bin",
        "yaw": f"{device_uri_base}_yaw.bin",
    }


def load_or_create_home_pos() -> dict:
    """Load home positions from yaml file or create if not exists"""

    if Path("home.yaml").exists():
        home_positions = load_yaml("home.yaml")
    else:
        home_positions = {"pitch": 0, "yaw": 0}
        save_home_pos(home_positions)

    return home_positions


def load_yaml(filename: str) -> dict:
    """Load data from yaml"""

    with open(filename) as file:
        data = yaml.safe_load(file)

        return data


def save_home_pos(data: dict) -> None:
    """save dict data to home.yaml"""

    with open("home.yaml", "w") as file:
        yaml.dump(data, file, default_flow_style=False)
