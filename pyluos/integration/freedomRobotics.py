from freedomrobotics.link import Link

import logging
import time

class FreedomLink(object):
    def __init__(self, device):
        self._link = Link("core", command_callback=self.callback)
        self._delegate = device

    def callback(msg):
        print("I receive:" + str(msg) )
        self._link.log("info", "I heard " + str(msg) )
        # Topic represent services.
        if hasattr(self._delegate, msg["topic"][1:]):
            service = getattr(self._delegate, msg["topic"][1:])
            print ("we have this service")
            # We have this service.
            if hasattr(service, msg["message"]):
                service_data = getattr(service, msg["message"])
                service_data = msg["message"][msg["message"]]

    def _update(self, alias, new_state):
        if 'io_state' in new_state:
            self._link.message("/" + alias + "/io_state", \
                    "sensor_msgs/Joy", \
                    {"io_state": new_state['io_state']})
        if 'temperature' in new_state:
            self._link.message("/" + alias + "/temperature", \
                    "sensor_msgs/Temperature", \
                    {"temperature": new_state['temperature']})
        if 'lux' in new_state:
            self._link.message("/" + alias + "/lux", \
                    "sensor_msgs/Illuminance", \
                    {"illuminance": new_state['lux']})
        if 'rot_position' in new_state:
            self._link.message("/" + alias + "/rot_position", \
                    "sensor_msgs/JointState", \
                    {"position": new_state['rot_position'], "name":alias})
        if 'trans_position' in new_state:
            self._link.message("/" + alias + "/trans_position", \
                    "sensor_msgs/Range", \
                    {"range": new_state['trans_position']})
        if 'rot_speed' in new_state:
            self._link.message("/" + alias + "/rot_speed", \
                    "sensor_msgs/JointState", \
                    {"velocity": new_state['rot_speed'], "name":alias})
        if 'trans_speed' in new_state:
            self._link.message("/" + alias + "/trans_speed", \
                    "sensor_msgs/JointState", \
                    {"velocity": new_state['trans_speed'], "name":alias})
        if 'force' in new_state:
            self._link.message("/" + alias + "/force", \
                    "sensor_msgs/JointState", \
                    {"effort": new_state['force'], "name":alias})
        if 'current' in new_state:
            self._link.message("/" + alias + "/current", \
                    "sensor_msgs/BatteryState", \
                    {"current": new_state['current']})
        if 'volt' in new_state:
            self._link.message("/" + alias + "/volt", \
                    "sensor_msgs/BatteryState", \
                    {"voltage": new_state['volt']})
        if 'quaternion' in new_state:
            self._link.message("/" + alias + "/quaternion", \
                    "geometry_msgs/Quaternion", \
                    {"y": new_state['quaternion'][0],"x": new_state['quaternion'][1],"z": new_state['quaternion'][2],"w": new_state['quaternion'][3]})
        if 'linear_accel' in new_state:
            self._link.message("/" + alias + "/linear_accel", \
                    "geometry_msgs/Accel", \
                    {"linear": {"y": new_state['linear_accel'][0],"x": new_state['linear_accel'][1],"z": new_state['linear_accel'][2]}})
        if 'accel' in new_state:
            self._link.message("/" + alias + "/accel", \
                    "geometry_msgs/Accel", \
                    {"angular": {"y": new_state['accel'][0],"x": new_state['accel'][1],"z": new_state['accel'][2]}})
        if 'gyro' in new_state:
            self._link.message("/" + alias + "/gyro", \
                    "geometry_msgs/Vector3", \
                    {"y": new_state['gyro'][0],"x": new_state['gyro'][1],"z": new_state['gyro'][2]})
        if 'euler' in new_state:
            self._link.message("/" + alias + "/euler", \
                    "geometry_msgs/Vector3", \
                    {"y": new_state['euler'][0],"x": new_state['euler'][1],"z": new_state['euler'][2]})
        if 'compass' in new_state:
            self._link.message("/" + alias + "/compass", \
                    "geometry_msgs/Vector3", \
                    {"y": new_state['compass'][0],"x": new_state['compass'][1],"z": new_state['compass'][2]})
        if 'gravity_vector' in new_state:
            self._link.message("/" + alias + "/gravity", \
                    "geometry_msgs/Vector3", \
                    {"y": new_state['gravity_vector'][0],"x": new_state['gravity_vector'][1],"z": new_state['gravity_vector'][2]})

# I don't know what to do with those ones :
        # if 'rotational_matrix' in new_state:
        #     self._rotational_matrix = new_state['rotational_matrix']
        # if 'pedometer' in new_state:
        #     self._pedometer = new_state['pedometer']
        # if 'walk_time' in new_state:
        #     self._walk_time = new_state['walk_time']

        # if 'heading' in new_state:
        #     self._heading = new_state['heading']
        # if 'revision' in new_state:
        #     self._firmware_revision = new_state['revision']
        # if 'luos_revision' in new_state:
        #     self._luos_revision = new_state['luos_revision']
        # if 'luos_statistics' in new_state:
        #     self._luos_statistics = new_state['luos_statistics']


    def _kill(self, alias):
        print ("service", alias, "have been excluded from the network due to no responses.")

    def _assert(self, alias):
        print ("service", alias, "assert.")
