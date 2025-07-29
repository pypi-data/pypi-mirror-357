from itertools import product
from shouldersurfscore.classes.timeout import DeviceLockout
import datetime

class Attacker:
    '''
    Class represents an attacker.

    This is used to structure how the attacker might try to break the password
    given a password and a device they are trying to break into.
    '''
    def __init__(self, strategy='default'):
        self.guessing_strategies = GuessingStrategies()
        self.strategy = []

        if strategy == 'default':
            self.strategy = [
                self.guessing_strategies.sequential_guesses
            ]
        else:
            for s in strategy:
                if type(s) == str:
                    self.strategy.append(getattr(self.guessing_strategies, s))
                else:
                    self.strategy.append(s)

    def obtain_device(self, observed_password, device):
        if not hasattr(device, 'password'):
            raise ValueError('Device must have password set.')
        
        self.guess_queue = []
        self.observed_password = observed_password
        self.device = device

    def _append_guesses(self, new_guesses):
        '''
        Helper function to make sure that new guesses are allowed before adding them to the guess queue.
        '''
        guesses = [guess for guess in new_guesses if guess not in self.device.prohibited]
        guesses = [guess for guess in guesses if guess not in self.guess_queue]

        self.guess_queue += guesses

    def break_in(self) -> dict:
        '''
        Method to simulate an attacker breaking into a device, from their strategies based on starting guess `guess`. 

        Returns a dictionary with a few metrics calculated in it.
        '''
        if not hasattr(self, 'device'):
            raise ValueError('No device found. Must call self.obtain_device() before breaking in.')
        
        analysis = {}

        for strategy in self.strategy:
            self._append_guesses(
                strategy(
                    observed_pin=self.observed_password,
                    valid_pin_lengths=self.device.valid_pin_lengths, 
                    key_space=self.device.key_space
                )
            )

        analysis['actual_password'] = self.device.password
        analysis['observed_password'] = self.observed_password
        analysis['guess_index'] = self.guess_queue.index(self.device.password)
        analysis['guess_percent'] = analysis['guess_index'] / len(self.guess_queue)

        device_unlocked = True

        for _ in range(analysis['guess_index']):
            try:
                self.device.timeout.make_guess()
            except DeviceLockout:
                device_unlocked = False
                break

        analysis['practical_time'] = self.device.timeout.elapsed_time
        analysis['device_unlocked'] = device_unlocked

        return analysis

class GuessingStrategies:
    def sequential_guesses(self, observed_pin, valid_pin_lengths, key_space):
        '''
        Sequential guess strategy. 

        The attacker uses each character in the password in order.

        This will guess any password that has not already been guessed.
        '''
        guesses = []
        for length in valid_pin_lengths:
            guesses += list(product(key_space, repeat=length))

        guesses = [''.join(guess) for guess in guesses]
        return guesses

    def observed_guess(self, observed_pin, valid_pin_lengths, key_space):
        '''
        Guessing the PIN that the attacker observed.

        For example:
            If the observed pin is 'ABCD', this simply appends 'ABCD' to the queue.

        This adds 1 new entry to the guess queue.
        '''
        return [observed_pin]

    def swap_adjacent(self, observed_pin, valid_pin_lengths, key_space):
        '''
        Swaps each value in pin with the value following it.

        For example:
            If the observed pin is 'ABCD', this will add the following
            to the guess queue:
                'BACD',
                'ACBD',
                'ABDC'

        This adds len(observed_pin) - 1 new entries to guess queue.
        '''
        swapped_guesses = []
        for i in range(len(observed_pin) - 1):
            shuffled = list(observed_pin)

            shuffled[i] = observed_pin[i + 1]
            shuffled[i + 1] = observed_pin[i]
            swapped_guesses.append(''.join(shuffled))

        return swapped_guesses