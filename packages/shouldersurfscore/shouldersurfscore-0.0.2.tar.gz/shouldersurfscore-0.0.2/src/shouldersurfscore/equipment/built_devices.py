from shouldersurfscore.equipment.built_components import iphone_timeout, normal_keypad, iphone_pin_lengths
from shouldersurfscore.classes.device import Device

iphone = Device(
    keypad=normal_keypad,
    timeout=iphone_timeout,
    valid_pin_lengths=iphone_pin_lengths
)