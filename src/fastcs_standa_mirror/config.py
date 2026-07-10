import os

from pydantic import BaseModel, model_validator


class SerialSettings(BaseModel):
    port: str | None = None
    port_env: str | None = None

    @model_validator(mode="after")
    def resolve_port_env(self) -> "SerialSettings":
        if self.port is not None and self.port_env is not None:
            raise ValueError("Cannot specify both port and port_env")
        if self.port is None and self.port_env is None:
            raise ValueError("Must specify either port or port_env")
        if self.port_env is not None:
            value = os.environ.get(self.port_env)
            if value is None:
                raise ValueError(f"Environment variable '{self.port_env}' is not set")
            self.port = value
        return self

    def as_uri(self) -> str:
        assert self.port is not None
        return f"xi-com://{self.port}"


class ControllerSerialSettings(BaseModel):
    pitch: SerialSettings
    yaw: SerialSettings


class MirrorOptions(BaseModel):
    serial_settings: ControllerSerialSettings


class URIs(BaseModel):
    pitch: str
    yaw: str
