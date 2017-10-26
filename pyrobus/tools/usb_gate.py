import os

from subprocess import Popen

from ..io.serial_io import Serial


def discover():
    return Serial.available_hosts()


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
