from .module import Module
import time

class Void(Module):

    def __init__(self, id, alias, device):
        Module.__init__(self, 'Void', id, alias, device)
        self._baudrate = 1000000

    def _update(self, new_state):
        Module._update(self, new_state)

    def dxl_detect(self):
        self._push_value('reinit', 0)
        print ("To get new detected Dxl motors usable on pyluos you should recreate your Pyluos object.")

    @property
    def baudrate(self):
        return self._baudrate


    def _baudrate(self, baud):
        new_val = [4, baud]
        self._push_value('register', new_val)
        self._baudrate = baud


    def baudrate(self, baud):
        values = [9600, 19200, 57600, 115200, 200000, 250000, 400000, 500000, 1000000]
        if baud in values :
            self._baudrate(baud)
            print ("If you try to recover a motor you should start 'dxl_detect()' command and recreate your Pyluos object.")
        else :
            err = "Possible values are :\n"
            for val in values :
                err = err + "\t- " + str(val) + "\n"
            raise ValueError(err)

    def _factory_reset(self):
        new_val = [0xFF, 0]
        self._push_value('register', new_val)

    def factory_reset(self):
        self._factory_reset()
        print("Motor reseted => baudrate : 1000000, ID : same")
        print("you should start 'dxl_detect()' command and recreate your Pyluos object.")

    def retrieve_dxl(self):
        values = [9600, 19200, 57600, 115200, 200000, 250000, 400000, 500000, 1000000]
        for baud in values :
            self._baudrate(baud)
            time.sleep(0.1)
            slef._factory_reset()
            time.sleep(0.1)
        self.baudrate(1000000)
        time.sleep(0.1)
        self.dxl_detect()
        print("Motor reseted => baudrate : 1000000, ID : same")
        print("recreate your Pyluos object.")
