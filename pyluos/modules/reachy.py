from .module import Module, interact

import numpy as np

from collections import defaultdict


class ReachyArm(Module):
    def __init__(self, id, alias, device):
        Module.__init__(self, 'ReachyArm', id, alias, device)

        # print(device.modules)
        if (alias == 'right_arm'):
            self.ids = [10, 11, 12, 13, 14, 15, 16, 17]

        elif (alias == 'left_arm'):
            self.ids = [20, 21, 22, 23, 24, 25, 26, 27]

        self.device = device

    def _update(self, new_state):
        Module._update(self, new_state)

        if 'rot_position' in new_state:
            for id, p in zip(self.ids, new_state['rot_position']):
                try:
                    getattr(self.device, f'dxl_{id}').rot_position = p
                except AttributeError:
                    pass

        if 'temperature' in new_state:
            for id, t in zip(self.ids, new_state['temperature']):
                try:
                    getattr(self.device, f'dxl_{id}').temperature = t
                except AttributeError:
                    pass


class FakeStateMod(object):
    def __init__(self, delegate, index):
        self._state = False
        self._delegate = delegate
        self._index = index

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self._delegate._set_fan(self._state, self._index)


class ReachyFan(Module):
    def __init__(self, id, alias, device):
        Module.__init__(self, 'ReachyFan', id, alias, device)

        setattr(device, 'shoulder_fan', FakeStateMod(self, 0))
        setattr(device, 'elbow_fan', FakeStateMod(self, 1))
        setattr(device, 'wrist_fan', FakeStateMod(self, 2))

        self._fans = [0, 0, 0]

    def _set_fan(self, state, index):
        self._fans[index] = 1 if state else 0
        self._push_value('color', self._fans)
