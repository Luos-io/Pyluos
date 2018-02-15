from __future__ import division

import json
import time
import serial as _serial

from threading import Event, Thread

from serial.tools.list_ports import comports

from . import IOHandler

black_list = [
    '/dev/cu.Bluetooth-Incoming-Port'
]


class Serial(IOHandler):
    poll_frequency = 100

    @classmethod
    def available_hosts(cls):
        return list(p.device for p in comports()
                    if p.device not in black_list)

    @classmethod
    def is_host_compatible(cls, host):
        return host in cls.available_hosts()

    def __init__(self, host, baudrate=57600):
        self._serial = _serial.Serial(host, baudrate)
        self._serial.flush()

        self._msg = None
        self._msg_ready = Event()
        self._running = True

        self._poll_loop = Thread(target=self._poll)
        self._poll_loop.daemon = True
        self._poll_loop.start()

    def is_ready(self):
        if self._serial.in_waiting == 0:
            return False

        try:
            self.read()
            return True
        except (UnicodeDecodeError, json.decoder.JSONDecodeError):
            return False

    def recv(self):
        self._msg_ready.wait()
        self._msg_ready.clear()
        return self._msg

    def write(self, data):
        self._serial.write(data + '\r'.encode())

    def close(self):
        self._running = False
        self._poll_loop.join()

        self._serial.close()

    def _poll(self):
        def extract_last_line(s):
            j = s.rfind(b'\n')

            if j == -1:
                return b'', s

            i = s[:j].rfind(b'\n') + 1
            return s[i:j], s[j + 1:]

        period = 1 / self.poll_frequency
        buff = b''

        while self._running:
            to_read = self._serial.in_waiting

            if to_read == 0:
                time.sleep(period)
                continue

            s = self._serial.read(to_read)
            line, buff = extract_last_line(buff + s)
            if len(line):
                self._msg = line
                self._msg_ready.set()
