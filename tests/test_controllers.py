import os
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio

from fastcs_standa_mirror.config import (
    ControllerSerialSettings,
    MirrorOptions,
    SerialSettings,
)
from fastcs_standa_mirror.mirror_controller import MirrorController
from fastcs_standa_mirror.utils import (
    DeviceNotFoundError,
    load_or_create_saved_pos,
    load_real_devices,
    save_pos,
)

REAL_SERIAL_SETTINGS = ControllerSerialSettings(
    pitch=SerialSettings(port="/dev/ttyACM0"),
    yaw=SerialSettings(port="/dev/ttyACM1"),
)

SIM_OPTIONS = MirrorOptions(
    serial_settings=ControllerSerialSettings(
        pitch=SerialSettings(port="SIM-00"),
        yaw=SerialSettings(port="SIM-01"),
    )
)


@pytest.fixture
def mock_motor():
    """Mocked ximc axis shared by both simulated motors.

    Speed is read via get_move_settings().Speed, so give it a real number
    (connect() seeds the mirror speed from it).
    """
    motor = Mock()
    motor.get_move_settings.return_value.Speed = 1000
    return motor


@pytest_asyncio.fixture
async def controller(mock_motor, tmp_path, monkeypatch):
    """A wired but *unconnected* MirrorController with both motors mocked.

    Wiring (initialise + _connect_attribute_ios) replays what FastCS does at
    startup, so attribute puts/polls and the connect() speed-seeding work.
    Tests call `await controller.connect()` themselves, to control timing.
    """
    monkeypatch.chdir(tmp_path)
    with patch(
        "fastcs_standa_mirror.motor_controller.ximc.Axis", return_value=mock_motor
    ):
        c = MirrorController(SIM_OPTIONS)
        await c.initialise()
        c._connect_attribute_ios()
        yield c


# --------------------------------------------------------------- device load ---


@patch("libximc.highlevel.enumerate_devices")
def test_detects_missing_motor(mock_enumerate):
    mock_enumerate.return_value = [{"uri": "xi-com:///dev/ttyACM1"}]
    with pytest.raises(DeviceNotFoundError):
        load_real_devices(REAL_SERIAL_SETTINGS)


@patch("libximc.highlevel.enumerate_devices")
def test_finds_both_motors_successfully(mock_enumerate):
    mock_enumerate.return_value = [
        {"uri": "xi-com:///dev/ttyACM0"},
        {"uri": "xi-com:///dev/ttyACM1"},
    ]
    result = load_real_devices(REAL_SERIAL_SETTINGS)
    assert result.pitch == "xi-com:///dev/ttyACM0"
    assert result.yaw == "xi-com:///dev/ttyACM1"


# ------------------------------------------------------------------- commands ---


@pytest.mark.asyncio
async def test_mirror_stop_affects_both_motors(controller, mock_motor):
    await controller.connect()
    await controller.stop_moving()
    assert mock_motor.command_stop.call_count == 2


@pytest.mark.asyncio
async def test_jog_commands_use_correct_step_size(controller, mock_motor):
    await controller.connect()
    await controller.up()
    mock_motor.command_movr.assert_called_with(1, 0)
    await controller.down()
    mock_motor.command_movr.assert_called_with(-1, 0)
    await controller.left()
    mock_motor.command_movr.assert_called_with(1, 0)
    await controller.right()
    mock_motor.command_movr.assert_called_with(-1, 0)


@patch("fastcs_standa_mirror.mirror_controller.load_or_create_saved_pos")
@pytest.mark.asyncio
async def test_return_moves_both_motors_to_saved(mock_saved, controller, mock_motor):
    mock_saved.return_value = {"pitch": 1500, "yaw": 2500}
    await controller.connect()
    await controller.return_to_saved()
    assert mock_motor.command_move.call_count == 2


def test_saved_position_save_and_load(tmp_path):
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        save_pos({"pitch": 1500, "yaw": 2500})
        loaded_data = load_or_create_saved_pos()
        assert loaded_data["pitch"] == 1500
        assert loaded_data["yaw"] == 2500
    finally:
        os.chdir(original_dir)


# ---------------------------------------------------------------------- speed ---


@pytest.mark.asyncio
async def test_speed_put_fans_out_to_both_motors(controller, mock_motor):
    """Writing the mirror speed commands set_speed on both motors."""
    await controller.connect()

    await controller.speed.put(500)

    assert mock_motor.set_move_settings.call_count == 2
    assert mock_motor.get_move_settings.return_value.Speed == 500


@pytest.mark.asyncio
async def test_mirror_flags_speed_mismatch(controller):
    """If the axes disagree, the mirror must not report a bogus common value."""
    await controller.connect()

    await controller.pitch.speed.update(750)
    await controller.yaw.speed.update(600)

    await controller.speed.bind_update_callback()()

    assert controller.speed.get() == 0.0


@pytest.mark.asyncio
async def test_mirror_reports_common_speed_when_axes_agree(controller):
    """When both axes read the same speed, the mirror reflects it."""
    await controller.connect()

    await controller.pitch.speed.update(1000)
    await controller.yaw.speed.update(1000)

    await controller.speed.bind_update_callback()()

    assert controller.speed.get() == 1000


@pytest.mark.asyncio
async def test_connect_seeds_speed_from_hardware(controller):
    """After connect(), the mirror reflects the motors' hardware speed, not 0."""
    assert controller.speed.get() == 0.0
    await controller.connect()
    assert controller.speed.get() == 1000
