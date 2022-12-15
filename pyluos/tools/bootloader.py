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
from pyluos.tools.discover import serial_discover
import numpy as np
import math
import crc8
import os
from ..io.serial_io import Serial
import serial
import struct

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
BOOTLOADER_APP_SAVED = 8
BOOTLOADER_RESET = 9
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

BOOTLOADER_SUCCESS = 0
BOOTLOADER_DETECT_ERROR = 1
BOOTLOADER_FLASH_ERROR = 2
BOOTLOADER_FLASH_BINARY_ERROR = 3
BOOTLOADER_FLASH_PORT_ERROR = 4
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
    retry = 0
    while ('routing_table' not in state):
        if ('route_table' in state):
            print('version of luos not supported')
            return
        state = device._poll_once()
        if (time.time()-startTime > 1):
            retry = retry +1
            if retry > 5:
                # detection is not working
                sys.exit("Detection failed.")
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
        # prevent programmation of node 1
        bypass_node = False
        if(node['node_id'] == 1):
            bypass_node = True
        # check if node is in target list
        if not (bypass_node):
            nodes_to_reboot.append(node['node_id'])
            for target in args.target:
                if(int(node['node_id']) == int(target)):
                    nodes_to_program.append(node['node_id'])
    for target in args.target:
        if not(int(target) in nodes_to_program):
            print ("**** Node " + target + " is not available and will be ignored. ****")

    return (nodes_to_reboot, nodes_to_program)

# *******************************************************************************
# @brief send commands
# @param command type
# @return None
# *******************************************************************************
def send_topic_command(device, topic, command, size = 0):
    # create a json file with the list of the nodes to program
    bootloader_cmd = {
        'bootloader': {
            'command': {
                'type': command,
                'topic': topic,
                'size': size
            },
        }
    }
    # send json command
    device._send(bootloader_cmd)

def send_node_command(device, node, topic, command, size = 0):
    # create a json file with the list of the nodes to program
    bootloader_cmd = {
        'bootloader': {
            'command': {
                'type': command,
                'node': node,
                'topic': topic,
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
def send_ready_cmd(device, node, topic):
    return_value = True
    # send ready command to the node
    send_node_command(device, node, topic, BOOTLOADER_READY, get_binary_size())
    # wait ready response
    state = device._poll_once()
    init_time = time.time()
    while (time.time() - init_time <= RESP_TIMEOUT):
        if 'bootloader' in state:
            for response in state['bootloader']:
                if response['response'] == BOOTLOADER_ERROR_SIZE:
                    print(u"  ╰> Node n°", response['node'], "has not enough space in flash memory.")
                    # don't load binary if there is not enough place in flash memory
                    return_value = False
                else:
                    print(u"  ╰> Node n°", response['node'], "is ready.")
                    return_value = True
            break

        state = device._poll_once()
        return_value = False

    return return_value
# *******************************************************************************
# @brief waiting for erase response
# @param
# @return binary size
# *******************************************************************************
def waiting_erase():
    count = 0
    period = 0.4
    print("\r                        ", end='')
    print(u"\r  ╰> Erase flash        ", end='')
    while(1):
        time.sleep(period)
        if(count == 0):
            print("\r                        ", end='')
            print(u"\r  ╰> Erase flash .      ", end='')
            count += 1
            continue
        if(count == 1):
            print("\r                        ", end='')
            print(u"\r  ╰> Erase flash ..     ", end='')
            count += 1
            continue
        if(count == 2):
            print("\r                        ", end='')
            print(u"\r  ╰> Erase flash ...    ", end='')
            count += 1
            continue
        if(count == 3):
            print("\r                        ", end='')
            print(u"\r  ╰> Erase flash        ", end='')
            count = 0
            continue

# *******************************************************************************
# @brief send erase command
# @param command type
# @return None
# *******************************************************************************
def erase_flash(device, topic, nodes_to_program):
    return_value = True
    failed_nodes = []
    failed_nodes.extend(nodes_to_program)
    timeout = ERASE_TIMEOUT * len(nodes_to_program)

    # send erase command
    send_topic_command(device, topic, BOOTLOADER_ERASE)

    # display a progress bar
    waiting_bg = Process(target=waiting_erase)
    waiting_bg.start()

    # pull serial data
    state = device._poll_once()
    # initialize the timer that counts until node number * response time
    init_time = time.time()
    # check if all messages are received
    while len(failed_nodes):
        # timeout for exiting loop in case of fails
        if(time.time() - init_time > timeout):
            return_value = False
            break
        # check if it is a response message
        if 'bootloader' in state:  
            for response in state['bootloader']:
                if (response['response'] == BOOTLOADER_ERASE_RESP):
                    # this node responded, delete it from the failed nodes list
                    if response['node'] in failed_nodes:
                        timeout -= ERASE_TIMEOUT
                        failed_nodes.remove(response['node'])
                        print(u"\r\n  ╰> Flash memory of node ", response['node'], " erased.")
        state = device._poll_once()

    # retry sending failed messages
    for node in failed_nodes:
        send_node_command(device, node, topic, BOOTLOADER_ERASE)
        print(u"\r\n  ╰> Retry erase memory of node ", node)
        init_time = time.time()
        state = device._poll_once()
        while len(failed_nodes):
            if(time.time() - init_time > ERASE_TIMEOUT):
                return_value = False
                break

            # check if it is a response message
            if 'bootloader' in state:  
                for response in state['bootloader']:
                    if (response['response'] == BOOTLOADER_ERASE_RESP):
                    # this node responded, delete it from the failed nodes list
                        if response['node'] in failed_nodes:
                            failed_nodes.remove(response['node'])
                            print(u"\r\n  ╰> Flash memory of node ", response['node'], " erased.")
            state = device._poll_once()

    if not len(failed_nodes):
        return_value = True

    waiting_bg.terminate()
    return return_value, failed_nodes

# *******************************************************************************
# @brief get binary size
# @param
# @return binary size
# *******************************************************************************
def loading_bar(loading_progress):
    period = 0.2
    while(1):
        time.sleep(period)
        print(u"\r  ╰> loading : {} %".format(loading_progress.value), end='')

# *******************************************************************************
# @brief send the binary file to the node
# @param command type
# @return None
# *******************************************************************************
def send_binary_data(device, topic, nodes_to_program):
    loading_state = True
    failed_nodes = []
    prev_fails = []
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
        loading_state, failed_nodes = send_frame_from_binary(device, topic, frame_size, file_offset, nodes_to_program)
        if not loading_state:
            print(u"\r  ╰> loading of node: ", failed_nodes, "FAILED %")
            for fail in failed_nodes:
                nodes_to_program.remove(fail)
            prev_fails.extend(failed_nodes)
            loading_state = True
        # update cursor position in the binary file
        file_offset += frame_size
        # update loading progress
        loading_progress.value = math.trunc(frame_index / nb_frames * 100)
        if not len(nodes_to_program):
            break;

    # kill the progress bar at the end of the loading
    loading_bar_bg.terminate()
    if loading_state:
        print(u"\r  ╰> loading : 100.0 %")
    if len(prev_fails):
        loading_state = False
    return loading_state, prev_fails

# *******************************************************************************
# @brief open binary file and send a frame
# @param
# @return None
# *******************************************************************************
def send_frame_from_binary(device, topic, frame_size, file_offset, nodes_to_program):
    return_value = True
    failed_nodes = []
    failed_nodes.extend(nodes_to_program)
    timeout = PROGRAM_TIMEOUT * len(nodes_to_program)

    with open(FILEPATH, mode="rb") as f:
        # put the cursor at the beginning of the file
        f.seek(file_offset)
        # read binary data
        data_bytes = f.read(1)
        for sample in range(frame_size-1):
            data_bytes = data_bytes + f.read(1)

    send_data(device, topic, BOOTLOADER_BIN_CHUNK, frame_size, data_bytes)
    # pull serial data
    state = device._poll_once()
    # wait nodes response
    init_time = time.time()
    while len(failed_nodes):
        # check for timeout of nodes
        if(time.time() - init_time > timeout):
            return_value = False
            break
        # check if it is a response message
        if 'bootloader' in state:
            for response in state['bootloader']:
                if (response['response'] == BOOTLOADER_BIN_CHUNK_RESP):
                    # the node responsed, remove it for fails list
                    if response['node'] in failed_nodes:
                        timeout -= PROGRAM_TIMEOUT
                        failed_nodes.remove(response['node'])
        # wait for next message
        state = device._poll_once()

    for node in failed_nodes:
        # retry sending failed messages
        send_data_node(device, node, BOOTLOADER_BIN_CHUNK, frame_size, data_bytes)
        state = device._poll_once()
        print(u"\r\n  ╰> Retry sending binary message to node ", node)
        init_time = time.time()
        while len(failed_nodes):
            # check for timeout of nodes
            if(time.time() - init_time > PROGRAM_TIMEOUT):
                return_value = False
                break

            # check if it is a response message
            if 'bootloader' in state:
                for response in state['bootloader']:
                    if (response['response'] == BOOTLOADER_BIN_CHUNK_RESP):
                        # the node responsed, remove it for fails list
                        if response['node'] in failed_nodes:
                            failed_nodes.remove(response['node'])
            # wait for next message
            state = device._poll_once()

    if not len(failed_nodes):
        return_value = True

    return return_value, failed_nodes

# *******************************************************************************
# @brief send binary data with a header
# @param
# @return None
# *******************************************************************************
def send_data(device, topic, command, size, data):
    # create a json file with the list of the nodes to program
    bootloader_cmd = {
        'bootloader': {
            'command': {
                'size': [size],
                'type': command,
                'topic': topic,
            },
        }
    }
    # send json command
    device._write(json.dumps(bootloader_cmd).encode() + '\n'.encode() + data)

# *******************************************************************************
# @brief send binary data with a header to a specific node
# @param
# @return None
# *******************************************************************************
def send_data_node(device, node, command, size, data):
    # create a json file with the list of the nodes to program
    bootloader_cmd = {
        'bootloader': {
            'command': {
                'size': [size],
                'type': command,
                'node': node,
            },
        }
    }
    # send json command
    device._write(json.dumps(bootloader_cmd).encode() + '\n'.encode() + data)

# *******************************************************************************
# @brief send the binary end command
# @param
# @return
# *******************************************************************************
def send_binary_end(device, topic, nodes_to_program):
    return_value = True
    failed_nodes = []
    failed_nodes.extend(nodes_to_program)
    timeout = RESP_TIMEOUT * len(nodes_to_program)
    # send command
    send_topic_command(device, topic, BOOTLOADER_BIN_END)
    # poll serial data
    state = device._poll_once()
    # wait bin_end response
    init_time = time.time()
    while len(failed_nodes) > 0:
        # check if we exit with timeout
        if(time.time() - init_time > timeout):
            return_value = False
            break
        if 'bootloader' in state:
            for response in state['bootloader']:
                # check each node response
                if (response['response'] == BOOTLOADER_BIN_END_RESP):
                    print(u"  ╰> Node", response['node'], "acknowledge received, loading is complete.")
                    # remove node from fails list
                    if response['node'] in failed_nodes:
                        timeout -= RESP_TIMEOUT
                        failed_nodes.remove(response['node'])
        state = device._poll_once()

    for node in failed_nodes:
        # retry sending failed messages
        send_node_command(device, node, topic, BOOTLOADER_BIN_END)
        print(u"\r\n  ╰> Retry sending end message to node ", node)
        state = device._poll_once()
        init_time = time.time()
        while len(failed_nodes):
            # check for timeout of nodes
            if(time.time() - init_time > RESP_TIMEOUT):
                return_value = False
                break

            # check if it is a response message
            if 'bootloader' in state:
                for response in state['bootloader']:
                    if (response['response'] == BOOTLOADER_BIN_END_RESP):
                        # the node responsed, remove it for fails list
                        if response['node'] in failed_nodes:
                            failed_nodes.remove(response['node'])
            # wait for next message
            state = device._poll_once()

    if not len(failed_nodes):
        return_value = True

    return return_value, failed_nodes

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
def check_crc(device, topic, nodes_to_program):
    return_value = True
    failed_nodes = []
    failed_nodes.extend(nodes_to_program)
    timeout = RESP_TIMEOUT * len(nodes_to_program)

    # send crc command
    send_topic_command(device, topic, BOOTLOADER_CRC_TEST)
    
    state = device._poll_once()
    # wait bin_end response
    init_time = time.time()
    while len(failed_nodes):
        # check for timeout exit
        if(time.time() - init_time > timeout):
            return_value = False
            break
        # check the response
        if 'bootloader' in state:
            for response in state['bootloader']:
                if (response['response'] == BOOTLOADER_CRC_RESP):
                    source_crc = int.from_bytes(compute_crc(), byteorder='big')
                    node_crc = response['crc_value']
                    node_id = response['node']
                        # crc properly received 
                    if (source_crc == node_crc):
                        print(u"  ╰> CRC test for node", node_id, " : OK.")
                        if node_id in failed_nodes:
                            timeout -= RESP_TIMEOUT
                            failed_nodes.remove(node_id)
                    else:
                        # not a good crc
                        print(u"  ╰> CRC test for node", node_id, ": NOK.")
                        print(u"  ╰> waited :", hex(source_crc), ", received :", hex(node_crc))
                        return_value = False
        state = device._poll_once()

    for node in failed_nodes:
        # retry sending failed messages
        send_node_command(device, node, topic, BOOTLOADER_CRC_TEST)
        print(u"\r\n  ╰> Retry sending crc demand to node ", node)
        state = device._poll_once()
        init_time = time.time()
        while len(failed_nodes):
            # check for timeout of nodes
            if(time.time() - init_time > RESP_TIMEOUT):
                return_value = False
                break

            # check if it is a response message
            if 'bootloader' in state:
                for response in state['bootloader']:
                    if (response['response'] == BOOTLOADER_CRC_RESP):
                        source_crc = int.from_bytes(compute_crc(), byteorder='big')
                        node_crc = response['crc_value']
                        node_id = response['node']
                            # crc properly received 
                        if (source_crc == node_crc):
                            print(u"  ╰> CRC test for node", node_id, " : OK.")
                            if node_id in failed_nodes:
                                timeout -= RESP_TIMEOUT
                                failed_nodes.remove(node_id)
                        else:
                            # not a good crc
                            print(u"  ╰> CRC test for node", node_id, ": NOK.")
                            print(u"  ╰> waited :", hex(source_crc), ", received :", hex(node_crc))
                            return_value = False
            state = device._poll_once()

    if not len(failed_nodes):
        return_value = True

    return return_value, failed_nodes

# *******************************************************************************
# @brief reboot all nodes in application mode
# @param
# @return
# *******************************************************************************
def reboot_network(device, topic, nodes_to_reboot):
    for node in nodes_to_reboot:
                send_node_command(device, node, topic, BOOTLOADER_STOP)
                # delay to let gate send commands
                time.sleep(0.01)
# *******************************************************************************
# @brief command used to flash luos nodes
# @param flash function arguments : -g, -t, -b
# @return None
# *******************************************************************************
def luos_flash(args):
    print('Luos flash subcommand with parameters :')
    print('\t--baudrate : ', args.baudrate)
    print('\t--gate : ', args.gate)
    print('\t--target : ', args.target)
    print('\t--binary : ', args.binary)
    print('\t--port : ', args.port)

    topic = 1

    if not (args.port):
        try:
            args.port= serial_discover(os.getenv('LUOS_BAUDRATE', args.baudrate))[0]
        except:
            sys.exit()
            return

    # state used to check each step
    machine_state = True
    # list of all the nodes that may fail in each step
    total_fails = []
    # update firmware path
    global FILEPATH
    FILEPATH = args.binary
    try:
        f = open(FILEPATH, mode="rb")
    except IOError:
        sys.exit("Cannot open :", FILEPATH)
        return BOOTLOADER_FLASH_BINARY_ERROR
    else:
        f.close()

    # init device
    device = Device(args.port, baudrate=os.getenv('LUOS_BAUDRATE', args.baudrate), background_task=False)

    # find routing table
    state = find_network(device)

    # searching nodes to program in network
    (nodes_to_reboot, nodes_to_program) = create_target_list(args, state)

    # check if we have available node to program
    if not nodes_to_program:
        sys.exit("No target found :\n" + str(device.nodes))

    # reboot all nodes in bootloader mode
    print("** Reboot all nodes in bootloader mode **")
    for node in nodes_to_reboot:
        send_node_command(device, node, topic, BOOTLOADER_START)
        # delay to let gate send commands
        time.sleep(0.01)

    # wait before next step
    time.sleep(0.1)

    # find routing table in boot mode
    # its necessary to give ids to bootloader services
    state = find_network(device)

    # wait before next step
    time.sleep(0.4)

    print("\n** Programming nodes **")
    
    # go to header state if node is ready
    for node in nodes_to_program:
        print("--> Check if node", node, " is ready.")
        machine_state = send_ready_cmd(device, node, topic)
        if not machine_state:
            total_fails.append(node)
            machine_state = True
            print("Node ", node, "failed to load!")
        time.sleep(0.01)

    for node in total_fails:
        nodes_to_program.remove(node)

    # erase node flash memory
    print("--> Erase flash memory.")
    machine_state, failed_nodes = erase_flash(device, topic, nodes_to_program)
    if not machine_state:
        for fail in failed_nodes:
            nodes_to_program.remove(fail)
        total_fails.extend(failed_nodes)
        machine_state = True
        print("Erase flash of node: ", failed_nodes, "failed!")

    # send binary data
    print("--> Send binary data.")
    machine_state, failed_nodes = send_binary_data(device, topic, nodes_to_program)
    if not machine_state:
        total_fails.extend(failed_nodes)
        machine_state = True
        print("Flash of node: ", failed_nodes, "failed!")
    
    # inform the node of the end of the loading
    print("--> Programmation finished, waiting for acknowledge.")
    machine_state, failed_nodes = send_binary_end(device, topic, nodes_to_program)
    if not machine_state:
        for fail in failed_nodes:
            nodes_to_program.remove(fail)
        total_fails.extend(failed_nodes)
        machine_state = True
        print("ACK of node: ", failed_nodes, "failed!")

    # Ask the node to send binary crc
    print("--> Check binary CRC.")
    machine_state, failed_nodes = check_crc(device, topic, nodes_to_program)
    if not machine_state:
        for fail in failed_nodes:
            nodes_to_program.remove(fail)
        total_fails.extend(failed_nodes)
        machine_state = True
        print("ACK of node: ", failed_nodes, "failed!")

    # Say to the bootloader that the integrity
    # of the app saved in flash has been verified
    send_topic_command(device, topic, BOOTLOADER_APP_SAVED)

    # wait before next step
    time.sleep(0.1)
    # reboot all nodes in application mode
    if len(total_fails) == 0:
        print("** Reboot all nodes in application mode **")
        reboot_network(device, topic, nodes_to_reboot)
        device.close()
        return BOOTLOADER_SUCCESS
    else:
        device.close()
        print("Load of nodes: ", total_fails, " failed, please reboot and retry.")
        return BOOTLOADER_FLASH_ERROR

# *******************************************************************************
# @brief command used to detect network
# @param detect function arguments : -p
# @return None
# *******************************************************************************
def luos_detect(args):
    print('Luos detect subcommand on port : ', args.port)
    print('\tLuos detect subcommand at baudrate : ', args.baudrate)

    if not (args.port):
        try:
            args.port= serial_discover(os.getenv('LUOS_BAUDRATE', args.baudrate))[0]
        except:
            sys.exit()
            return

    # detect network
    device = Device(args.port, baudrate=os.getenv('LUOS_BAUDRATE', args.baudrate))
    # print network to user
    print(device.nodes)
    device.close()

    return BOOTLOADER_SUCCESS

# *******************************************************************************
# @brief command used to force reset a node in bootloader mode
# @param detect function arguments : -p
# @return None
# *******************************************************************************
def luos_reset(args):
    print('Luos discover subcommand on port : ', args.port)
    print('\tLuos discover subcommand at baudrate : ', args.baudrate)

    if not (args.port):
        try:
            args.port= serial_discover(os.getenv('LUOS_BAUDRATE', args.baudrate))[0]
        except:
            sys.exit()
            return


    # send rescue command
    print('Send reset command.')
    port = serial.Serial(args.port, os.getenv('LUOS_BAUDRATE', args.baudrate), timeout=0.05)
    rst_cmd = {
        'bootloader': {
            'command': {
                'type': BOOTLOADER_RESET,
                'node': 0,
                'size': 0
            },
        }
    }
    s = json.dumps(rst_cmd).encode()
    port.write(b'\x7E' + struct.pack('<H', len(s)) + s + b'\x81')
    port.close()

    # detect network
    device = Device(args.port, baudrate=os.getenv('LUOS_BAUDRATE', args.baudrate), background_task=False)

    print(device.nodes)
    device.close()

    return BOOTLOADER_SUCCESS

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
    flash_parser.add_argument('port',
                              help='port used to detect network',
                              nargs='?')
    flash_parser.add_argument('-g', '--gate',
                              help='id of the gate used to access the luos network')
    flash_parser.add_argument('-b', '--binary',
                              help='path to the binary file to flash')
    flash_parser.add_argument('-t', '--target',
                              help='target node to flash',
                              default=['2'],
                              nargs='*')
    flash_parser.add_argument('--baudrate',
                              help='Choose pyluos serial baudrate default value = 1000000',
                              default=1000000)
    flash_parser.set_defaults(func=luos_flash)

    # declare "detect" subcommand
    detect_parser = subparsers.add_parser('detect',
                                          help='tool to detect luos network')
    detect_parser.add_argument('port', help='port used to detect network',
                              nargs='?')
    detect_parser.add_argument('--baudrate',
                               help='Choose pyluos serial baudrate default value = 1000000',
                               default=1000000)
    detect_parser.set_defaults(func=luos_detect)

    # declare "rescue" subcommand
    rescue_parser = subparsers.add_parser('reset',
                                          help='tool to reset one or multiple blocked nodes in rescue mode')
    rescue_parser.add_argument('port', help='port used to access to the network',
                              nargs='?')
    rescue_parser.add_argument('--baudrate',
                               help='Choose pyluos serial baudrate default value = 1000000',
                               default=1000000)
    rescue_parser.set_defaults(func=luos_reset)

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
    return args.func(args)

if __name__ == '__main__':
    sys.exit(main())
