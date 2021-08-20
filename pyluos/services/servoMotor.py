from __future__ import division
from __future__ import division
import collections
from copy import copy
import time

from .service import Service, interact
import numpy as np


class ServoMotor(Service):
    # target modes
    _MODE_COMPLIANT = 13
    _MODE_POWER = 12
    _MODE_TORQUE = 11
    _MODE_ANGULAR_SPEED = 10
    _MODE_ANGULAR_POSITION = 9
    _MODE_LINEAR_SPEED = 8
    _MODE_LINEAR_POSITION = 7
    # report modes
    _ANGULAR_POSITION = 6
    _ANGULAR_SPEED = 5
    _LINEAR_POSITION = 4
    _LINEAR_SPEED = 3
    _CURRENT = 2
    _TEMPERATURE = 1
    _TORQUE = 0

    # control modes
    _PLAY = 0
    _PAUSE = 1
    _STOP = 2
    _REC = 4

    def __init__(self, id, alias, device):
        Service.__init__(self, 'ServoMotor', id, alias, device)
        self._config = [False] * (ServoMotor._MODE_COMPLIANT + 1)
        # default configs, enable compliant, power_mode, and rotation position report
        self._config[ServoMotor._MODE_COMPLIANT] = True
        self._config[ServoMotor._MODE_POWER] = True
        self._config[ServoMotor._ANGULAR_POSITION] = True

        #configuration
        self._positionPid = [0.0, 0.0, 0.0]
        self._speedPid = [0.0, 0.0, 0.0]
        self._resolution = 16 # encoder resolution
        self._reduction = 131 # mechanical reduction after encoder
        self._dimension = 100 # Wheel size (mm)
        self._limit_rot_position = None
        self._limit_trans_position = None
        self._limit_rot_speed = None
        self._limit_trans_speed = None
        self._limit_power = 100.0
        self._limit_current = 6.0
        self._sampling_freq = 100.0
        self._control = 0

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
        self._temperature = 0.0

    def _convert_config(self):
        return int(''.join(['1' if c else '0' for c in self._config]), 2) # Table read reversly

    def bit(self, i, enable):
        self._config = self._config[:i] + () + self._config[i + 1:]

#************************** configurations *****************************

    def play(self):
        if (self._control >= self._REC):
            self._control = self._PLAY + self._REC
        else :
            self._control = self._PLAY
        self._push_value('control', self._control)

    def pause(self):
        if (self._control >= self._REC):
            self._control = self._PAUSE + self._REC
        else :
            self._control = self._PAUSE
        self._push_value('control', self._control)

    def stop(self):
        # also stop recording
        self._control = self._STOP
        self._push_value('control', self._control)

    def rec(self, enable):
        if (self._control >= self._REC):
            if (enable == False):
                self._control = self._control - self._REC
        else :
            if (enable == True):
                self._control = self._control + self._REC
        self._push_value('control', self._control)

    def setToZero(self):
        self._push_value('reinit', None)

    @property
    def sampling_freq(self):
        return self._sampling_freq

    @sampling_freq.setter
    def sampling_freq(self, sampling_freq):
        self._sampling_freq = sampling_freq
        self._push_value("time", 1.0 / sampling_freq)

    @property
    def positionPid(self):
        return self._positionPid

    @positionPid.setter
    def positionPid(self, new_pid):
        bak = copy(self._config)
        self.compliant = True
        self.rot_position_mode = True
        self.rot_speed_mode = False
        time.sleep(0.2)
        self._positionPid = new_pid
        self._push_value('pid', new_pid)
        time.sleep(0.2)
        self._config = bak
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    @property
    def speedPid(self):
        return self._speedPid

    @speedPid.setter
    def speedPid(self, new_pid):
        bak = copy(self._config)
        self.compliant = True
        self.rot_position_mode = False
        self.rot_speed_mode = True
        time.sleep(0.2)
        self._speedPid = new_pid
        self._push_value('pid', new_pid)
        time.sleep(0.2)
        self._config = bak
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    @property
    def encoder_res(self):
        return self._resolution

    @encoder_res.setter
    def encoder_res(self, s):
        self._resolution = s
        self._push_value("resolution", s)

    @property
    def reduction(self):
        return self._resolution

    @reduction.setter
    def reduction(self, s):
        self._reduction = s
        self._push_value("reduction", s)

    @property
    def wheel_size(self):
        return self._dimension

    @wheel_size.setter
    def wheel_size(self, s):
        self._dimension = s
        self._push_value("dimension", s)

    @property
    def limit_rot_position(self):
        return self._limit_rot_position

    @limit_rot_position.setter
    def limit_rot_position(self, s):
        self._limit_rot_position = s
        self._push_value("limit_rot_position", s)

    @property
    def limit_trans_position(self):
        return self._limit_trans_position

    @limit_trans_position.setter
    def limit_trans_position(self, s):
        self._limit_trans_position = s
        self._push_value("limit_trans_position", s)

    @property
    def limit_rot_speed(self):
        return self._limit_rot_speed

    @limit_rot_speed.setter
    def limit_rot_speed(self, s):
        self._limit_rot_speed = s
        self._push_value("limit_rot_speed", s)

    @property
    def limit_trans_speed(self):
        return self._limit_trans_speed

    @limit_trans_speed.setter
    def limit_trans_speed(self, s):
        self._limit_trans_speed = s
        self._push_value("limit_trans_speed", s)

    @property
    def limit_power(self):
        return self._limit_power

    @limit_power.setter
    def limit_power(self, s):
        self._limit_power = abs(s)
        s = min(s, 100.0)
        self._push_value("limit_power", s)

    @property
    def limit_current(self):
        return self._limit_current

    @limit_current.setter
    def limit_current(self, s):
        self._limit_current = s
        self._push_value("limit_current", s)

#************************** target modes *****************************

    # compliant
    @property
    def compliant(self):
        return self._config[ServoMotor._MODE_COMPLIANT]

    @compliant.setter
    def compliant(self, enable):
        self._config[ServoMotor._MODE_COMPLIANT] = True if enable != 0  else False
        self._compliant = enable
        self._push_value('parameters', self._convert_config())
        if (enable == False):
            self._target_rot_position = self._rot_position
        time.sleep(0.01)

    # power
    @property
    def power_ratio(self):
        if (self._config[ServoMotor._MODE_POWER] != True):
            print("power mode is not enabled in the service please use 'device.service.power_mode = True' to enable it")
            return
        return self._target_power

    @power_ratio.setter
    def power_ratio(self, s):
        if (self._config[ServoMotor._MODE_POWER] != True):
            print("power mode is not enabled in the service please use 'device.service.power_mode = True' to enable it")
        s = min(max(s, -100.0), 100.0)
        #if s != self._target_power:
        self._target_power = s
        self._push_value("power_ratio",s)

    @property
    def power_mode(self):
        return self._config[ServoMotor._MODE_POWER]

    @power_mode.setter
    def power_mode(self, enable):
        self._config[ServoMotor._MODE_POWER] = True if enable != 0  else False
        if (enable == True) :
            self._config[ServoMotor._MODE_ANGULAR_SPEED] = False
            self._config[ServoMotor._MODE_ANGULAR_POSITION] = False
            self._config[ServoMotor._MODE_LINEAR_SPEED] = False
            self._config[ServoMotor._MODE_LINEAR_POSITION] = False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # rotation speed
    @property
    def target_rot_speed(self):
        if (self._config[ServoMotor._MODE_ANGULAR_SPEED] != True):
            print("rotation speed mode could be not enabled in the service please use 'device.service.rot_speed_mode = True' to enable it")
        return self._target_rot_speed

    @target_rot_speed.setter
    def target_rot_speed(self, s):
        if (self._config[ServoMotor._MODE_ANGULAR_SPEED] != True):
            print("rotation speed mode could be not enabled in the service please use 'device.service.rot_speed_mode = True' to enable it")
        self._target_rot_speed = s
        self._push_value("target_rot_speed", s)

    @property
    def rot_speed_mode(self):
        return self._config[ServoMotor._MODE_ANGULAR_SPEED]

    @rot_speed_mode.setter
    def rot_speed_mode(self, enable):
        self._config[ServoMotor._MODE_ANGULAR_SPEED] = True if enable != 0  else False
        if (enable == True) :
            self._config[ServoMotor._MODE_LINEAR_SPEED] = False
            self._config[ServoMotor._MODE_POWER] = False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # rotation position
    @property
    def target_rot_position(self):
        if (self._config[ServoMotor._MODE_ANGULAR_POSITION] != True):
            print("rotation position mode could be not enabled in the service please use 'device.service.rot_position_mode = True' to enable it")
        return self._target_rot_position

    @target_rot_position.setter
    def target_rot_position(self, s):
        if (self._config[ServoMotor._MODE_ANGULAR_POSITION] != True):
            print("rotation position mode could be not enabled in the service please use 'device.service.rot_position_mode = True' to enable it")
        self._target_rot_position = s
        if hasattr(s, "__len__"):
            self._push_data('target_rot_position', [len(s) * 4], np.array(s, dtype=np.float32)) # multiplying by the size of float32
        else :
            self._push_value("target_rot_position", s)

    @property
    def rot_position_mode(self):
        return self._config[ServoMotor._MODE_ANGULAR_POSITION]

    @rot_position_mode.setter
    def rot_position_mode(self, enable):
        self._config[ServoMotor._MODE_ANGULAR_POSITION] = True if enable != 0  else False
        if (enable == True) :
            self._config[ServoMotor._MODE_LINEAR_POSITION] = False
            self._config[ServoMotor._MODE_POWER] = False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # translation speed
    @property
    def target_trans_speed(self):
        if (self._config[ServoMotor._MODE_LINEAR_SPEED] != True):
            print("translation speed mode could be not enabled in the service please use 'device.service.trans_speed_mode = True' to enable it")
        return self._target_trans_speed

    @target_trans_speed.setter
    def target_trans_speed(self, s):
        if (self._config[ServoMotor._MODE_LINEAR_SPEED] != True):
            print("translation speed mode could be not enabled in the service please use 'device.service.trans_speed_mode = True' to enable it")
        self._target_trans_speed = s
        self._push_value("target_trans_speed", s)

    @property
    def trans_speed_mode(self):
        return self._config[ServoMotor._MODE_LINEAR_SPEED]

    @trans_speed_mode.setter
    def trans_speed_mode(self, enable):
        self._config[ServoMotor._MODE_LINEAR_SPEED] = True if enable != 0  else False
        if (enable == True) :
            self._config[ServoMotor._MODE_ANGULAR_SPEED] = False
            self._config[ServoMotor._MODE_POWER] = False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # translation position
    @property
    def target_trans_position(self):
        if (self._config[ServoMotor._MODE_LINEAR_POSITION] != True):
            print("translation speed mode could be not enabled in the service please use 'device.service.trans_pos_mode = True' to enable it")
        return self._target_trans_position

    @target_trans_position.setter
    def target_trans_position(self, s):
        if (self._config[ServoMotor._MODE_LINEAR_POSITION] != True):
            print("translation speed mode could be not enabled in the service please use 'device.service.trans_position_mode = True' to enable it")
        self._target_trans_position = s
        if hasattr(s, "__len__"):
            self._push_value('target_trans_position', [len(s) * 4]) # multiplying by the size of float32
            self._push_data(np.array(s, dtype=np.float32))
        else :
            self._push_value("target_trans_position", s)

    @property
    def trans_position_mode(self):
        return self._config[ServoMotor._MODE_LINEAR_POSITION]

    @trans_position_mode.setter
    def trans_position_mode(self, enable):
        self._config[ServoMotor._MODE_LINEAR_POSITION] = True if enable != 0  else False
        if (enable == True) :
            self._config[ServoMotor._MODE_ANGULAR_POSITION] = False
            self._config[ServoMotor._MODE_POWER] = False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)
#************************** report modes *****************************

    # rotation position
    @property
    def rot_position(self):
        if (self._config[ServoMotor._ANGULAR_POSITION] != True):
            self.rot_position = True
        return self._rot_position

    @rot_position.setter
    def rot_position(self, enable):
        self._config[ServoMotor._ANGULAR_POSITION] = True if enable != 0  else False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # rotation speed
    @property
    def rot_speed(self):
        if (self._config[ServoMotor._ANGULAR_SPEED] != True):
            self.rot_speed = True
        return self._rot_speed

    @rot_speed.setter
    def rot_speed(self, enable):
        self._config[ServoMotor._ANGULAR_SPEED] = True if enable != 0  else False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # translation position
    @property
    def trans_position(self):
        if (self._config[ServoMotor._LINEAR_POSITION] != True):
            self.trans_position = True
        return self._rot_position

    @trans_position.setter
    def trans_position(self, enable):
        self._config[ServoMotor._LINEAR_POSITION] = True if enable != 0  else False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # translation speed
    @property
    def trans_speed(self):
        if (self._config[ServoMotor._LINEAR_SPEED] != True):
            self.trans_speed = True
        return self._rot_speed

    @trans_speed.setter
    def trans_speed(self, enable):
        self._config[ServoMotor._LINEAR_SPEED] = True if enable != 0  else False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # current
    @property
    def current(self):
        if (self._config[ServoMotor._CURRENT] != True):
            self.current = True
        return self._current

    @current.setter
    def current(self, enable):
        self._config[ServoMotor._CURRENT] = True if enable != 0  else False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

    # temperature
    @property
    def temperature(self):
        if (self._config[ServoMotor._TEMPERATURE] != True):
            self.temperature = True
        return self._temperature

    @temperature.setter
    def temperature(self, enable):
        self._config[ServoMotor._TEMPERATURE] = True if enable != 0  else False
        self._push_value('parameters', self._convert_config())
        time.sleep(0.01)

#************************** custom motor type commands *****************************

    def dxl_set_id(self, id):
        self._push_value('set_id', id)

    def dxl_detect(self):
        self._push_value('reinit', 0)
        print ("To get new detected Dxl motors usable on pyluos you should recreate your Pyluos object.")

    def dxl_register(self, register, val):
        new_val = [register, val]
        self._push_value('register', new_val)

#************************** controls and updates *****************************

    def _update(self, new_state):
        Service._update(self, new_state)
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
        if 'temperature' in new_state:
            self._temperature = new_state['temperature']

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
            self.power_mode = power_mode
            if (power_mode) :
                self.power_ratio = power_ratio

            self.rot_speed_mode = rot_speed_mode
            if (rot_speed_mode) :
                self.target_rot_speed = rot_speed

            self.rot_position_mode = rot_position_mode
            if (rot_position_mode) :
                self.target_rot_position = rot_position

            self.trans_speed_mode = trans_speed_mode
            if (trans_speed_mode) :
                self.target_trans_speed = trans_speed

            self.trans_position_mode = trans_position_mode
            if (trans_position_mode) :
                self.target_trans_position = trans_position

        w = interact(change_config,
                        rot_speed_report = self._config[ServoMotor._ANGULAR_SPEED],
                        rot_position_report = self._config[ServoMotor._ANGULAR_POSITION],
                        trans_speed_report = self._config[ServoMotor._LINEAR_SPEED],
                        trans_position_report = self._config[ServoMotor._LINEAR_POSITION],
                        current_report = self._config[ServoMotor._CURRENT],
                        temperature_report = self._config[ServoMotor._TEMPERATURE],

                        compliant_mode = self._config[ServoMotor._MODE_COMPLIANT],
                        power_mode = self._config[ServoMotor._MODE_POWER],
                        power_ratio=(-100.0, 100.0, 1.0),
                        rot_speed_mode = self._config[ServoMotor._MODE_ANGULAR_SPEED],
                        rot_speed = (-300.0, 300.0, 1.0),
                        rot_position_mode = self._config[ServoMotor._MODE_ANGULAR_POSITION],
                        rot_position = (-360.0, 360.0, 1.0),
                        trans_speed_mode = self._config[ServoMotor._MODE_LINEAR_SPEED],
                        trans_speed = (-1000.0, 1000.0, 1.0),
                        trans_position_mode = self._config[ServoMotor._MODE_LINEAR_POSITION],
                        trans_position = (-1000.0, 1000.0, 1.0))
