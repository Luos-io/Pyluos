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
        print("Search a Gate on port " + str(serial_host))
        try:
            port = serial.Serial(serial_host, baudrate, timeout=0.2)
            time.sleep(0.1)
        except:
            continue

        if port is not None:
            s = b'{}'
            port.write(b'\x7E' + struct.pack('<H', len(s)) + s + b'\x81')
            time.sleep(0.01)
            port.readline()
            port.flush()
            time.sleep(0.01)
            s = b'{\"discover\": {}}'
            port.write(b'\x7E' + struct.pack('<H', len(s)) + s + b'\x81')
            state = port.readline()
            gateResponse = False
            if 'gate'.encode() in state:
                gateResponse = True
            elif len(state):
                # if many other messages are received, drop them and retry reception
                for read_retry in range(1000):
                    state = port.readline()
                    if 'gate'.encode() in state:
                        gateResponse = True
                        break
            if gateResponse:
                available_serial.append(serial_host)
            port.reset_output_buffer()
            port.close()

    if available_serial :
        return available_serial
    else:
        print("... No gate detected")
        return []

def main():
    parser = argparse.ArgumentParser()
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
