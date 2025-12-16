import os
import yaml
from pathlib import Path
from typing import List, Dict

def create_virtual_device_uris() -> List[str]:
    virtual_device_filename = "virtual_motor_controller"
    virtual_device_file_path = os.path.join(Path().cwd(), "virt", virtual_device_filename)
    device_uri_base = "xi-emu:///{}".format(virtual_device_file_path)

    return ["_".join([device_uri_base, "pitch.bin"]), "_".join([device_uri_base, "yaw.bin"])]

def load_home_pos() -> Dict:
    with open('home.yaml', 'r') as file:
        data = yaml.safe_load(file)

        return(data)

def save_home_pos(data) -> None:

    with open('home.yaml', 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
