import math
import time

from .robot import Robot


class Finger(object):
    def __init__(self, m):
        self._m = m
        self._flex = None

    @property
    def flex(self):
        return self._flex

    @flex.setter
    def flex(self, val):
        self._flex = val
        val = min(max(val, 0), 100)
        val = val * 1.65
        self._m.target_position = int(val)


class Handy(object):
    def __init__(self, host=None):
        if host is None:
            hosts = Robot.discover()['handy']
            if len(hosts) != 1:
                raise IOError('Handy not found! {}'.format(hosts))
            host = hosts[0]

        self._robot = Robot(host)

        self.index = Finger(self._robot.handy.m1)
        self.middle_finger = Finger(self._robot.handy.m2)
        self.ring_finger = Finger(self._robot.handy.m3)
        self.pinky = Finger(self._robot.handy.m4)
        self.thumb = Finger(self._robot.handy.m5)

        self.fingers = [
            self.thumb,
            self.index,
            self.middle_finger,
            self.ring_finger,
            self.pinky,
        ]

    def sync_wave(self):
        t0 = time.time()

        while True:
            t = time.time() - t0
            target = 50 + 50 * math.sin(1 * t)

            for f in self.fingers:
                f.flex = target

    def wave(self):
        while True:
            t = time.time()
            for i, f in enumerate(self.fingers):
                f.flex = 50 + 50 * math.sin(1 * t + i * math.pi / 5)
