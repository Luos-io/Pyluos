from __future__ import division

import json
import time
import serial as _serial
import platform
import logging
import sys
if sys.version_info >= (3, 0):
    import queue
else:
    import Queue as queue


from threading import Event, Thread

from serial.tools.list_ports import comports

from . import IOHandler

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError

class Serial(IOHandler):
    poll_frequency = 200

    @classmethod
    def available_hosts(cls):
        devices = comports(include_links=True)

        return [d.device for d in devices]

    @classmethod
    def is_host_compatible(cls, host):
        return host in cls.available_hosts()

    def __init__(self, host, baudrate=1000000):
        self._serial = _serial.Serial(host, baudrate)
        self._serial.flush()

        self._msg = queue.Queue(100)
        self._running = True

        self._poll_loop = Thread(target=self._poll)
        self._poll_loop.daemon = True
        self._poll_loop.start()

    def is_ready(self):
        if self._serial.in_waiting == 0:
            return False

        try:
            self.read()
            return True
        except (UnicodeDecodeError, JSONDecodeError):
            return False

    def recv(self):
        return self._msg.get()

    def write(self, data):
        self._serial.write(data + '\r'.encode())
        #print(data + '\r'.encode())

    def close(self):
        self._running = False
        self._poll_loop.join()

        self._serial.close()

    def _poll(self):
        def extract_line(s):
            j = s.find(b'\n')
            if j == -1:
                return b'', s
            # Sometimes the begin of serial data can be wrong remove it
            # Find the first '{'

            x = s.find(b'{')
            if x == -1:
                return b'', s[j + 1:]

            return s[x:j], s[j + 1:]

        period = 1 / self.poll_frequency
        buff = b''

        while self._running:
            to_read = self._serial.in_waiting

            if to_read == 0:
                time.sleep(period)
                continue

            s = self._serial.read(to_read)
            buff = buff + s

            while self._running:
                line, buff = extract_line(buff)
                if not len(line):
                    break
                if self._msg.full():
                    self._msg.get()
                self._msg.put(line)
############ Sniffer Code #############
class Sniffer_Serial(IOHandler):
    poll_frequency = 200

    @classmethod
    def available_hosts(cls):
        devices = comports()

        return [d.device for d in devices]

    @classmethod
    def is_host_compatible(cls, host):
        return host in cls.available_hosts()

    def __init__(self, host, baudrate=1000000):
        self._serial = _serial.Serial(host, baudrate)
        self._serial.flush()

        self._msg = queue.Queue(100)
        self._running = True

        self._poll_loop = Thread(target=self._poll)
        self._poll_loop.daemon = True
        self._poll_loop.start()

    def recv(self):
        return self._msg.get()

    def write(self, data):
        self._serial.write(data)

    def close(self):
        self._running = False
        self._poll_loop.join()

        self._serial.close()

    def _poll(self):

        def mode_translator(mode):
            switcher = {
                b'0': 'ID',
                b'1': 'IDACK',
                b'2': 'TYPE',
                b'3': 'BROADCAST',
                b'4': 'MULTICAST',
                b'5': 'NODEID',
                b'6': 'NODEIDACK'
            }
            return switcher.get(mode)
 
        def cmd_translator(cmd):
            switcher = {
                b'00': 'WRITE_NODE_ID',
                b'01': 'RESET_DETECTION',
                b'02': 'SET_BAUDRATE',
                b'03': 'ASSERT',
                b'04': 'RTB_CMD',
                b'05': 'WRITE_ALIAS',
                b'06': 'UPDATE_PUB',
                b'07': 'NODE_UUID',
                b'08': 'REVISION',
                b'09': 'LUOS_REVISION',
                b'0a': 'LUOS_STATISTICS',
                b'0b': 'GET_CMD',
                b'0c': 'SET_CMD',
                b'0d': 'COLOR',
                b'0e': 'COMPLIANT',
                b'0f': 'IO_STATE',
                b'10': 'RATIO',
                b'11': 'PEDOMETER',
                b'12': 'ILLUMINANCE',
                b'13': 'VOLTAGE',
                b'14': 'CURRENT',
                b'15': 'POWER',
                b'16': 'TEMPERATURE',
                b'17': 'TIME',
                b'18': 'FORCE',
                b'19': 'MOMENT',
                b'1a': 'CONTROL',
                b'1b': 'REGISTER',
                b'1c': 'REINIT',
                b'1d': 'PID',
                b'1e': 'RESOLUTION',
                b'1f': 'REDUCTION',
                b'20': 'DIMENSION',
                b'21': 'OFFSET',
                b'22': 'SETID',
                b'23': 'ANGULAR_POSITION',
                b'24': 'ANGULAR_SPEED',
                b'25': 'LINEAR_POSITION',
                b'26': 'LINEAR_SPEED',
                b'27': 'ACCEL_3D',
                b'28': 'GYRO_3D',
                b'29': 'QUATERNION',
                b'2a': 'COMPASS_3D',
                b'2b': 'EULER_3D',
                b'2c': 'ROT_MAT',
                b'2d': 'LINEAR_ACCEL',
                b'2e': 'GRAVITY_VECTOR',
                b'2f': 'HEADING',
                b'30': 'ANGULAR_POSITION_LIMIT',
                b'31': 'LINEAR_POSITION_LIMIT',
                b'32': 'RATIO_LIMIT',
                b'33': 'CURRENT_LIMIT',
                b'34': 'ANGULAR_SPEED_LIMIT',
                b'35': 'LINEAR_SPEED_LIMIT',
                b'36': 'TORQUE_LIMIT',
                b'37': 'TEMPERATURE_LIMIT',
                b'38': 'HANDY_SET_POSITION',
                b'39': 'PARAMETERS',
                b'3a': 'LUOS_PROTOCOL_NB'
            }
            return switcher.get(cmd)
        

        #function for decoding and logging a msg
        #param s: a full received msg
        def data_decode(s):
            time_hex = bytearray.fromhex(s[0 : 16])
            time_hex.reverse()
            timestamp = int(time_hex.hex(), 16)
            s = s[16 :]
            self.logger = logging.getLogger('pysniffer')

            protocol = s[1 : 2]
            target = s[2 : 4] + s[0 : 1]
            target_mode = s[5 : 6]
            source = s[6 : 8] + s[4 : 5]
            cmd = s[8 : 10]
            size = s[12 : 14] + s[10 : 12]
            size_num = int(size, 16)

            if size_num > 128:
                data = s[14 : 14 + (128 * 2)]
            elif size_num == 0:
                data = 0
            else:
                data = s[14 : 14 + (size_num * 2)]

            
            if len(str(data))>1:
                msg = "| TIMESTAMP = " + str(timestamp) + "ns | PROTOCOL = 0x" + protocol + " | TARGET = 0x" + target + " | TARGET_MODE = 0x" + target_mode + " " + str(mode_translator(bytes(target_mode, 'utf-8'))) + " | SOURCE = 0x" + source + " | CMD = 0x" + cmd + " " + str(cmd_translator(bytes(cmd, 'utf-8'))) + " | SIZE = 0x" + size + " | DATA = 0x" + data + " |"
            else: 
                msg = "| TIMESTAMP = " + str(timestamp) + "ns | PROTOCOL = 0x" + protocol + " | TARGET = 0x" + target + " | TARGET_MODE = 0x" + target_mode + " " + str(mode_translator(bytes(target_mode, 'utf-8'))) + " | SOURCE = 0x" + source + " | CMD = 0x" + cmd + " " + str(cmd_translator(bytes(cmd, 'utf-8'))) + " | SIZE = 0x" + size + " |"
            
            text = "{'t':" + str(timestamp) + ",'d':1,'s':" + str(size_num + 7) + "}0x" + str(s)
            self.logger.info(text)

        def extract_msg(s):
            i = s.find(b'~~~')
            if i != -1:
                return s[:i].hex(), s[i+3:]
            return "0", s

        period = 1 / self.poll_frequency
        first_run = 1
        half = b''
        half_msg = half.hex()
        s = b''
        while self._running:
            to_read = self._serial.in_waiting

            if to_read == 0:
                time.sleep(period)
                continue

            self.logger = logging.getLogger('pysniffer')

            if first_run:
                s = self._serial.read(to_read)
            if s.find(b'yes')!=-1 and first_run == 1:
                self.logger.info('Sniffer was Successfully Added')
                first_run = 0
                s = b''
                continue

            if (len(s)>0):
                s = s + self._serial.read(to_read)
            else:
                s = self._serial.read(to_read) 
            while self._running:
                msg, s = extract_msg(s)
                if len(half_msg) > 0:
                    msg = half_msg + msg 
                if len(msg) >= 30:
                    data_decode(msg)
                    half = b''
                    half_msg = half.hex()
                elif len(msg) > 1:
                    half_msg = msg
                else:
                    k = s.find(b'stat')
                    if k!=-1:
                        while self._running:
                            if len(s)>=20:
                                self.logger.info('Statistics')
                                err_num = s[k + 4: k + 12].hex()
                                err_num = bytearray.fromhex(err_num)
                                err_num.reverse()
                                self.logger.info('Bad crc msgs number: ' + str(int(err_num.hex(), 16)))
                                err_num = s[k + 12: k + 20].hex()
                                err_num = bytearray.fromhex(err_num)
                                err_num.reverse()
                                self.logger.info('Corruption number: ' + str(int(err_num.hex(), 16)))
                                s = s[20:]
                                break;
                            else:
                                to_read = self._serial.in_waiting
                                if to_read == 0:
                                    time.sleep(period)   
                                    continue
                                s = s + self._serial.read(to_read)

                    break
