from __future__ import annotations

import asyncio
from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrW

from fastcs_standa_mirror.motor_controller import MotorController

NumberT = TypeVar("NumberT", int, float)


@dataclass
class MirrorAttributeIORef(AttributeIORef):
    name: str
    motors: list[MotorController]
    _: KW_ONLY
    update_period: float | None = 0.2


class MirrorAttributeIO(AttributeIO[NumberT, MirrorAttributeIORef]):
    """IO for mirror attribute"""

    def __init__(self, master):
        super().__init__()
        self._master = master

    async def update(self, attr: AttrR[NumberT, MirrorAttributeIORef]):
        speeds = [motor.speed.get() for motor in attr.io_ref.motors]

        if attr.datatype.all_equal(speeds):
            await attr.update(speeds[0])
        else:
            # TODO: Set an alarm - https://github.com/DiamondLightSource/FastCS/issues/286
            await attr.update(attr.datatype.initial_value)

    async def send(self, attr: AttrW[NumberT, MirrorAttributeIORef], value: NumberT):
        await asyncio.gather(*[motor.set_speed(value) for motor in attr.io_ref.motors])
