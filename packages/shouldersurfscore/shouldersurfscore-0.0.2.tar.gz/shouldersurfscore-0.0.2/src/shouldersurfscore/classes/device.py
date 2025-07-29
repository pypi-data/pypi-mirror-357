from itertools import product
from typing import List, Optional
from copy import deepcopy
import numpy as np

from shouldersurfscore.classes.timeout import Timeout
from shouldersurfscore.classes.keyboard import Keys

class Device:
    """
    Represents a security device with a password, keypad, and timeout mechanism.

    Attributes
    ----------
    valid_pin_lengths : List[int]
        A list of integers representing the valid lengths for a PIN.
    password : str
        The current password of the device.
    keypad : Keys
        An instance of the Keys class representing the device's keypad.
    timeout : Timeout
        An instance of the Timeout class managing failed password attempts.
    key_space : List[str]
        A list of all valid characters (keys) that can be part of a password.
        Derived from the keypad's positions if not explicitly provided.
    prohibited : List[str]
        A list of passwords that are explicitly disallowed, primarily generated
        based on `duplicate_keys_allowed` setting.
    locked : bool
        The current locked status of the device. True if locked, False if unlocked.
    """
    def __init__(self, keypad: Keys, timeout: Timeout, valid_pin_lengths: List[int], password: Optional[str] = None,
                 duplicate_keys_allowed: bool = True, sequential_keys_allowed: bool = True,
                 key_space: Optional[List[str]] = None) -> None:
        """
        Initializes a Device instance.

        Parameters
        ----------
        password : str
            The initial password for the device. This password will be validated
            against `valid_pin_lengths`, `key_space`, and `prohibited` list.
        keypad : Keys
            An instance of the Keys class representing the physical keypad of the device.
        timeout : Timeout
            An object that manages and tracks failed login attempts (e.g., locking mechanism).
        valid_pin_lengths : List[int]
            A list of allowed integer lengths for any PIN/password.
        duplicate_keys_allowed : bool, optional
            If False, passwords consisting of repeated characters (e.g., "111", "AAAA")
            will be prohibited. Defaults to True.
        sequential_keys_allowed : bool, optional
            If False, passwords with sequential keys (e.g., "123", "abc") will be prohibited.
            Defaults to True.
        key_space : Optional[List[str]], optional
            A list of characters that are valid keys on the keypad. If None, it
            defaults to all keys defined in `keypad.positions.keys()`.

        Raises
        ------
        ValueError
            If the initial `password` does not meet the defined criteria
            (length, character validity, or if it's in the prohibited list).
        """
        self.valid_pin_lengths = valid_pin_lengths
        self.keypad = keypad
        self.original_timeout = timeout

        if key_space:
            self.key_space=key_space
        else:
            self.key_space = self.keypad.positions.keys()
            
        self.prohibited = []

        if not sequential_keys_allowed:
            # Generate the key sequence from the key_space. This needs to be long enough that
            # it works when the pin length is greater thanthe number of keys in the key_space.
            key_sequence = ''.join(self.key_space)
            # Lengthen key_sequence until it is long enough
            while len(key_sequence) < len(self.key_space) + np.max(self.valid_pin_lengths):
                key_sequence += key_sequence

            # Get slices of key_sequence
            for i, length in product(range(len(self.key_space)), self.valid_pin_lengths):
                self.prohibited.append(key_sequence[i:i+length])
                
        if not duplicate_keys_allowed:
            for key, length in product(self.key_space, self.valid_pin_lengths):
                self.prohibited.append(key * length)

        if password:
            self.set_password(password)
        
        self.reset_device()
        
    def reset_device(self):
        """
        Resets the device to its default locked state, and resets self.timeout
        """
        self.locked=True
        self.timeout = deepcopy(self.original_timeout)

    def set_password(self, password):
        """
        Sets the device password after performing several validation checks.

        The password must adhere to the following rules:
        1. It must not be in the `prohibited` passwords list.
        2. Its length must be among the `valid_pin_lengths`.
        3. All characters in the password must be present in the `key_space`.

        Parameters
        ----------
        password : str
            The new password to set for the device.

        Raises
        ------
        ValueError
            If the provided password fails any of the validation checks.
        """
        # Reset the device to ensure it's locked.
        self.reset_device()

        # Is the password in the prohibited list?
        if password in self.prohibited:
            raise ValueError('Password in prohibited passwords list. Check the .prohibited attribute to get a list of passwords that are banned.')
        
        # Is the password length valid?
        elif len(password) not in self.valid_pin_lengths:
            raise ValueError('Password not a valid length. Check the .valid_pin_lengths attribute to get a list of valid password lengths.')
        
        # Are all characters in the password part of the valid key space?
        elif len([c for c in password if c not in self.key_space]) != 0:
            raise ValueError('Password characters are not valid. Check the .key_space attribute for a list of valid keys.')

        # If all validation checks pass, set the new password.
        else:
            self.password = password

    def enter_password(self, attempted_password):
        """
        Attempts to unlock the device with the provided password.

        If the `attempted_password` matches the device's `password`:
        - The device's `locked` status is set to False (unlocked).
        Otherwise (if the password does not match):
        - The `make_guess()` method of the `timeout` object is called,
          which typically increments a failed attempt counter or triggers a lockout.

        Parameters
        ----------
        attempted_password : str
            The password string provided by the user to unlock the device.
        """
        # Compare the attempted password with the stored password.
        if attempted_password == self.password:
            self.locked = False # Unlock the device if passwords match.
        else:
            # If passwords do not match, inform the timeout mechanism of a failed attempt.
            self.timeout.make_guess()