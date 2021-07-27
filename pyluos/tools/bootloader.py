#
# LUOS CLI tool

# *******************************************************************************
# Import packages
# *******************************************************************************
import argparse
import sys
import time
from multiprocessing import Process, Value
import json
from pyluos import Device
import numpy as np
import math
import crc8

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

FILEPATH = None
NB_SAMPLE_BY_FRAME_MAX = 127

RESP_TIMEOUT = 3
ERASE_TIMEOUT = 10
PROGRAM_TIMEOUT = 5
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
        # bypass if node contains a Gate service
        # prevent programmation of a Gate
        for service in node['services']:
            bypass_node = False
            if(service['type'] == 'Gate'):
                bypass_node = True
                break
            if(service['alias'] == 'Pipe_mod'):
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
# @brief get binary size
# @param
# @return binary size
# *******************************************************************************
def get_binary_size():
    # get number of bytes in binary file
    with open(FILEPATH, mode="rb") as f:
        nb_bytes = len(f.read())

    return nb_bytes

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
# *******************************************************************************
# @brief waiting for erase response
# @param
# @return binary size
# *******************************************************************************
def waiting_erase():
    init_time = time.time()
    count = 0
    period = 0.4
    print("\r                        ", end='')
    print("\r  ╰> Erase flash        ", end='')
    while(1):
        if(time.time() - init_time > period):
            init_time = time.time()
            if(count == 0):
                print("\r                        ", end='')
                print("\r  ╰> Erase flash .      ", end='')
                count += 1
                continue
            if(count == 1):
                print("\r                        ", end='')
                print("\r  ╰> Erase flash ..     ", end='')
                count += 1
                continue
            if(count == 2):
                print("\r                        ", end='')
                print("\r  ╰> Erase flash ...    ", end='')
                count += 1
                continue
            if(count == 3):
                print("\r                        ", end='')
                print("\r  ╰> Erase flash        ", end='')
                count = 0
                continue

# *******************************************************************************
# @brief send erase command
# @param command type
# @return None
# *******************************************************************************
def erase_flash(device, node):
    return_value = True

    # send erase command
    send_command(device, node, BOOTLOADER_ERASE)

    # display a progress bar
    waiting_bg = Process(target=waiting_erase)
    waiting_bg.start()

    # wait ready response
    state = device._poll_once()
    init_time = time.time()
    while ('bootloader' not in state):
        state = device._poll_once()
        if(time.time() - init_time > ERASE_TIMEOUT):
            print("  ╰> Node n°", node, "is not responding.")
            print("  ╰> Loading program aborted, please reboot the system.")
            return_value = False
            break
    if (state['bootloader']['response'] == BOOTLOADER_ERASE_RESP):
        waiting_bg.terminate()
        print("\r\n  ╰> Flash memory erased.")

    return return_value

# *******************************************************************************
# @brief get binary size
# @param
# @return binary size
# *******************************************************************************
def loading_bar(loading_progress):
    init_time = time.time()
    period = 0.2
    while(1):
        if(time.time() - init_time > period):
            init_time = time.time()
            print("\r  ╰> loading : {} %".format(loading_progress.value), end='')

# *******************************************************************************
# @brief send the binary file to the node
# @param command type
# @return None
# *******************************************************************************
def send_binary_data(device, node):
    loading_state = True
    # compute total number of bytes to send
    with open(FILEPATH, mode="rb") as f:
        nb_bytes = len(f.read())
    # compute total number of frames to send
    nb_frames = math.ceil(nb_bytes / NB_SAMPLE_BY_FRAME_MAX)

    # display a progress bar to inform user
    loading_progress = Value('f', 0.0)
    loading_bar_bg = Process(target=loading_bar, args=(loading_progress,))
    loading_bar_bg.start()

    # send each frame to the network
    file_offset = 0
    for frame_index in range(nb_frames):
        if (frame_index == (nb_frames-1)):
            # last frame, compute size
            frame_size = nb_bytes - (nb_frames-1)*NB_SAMPLE_BY_FRAME_MAX
        else:
            frame_size = NB_SAMPLE_BY_FRAME_MAX

        # send the current frame
        loading_state = send_frame_from_binary(device, node, frame_size, file_offset)
        if( loading_state != True):
            break
        # update cursor position in the binary file
        file_offset += frame_size
        # update loading progress
        loading_progress.value = math.trunc(frame_index / nb_frames * 100)

    # kill the progress bar at the end of the loading
    loading_bar_bg.terminate()
    if( loading_state == True):
        print("\r  ╰> loading : 100.0 %")

    return loading_state

# *******************************************************************************
# @brief open binary file and send a frame
# @param
# @return None
# *******************************************************************************
def send_frame_from_binary(device, node, frame_size, file_offset):
    return_value = True

    with open(FILEPATH, mode="rb") as f:
        # put the cursor at the beginning of the file
        f.seek(file_offset)
        # read binary data
        data_bytes = f.read(1)
        for sample in range(frame_size):
            data_bytes = data_bytes + f.read(1)

    send_data(device, node, BOOTLOADER_BIN_CHUNK, frame_size, data_bytes)

    # wait node response
    lock = 1
    state = device._poll_once()
    init_time = time.time()
    while (lock):
        if(time.time() - init_time > PROGRAM_TIMEOUT):
            print("\r\n  ╰> Node n°", node, "is not responding.")
            print("  ╰> Loading program aborted, please reboot the system.")
            return_value = False
            break
        if 'bootloader' in state:
            if (state['bootloader']['response'] == BOOTLOADER_BIN_CHUNK_RESP):
                lock = 0
        state = device._poll_once()

    return return_value

# *******************************************************************************
# @brief send binary data with a header
# @param
# @return None
# *******************************************************************************
def send_data(device, node, command, size, data):
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
    device._write(json.dumps(bootloader_cmd).encode() + '\r'.encode() + data)

# *******************************************************************************
# @brief send the binary end command
# @param
# @return
# *******************************************************************************
def send_binary_end(device, node):
    return_value = True

    # send command
    send_command(device, node, BOOTLOADER_BIN_END)
    # wait bin_end response
    state = device._poll_once()
    init_time = time.time()
    while ('bootloader' not in state):
        state = device._poll_once()
        if(time.time() - init_time > RESP_TIMEOUT):
            print("  ╰> Node n°", node, "is not responding.")
            print("  ╰> Loading program aborted, please reboot the system.")
            return_value = False
            break
    if (state['bootloader']['response'] == BOOTLOADER_BIN_END_RESP):
        print("  ╰> Node acknowledge received, loading is complete.")

    return return_value

# *******************************************************************************
# @brief compute binary crc
# @param
# @return None
# *******************************************************************************
def compute_crc():
    # create crc8 function object
    hash = crc8.crc8()
    # get number of bytes in binary file
    with open(FILEPATH, mode="rb") as f:
        nb_bytes = len(f.read())

    with open(FILEPATH, mode="rb") as f:
        for bytes in range(nb_bytes):
            data = f.read(1)
            hash.update(data)
            crc = hash.digest()

    return crc

# *******************************************************************************
# @brief send the binary end command
# @param
# @return
# *******************************************************************************
def check_crc(device, node):
    return_value = True

    # send crc command
    send_command(device, node, BOOTLOADER_CRC_TEST)
    # wait bin_end response
    state = device._poll_once()
    init_time = time.time()
    while ('bootloader' not in state):
        state = device._poll_once()
        if(time.time() - init_time > RESP_TIMEOUT):
            print("  ╰> Node n°", node, "is not responding.")
            print("  ╰> Loading program aborted, please reboot the system.")
            return_value = False
            break
    if (state['bootloader']['response'] == BOOTLOADER_CRC_RESP):
        source_crc = int.from_bytes(compute_crc(), byteorder='big')
        node_crc = state['bootloader']['crc_value']
        if ( source_crc == node_crc ):
            print("  ╰> CRC test : OK.")
        else:
            print("  ╰> CRC test : NOK.")
            print("  ╰> waited :", hex(source_crc), ", received :", hex(node_crc))
            return_value = False
    else:
        print("  ╰> CRC note received.")
        return_value = False

    return return_value

# *******************************************************************************
# @brief reboot all nodes in application mode
# @param
# @return
# *******************************************************************************
def reboot_network(device, nodes_to_reboot):
    for node in nodes_to_reboot:
                send_command(device, node, BOOTLOADER_STOP)
                # delay to let gate send commands
                time.sleep(0.01)
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

    if not (args.port):
        print('Please specify a port to access the network.')
        sys.exit()

    # state used to check each step
    machine_state = True

    # update firmware path
    global FILEPATH
    FILEPATH = args.binary
    try:
        f = open(FILEPATH, mode="rb")
    except IOError:
        print("Cannot open :", FILEPATH)
        sys.exit()
    else:
        f.close()

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

        # erase node flash memory
        print("--> Erase flash memory.")
        machine_state = erase_flash(device, node)
        if( machine_state != True):
            break

        # send binary data
        print("--> Send binary data.")
        machine_state = send_binary_data(device, node)
        if( machine_state != True):
            break

        # inform the node of the end of the loading
        print("--> Programmation finished, waiting for acknowledge.")
        machine_state = send_binary_end(device, node)
        if( machine_state != True):
            break

        # Ask the node to send binary crc
        print("--> Check binary CRC.")
        machine_state = check_crc(device, node)
        if( machine_state != True):
            break

    # wait before next step
    time.sleep(0.1)

    # reboot all nodes in application mode
    if (machine_state == True):
        print("** Reboot all nodes in application mode **")
        reboot_network(device, nodes_to_reboot)


# *******************************************************************************
# @brief command used to detect network
# @param detect function arguments : -p
# @return None
# *******************************************************************************
def luos_detect(args):
    print('Luos detect subcommand on port : ', args.port)

    if not (args.port):
        print('Please specify a port to access the network.')
        sys.exit()

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
    flash_parser.add_argument('port', help='port used to detect network')
    flash_parser.add_argument('-g', '--gate',
                              help='id of the gate used to access the luos network')
    flash_parser.add_argument('-b', '--binary',
                              help='path to the binary file to flash')
    flash_parser.add_argument('-t', '--target',
                              help='target node to flash',
                              default=['2'],
                              nargs='*')
    flash_parser.set_defaults(func=luos_flash)

    # declare "detect" subcommand
    detect_parser = subparsers.add_parser('detect',
                                          help='tool to detect luos network')
    detect_parser.add_argument('port', help='port used to detect network')
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
