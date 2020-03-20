from .module import Module, interact
import numpy as np

class DynamixelMotor(Module):

    # control modes
    _PLAY = 0
    _PAUSE = 1
    _STOP = 2
    _REC = 4

    def __init__(self, id, alias, device):
        Module.__init__(self, 'DynamixelMotor', id, alias, device)
        # Read
        self.rot_position = None
        self.temperature = None

        # Write
        self._target_rot_position = None
        self._rot_speed = None
        self._compliant = None
        self._wheel_mode = None
        self._power_limit = None
        self._positionPid = [None, None, None]
        self._limit_rot_position = [None, None]
        self._baudrate = 1000000

        # Config
        self._control = 0
        self._sampling_freq = 100.0

    def _update(self, new_state):
        Module._update(self, new_state)

        if 'rot_position' in new_state:
            self.rot_position = new_state['rot_position']
        if 'temperature' in new_state:
            self.temperature = new_state['temperature']

    @property
    def target_rot_position(self):
        return self._target_rot_position

    @target_rot_position.setter
    def target_rot_position(self, target_position):
        self._target_rot_position = target_position
        if hasattr(target_position, "__len__"):
            self._push_data('target_rot_position', [len(target_position) * 4], np.array(target_position, dtype=np.float32)) # multiplying by the size of float32
        else :
            self._push_value("target_rot_position", target_position)

    @property
    def rot_position_limit(self):
        return self._limit_rot_position

    @rot_position_limit.setter
    def rot_position_limit(self, limit_position):
        self._push_value('limit_rot_position', limit_position)
        self._limit_rot_position = limit_position

    @property
    def target_rot_speed(self):
        return self._rot_speed

    @target_rot_speed.setter
    def target_rot_speed(self, moving_speed):
        self._push_value('target_rot_speed', moving_speed)
        self._rot_speed = moving_speed

    @property
    def positionPid(self):
        return self._positionPid

    @positionPid.setter
    def positionPid(self, new_pid):
        self._positionPid = new_pid
        self._push_value('pid', new_pid)

    # power limit
    @property
    def power_ratio_limit(self):
        return self._power_limit

    @power_ratio_limit.setter
    def power_ratio_limit(self, s):
        s = min(max(s, 0), 100.0)
        self._power_limit = s
        self._push_value("limit_power",s)

    @property
    def compliant(self):
        return self._compliant

    @compliant.setter
    def compliant(self, compliant):
        self._push_value('compliant', compliant)
        self._compliant = compliant
        if (self.compliant == False):
            self.target_rot_position = self.rot_position

    @property
    def wheel_mode(self):
        return self._wheel_mode

    @wheel_mode.setter
    def wheel_mode(self, wheel_mode):
        self._push_value('wheel_mode', wheel_mode)
        self._wheel_mode = wheel_mode

    def set_id(self, id):
        self._push_value('set_id', id)

    def dxl_detect(self):
        self._push_value('reinit', 0)
        print ("To get new detected Dxl motors usable on pyluos you should recreate your Pyluos object.")

    def register(self, register, val):
        new_val = [register, val]
        self._push_value('register', new_val)

    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, baud):
        values = [9600, 19200, 57600, 115200, 200000, 250000, 400000, 500000, 1000000]
        if baud in values :
            new_val = [4, baud]
            self._push_value('register', new_val)
            self._baudrate = baud
            print ("If you try to recover a motor you should start 'dxl_detect()' command and recreate your Pyluos object.")
        else :
            err = "Possible values are :\n"
            for val in values :
                err = err + "\t- " + str(val) + "\n"
            raise ValueError(err)

    def factory_reset(self):
        new_val = [0xFF, 0]
        self._push_value('register', new_val)
        print("Motor reseted => baudrate : 1000000, ID : 1")

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

    @property
    def sampling_freq(self):
        return self._sampling_freq

    @sampling_freq.setter
    def sampling_freq(self, sampling_freq):
        self._sampling_freq = sampling_freq
        self._push_value("time", 1.0 / sampling_freq)


    # notebook things
    def control(self):
        def change_position(target_position):
            self.target_position = target_position

        return interact(change_position, target_position=(-150.0, 150.0, 1.0))
