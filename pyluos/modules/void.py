from .module import Module


class Void(Module):

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Void', id, alias, robot)
        self._baudrate = 1000000

    def _update(self, new_state):
        Module._update(self, new_state)

    def dxl_detect(self):
        self._push_value('reinit', 0)
        print ("To get new detected Dxl motors usable on pyluos you should recreate your Luos object.")

    @property
    def baudrate(self):
        return self._baudrate

    def baudrate(self, baud):
        values = [9600, 19200, 57600, 115200, 200000, 250000, 400000, 500000, 1000000]
        if baud in values :
            new_val = [4, baud]
            self._push_value('register', new_val)
            self._baudrate = baud
            print ("If you try to recover a motor you should start 'dxl_detect()' command and recreate your Luos object.")
        else :
            err = "Possible values are :\n"
            for val in values :
                err = err + "\t- " + str(val) + "\n"
            raise ValueError(err)

    def factory_reset(self):
        new_val = [0xFF, 0]
        self._push_value('register', new_val)
        print("Motor reseted => baudrate : 1000000, ID : same")
