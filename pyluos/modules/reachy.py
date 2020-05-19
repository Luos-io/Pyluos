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
