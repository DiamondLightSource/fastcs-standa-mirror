from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

import libximc.highlevel as ximc
from fastcs.attributes import AttributeIO, AttributeIORef, AttrR

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

        elif attr.io_ref.name == "home":
            await attr.update(await self._master.get_home_position())

        elif attr.io_ref.name == "moving":
            status = self._master.motor.get_status()
            is_moving = bool(status.MvCmdSts & ximc.MvcmdStatus.MVCMD_RUNNING)
            await attr.update(is_moving)
