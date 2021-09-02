import os
import time

from ..io.serial_io import Serial
import serial

def serial_ports():
    return Serial.available_hosts()

def serial_discover():
    serial_hosts = serial_ports()
    available_serial = []
    print("Searching for a gate available")
    for serial_host in serial_hosts:
        print("Testing " + str(serial_host))
        try:
            port = serial.Serial(serial_host, 1000000, timeout=0.05)
        except:
            continue
        port.write("{\"discover\": {}}\r".encode())
        port.flush()
        for x in range(10):
            state = port.readline()
            if ('gate'.encode() in state):
                available_serial.append(serial_host)
                continue

        port.close()
    return available_serial

def main():
    gate_list = serial_discover()

    if gate_list:
        print("Available Luos gate on port : " + str(gate_list))
    else:
        print("No gate detected")


if __name__ == '__main__':
    main()
