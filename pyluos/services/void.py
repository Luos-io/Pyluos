from .service import Service
import time

class Void(Service):

    def __init__(self, id, alias, device):
        Service.__init__(self, 'Void', id, alias, device)

    def _update(self, new_state):
        Service._update(self, new_state)

    def dxl_detect(self):
        self._push_value('reinit', 0)
        print ("To get new detected Dxl motors usable on pyluos you should recreate your Pyluos object.")

    def _factory_reset(self):
        new_val = [0xFF, 0]
        self._push_value('register', new_val)

    def factory_reset(self):
        self._factory_reset()
        print("Motor reseted => baudrate : 1000000, ID : same")
        print("you should start 'dxl_detect()' command and recreate your Pyluos object.")

    def retrieve_dxl(self):
        time.sleep(0.5)
        self.dxl_detect()
        print("Motor reseted => baudrate : 1000000, ID : same")
        print("recreate your Pyluos object.")
