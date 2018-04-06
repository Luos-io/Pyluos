from __future__ import division

from .module import Module
from .gpio import AnalogInputPin
from .l0_dc_motor import DCMotor


class Eddy(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Eddy', id, alias, robot)

        self.right_wheel = DCMotor('s1', self)
        self.left_wheel = DCMotor('s2', self)

        self.left_light_sensor = AnalogInputPin('p7')
        self.right_light_sensor = AnalogInputPin('p9')

    def _update(self, new_state):
        self.left_light_sensor._update(new_state['p7'])
        self.right_light_sensor._update(new_state['p9'])
