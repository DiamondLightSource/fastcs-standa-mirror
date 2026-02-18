from pydantic import BaseModel


class URIs(BaseModel):
    pitch: str
    yaw: str


class ControllerConfig(BaseModel):
    uris: URIs
    sim: bool = False


class IOCConfig(BaseModel):
    pv_prefix: str


class GUIConfig(BaseModel):
    output_path: str
    title: str


class TransportConfig(BaseModel):
    ioc: IOCConfig
    gui: GUIConfig


class Config(BaseModel):
    controller: ControllerConfig
    transport: list[TransportConfig]
