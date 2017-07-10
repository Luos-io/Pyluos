import os

from subprocess import Popen

from serial.tools.list_ports import comports

white_list = {
    # Add here the USB gates you want to automatically be used
    # name: serial-port
    'my_usb_gate1': '/dev/cu.usbmodem3203731',
}


def discover():
    gates = [p.device for p in comports()]
    return {
        alias: port

        for (alias, port) in white_list.items()
        if port in gates
    }


def redirect_to_ws(serial_port, ws_port):
    base_path = os.path.dirname(__file__)

    return Popen(['python', os.path.join(base_path, 'usb2ws.py'),
                  '--serial-port', serial_port,
                  '--ws-port', str(ws_port)])


def main():
    import time
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', choices=('discover', ))
    args = parser.parse_args()

    if args.cmd == 'discover':
        while True:
            print(discover())
            time.sleep(1.0)


if __name__ == '__main__':
    main()
