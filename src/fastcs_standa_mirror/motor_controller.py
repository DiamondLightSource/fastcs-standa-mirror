import logging

import libximc.highlevel as ximc
from fastcs.attributes import AttrR
from fastcs.controllers import Controller
from fastcs.datatypes import Bool, Float
from fastcs.methods import command

from fastcs_standa_mirror.io.motor_attribute import (
    MotorAttributeIO,
    MotorAttributeIORef,
)


class MotorController(Controller):
    """Subcontroller for Standa motor"""

    _device_uri: str = ""

    current: AttrR
    saved: AttrR
    moving: AttrR
    speed: AttrR

    def __init__(self, device_uri: str) -> None:
        super().__init__(ios=[MotorAttributeIO(self)])
        self._device_uri = device_uri
        self.saved_position: int = 0

        self.current = AttrR(
            Float(), io_ref=MotorAttributeIORef("current"), group="Position"
        )
        self.saved = AttrR(
            Float(), io_ref=MotorAttributeIORef("saved"), group="Position"
        )
        self.moving = AttrR(
            Bool(), io_ref=MotorAttributeIORef("moving"), group="Status"
        )
        self.speed = AttrR(Float(), io_ref=MotorAttributeIORef("speed"), group="Status")

    async def connect(self) -> None:
        try:
            self.motor = ximc.Axis(self._device_uri)
            self.motor.open_device()
            logging.info(f"Successfully opened device at {self._device_uri}")
        except Exception as e:
            logging.error(f"Failed to open device at {self._device_uri}: {e}")
            raise
        await super().connect()

    async def home(self) -> None:
        logging.info(f"Homing {self.path[-1]}")
        self.motor.command_home()

    @command()
    async def stop_moving(self) -> None:
        """Stop motor"""
        logging.info(f"Stopping {self.path[-1]} motor")
        self.motor.command_stop()

    async def set_speed(self, value: float) -> None:
        """Command the motor speed on the hardware.

        Deliberately not a an AttrW, so operators get no per-axis speed control. Only
        the mirror calls this.
        """
        move_settings = self.motor.get_move_settings()
        move_settings.Speed = int(value)
        self.motor.set_move_settings(move_settings)

    async def move_absolute(self, position: int) -> None:
        """Move to absolute position"""
        self.motor.command_move(position, 0)

    async def move_relative(self, distance: int) -> None:
        """Move by relative distance"""
        self.motor.command_movr(distance, 0)

    async def move_to_saved(self) -> None:
        """Move to saved position"""
        self.motor.command_move(self.saved_position, 0)

    async def get_current_position(self) -> int:
        """Get current position"""
        return self.motor.get_position().Position

    async def get_saved_position(self) -> int:
        """Get saved position"""
        return self.saved_position

    def set_saved_position(self, new_saved_position) -> None:
        """Set a new saved position"""
        self.saved_position = new_saved_position
