import os
from pathlib import Path

import yaml


def create_virtual_device_uris() -> list[str]:
    virtual_device_filename = "virtual_motor_controller"
    virtual_device_file_path = os.path.join(
        Path().cwd(), "virt", virtual_device_filename
    )
    device_uri_base = f"xi-emu:///{virtual_device_file_path}"

    return [
        "_".join([device_uri_base, "pitch.bin"]),
        "_".join([device_uri_base, "yaw.bin"]),
    ]


def load_home_pos() -> dict:
    with open("home.yaml") as file:
        data = yaml.safe_load(file)

        return data


def save_home_pos(data) -> None:
    with open("home.yaml", "w") as file:
        yaml.dump(data, file, default_flow_style=False)
