import pytest
from pydantic import ValidationError

from fastcs_standa_mirror.config import (
    ControllerSerialSettings,
    SerialSettings,
)


class TestSerialSettings:
    def test_port_sets_uri(self):
        s = SerialSettings(port="/dev/ttyACM0")
        assert s.as_uri() == "xi-com:///dev/ttyACM0"

    def test_port_env_resolves(self, monkeypatch):
        monkeypatch.setenv("PITCH_PORT", "/dev/ttyACM0")
        s = SerialSettings(port_env="PITCH_PORT")
        assert s.port == "/dev/ttyACM0"
        assert s.as_uri() == "xi-com:///dev/ttyACM0"

    def test_port_env_missing_raises(self, monkeypatch):
        monkeypatch.delenv("MISSING_PORT", raising=False)
        with pytest.raises(ValidationError, match="MISSING_PORT"):
            SerialSettings(port_env="MISSING_PORT")

    def test_both_port_and_port_env_raises(self):
        with pytest.raises(ValidationError, match="Cannot specify both"):
            SerialSettings(port="/dev/ttyACM0", port_env="PITCH_PORT")

    def test_neither_port_nor_port_env_raises(self):
        with pytest.raises(ValidationError, match="Must specify either"):
            SerialSettings()

    def test_sim_port(self):
        s = SerialSettings(port="SIM")
        assert s.port is not None
        assert s.port.upper() == "SIM"


class TestControllerSerialSettings:
    def test_pitch_and_yaw(self):
        css = ControllerSerialSettings(
            pitch=SerialSettings(port="/dev/ttyACM0"),
            yaw=SerialSettings(port="/dev/ttyACM1"),
        )
        assert css.pitch.as_uri() == "xi-com:///dev/ttyACM0"
        assert css.yaw.as_uri() == "xi-com:///dev/ttyACM1"
