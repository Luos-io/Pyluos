from .module import Module, interact
from copy import copy
import time

class Stepper(Module):
    # target modes
    _MODE_COMPLIANT = 11
    _MODE_POWER = 10
    _MODE_ROT_SPEED = 8
    _MODE_ROT_POSITION = 7
    _MODE_TRANS_SPEED = 6
    _MODE_TRANS_POSITION = 5
    # report modes
    _ROTATION_POSITION = 4
    _ROTATION_SPEED = 3
    _TRANSLATION_POSITION = 2
    _TRANSLATION_SPEED = 1
    _CURRENT = 0

    def __init__(self, id, alias, device):
        Module.__init__(self, 'Stepper', id, alias, device)
        self._config = [False] * (Stepper._MODE_COMPLIANT + 1)
        # default configs, enable compliant, power_mode, and rotation position report
        self._config[Stepper._MODE_ROT_POSITION] = True
        self._config[Stepper._MODE_COMPLIANT] = True

        #configuration
        self._resolution = 200.0
        self._dimension = 0.0

        #targets
        self._target_rot_speed = 100.0
        self._target_rot_position = 0.0
        self._target_trans_speed = 0.0
        self._target_trans_position = 0.0

    def _convert_config(self):
        return int(''.join(['1' if c else '0' for c in self._config]), 2) # Table read reversly

    def bit(self, i, enable):
        self._config = self._config[:i] + () + self._config[i + 1:]

#************************** configurations *****************************

    def setToZero(self):
        self._push_value('reinit', None)

    @property
    def stepPerTurn(self):
        return self._resolution

    @stepPerTurn.setter
    def stepPerTurn(self, s):
        self._resolution = s
        self._push_value("resolution", s)

    @property
    def wheel_size(self):
        return self._dimension

    @wheel_size.setter
    def wheel_size(self, s):
        self._dimension = s
        self._push_value("dimension", s)

#************************** target modes *****************************

    # compliant
    @property
    def compliant(self):
        self._compliant

    @compliant.setter
    def compliant(self, enable):
        self._config[Stepper._MODE_COMPLIANT] = True if enable != 0  else False
        self._compliant = enable
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # rotation speed
    @property
    def target_rot_speed(self):
        return self._target_rot_speed

    @target_rot_speed.setter
    def target_rot_speed(self, s):
        self._target_rot_speed = s
        self._push_value("target_rot_speed", s)

    # rotation position
    @property
    def target_rot_position(self):
        if (self._config[Stepper._MODE_ROT_POSITION] != True):
            print("rotation position mode is not enabled in the module please use 'device.module.rot_position_mode(True)' to enable it")
        return self._target_rot_position

    @target_rot_position.setter
    def target_rot_position(self, s):
        if (self._config[Stepper._MODE_ROT_POSITION] != True):
            print("rotation position mode is not enabled in the module please use 'device.module.rot_position_mode(True)' to enable it")
        self._target_rot_position = s
        self._push_value("target_rot_position", s)

    def rot_position_mode(self, enable):
        self._config[Stepper._MODE_ROT_POSITION] = True if enable != 0  else False
        if (enable == True) :
            self._config[Stepper._MODE_TRANS_POSITION] = False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # translation speed
    @property
    def target_trans_speed(self):
        return self._target_trans_speed

    @target_trans_speed.setter
    def target_trans_speed(self, s):
        if (self._dimension == 0) :
            print("you have to setup a wheel_size before using translation command")
        self._target_trans_speed = s
        self._push_value("target_trans_speed", s)

    # translation position
    @property
    def target_trans_position(self):
        if (self._config[Stepper._MODE_TRANS_POSITION] != True):
            print("translation speed mode is not enabled in the module please use 'device.module.trans_speed_mode(True)' to enable it")
        return self._target_trans_position

    @target_trans_position.setter
    def target_trans_position(self, s):
        if (self._config[Stepper._MODE_TRANS_POSITION] != True):
            print("translation speed mode is not enabled in the module please use 'device.module.trans_speed_mode(True)' to enable it")
        self._target_trans_position = s
        self._push_value("target_trans_position", s)

    def trans_position_mode(self, enable):
        if (self._dimension == 0) :
            print("you have to setup a wheel_size before using translation command")
        self._config[Stepper._MODE_TRANS_POSITION] = True if enable != 0  else False
        if (enable == True) :
            self._config[Stepper._MODE_ROT_POSITION] = False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

#************************** controls and updates *****************************

    def _update(self, new_state):
        Module._update(self, new_state)

    def control(self):
        def change_config(compliant_mode, rot_speed, rot_position_mode, rot_position, trans_speed, trans_position_mode, trans_position):
            # target mode
            self.compliant = compliant_mode
            self.target_rot_speed = rot_speed

            self.rot_position_mode(rot_position_mode)
            if (rot_position_mode) :
                self.target_rot_position = rot_position

            self.target_trans_speed = trans_speed

            self.trans_position_mode(trans_position_mode)
            if (trans_position_mode) :
                self.target_trans_position = trans_position


        w = interact(change_config,
                        compliant_mode = self._config[Stepper._MODE_COMPLIANT],
                        rot_speed = (-700, 700, 1),
                        rot_position_mode = self._config[Stepper._MODE_ROT_POSITION],
                        rot_position = (-360.0, 360.0, 1.0),
                        trans_speed = (-1000, 1000, 1),
                        trans_position_mode = self._config[Stepper._MODE_TRANS_POSITION],
                        trans_position = (-1000, 1000, 1))
