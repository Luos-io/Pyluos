"""
Pyluos command line utility

"""

from __future__ import print_function
import sys

import sys
import os
import argparse
from IPython import embed

import pyluos
from pyluos import Device
from pyluos.tools.discover import serial_discover


# *******************************************************************************
# @brief parse arguments and launch subcommand function
# @param None
# @return None
# *******************************************************************************
def main():

    ## Parse arguments ##
    parser = argparse.ArgumentParser(description='Luos command line utility based on pyluos\n',
                                     formatter_class=argparse.RawTextHelpFormatter)

    # General arguments
    parser.add_argument("-p", "--port", metavar="PORT", action="store",
                        help="The port where a Luos device should be discovered.\n"
                        "This can be a serial interface or an IP adress.\n"
                        "For example to specify a serial port : luostool --port \"cu.usbserial-DN2YEFLN\"",
                        default=None)

    parser.add_argument("--version", action="store_true",
                        help="print version information and exit")

    parser.add_argument("--baudrate", action="store",
                        help="Choose pyluos serial baudrate default value = 1000000",
                        default=1000000)

    args = parser.parse_args()

    def print_version():
        from pyluos.version import version
        sys.stderr.write("luos control utility v" + version + "\n")
        sys.stderr.flush()
        return 0

    try:
        if args.version == True:
            print_version()

        if args.port is not None:
            # Ready to rocks
            device = Device(args.port, baudrate=os.getenv('LUOS_BAUDRATE', args.baudrate))
            embed(banner1 = "\n Hit Ctrl-D to exit this interpreter.\n\nYour luos device has been successfully mounted into a \"device\" object:\n" + str(device.nodes) + "\n")
        else:
            Gates = serial_discover(os.getenv('LUOS_BAUDRATE', args.baudrate))
            if Gates:
                device = Device(Gates[0], baudrate=os.getenv('LUOS_BAUDRATE', args.baudrate))
                embed(banner1 = "\n Hit Ctrl-D to exit this interpreter.\n\nYour luos device has been successfully mounted into a \"device\" object:\n" + str(device.nodes) + "\n")

    except OperationAbortedException:
        logger.info("Operation aborted.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
