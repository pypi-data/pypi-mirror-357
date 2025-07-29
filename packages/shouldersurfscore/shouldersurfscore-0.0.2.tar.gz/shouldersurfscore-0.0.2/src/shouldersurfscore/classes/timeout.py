import datetime

class DeviceLockout(Exception):
    def __init__(self, number_of_guesses):
        message = f'Device is now locked, after {number_of_guesses} guesses.'
        super().__init__(message)

class ConsistentPause:
    def __init__(self, pause=None):
        '''
        Initializes ConsistentPause object, takes single argument: pause, indicating how long the pause
        for each guess should be in seconds.

        If no value for pause is provided, the pause is assumed to be 0 seconds.
        '''
        if pause:
            self.pause = datetime.timedelta(seconds=pause)
        else:
            self.pause = datetime.timedelta(seconds=0)

    def __next__(self):
        return self.pause

class Timeout:
    def __init__(self, time_out_iterable, factory_reset_tries: int):
        '''
        Object represents the timeout feature on a password entry interface after a bad guess.

        This takes a time_out_iterable, which is something that returns a datetime.timedelta, e.g. a list that
        represents timeouts, or a different iterable that works with the next() function, e.g. like an instance of the 
        ConsistentPause object. 
        '''
        self.time_out_iterable = time_out_iterable
        self.factory_reset_tries = factory_reset_tries

        self.elapsed_time = datetime.timedelta(seconds=0.0)
        self.guesses = 0
    

    def make_guess(self):
        '''
        Represents a password guess. This will add the next item from the time_out_iterable to the elapsed_time attribute.
        
        If the number of guesses == factory_reset_tries, this will raise DeviceLockout.
        '''
        self.guesses += 1

        if self.guesses == self.factory_reset_tries:
            raise DeviceLockout(self.guesses)
        
        if type(self.time_out_iterable) == list:
            try:
                self.elapsed_time += self.time_out_iterable.pop(0)
            except IndexError:
                self.time_out_iterable = ConsistentPause(0) # Handles error, still shows total elapsed time.
                self.elapsed_time += datetime.timedelta(seconds=0)
        
        else:
            self.elapsed_time += next(self.time_out_iterable)