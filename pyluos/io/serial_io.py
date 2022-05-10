from __future__ import division

import json
import time
import serial as _serial
import platform
import sys
import struct
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
    poll_frequency = 200

    @classmethod
    def available_hosts(cls):
        devices = comports(include_links=True)

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
        try:
            data = self._msg.get(True, 1)
        except queue.Empty:
            data = None
        return data

    def write(self, data):
        self._serial.write(b'\x7E' + struct.pack('<H', len(data)) + data + b'\x81')

    def close(self):
        self._running = False
        self._poll_loop.join()

        self._serial.close()

    def _poll(self):
        def extract_line(s):
            # Find a serial header
            H = s.find(b'\x7E')
            if H == -1:
                # No header found
                return b'', s[0:0]
            else:
                # Header found, get size
                try:
                    size = struct.unpack('<H', s[H+1:H+3])[0]
                except:
                    # size not completely received
                    return b'', s[H:]
                if (size == 0) or (size > 20000):
                    # Bad header
                    # Remove the header and do it again
                    return extract_line(s[H+1:])
                else:
                    # Size seems ok
                    # Check if we receive the entire data
                    if len(s[H+3:]) < size+1:
                        # We don't have the entire data
                        return b'', s
                    else:
                        # We have the complete data
                        # Check the footer
                        data_start = H+3
                        data_end = data_start + size
                        if (s[data_end] != ord(b'\x81')):
                            # The footer is not ok, this mean we don't have a good header
                            # Remove the header and do it again
                            return extract_line(s[H+1:])
                        else:
                            # Footer is ok
                            return s[data_start:data_end], s[data_end + 1:]

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
