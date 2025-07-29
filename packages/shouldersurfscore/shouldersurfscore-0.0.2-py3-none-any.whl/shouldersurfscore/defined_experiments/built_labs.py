from shouldersurfscore.classes.lab import Lab
from shouldersurfscore.classes.attacker import Attacker
from shouldersurfscore.equipment.built_devices import iphone

initial_shouldersurfscore_paper_lab = Lab(
    device=iphone,
    attacker=Attacker(
        strategy=[
            'observed_guess',
            'swap_adjacent',
            'sequential_guesses'
        ]
    )
)