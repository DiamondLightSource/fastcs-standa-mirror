from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

import libximc.highlevel as ximc
from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrW

NumberT = TypeVar("NumberT", int, float)


@dataclass
class MotorAttributeIORef(AttributeIORef):
    name: str
    _: KW_ONLY
    update_period: float | None = 0.05


class MotorAttributeIO(AttributeIO[NumberT, MotorAttributeIORef]):
    """IO for motor attribute"""

    def __init__(self, master):
        super().__init__()
        self._master = master

    async def update(self, attr: AttrR[NumberT, MotorAttributeIORef]):
        """Read motor attribute"""

        if attr.io_ref.name == "current":
            position = self._master.motor.get_position()
            await attr.update(position.Position)

        elif attr.io_ref.name == "speed":
            move_settings = self._master.motor.get_move_settings()
            await attr.update(move_settings.Speed)

        elif attr.io_ref.name == "saved":
            await attr.update(await self._master.get_saved_position())

        elif attr.io_ref.name == "moving":
            status = self._master.motor.get_status()
            is_moving = bool(status.MvCmdSts & ximc.MvcmdStatus.MVCMD_RUNNING)
            await attr.update(is_moving)

    async def send(
        self, attr: AttrW[NumberT, MotorAttributeIORef], value: NumberT
    ) -> None:
        """Change mirror attribute"""

        if attr.io_ref.name == "speed":
            move_settings = self._master.motor.get_move_settings()
            move_settings.Speed = int(value)
            self._master.motor.set_move_settings(move_settings)
