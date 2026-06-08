import logging
from pathlib import Path

import libximc.highlevel as ximc
import libximc.highlevel.flag_enumerations as flag_enumerations
import yaml
from libximc.highlevel import _structure_types as st

from fastcs_standa_mirror.config import ControllerSerialSettings, URIs


class DeviceNotFoundError(Exception):
    """Raised when expected device uris are not found"""

    pass


def patch_move_flags():
    """Work around libximc MoveFlags enum rejecting valid hardware values.

    The highlevel API's MoveFlags enum only defines RPM_DIV_1000 (0x01),
    but real hardware can return additional undocumented bits (e.g. 0xCC),
    causing a ValueError. This masks unrecognised bits until there is a fix
    on the enum upstream.
    """
    prop = st.move_settings_t.__dict__["MoveFlags"]
    assert prop.fset is not None, "MoveFlags property has no setter"
    original_fset = prop.fset

    def tolerant_setter(self, val):
        if isinstance(val, int):
            known_bits = 0
            for member in flag_enumerations.MoveFlags:
                known_bits |= member.value
            val = val & known_bits
        original_fset(self, val)

    st.move_settings_t.MoveFlags = st.move_settings_t.MoveFlags.setter(tolerant_setter)


def load_devices(serial_settings: ControllerSerialSettings) -> URIs:
    """Load devices for pitch and yaw controllers"""

    assert serial_settings.pitch.port is not None
    if serial_settings.pitch.port.upper().startswith("SIM"):
        return create_simulated_devices()
    return load_real_devices(serial_settings)


def load_real_devices(serial_settings: ControllerSerialSettings) -> URIs:
    """Discover and validate real device uris against config"""

    logging.info("Looking for real standa devices")

    devices = ximc.enumerate_devices(ximc.EnumerateFlags.ENUMERATE_ALL_COM)
    real_uris = [device["uri"] for device in devices]

    logging.debug("Real device uris: %s", real_uris)

    missing_devices = []

    for name, settings in [
        ("pitch", serial_settings.pitch),
        ("yaw", serial_settings.yaw),
    ]:
        if settings.as_uri() in real_uris:
            logging.info(f"Found {name} controller")
        else:
            missing_devices.append(name)

    if missing_devices:
        raise DeviceNotFoundError(
            f"Expected devices not found: {', '.join(missing_devices)}"
        )

    return URIs(
        pitch=serial_settings.pitch.as_uri(),
        yaw=serial_settings.yaw.as_uri(),
    )


def create_simulated_devices() -> URIs:
    """Create simulated devices and return uris"""
    logging.info("Creating simulated standa devices")

    sim_dir = Path.cwd() / "sim"
    device_uri_base = f"xi-emu:///{sim_dir}/simulated_motor_controller"

    return URIs(
        pitch=f"{device_uri_base}_pitch.bin",
        yaw=f"{device_uri_base}_yaw.bin",
    )


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
        return yaml.safe_load(file)


def save_pos(data: dict) -> None:
    """save dict data to saved.yaml"""

    with open("saved.yaml", "w") as file:
        yaml.dump(data, file, default_flow_style=False)
