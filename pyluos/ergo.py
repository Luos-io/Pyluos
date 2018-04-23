from .robot import Robot


class ErgoJr(object):
    def __init__(self, host=None):
        if host is None:
            hosts = Robot.discover()['ergo']
            if len(hosts) != 1:
                raise IOError('ErgoJr not found! {}'.format(hosts))
            host = hosts[0]

        self._robot = Robot(host)

        self._dxl = self._robot.dxl
        while not self._dxl._setup:
            pass
        setattr(self, 'motors', self._dxl.motors)
        for i, m in enumerate(self._dxl.motors):
            setattr(self, 'm{}'.format(i + 1), m)

        for mod in self._robot.modules:
            if mod.type != 'Dynamixel':
                setattr(self, mod.alias, mod)
