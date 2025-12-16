from __future__ import annotations
from dataclasses import dataclass, KW_ONLY
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrW

NumberT = TypeVar("NumberT", int, float)


@dataclass
class MirrorAttributeIORef(AttributeIORef):
    name: str
    _: KW_ONLY
    update_period: float | None = 0.2
    

class MirrorAttributeIO(AttributeIO[float, MirrorAttributeIORef]):
    """IO for mirror attribute"""
    def __init__(self, master):
        super().__init__()
        self._master = master
    
    async def update(self, attr: AttrR[float, MirrorAttributeIORef]):
        """Read mirror attribute"""
        if attr.io_ref.name == 'speed':
            move_settings = self._master.pitch._connection.get_move_settings()
            await attr.update(move_settings.Speed)

        elif attr.io_ref.name == 'jog_step':
            await attr.update(self._master.jog_step_size)

    async def send(self, attr: AttrW[NumberT, MirrorAttributeIORef], value: NumberT) -> None:
        """Change mirror attribute"""

        if attr.io_ref.name == 'speed':
            print(f"Changing speed to {value}")
            move_settings_pitch = self._master.pitch._connection.get_move_settings()
            move_settings_yaw = self._master.yaw._connection.get_move_settings()
            move_settings_pitch.Speed = int(value)
            move_settings_yaw.Speed = int(value)
            self._master.pitch._connection.set_move_settings(move_settings_pitch)
            self._master.yaw._connection.set_move_settings(move_settings_yaw)

        elif attr.io_ref.name == 'jog_step':
            self._master.jog_step_size = value
