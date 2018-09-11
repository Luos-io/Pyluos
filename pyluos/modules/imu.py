from .module import Module, interact


class Imu(Module):
    _ACCELL = 0
    _GYRO = 1
    _QUAT = 2
    _COMPASS = 3
    _EULER = 4
    _ROT_MAT = 5
    _PEDO = 6
    _LINEAR_ACCEL = 7
    _GRAVITY_VECTOR = 8
    _HEADING = 9


    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Imu', id, alias, robot)
        self._config = [False] * (Imu._HEADING + 1)
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

    def convert_config(self):
        return int(''.join(['1' if c else '0' for c in self._config]), 2)


    def bit(self, i, enable):
        self._config = self._config[:i] + () + self._config[i + 1:]

    @property
    def quaternion(self):
        return self._quaternion

    @quaternion.setter
    def quaternion(self, enable):
        bak = str(self._config)
        self._config[Imu._QUAT] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())

    @property
    def acceleration(self):
        return self._acceleration

    @acceleration.setter
    def acceleration(self, enable):
        bak = str(self._config)
        self._config[Imu._ACCELL] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())

    @property
    def gyro(self):
        return self._gyro

    @gyro.setter
    def gyro(self, enable):
        bak = str(self._config)
        self._config[Imu._GYRO] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())

    @property
    def compass(self):
        return self._compass

    @compass.setter
    def compass(self, enable):
        bak = str(self._config)
        self._config[Imu._COMPASS] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())

    @property
    def euler(self):
        return self._euler

    @euler.setter
    def euler(self, enable):
        bak = str(self._config)
        self._config[Imu._EULER] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())

    @property
    def rotational_matrix(self):
        return self._rotational_matrix

    @rotational_matrix.setter
    def rotational_matrix(self, enable):
        bak = str(self._config)
        self._config[Imu._ROT_MAT] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())

    @property
    def pedometer(self):
        return self._pedometer

    @pedometer.setter
    def pedometer(self, enable):
        bak = str(self._config)
        self._config[Imu._PEDO] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())

    @property
    def walk_time(self):
        return self._walk_time

    @walk_time.setter
    def walk_time(self, enable):
        self.pedometer = enable

    @property
    def linear_acceleration(self):
        return self._linear_acceleration

    @linear_acceleration.setter
    def linear_acceleration(self, enable):
        bak = str(self._config)
        self._config[Imu._LINEAR_ACCEL] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())

    @property
    def gravity_vector(self):
        return self._gravity_vector

    @gravity_vector.setter
    def gravity_vector(self, enable):
        bak = str(self._config)
        self._config[Imu._GRAVITY_VECTOR] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, enable):
        bak = str(self._config)
        self._config[Imu._HEADING] = True if enable != 0  else False
        if bak != self._config:
            self._push_value('imu_enable', self.convert_config())



    def _update(self, new_state):
        Module._update(self, new_state)
        self._quaternion = new_state['quaternion']
        self._acceleration = new_state['accel']
        self._gyro = new_state['gyro']
        self._compass = new_state['compass']
        self._euler = new_state['euler']
        self._rotational_matrix = new_state['rotational_matrix']
        self._pedometer = new_state['pedometer']
        self._walk_time = new_state['walk_time']
        self._linear_acceleration = new_state['linear_accel']
        self._gravity_vector = new_state['gravity_vector']
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

        return interact(change_pin,
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
