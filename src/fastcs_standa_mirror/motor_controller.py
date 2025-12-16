from fastcs.attributes import AttrR
from fastcs.controllers import Controller
from fastcs.datatypes import Float, Bool

import libximc.highlevel as ximc

from fastcs_standa_mirror.io.motor_attribute import MotorAttributeIO, MotorAttributeIORef

class MotorController(Controller):

    position = AttrR(Float(), io_ref=MotorAttributeIORef("position"))
    home = AttrR(Float(), io_ref=MotorAttributeIORef("home"))
    moving = AttrR(Bool(), io_ref=MotorAttributeIORef("status"))

    def __init__(self, name: str, device_uri: str):
        self.name = name
        self._device_uri = device_uri
        self._connection = ximc.Axis(self._device_uri)
        self._connection.open_device()
        
        super().__init__(
            name, ios=[MotorAttributeIO(self)]
        )

        self.home_position = 0

    async def move_absolute(self, position: int) -> None:
        """Move to absolute position"""
        self._connection.command_move(position, 0)

    async def move_relative(self, distance: int) -> None:
        """Move by relative distance"""
        self._connection.command_movr(distance, 0)

    async def move_home(self) -> None:
        """Move to home position"""
        self._connection.command_move(self.home_position, 0)

    async def get_current_position(self) -> int:
        """Get current position"""
        return self._connection.get_position().Position
    
    async def get_home_position(self) -> int:
        """Get home position"""
        return self.home_position
    
    def set_home_position(self, new_position) -> None:
        """Set a new home position"""
        self.home_position = new_position

