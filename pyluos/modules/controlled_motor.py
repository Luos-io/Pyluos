from __future__ import division
from __future__ import division
import collections
from copy import copy
import time

from .module import Module, interact


class ControlledMotor(Module):
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

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'ControlledMotor', id, alias, robot)
        self._config = [False] * (ControlledMotor._MODE_COMPLIANT + 1)
        # default configs, enable compliant, power_mode, and rotation position report
        self._config[ControlledMotor._MODE_COMPLIANT] = True
        self._config[ControlledMotor._MODE_POWER] = True
        self._config[ControlledMotor._ROTATION_POSITION] = True

        #configuration
        self._positionPid = [0.0, 0.0, 0.0]
        self._speedPid = [0.0, 0.0, 0.0]
        self._resolution = 16 # encoder resolution
        self._reduction = 131 # mechanical reduction after encoder
        self._dimension = 100 # Wheel size (mm)

        #targets
        self._compliant = True
        self._target_power = 0.0
        self._target_rot_speed = 0.0
        self._target_rot_position = 0.0
        self._target_trans_speed = 0.0
        self._target_trans_position = 0.0

        # report modes
        self._rot_position = 0.0
        self._rot_speed = 0.0
        self._trans_position= 0.0
        self._trans_speed = 0.0
        self._current = 0.0

    def _convert_config(self):
        return int(''.join(['1' if c else '0' for c in self._config]), 2) # Table read reversly

    def bit(self, i, enable):
        self._config = self._config[:i] + () + self._config[i + 1:]

#************************** configurations *****************************

    def setToZero(self):
        self._push_value('reinit', None)

    @property
    def positionPid(self):
        return self._positionPid

    @positionPid.setter
    def positionPid(self, new_pid):
        if new_pid != self._positionPid:
            bak = copy(self._config)
            self.compliant = True
            self.rot_position_mode(True)
            self.rot_speed_mode(False)
            time.sleep(0.1)
            self._positionPid = new_pid
            self._push_value('pid', new_pid)
            time.sleep(0.1)
            self._config = bak
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    @property
    def speedPid(self):
        return self._positionPid

    @speedPid.setter
    def speedPid(self, new_pid):
        if new_pid != self._speedPid:
            bak = copy(self._config)
            self.compliant = True
            self.rot_position_mode(False)
            self.rot_speed_mode(True)
            time.sleep(0.1)
            self._speedPid = new_pid
            self._push_value('pid', new_pid)
            time.sleep(0.1)
            self._config = bak
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)


    @property
    def encoder_res(self):
        return self._resolution

    @encoder_res.setter
    def encoder_res(self, s):
        self._resolution = s
        if s != self._resolution:
            self._push_value("resolution", s)

    @property
    def reduction(self):
        return self._resolution

    @reduction.setter
    def reduction(self, s):
        self._reduction = s
        if s != self._reduction:
            self._push_value("reduction", s)

    @property
    def wheel_size(self):
        return self._dimension

    @wheel_size.setter
    def wheel_size(self, s):
        self._dimension = s
        if s != self._dimension:
            self._push_value("dimension", s)

#************************** target modes *****************************

    # compliant
    @property
    def compliant(self):
        self._compliant

    @compliant.setter
    def compliant(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._MODE_COMPLIANT] = True if enable != 0  else False
        self._compliant = enable
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    # power
    @property
    def power_ratio(self):
        if (self._config[ControlledMotor._MODE_POWER] != True):
            print("power mode is not enabled in the module please use 'robot.module.power_mode(True)' to enable it")
            return
        return self._target_power

    @power_ratio.setter
    def power_ratio(self, s):
        if (self._config[ControlledMotor._MODE_POWER] != True):
            print("power mode is not enabled in the module please use 'robot.module.power_mode(True)' to enable it")
            return
        s = min(max(s, -100.0), 100.0)
        if s != self._target_power:
            self._target_power = s
            self._push_value("power_ratio",s)

    def power_mode(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._MODE_POWER] = True if enable != 0  else False
        if (enable == True) :
            self._config[ControlledMotor._MODE_ROT_SPEED] = False
            self._config[ControlledMotor._MODE_ROT_POSITION] = False
            self._config[ControlledMotor._MODE_TRANS_SPEED] = False
            self._config[ControlledMotor._MODE_TRANS_POSITION] = False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    # rotation speed
    @property
    def target_rot_speed(self):
        if (self._config[ControlledMotor._MODE_ROT_SPEED] != True):
            print("rotation speed mode is not enabled in the module please use 'robot.module.rot_speed_mode(True)' to enable it")
            return
        return self._target_rot_speed

    @target_rot_speed.setter
    def target_rot_speed(self, s):
        if (self._config[ControlledMotor._MODE_ROT_SPEED] != True):
            print("rotation speed mode is not enabled in the module please use 'robot.module.rot_speed_mode(True)' to enable it")
            return
        if s != self._target_rot_speed:
            self._target_rot_speed = s
            self._push_value("target_rot_speed", s)
            return

    def rot_speed_mode(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._MODE_ROT_SPEED] = True if enable != 0  else False
        if (enable == True) :
            self._config[ControlledMotor._MODE_TRANS_SPEED] = False
            self._config[ControlledMotor._MODE_POWER] = False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    # rotation position
    @property
    def target_rot_position(self):
        if (self._config[ControlledMotor._MODE_ROT_POSITION] != True):
            print("rotation position mode is not enabled in the module please use 'robot.module.rot_position_mode(True)' to enable it")
            return
        return self._target_rot_position

    @target_rot_position.setter
    def target_rot_position(self, s):
        if (self._config[ControlledMotor._MODE_ROT_POSITION] != True):
            print("rotation position mode is not enabled in the module please use 'robot.module.rot_position_mode(True)' to enable it")
            return
        if s != self._target_rot_position:
            self._target_rot_position = s
            self._push_value("target_rot_position", s)

    def rot_position_mode(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._MODE_ROT_POSITION] = True if enable != 0  else False
        if (enable == True) :
            self._config[ControlledMotor._MODE_TRANS_POSITION] = False
            self._config[ControlledMotor._MODE_POWER] = False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    # translation speed
    @property
    def target_trans_speed(self):
        if (self._config[ControlledMotor._MODE_TRANS_SPEED] != True):
            print("translation speed mode is not enabled in the module please use 'robot.module.trans_speed_mode(True)' to enable it")
            return
        return self._target_trans_speed

    @target_trans_speed.setter
    def target_trans_speed(self, s):
        if (self._config[ControlledMotor._MODE_TRANS_SPEED] != True):
            print("translation speed mode is not enabled in the module please use 'robot.module.trans_speed_mode(True)' to enable it")
            return
        if s != self._target_trans_speed:
            self._target_trans_speed = s
            self._push_value("target_trans_speed", s)

    def trans_speed_mode(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._MODE_TRANS_SPEED] = True if enable != 0  else False
        if (enable == True) :
            self._config[ControlledMotor._MODE_ROT_SPEED] = False
            self._config[ControlledMotor._MODE_POWER] = False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    # translation position
    @property
    def target_trans_position(self):
        if (self._config[ControlledMotor._MODE_TRANS_POSITION] != True):
            print("translation speed mode is not enabled in the module please use 'robot.module.trans_speed_mode(True)' to enable it")
            return
        return self._target_trans_position

    @target_trans_position.setter
    def target_trans_position(self, s):
        if (self._config[ControlledMotor._MODE_TRANS_POSITION] != True):
            print("translation speed mode is not enabled in the module please use 'robot.module.trans_speed_mode(True)' to enable it")
            return
        if s != self._target_trans_position:
            self._target_trans_position = s
            self._push_value("target_trans_position", s)

    def trans_position_mode(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._MODE_TRANS_POSITION] = True if enable != 0  else False
        if (enable == True) :
            self._config[ControlledMotor._MODE_ROT_POSITION] = False
            self._config[ControlledMotor._MODE_POWER] = False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)
#************************** report modes *****************************

    # rotation position
    @property
    def rot_position(self):
        if (self._config[ControlledMotor._ROTATION_POSITION] != True):
            print("rotation position report is not enabled in the module please use 'robot.module.rot_position = True' to enable it")
            return
        return self._rot_position

    @rot_position.setter
    def rot_position(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._ROTATION_POSITION] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    # rotation speed
    @property
    def rot_speed(self):
        if (self._config[ControlledMotor._ROTATION_SPEED] != True):
            print("rotation speed report is not enabled in the module please use 'robot.module.rot_speed = True' to enable it")
            return
        return self._rot_speed

    @rot_speed.setter
    def rot_speed(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._ROTATION_SPEED] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    # translation position
    @property
    def trans_position(self):
        if (self._config[ControlledMotor._TRANSLATION_POSITION] != True):
            print("translation position report is not enabled in the module please use 'robot.module.trans_position = True' to enable it")
            return
        return self._rot_position

    @trans_position.setter
    def trans_position(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._TRANSLATION_POSITION] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    # translation speed
    @property
    def trans_speed(self):
        if (self._config[ControlledMotor._TRANSLATION_SPEED] != True):
            print("translation speed report is not enabled in the module please use 'robot.module.trans_speed = True' to enable it")
            return
        return self._rot_speed

    @trans_speed.setter
    def trans_speed(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._TRANSLATION_SPEED] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

    # current
    @property
    def current(self):
        if (self._config[ControlledMotor._CURRENT] != True):
            print("translation speed report is not enabled in the module please use 'robot.module.current = True' to enable it")
            return
        return self._current

    @current.setter
    def current(self, enable):
        bak = copy(self._config)
        self._config[ControlledMotor._CURRENT] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('parameters', self._convert_config())
            time.sleep(0.1)

#************************** controls and updates *****************************

    def _update(self, new_state):
        Module._update(self, new_state)
        if 'rot_position' in new_state:
            self._rot_position = new_state['rot_position']
        if 'rot_speed' in new_state:
            self._rot_speed = new_state['rot_speed']
        if 'trans_position' in new_state:
            self._trans_position = new_state['trans_position']
        if 'trans_speed' in new_state:
            self._trans_speed = new_state['trans_speed']
        if 'current' in new_state:
            self._current = new_state['current']

    def control(self):
        def change_config(rot_speed_report, rot_position_report, trans_speed_report, trans_position_report, current_report, compliant_mode, power_mode, power_ratio, rot_speed_mode, rot_speed, rot_position_mode, rot_position, trans_speed_mode, trans_speed, trans_position_mode, trans_position):
            # report config
            self.rot_speed = rot_speed_report
            self.rot_position = rot_position_report
            self.trans_speed = trans_speed_report
            self.trans_position = trans_position_report
            self.current = current_report
            # target mode
            self.compliant = compliant_mode
            self.power_mode(power_mode)
            if (power_mode) :
                self.power_ratio = power_ratio

            self.rot_speed_mode(rot_speed_mode)
            if (rot_speed_mode) :
                self.target_rot_speed = rot_speed

            self.rot_position_mode(rot_position_mode)
            if (rot_position_mode) :
                self.target_rot_position = rot_position

            self.trans_speed_mode(trans_speed_mode)
            if (trans_speed_mode) :
                self.target_trans_speed = trans_speed

            self.trans_position_mode(trans_position_mode)
            if (trans_position_mode) :
                self.target_trans_position = trans_position

        w = interact(change_config,
                        rot_speed_report = self._config[ControlledMotor._ROTATION_SPEED],
                        rot_position_report = self._config[ControlledMotor._ROTATION_POSITION],
                        trans_speed_report = self._config[ControlledMotor._TRANSLATION_SPEED],
                        trans_position_report = self._config[ControlledMotor._TRANSLATION_POSITION],
                        current_report = self._config[ControlledMotor._CURRENT],

                        compliant_mode = self._config[ControlledMotor._MODE_COMPLIANT],
                        power_mode = self._config[ControlledMotor._MODE_POWER],
                        power_ratio=(-100.0, 100.0, 1.0),
                        rot_speed_mode = self._config[ControlledMotor._MODE_ROT_SPEED],
                        rot_speed = (-300.0, 300.0, 1.0),
                        rot_position_mode = self._config[ControlledMotor._MODE_ROT_POSITION],
                        rot_position = (-360.0, 360.0, 1.0),
                        trans_speed_mode = self._config[ControlledMotor._MODE_TRANS_SPEED],
                        trans_speed = (-1000.0, 1000.0, 1.0),
                        trans_position_mode = self._config[ControlledMotor._MODE_TRANS_POSITION],
                        trans_position = (-1000.0, 1000.0, 1.0))

