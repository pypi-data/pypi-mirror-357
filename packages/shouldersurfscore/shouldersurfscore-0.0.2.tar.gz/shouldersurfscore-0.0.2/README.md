# `shouldersurfscore`
This library helps researchers in lab settings develop better metrics to understand the practical password guess quality of shoulder surfing and password guessing attacks. 

The library provides the following (their complexity for you to use in parentheses):
 - (Advanced): a nuanced set of classes to build an experiment environment including different keyboard layouts, device lockout patterns, and different styles of attackers that can help to better estimate different 
 - (Medium): predefined equipment to make it easier to get up and running (e.g. an iPhone, with common login restrictions).
 - (Easy): defined scores to make it easier to reproduce other researchers' experiments (and when you're ready, hopefully yours too!).
 - (Easy): implementations of a few other common metrics for assessing password quality.

# Installation
To install, simply use:
```
pip install shouldersurfscore
```
# How-To Use

## Defined Labs
Pre-defined labs can be used to recreate scores used in others' experiments. 

For example:
```
from shouldersurfscore.defined_experiments.built_labs import initial_shouldersurfscore_paper_lab

initial_shouldersurfscore_paper_lab.run(
    actual_password='9163',
    observed_password='9613'
)

## Expected results:
#{'actual_password': '9163',
# 'observed_password': '9613',
# 'guess_index': 2,
# 'guess_percent': 1.9801980198019803e-06,
# 'practical_time': datetime.timedelta(0),
# 'device_unlocked': True}
```

## Other Metrics
## Predefined Objects
```{python}
from shouldersurfscore.classes import attacker, lab

# Define attacker
eve = attacker.Attacker(
    # Try observed password, then if that fails, try all other passwords.
    strategy=[
        'observed_guess',
        'sequential_guesses'
    ]
)

example_lab = lab.Lab(
    device=iphone,
    attacker=eve
)

example_lab.run(actual_password='2290', observed_password='9163')
```
## Classes