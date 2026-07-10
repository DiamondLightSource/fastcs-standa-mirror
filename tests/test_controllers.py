import os
from unittest.mock import Mock, patch

import pytest

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


@patch("fastcs_standa_mirror.motor_controller.ximc.Axis")
@pytest.mark.asyncio
async def test_mirror_stop_affects_both_motors(mock_axis, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mock_motor = Mock()
    mock_axis.return_value = mock_motor
    controller = MirrorController(SIM_OPTIONS)
    await controller.connect()
    await controller.stop_moving()
    assert mock_motor.command_stop.call_count == 2


@patch("fastcs_standa_mirror.motor_controller.ximc.Axis")
@pytest.mark.asyncio
async def test_jog_commands_use_correct_step_size(mock_axis, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mock_motor = Mock()
    mock_axis.return_value = mock_motor
    controller = MirrorController(SIM_OPTIONS)
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
@patch("fastcs_standa_mirror.motor_controller.ximc.Axis")
@pytest.mark.asyncio
async def test_return_moves_both_motors_to_saved(mock_axis, mock_saved):
    mock_saved.return_value = {"pitch": 1500, "yaw": 2500}
    mock_motor = Mock()
    mock_axis.return_value = mock_motor
    controller = MirrorController(SIM_OPTIONS)
    await controller.connect()
    await controller.return_to_saved()
    assert mock_motor.command_move.call_count == 2


def test_saved_position_save_and_load(tmp_path):
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        saved_data = {"pitch": 1500, "yaw": 2500}
        save_pos(saved_data)
        loaded_data = load_or_create_saved_pos()
        assert loaded_data["pitch"] == 1500
        assert loaded_data["yaw"] == 2500
    finally:
        os.chdir(original_dir)
