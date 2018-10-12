from .module import Module, interact
import collections
from copy import copy
import time

compare = lambda x, y: collections.Counter(x) == collections.Counter(y)


class Imu(Module):
    _ACCELL = 9
    _GYRO = 8
    _QUAT = 7
    _COMPASS = 6
    _EULER = 5
    _ROT_MAT = 4
    _PEDO = 3
    _LINEAR_ACCEL = 2
    _GRAVITY_VECTOR = 1
    _HEADING = 0


    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Imu', id, alias, robot)
        self._config = [False] * (Imu._ACCELL + 1)
        self._config[Imu._QUAT] = True # by default enable quaternion
        self._quaternion = (0, 0, 0, 0)
        self._acceleration = (0, 0, 0)
        self._gyro = (0, 0, 0)
        self._compass = (0, 0, 0)
        self._euler = (0, 0, 0)
        self._rotational_matrix = (0, 0, 0, 0, 0, 0, 0, 0, 0)
        self._pedometer = 0
        self._walk_time = 0
        self._linear_acceleration = (0, 0, 0)
        self._gravity_vector = (0, 0, 0)
        self._heading = 0

    def _convert_config(self):
        return int(''.join(['1' if c else '0' for c in self._config]), 2) # Tableaux lu a l'envert


    def bit(self, i, enable):
        self._config = self._config[:i] + () + self._config[i + 1:]

    @property
    def quaternion(self):
        self.quaternion = True
        return self._quaternion

    @quaternion.setter
    def quaternion(self, enable):
        bak = copy(self._config)
        self._config[Imu._QUAT] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)

    @property
    def acceleration(self):
        self.acceleration = True
        return self._acceleration

    @acceleration.setter
    def acceleration(self, enable):
        bak = copy(self._config)
        self._config[Imu._ACCELL] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)

    @property
    def gyro(self):
        self.gyro = True
        return self._gyro

    @gyro.setter
    def gyro(self, enable):
        bak = copy(self._config)
        self._config[Imu._GYRO] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)

    @property
    def compass(self):
        self.compass = True
        return self._compass

    @compass.setter
    def compass(self, enable):
        bak = copy(self._config)
        self._config[Imu._COMPASS] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)

    @property
    def euler(self):
        self.euler = True
        return self._euler

    @euler.setter
    def euler(self, enable):
        bak = copy(self._config)
        self._config[Imu._EULER] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)

    @property
    def rotational_matrix(self):
        self.rotational_matrix = True
        return self._rotational_matrix

    @rotational_matrix.setter
    def rotational_matrix(self, enable):
        bak = copy(self._config)
        self._config[Imu._ROT_MAT] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)

    @property
    def pedometer(self):
        self.pedometer = True
        return self._pedometer

    @pedometer.setter
    def pedometer(self, enable):
        bak = copy(self._config)
        self._config[Imu._PEDO] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)

    @property
    def walk_time(self):
        self.walk_time = True
        return self._walk_time

    @walk_time.setter
    def walk_time(self, enable):
        self.pedometer = enable

    @property
    def linear_acceleration(self):
        self.linear_acceleration = True
        return self._linear_acceleration

    @linear_acceleration.setter
    def linear_acceleration(self, enable):
        bak = copy(self._config)
        self._config[Imu._LINEAR_ACCEL] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)

    @property
    def gravity_vector(self):
        self.gravity_vector = True
        return self._gravity_vector

    @gravity_vector.setter
    def gravity_vector(self, enable):
        bak = copy(self._config)
        self._config[Imu._GRAVITY_VECTOR] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)

    @property
    def heading(self):
        self.heading = True
        return self._heading

    @heading.setter
    def heading(self, enable):
        bak = copy(self._config)
        self._config[Imu._HEADING] = True if enable != 0  else False
        if bak != self._config:
            print (bak)
            print (self._config)
            self._push_value('imu_enable', self._convert_config())
            time.sleep(0.1)


    def _update(self, new_state):
        Module._update(self, new_state)
        if 'quaternion' in new_state:
            self._quaternion = new_state['quaternion']
        if 'accel' in new_state:
            self._acceleration = new_state['accel']
        if 'gyro' in new_state:
            self._gyro = new_state['gyro']
        if 'compass' in new_state:
            self._compass = new_state['compass']
        if 'euler' in new_state:
            self._euler = new_state['euler']
        if 'rotational_matrix' in new_state:
            self._rotational_matrix = new_state['rotational_matrix']
        if 'pedometer' in new_state:
            self._pedometer = new_state['pedometer']
        if 'walk_time' in new_state:
            self._walk_time = new_state['walk_time']
        if 'linear_accel' in new_state:
            self._linear_acceleration = new_state['linear_accel']
        if 'gravity_vector' in new_state:
            self._gravity_vector = new_state['gravity_vector']
        if 'heading' in new_state:
            self._heading = new_state['heading']

    def control(self):
        def change_config(accel, gyro, quat, compass, euler, rot_mat, pedo, linear_accel, gravity_vector, heading):
            self.acceleration = accel
            self.gyro = gyro
            self.quaternion = quat
            self.compass = compass
            self.euler = euler
            self.rotational_matrix = rot_mat
            self.pedometer = pedo
            self.linear_acceleration = linear_accel
            self.gravity_vector = gravity_vector
            self.heading = heading
            self._push_value('imu_enable', self._convert_config())

        return interact(change_config,
                        accel=self._config[Imu._ACCELL],
                        gyro=self._config[Imu._GYRO],
                        quat=self._config[Imu._QUAT],
                        compass=self._config[Imu._COMPASS],
                        euler=self._config[Imu._EULER],
                        rot_mat=self._config[Imu._ROT_MAT],
                        pedo=self._config[Imu._PEDO],
                        linear_accel=self._config[Imu._LINEAR_ACCEL],
                        gravity_vector=self._config[Imu._GRAVITY_VECTOR],
                        heading=self._config[Imu._HEADING])
