#
# LUOS CLI tool

# *******************************************************************************
# Import packages
# *******************************************************************************
import argparse
import sys
from pyluos import Device

# *******************************************************************************
# Global Variables
# *******************************************************************************
# *******************************************************************************
# Function
# *******************************************************************************

# *******************************************************************************
# @brief command used to flash luos nodes
# @param flash function arguments : -g, -t, -b
# @return None
# *******************************************************************************
def luos_flash(args):
    print('Luos flash subcommand with parameters :')
    print('\t--gate : ', args.gate)
    print('\t--target : ', args.target)
    print('\t--binary : ', args.binary)
    print('\t--port : ', args.port)

# *******************************************************************************
# @brief command used to detect network
# @param detect function arguments : -p
# @return None
# *******************************************************************************
def luos_detect(args):
    print('Luos detect subcommand on port : ', args.port)

    # detect network
    device = Device(args.port)

    # print network to user
    print(device.nodes)

# *******************************************************************************
# @brief command used to detect network
# @param detect function arguments : -p
# @return None
# *******************************************************************************
def luos_options():
    parser = argparse.ArgumentParser(
        description='Luos command line interface')

    # create subcommands
    subparsers = parser.add_subparsers()

    # declare "flash" subcommand
    flash_parser = subparsers.add_parser('flash',
                                         help='tool to program luos nodes')
    flash_parser.add_argument('-g', '--gate',
                              help='id of the gate used to access the luos network')
    flash_parser.add_argument('-b', '--binary',
                              help='path to the binary file to flash')
    flash_parser.add_argument('-t', '--target',
                              help='target node to flash',
                              default=['2'],
                              nargs='*')
    flash_parser.add_argument('-p', '--port',
                              help='serial port used to detect network',
                              default='COM3')
    flash_parser.set_defaults(func=luos_flash)

    # declare "detect" subcommand
    detect_parser = subparsers.add_parser('detect',
                                          help='tool to detect luos network')
    detect_parser.add_argument('-p', '--port',
                               help='serial port used to detect network',
                               default='COM3')
    detect_parser.set_defaults(func=luos_detect)

    return parser

# *******************************************************************************
# @brief parse arguments and launch subcommand function
# @param None
# @return None
# *******************************************************************************
def main():
    # declare options of the CLI
    parser = luos_options()

    # parse options
    args = parser.parse_args()

    # execute CLI subcommand
    args.func(args)

    return 0


if __name__ == '__main__':
    sys.exit(main())
