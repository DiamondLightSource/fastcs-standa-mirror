import logging

from fastcs.attributes import AttrRW
from fastcs.controllers import Controller
from fastcs.datatypes import Float, Int
from fastcs.methods import command

from fastcs_standa_mirror.config import MirrorOptions
from fastcs_standa_mirror.io.mirror_attribute import (
    MirrorAttributeIO,
    MirrorAttributeIORef,
)
from fastcs_standa_mirror.motor_controller import MotorController
from fastcs_standa_mirror.utils import load_devices, load_or_create_saved_pos, save_pos


class MirrorController(Controller):
    """Controller for two axis mirror"""

    pitch: MotorController
    yaw: MotorController

    speed: AttrRW
    jog_step: AttrRW

    def __init__(self, options: MirrorOptions) -> None:
        super().__init__(ios=[MirrorAttributeIO(self)])
        uris = load_devices(options.serial_settings)

        self.pitch = MotorController(uris.pitch)
        self.yaw = MotorController(uris.yaw)

        self.speed = AttrRW(
            Float(),
            io_ref=MirrorAttributeIORef(
                name="speed",
                motors=[self.pitch, self.yaw],
            ),
            group="Global",
        )
        self.jog_step = AttrRW(Int(), initial_value=1, group="Global")

    async def connect(self) -> None:
        await self.pitch.connect()
        await self.yaw.connect()

        saved = load_or_create_saved_pos()
        self.pitch.set_saved_position(saved.get("pitch", 0))
        self.yaw.set_saved_position(saved.get("yaw", 0))

        await super().connect()

    @command()
    async def home(self) -> None:
        logging.info("Homing motors")
        await self.pitch.home()
        await self.yaw.home()

    @command()
    async def stop_moving(self) -> None:
        """Stop all motors"""
        await self.pitch.stop_moving()
        await self.yaw.stop_moving()

    @command(group="Saved")
    async def return_to_saved(self) -> None:
        """Return to saved position"""
        logging.info("Returning to saved position")
        await self.pitch.move_to_saved()
        await self.yaw.move_to_saved()

    @command(group="Saved")
    async def save(self) -> None:
        """Save location"""
        pitch = await self.pitch.get_current_position()
        yaw = await self.yaw.get_current_position()

        logging.info(f"Saving position - (pitch: {pitch} - yaw: {yaw})")
        self.pitch.set_saved_position(pitch)
        self.yaw.set_saved_position(yaw)

        save_pos({"pitch": pitch, "yaw": yaw})

    @command(group="Jog")
    async def up(self) -> None:
        """Jog up"""
        step = self.jog_step.get()
        logging.info(f"Jogging up by {step}")
        await self.pitch.move_relative(step)

    @command(group="Jog")
    async def left(self) -> None:
        """Jog left"""
        step = self.jog_step.get()
        logging.info(f"Jogging left by {step}")
        await self.yaw.move_relative(step)

    @command(group="Jog")
    async def down(self) -> None:
        """Jog down"""
        step = self.jog_step.get()
        logging.info(f"Jogging down by {step}")
        await self.pitch.move_relative(step)

    @command(group="Jog")
    async def right(self) -> None:
        """Jog right"""
        step = self.jog_step.get()
        logging.info(f"Jogging right by {step}")
        await self.yaw.move_relative(step)
