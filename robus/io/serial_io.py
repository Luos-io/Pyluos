import serial as _serial

from serial.tools.list_ports import comports

from . import IOHandler


class Serial(IOHandler):
    @classmethod
    def is_host_compatible(cls, host):
        available_host = (p.device for p in comports())
        return host in available_host

    def __init__(self, host, baudrate):
        self._serial = _serial.Serial(host, baudrate)

    def recv(self):
        return self._serial.readline()

    def write(self, data):
        self._serial.write(data + '\r'.encode())
