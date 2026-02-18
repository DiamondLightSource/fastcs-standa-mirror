import os
from unittest.mock import Mock, patch

import pytest

from fastcs_standa_mirror.config import URIs
from fastcs_standa_mirror.mirror_controller import MirrorController
from fastcs_standa_mirror.utils import (
    DeviceNotFoundError,
    load_or_create_saved_pos,
    load_real_devices,
    save_pos,
)

REAL_URIS = URIs(pitch="xi-com:\\\\.\\COM3", yaw="xi-com:\\\\.\\COM4")
SIM_URIS = URIs(pitch="SIM/ttyACM0", yaw="SIM/ttyACM1")


@patch("libximc.highlevel.enumerate_devices")
def test_detects_missing_motor(mock_enumerate):
    mock_enumerate.return_value = [{"uri": "xi-com:\\\\.\\COM4"}]
    with pytest.raises(DeviceNotFoundError):
        load_real_devices(REAL_URIS)


@patch("libximc.highlevel.enumerate_devices")
def test_finds_both_motors_successfully(mock_enumerate):
    mock_enumerate.return_value = [
        {"uri": "xi-com:\\\\.\\COM3"},
        {"uri": "xi-com:\\\\.\\COM4"},
    ]
    result = load_real_devices(REAL_URIS)
    assert result.pitch == "xi-com:\\\\.\\COM3"
    assert result.yaw == "xi-com:\\\\.\\COM4"


@patch("fastcs_standa_mirror.motor_controller.ximc.Axis")
@pytest.mark.asyncio
async def test_mirror_stop_affects_both_motors(mock_axis):
    mock_motor = Mock()
    mock_axis.return_value = mock_motor
    controller = MirrorController(REAL_URIS, {"pitch": 0, "yaw": 0})
    await controller.stop_moving()
    assert mock_motor.command_stop.call_count == 2


@patch("fastcs_standa_mirror.motor_controller.ximc.Axis")
@pytest.mark.asyncio
async def test_jog_commands_use_correct_step_size(mock_axis):
    mock_motor = Mock()
    mock_axis.return_value = mock_motor
    controller = MirrorController(REAL_URIS, {"pitch": 0, "yaw": 0})
    await controller.up()
    mock_motor.command_movr.assert_called_with(100, 0)
    await controller.down()
    mock_motor.command_movr.assert_called_with(-100, 0)
    await controller.left()
    mock_motor.command_movr.assert_called_with(100, 0)
    await controller.right()
    mock_motor.command_movr.assert_called_with(-100, 0)


@patch("fastcs_standa_mirror.motor_controller.ximc.Axis")
@pytest.mark.asyncio
async def test_return_moves_both_motors_to_saved(mock_axis):
    mock_motor = Mock()
    mock_axis.return_value = mock_motor
    controller = MirrorController(REAL_URIS, {"pitch": 1000, "yaw": 2000})
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
