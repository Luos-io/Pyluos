from .service import Service


class Load(Service):
    possible_events = {'changed', 'filter_changed'}
    threshold = 10

    def __init__(self, id, alias, device):
        Service.__init__(self, 'Load', id, alias, device)
        self._load = 0.0
        self._offset = 0.0
        self._scale = 1.0

    @property
    def load(self):
        """ force """
        return self._load

    def tare(self):
        # measure and offset
        self._push_value("reinit", None)
        time.sleep(1.0)

    @property
    def offset(self):
            return self._offset

    @offset.setter
    def offset(self, value):
            self._offset = value
            self._push_value("offset",value)

    @property
    def scale(self):
            return self._scale

    @scale.setter
    def scale(self, value):
            self._scale = value
            self._push_value("resolution",value)

    def _update(self, new_state):
        Service._update(self, new_state)
        if 'force' in new_state:
            new_force = new_state['force']
            if new_force != self._value:
                self._pub_event('changed', self._value, new_force)
                if abs(new_force - self._load) > self.threshold:
                    self._pub_event('filter_changed',
                                    self._value, new_force)

                self._load = new_force

    def control(self):
        def change_config(offset, scale):
            # report config
            self.offset = offset
            self.scale = scale

        w = interact(change_config,
                    offset = self.offset,
                    scale = self.scale)
