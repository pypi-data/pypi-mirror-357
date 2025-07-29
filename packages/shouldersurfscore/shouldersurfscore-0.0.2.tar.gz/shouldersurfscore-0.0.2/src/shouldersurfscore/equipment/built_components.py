import datetime

from shouldersurfscore.classes import keyboard, timeout

normal_keyboard_list = [
    list('`1234567890-='),
    list('qwertyuiop[]\\'),
    list('asdfghjkl;\''),
    list('zxcvbnm,./')
]

normal_keyboard = keyboard.Keys(normal_keyboard_list, row_offset=[0, 1, 0.5, 0.5])

keypad_list = [
    list('123'),
    list('456'),
    list('789'),
    list('0')
]

normal_keypad = keyboard.Keys(keypad_list, row_offset=[0,0,0,1])

##################################################
#                iphone components               #
##################################################
# Timeout numbers from here:
#  - https://www.simplymac.com/ios/what-is-the-maximum-lockout-time-on-iphone
iphone_reset_timedeltas = [
    datetime.timedelta(0),
    datetime.timedelta(0),
    datetime.timedelta(0),
    datetime.timedelta(0),
    datetime.timedelta(0),
    datetime.timedelta(minutes=1),
    datetime.timedelta(minutes=5),
    datetime.timedelta(minutes=15),
    datetime.timedelta(minutes=60)
]

iphone_pin_lengths = [4, 6]

iphone_reset_tries = 10

iphone_timeout = timeout.Timeout(
    time_out_iterable=iphone_reset_timedeltas, 
    factory_reset_tries=iphone_reset_tries
)