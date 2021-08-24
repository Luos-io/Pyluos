from .service import Service


class Unknown(Service):
    possible_events = {'changed', 'pressed', 'released'}

    # control modes
    _PLAY = 0
    _PAUSE = 1
    _STOP = 2
    _REC = 4

    def __init__(self, id, alias, device):
        Service.__init__(self, 'Unknown', id, alias, device)
        self._control = 0
        self._state = False
        self._angular_position = 0.0
        self._angular_speed = 0.0
        self._trans_position = 0.0
        self._trans_speed = 0.0
        self._current = 0.0
        self._temperature = 0.0
        self._color = [0, 0, 0]
        self._time = 0.0
        self._parameters = 0
        self._pid = [0, 0, 0]
        self._power_ratio = 0.0
        self._lux = 0.0
        self._load = 0.0
        self._volt = 0.0

    def _update(self, new_state):
        Service._update(self, new_state)
        if 'io_state' in new_state:
            val = new_state['io_state']
            if val != self._state:
                self._pub_event('changed', self._state, val)

                evt = 'pressed' if val == True else 'released'
                self._pub_event(evt, self._state, val)

                self._state = val
        if 'rot_position' in new_state:
            self._angular_position = new_state['rot_position']
        if 'rot_speed' in new_state:
            self._angular_speed = new_state['rot_speed']
        if 'trans_position' in new_state:
            self._trans_position = new_state['trans_position']
        if 'trans_speed' in new_state:
            self._trans_speed = new_state['trans_speed']
        if 'current' in new_state:
            self._current = new_state['current']
        if 'temperature' in new_state:
            self._temperature = new_state['temperature']
        if 'lux' in new_state:
            self._lux = new_state['lux']
        if 'force' in new_state:
            self._load = new_state['force']
        if 'volt' in new_state:
            self._volt = new_state['volt']



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
    def state(self):
        return self._state == True

    @state.setter
    def state(self, new_val):
        self._state = new_val
        self._push_value('io_state', new_val)

    @property
    def angular_position(self):
        """ Position in degrees. """
        return self._angular_position

    @angular_position.setter
    def angular_position(self, new_val):
        self._angular_position == new_val
        self._push_value('target_rot_position', new_val)

    @property
    def angular_speed(self):
        return self._angular_speed

    @angular_speed.setter
    def angular_speed(self, s):
        self._angular_speed = s
        self._push_value("target_rot_speed", s)

    @property
    def translation_position(self):
        """ Position in degrees. """
        return self._trans_position

    @translation_position.setter
    def translation_position(self, new_val):
        self._trans_position == new_val
        self._push_value('target_trans_position', new_val)

    @property
    def translation_speed(self):
        return self._angular_speed

    @angular_speed.setter
    def translation_speed(self, s):
        self._angular_speed = s
        self._push_value("target_rot_speed", s)

    @property
    def current(self):
        return self._current

     # temperature
    @property
    def temperature(self):
        return self._temperature

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, new_color):
        new_color = [int(min(max(c, 0), 255)) for c in new_color]
        if len(new_color) > 3 :
            self._color = new_color
            self._push_data('color', [len(new_color)], np.array(new_color, dtype=np.uint8))
        else :
            self._color = new_color
            self._push_value('color', new_color)
    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, new_time):
        self._time = new_time
        self._push_value('time', new_time)

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, new_val):
        self._parameters = new_val
        self._push_value('parameters', new_val)

    def reinit(self):
        self._push_value('reinit', None)

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, new_pid):
        self._pid = new_pid
        self._push_value('pid', new_pid)

    @property
    def power_ratio(self):
        self._power_ratio

    @power_ratio.setter
    def power_ratio(self, s):
        s = min(max(s, -100.0), 100.0)
        self._power_ratio = s
        self._push_value("power_ratio",s)

    @property
    def lux(self):
        """ Light in lux. """
        return self._lux

    @property
    def load(self):
        """ force """
        return self._load

    @property
    def volt(self):
        """ Voltage in volt. """
        return self._volt

    @volt.setter
    def volt(self, new_val):
        self._volt = new_val
        self._push_value('volt', new_val)
