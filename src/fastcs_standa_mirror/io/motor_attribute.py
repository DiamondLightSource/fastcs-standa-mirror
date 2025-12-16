from __future__ import annotations
from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR

import libximc.highlevel as ximc

NumberT = TypeVar("NumberT", int, float)

@dataclass
class MotorAttributeIORef(AttributeIORef):
    name: str
    _: KW_ONLY
    update_period: float | None = 0.05


class MotorAttributeIO(AttributeIO[NumberT, MotorAttributeIORef]):
    def __init__(self, master):
        super().__init__()
        self._master = master
    
    async def update(self, attr: AttrR[NumberT, MotorAttributeIORef]):
        """Read position"""

        if attr.io_ref.name == 'position':
            position = self._master._connection.get_position()
            await attr.update(position.Position)

        elif attr.io_ref.name == 'home':
            await attr.update(await self._master.get_home_position())

        elif attr.io_ref.name == 'status':
            status = self._master._connection.get_status()
            is_moving = bool(status.MvCmdSts & ximc.MvcmdStatus.MVCMD_RUNNING)
            await attr.update(is_moving)


    
