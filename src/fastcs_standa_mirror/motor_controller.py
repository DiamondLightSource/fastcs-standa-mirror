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

    _name: str = ""
    _device_uri: str = ""

    current = AttrR(Float(), io_ref=MotorAttributeIORef("current"), group="Position")
    home = AttrR(Float(), io_ref=MotorAttributeIORef("home"), group="Position")
    moving = AttrR(Bool(), io_ref=MotorAttributeIORef("moving"), group="Status")

    def __init__(self, name: str, device_uri: str):
        self._name = name
        self._device_uri = device_uri

        try:
            self.motor = ximc.Axis(self._device_uri)
            self.motor.open_device()
            logging.info(
                f"Successfully opened device\n'{self._name}' at {self._device_uri}"
            )

        except Exception as e:
            logging.error(
                f"Failed to open device!\n'{self._name}' at {self._device_uri}: {e}"
            )
            raise

        self.home_position: int = 0

        super().__init__(name, ios=[MotorAttributeIO(self)])

    @command()
    async def stop_moving(self) -> None:
        """Stop motor"""
        logging.info(f"Stopping {self._name} motor")
        self.motor.command_stop()

    async def move_absolute(self, position: int) -> None:
        """Move to absolute position"""
        self.motor.command_move(position, 0)

    async def move_relative(self, distance: int) -> None:
        """Move by relative distance"""
        self.motor.command_movr(distance, 0)

    async def move_home(self) -> None:
        """Move to home position"""
        self.motor.command_move(self.home_position, 0)

    async def get_current_position(self) -> int:
        """Get current position"""
        return self.motor.get_position().Position

    async def get_home_position(self) -> int:
        """Get home position"""
        return self.home_position

    def set_home_position(self, new_home_position) -> None:
        """Set a new home position"""
        self.home_position = new_home_position
