from .module import Module, interact


class GenericMotorController(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'generic_motor_controller', id, alias, robot)
        self._power = None

    @property
    def power_ratio(self):
        return self._power

    @power_ratio.setter
    def power_ratio(self, new_power):
        new_power = min(max(new_power, -100.0), 100.0)

        if new_power != self._power:
            self._power = new_power
            self._push_value('power_ratio', new_power)

    def control(self):
        def set_power(power):
            self.power_ratio = power

        return interact(set_power, power=(-100.0, 100.0, 1.0))
