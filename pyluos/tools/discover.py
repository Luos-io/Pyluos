import os
import time

from ..io.serial_io import Serial
import serial
import struct
import argparse

def serial_ports():
    return Serial.available_hosts()

def serial_discover(baudrate=1000000):
    serial_hosts = serial_ports()
    available_serial = []
    print("Searching for a gate available")
    for serial_host in serial_hosts:
        print("Testing " + str(serial_host))
        try:
            port = serial.Serial(serial_host, baudrate, timeout=0.05)
        except:
            continue

        s = b'{}'
        port.write(b'\x7E' + struct.pack('<H', len(s)) + s + b'\x81')
        time.sleep(0.01)
        s = b'{\"discover\": {}}'
        port.write(b'\x7E' + struct.pack('<H', len(s)) + s + b'\x81')
        port.flush()
        for x in range(10):
            state = port.readline()
            if ('gate'.encode() in state):
                available_serial.append(serial_host)
                continue

        port.close()
    return available_serial

def main():
    parser.add_argument("--baudrate", action="store",
                        help="Choose pyluos serial baudrate default value = 1000000",
                        default=1000000)

    args = parser.parse_args()

    gate_list = serial_discover(os.getenv('LUOS_BAUDRATE', args.baudrate))

    if gate_list:
        print("Available Luos gate on port : " + str(gate_list))
    else:
        print("No gate detected")


if __name__ == '__main__':
    main()
