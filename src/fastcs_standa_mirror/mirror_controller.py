from fastcs.attributes import AttrRW
from fastcs.controllers import Controller
from fastcs.datatypes import Float
from fastcs.methods import command

from fastcs_standa_mirror.io.mirror_attribute import (
    MirrorAttributeIO,
    MirrorAttributeIORef,
)
from fastcs_standa_mirror.motor_controller import MotorController
from fastcs_standa_mirror.utils import save_home_pos


class MirrorController(Controller):
    """Controller for two axis mirror"""

    speed = AttrRW(Float(), io_ref=MirrorAttributeIORef("speed"), group="Global")
    jog_step = AttrRW(Float(), io_ref=MirrorAttributeIORef("jog_step"), group="Global")

    def __init__(self, pitch_uri: str, yaw_uri: str, home_positions: dict):
        super().__init__(ios=[MirrorAttributeIO(self)])

        pitch = MotorController("pitch", pitch_uri)
        yaw = MotorController("yaw", yaw_uri)

        self.pitch: MotorController
        self.yaw: MotorController

        self.add_sub_controller("pitch", pitch)
        self.add_sub_controller("yaw", yaw)

        self.pitch.set_home_position(home_positions.get("pitch", 0))
        self.yaw.set_home_position(home_positions.get("yaw", 0))

        self.jog_step_size = 100.0

    @command(group="Home")
    async def rehome(self) -> None:
        """Return to home"""
        print("Returning to home position")
        await self.pitch.move_home()
        await self.yaw.move_home()

    @command(group="Home")
    async def save(self) -> None:
        """Save home location"""
        pitch = await self.pitch.get_current_position()
        yaw = await self.yaw.get_current_position()

        print(f"Saving pitch: {pitch} - yaw: {yaw} as home position")
        self.pitch.set_home_position(pitch)
        self.yaw.set_home_position(yaw)

        save_home_pos({"pitch": pitch, "yaw": yaw})

    @command(group="Jog")
    async def up(self) -> None:
        """Jog up"""
        print(f"Jogging up by {self.jog_step_size}")
        await self.pitch.move_relative(int(self.jog_step_size))

    @command(group="Jog")
    async def left(self) -> None:
        """Jog left"""
        print(f"Jogging left by {self.jog_step_size}")
        await self.yaw.move_relative(int(self.jog_step_size))

    @command(group="Jog")
    async def down(self) -> None:
        """Jog down"""
        print(f"Jogging down by {self.jog_step_size}")
        await self.pitch.move_relative(-int(self.jog_step_size))

    @command(group="Jog")
    async def right(self) -> None:
        """Jog right"""
        print(f"Jogging right by {self.jog_step_size}")
        await self.yaw.move_relative(-int(self.jog_step_size))
