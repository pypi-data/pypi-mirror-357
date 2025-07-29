from shouldersurfscore.classes import attacker, device
from typing import Dict

class Lab:
    def __init__(self, device: device.Device, attacker: attacker.Attacker):
        '''
        Initializes experiment object.
        '''
        self.device = device
        self.attacker = attacker

        self.results = []

    def run(self, actual_password: str, observed_password:str):
        '''
        Runs experiments based on the defined device and attacker, calculates metrics based on the results.

        Takes two arguments:
         - actual_password (str): The actual password of the device.
         - observed_password (str): The password the attacker observed.
        '''
        self.device.set_password(actual_password)
        self.attacker.obtain_device(observed_password=observed_password, device=self.device)

        result = self.attacker.break_in()
        self.results += [result]

        return result