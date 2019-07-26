from __future__ import division

import json
import time
import serial as _serial
import platform
import sys
if sys.version_info >= (3, 0):
    import queue
else:
    import Queue as queue


from threading import Event, Thread

from serial.tools.list_ports import comports

from . import IOHandler

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError

class Serial(IOHandler):
    poll_frequency = 100

    @classmethod
    def available_hosts(cls):
        devices = comports()

        return [d.device for d in devices]

    @classmethod
    def is_host_compatible(cls, host):
        return host in cls.available_hosts()

    def __init__(self, host, baudrate=1000000):
        self._serial = _serial.Serial(host, baudrate)
        self._serial.flush()

        self._msg = queue.Queue(100)
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
        except (UnicodeDecodeError, JSONDecodeError):
            return False

    def recv(self):
        return self._msg.get()

    def write(self, data):
        self._serial.write(data + '\r'.encode())

    def close(self):
        self._running = False
        self._poll_loop.join()

        self._serial.close()

    def _poll(self):
        def extract_line(s):
            j = s.find(b'\n')
            if j == -1:
                return b'', s
            # Sometimes the begin of serial data can be wrong remove it
            # Find the first '{'

            x = s.find(b'{')
            if x == -1:
                return b'', s[j + 1:]

            return s[x:j], s[j + 1:]

        period = 1 / self.poll_frequency
        buff = b''

        while self._running:
            to_read = self._serial.in_waiting

            if to_read == 0:
                time.sleep(period)
                continue

            s = self._serial.read(to_read)
            buff = buff + s

            while self._running:
                line, buff = extract_line(buff)
                if not len(line):
                    break
                if self._msg.full():
                    self._msg.get()
                self._msg.put(line)
