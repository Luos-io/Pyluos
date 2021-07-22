#
# LUOS CLI tool

# *******************************************************************************
# Import packages
# *******************************************************************************
import argparse
import sys
import time
from pyluos import Device

# *******************************************************************************
# Global Variables
# *******************************************************************************
# *******************************************************************************
# Function
# *******************************************************************************

# *******************************************************************************
# @brief find routing table
# @param port connected to the luos gate
# @return an object containing routing table
# *******************************************************************************
def find_network(device):
    device._send({'detection': {}})
    startTime = time.time()
    state = device._poll_once()
    while ('routing_table' not in state):
        if ('route_table' in state):
            print('version of luos not supported')
            return
        state = device._poll_once()
        if (time.time()-startTime > 1):
            device._send({'detection': {}})
            startTime = time.time()

    return state

# *******************************************************************************
# @brief find nodes to program in the network
# @param target list, routing table
# @return a tuple with 2 lists : nodes to reboot and nodes to program
# *******************************************************************************
def create_target_list(args, state):
    bypass_node = False
    nodes_to_program = []
    nodes_to_reboot = []
    for node in state['routing_table']:
        # bypass if node contains a Gate container
        # prevent programmation of a Gate
        for container in node['containers']:
            bypass_node = False
            if(container['type'] == 'Gate'):
                bypass_node = True
                break
            if(container['alias'] == 'Pipe_mod'):
                bypass_node = True
        # check if node is in target list
        if not (bypass_node):
            nodes_to_reboot.append(node['node_id'])
            for target in args.target:
                if(int(node['node_id']) == int(target)):
                    nodes_to_program.append(node['node_id'])

    return (nodes_to_reboot, nodes_to_program)

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


    # init device
    device = Device(args.port, background_task=False)

    # find routing table
    state = find_network(device)

    # searching nodes to program in network
    (nodes_to_reboot, nodes_to_program) = create_target_list(args, state)

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
