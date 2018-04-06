from .robot import Robot


class Eddy(object):
    def __init__(self, host=None):
        if host is None:
            hosts = Robot.discover()['eddy']
            if len(hosts) != 1:
                raise IOError('Eddy not found! {}'.format(hosts))
            host = hosts[0]

        self._robot = Robot(host)

        self.left_wheel = self._robot.eddy.left_wheel
        self.right_wheel = self._robot.eddy.right_wheel

        self.left_light_sensor = self._robot.eddy.right_light_sensor
        self.right_light_sensor = self._robot.eddy.left_light_sensor
