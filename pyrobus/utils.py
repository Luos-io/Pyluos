from __future__ import division

from threading import Thread
from time import time, sleep
from math import sin, pi


class Sinus(object):
    update_frequency = 25.0

    def __init__(self, motor, frequency, amplitude, offset, phase):
        self.motor = motor

        self.frequency = frequency
        self.amplitude = amplitude
        self.offset = offset
        self.phase = phase

        self._running = False
        self._t = None

    def start(self):
        if self._t is not None:
            raise EnvironmentError('Sinus already running!')

        self._running = True
        self._t = Thread(target=self._run)
        self._t.start()

    def stop(self):
        self._running = False
        if self._t is not None:
            self._t.join()
            self._t = None

    def _run(self):
        t0 = time()

        while self._running:
            t = time() - t0
            pos = self.amplitude * sin(2 * pi * self.frequency * t + (self.phase * pi / 180)) + self.offset

            self.motor.target_position = pos
            sleep(1 / self.update_frequency)
