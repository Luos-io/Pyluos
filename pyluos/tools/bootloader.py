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
BOOTLOADER_IDLE = 0
BOOTLOADER_START = 1
BOOTLOADER_STOP = 2
BOOTLOADER_READY = 3
BOOTLOADER_ERASE = 4
BOOTLOADER_BIN_CHUNK = 5
BOOTLOADER_BIN_END = 6
BOOTLOADER_CRC_TEST = 7
BOOTLOADER_READY_RESP = 16
BOOTLOADER_BIN_HEADER_RESP = 17
BOOTLOADER_ERASE_RESP = 18
BOOTLOADER_BIN_CHUNK_RESP = 19
BOOTLOADER_BIN_END_RESP = 20
BOOTLOADER_CRC_RESP = 21
BOOTLOADER_ERROR_SIZE = 32

RESP_TIMEOUT = 3
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

# *******************************************************************************
# @brief send commands
# @param command type
# @return None
# *******************************************************************************
def send_command(device, node, command, size = 0):
    # create a json file with the list of the nodes to program
    bootloader_cmd = {
        'bootloader': {
            'command': {
                'type': command,
                'node': node,
                'size': size
            },
        }
    }
    # send json command
    device._send(bootloader_cmd)

# *******************************************************************************
# @brief send erase command
# @param command type
# @return None
# *******************************************************************************
def send_ready_cmd(device, node):
    return_value = True

    # send ready command to the node
    send_command(device, node, BOOTLOADER_READY, get_binary_size())

    # wait ready response
    state = device._poll_once()
    init_time = time.time()
    while ('bootloader' not in state):
        state = device._poll_once()
        if(time.time() - init_time > RESP_TIMEOUT):
            print("  ╰> Node n°", node, "is not responding.")
            print("  ╰> Loading program aborted, please reboot the system.")
            return_value = False
            break
    if (state['bootloader']['response'] == BOOTLOADER_ERROR_SIZE):
        print("  ╰> Node n°", node, "has not enough space in flash memory.")
        # don't load binary if there is not enough place in flash memory
        return_value = False
    if (state['bootloader']['response'] == BOOTLOADER_READY_RESP):
        print("  ╰> Node n°", node, "is ready.")

    return return_value
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

    # state used to check each step
    machine_state = True

    # init device
    device = Device(args.port, background_task=False)

    # find routing table
    state = find_network(device)

    # searching nodes to program in network
    (nodes_to_reboot, nodes_to_program) = create_target_list(args, state)

    # reboot all nodes in bootloader mode
    print("** Reboot all nodes in bootloader mode **")
    for node in nodes_to_reboot:
        send_command(device, node, BOOTLOADER_START)
        # delay to let gate send commands
        time.sleep(0.01)

    # wait before next step
    time.sleep(0.1)
    # program nodes
    for node in nodes_to_program:
        print("** Programming node n°", node, "**")

        # go to header state if node is ready
        print("--> Check if node n°", node, "is ready.")
        machine_state = send_ready_cmd(device, node)
        if( machine_state != True):
            break
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
